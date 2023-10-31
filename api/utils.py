from transformers import WhisperFeatureExtractor, WhisperTokenizer, WhisperForConditionalGeneration
import opencc
from pypinyin import lazy_pinyin, Style
import requests
import os

def download_model():
    model_url = "https://drive.google.com/uc?export=download&id=1Inmqv4IkjU6wCIB0Vvjzs0M88epXPEtY"
    model_save_path = "./model/pytorch_model.bin"

    if not os.path.exists("./model"):
        os.makedirs("./model")

    try:
        # Initial request to get the confirm token
        session = requests.Session()
        response = session.get(model_url, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                token = value
                break

        if token:
            model_url += "&confirm=" + token

        # Downloading the file
        response = session.get(model_url, stream=True)
        with open(model_save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print("Model downloaded successfully.")

    except requests.RequestException as e:
        print(f"Error downloading the model: {e}")
    except Exception as e:
        print(f"Error occurred: {e}")


model_path = "./model"
_instance = None

class Utils:

    def __init__(self):
        download_model()
        try:
            self.model = WhisperForConditionalGeneration.from_pretrained(model_path)
            self.feature_extractor = WhisperFeatureExtractor.from_pretrained("openai/whisper-small")
            self.tokenizer = WhisperTokenizer.from_pretrained("openai/whisper-small", language="chinese", task="transcribe")
            self.converter = opencc.OpenCC('t2s')
        except Exception as e:
            print(f"Error initializing the utilities: {e}")
            raise e

    @staticmethod
    def get_instance():
        global _instance
        if _instance is None:
            _instance = Utils()
        return _instance

    def post_process_text(self, text):
        # Convert text to Simplified Chinese if it's not
        simplified_text = self.converter.convert(text)

        # Convert Chinese characters into Pinyin with tone numbers
        pinyin = lazy_pinyin(simplified_text, style=Style.TONE3)

        # Words that often take a neutral tone in daily speech
        often_neutral = ["个", "么", "了"]

        # Extract tone numbers from the Pinyin and handle tone sandhi
        tones = ""
        for i, word in enumerate(pinyin):
            current_tone = word[-1] if word[-1].isdigit() else "5"

            # Handle third-tone sandhi
            if current_tone == '3' and i < len(pinyin) - 1:  
                next_word = pinyin[i + 1]
                next_tone = next_word[-1] if next_word[-1].isdigit() else "5"
                
                # If next tone is third tone, current word changes to second tone
                if next_tone == '3':
                    current_tone = '2'

            # Handle tone change for "一"
            if simplified_text[i] == "一":
                next_tone = pinyin[i + 1][-1] if i + 1 < len(pinyin) and pinyin[i + 1][-1].isdigit() else "5"
                current_tone = '2' if next_tone == '4' else '4'

            # Handle tone change for "不"
            if simplified_text[i] == "不" and i + 1 < len(pinyin):
                next_tone = pinyin[i + 1][-1] if pinyin[i + 1][-1].isdigit() else "5"
                current_tone = '2' if next_tone == '4' else '4'

            # Handle words that often take a neutral tone
            if simplified_text[i] in often_neutral:
                current_tone = '5'

            tones += current_tone

        return simplified_text, tones

