from flask import Flask
from .routes import bp
from .utils import model, feature_extractor, tokenizer  # This line imports from utils.py

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
