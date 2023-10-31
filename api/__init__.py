from flask import Flask
from .routes import bp
from .utils import Utils

utils_instance = Utils.get_instance()

model = utils_instance.model
feature_extractor = utils_instance.feature_extractor
tokenizer = utils_instance.tokenizer

def create_app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app
