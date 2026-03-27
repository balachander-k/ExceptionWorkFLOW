from flask import Flask

from app.config import Config
from app.extensions import db
from app.routes.ai_routes import ai_bp
from app.routes.approval_routes import approval_bp
from app.routes.attachment_routes import attachment_bp
from app.routes.auth_routes import auth_bp
from app.routes.comment_routes import comment_bp
from app.routes.exception_routes import exception_bp
from app.routes.opportunity_routes import opportunity_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(exception_bp)
    app.register_blueprint(approval_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(attachment_bp)
    app.register_blueprint(opportunity_bp)
    app.register_blueprint(ai_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
