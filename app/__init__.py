from flask import Flask
from .config import Config
from .routes.co2 import bp as co2_bp

def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # register blueprints
    app.register_blueprint(co2_bp, url_prefix="/")

    return app
