# app/__init__.py
# Defines create_app() to build the Flask app.

import os
from flask import Flask
from config import Config


def create_app(config_class=Config):
    """
    Application factory function.
    Creates and configures the Flask app instance.
    """
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Load configuration from Config class
    app.config.from_object(config_class)

    # Make sure WORKDIR exists
    os.makedirs(app.config["WORKDIR"], exist_ok=True)

    # Import and register routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
