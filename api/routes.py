from flask import Blueprint, request, jsonify
import torch
import torchaudio
import numpy as np
from .utils import Utils

# Get the utils instance
utils_instance = Utils.get_instance()

model = utils_instance.model
feature_extractor = utils_instance.feature_extractor
tokenizer = utils_instance.tokenizer

bp = Blueprint('api', __name__)

@bp.route('/predict', methods=['POST'])
def predict():
    try:
        # Step 1: Load the audio from the POST request
        if 'audio' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Check for file format for additional safety
        if not file.filename.endswith('.wav'):
            return jsonify({'error': 'Invalid file format. Only .wav files are supported.'}), 400

        waveform, sampling_rate = torchaudio.load(file)

        # Step 2: Preprocessing
        # Resample to 16kHz
        if sampling_rate != 16000:
            resampler = torchaudio.transforms.Resample(sampling_rate, 16000)
            waveform = resampler(waveform)
            sampling_rate = 16000

        # Extract features
        input_features = utils_instance.feature_extractor(waveform.numpy().squeeze(), sampling_rate=sampling_rate).input_features[0]

        # Step 3: Predict using the model
        # Convert input_features to tensor and run through the model
        input_tensor = torch.tensor(input_features[np.newaxis, ...])  # Adding batch dimension
        with torch.no_grad():
            # Adjust this depending on how your model takes input
            output = utils_instance.model.generate(input_tensor, max_new_tokens=120)

        # Decode the output (Get the actual transcription)
        predicted_text = utils_instance.tokenizer.decode(output[0], skip_special_tokens=True)
        simplified_text, tones = utils_instance.post_process_text(predicted_text)

        return jsonify({"prediction": simplified_text, "tones": tones})

    except torchaudio.common_errors as e:  # Replace `common_errors` with actual exception class(es) from torchaudio
        return jsonify({'error': f'Audio processing error: {str(e)}'}), 500

    except Exception as e:  # Catch all other exceptions
        return jsonify({'error': f'Unexpected error occurred: {str(e)}'}), 500
