from flask import Blueprint, request, jsonify
import torch
import torchaudio
import numpy as np
from .utils import model, feature_extractor, tokenizer, post_process_text



bp = Blueprint('api', __name__)

@bp.route('/predict', methods=['POST'])


def predict():
    print("request.files:", request.files)
    print("request.form:", request.form)

    # Step 1: Load the audio from the POST request
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    waveform, sampling_rate = torchaudio.load(file)

    # Step 2: Preprocessing
    # Resample to 16kHz
    if sampling_rate != 16000:
        resampler = torchaudio.transforms.Resample(sampling_rate, 16000)
        waveform = resampler(waveform)
        sampling_rate = 16000
    
    # Extract features
    input_features = feature_extractor(waveform.numpy().squeeze(), sampling_rate=sampling_rate).input_features[0]

    # Tokenization (optional, depending on your model's requirements)
    # We're skipping this part as your model might not require tokenization for audio-to-text prediction

    # Step 3: Predict using the model
    # Convert input_features to tensor and run through the model
    input_tensor = torch.tensor(input_features[np.newaxis, ...])# Adding batch dimension
    with torch.no_grad():
        # Adjust this depending on how your model takes input
        output = model.generate(input_tensor, max_new_tokens=120)

    # Decode the output (Get the actual transcription)
    predicted_text = tokenizer.decode(output[0], skip_special_tokens=True)
    simplified_text, tones = post_process_text(predicted_text)
    return jsonify({"prediction": simplified_text, "tones": tones})