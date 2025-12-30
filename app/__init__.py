from flask import Flask

from app.services.fund_catalog import initialize_available_funds


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY="dev")  # TODO: override via env var in production

    initialize_available_funds()

    from .routes import bp as main_bp  # pylint:disable=import-outside-toplevel

    app.register_blueprint(main_bp)
    return app
