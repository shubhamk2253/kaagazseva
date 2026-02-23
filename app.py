from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from sqlalchemy import text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import JWT_SECRET_KEY
from models import db

from routes.auth_routes import auth_bp
from routes.agent_routes import agent_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.public_routes import public_bp


def create_app():
    app = Flask(__name__)

    # ---------------- RATE LIMITING ----------------
    Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    CORS(app)

    # ---------------- DATABASE CONFIG ----------------
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL not set")

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    # ---------------- EXTENSIONS ----------------
    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)

    # ---------------- BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(public_bp, url_prefix="/api")

    # ---------------- HEALTH ----------------
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "KaagazSeva Backend Live 🚀",
            "version": "2.0.0"
        }

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
