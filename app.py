from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from sqlalchemy import text
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Core internal modules
from config import JWT_SECRET_KEY
from models import db

# Route blueprints
from routes.auth_routes import auth_bp
from routes.agent_routes import agent_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.public_routes import public_bp


def create_app():
    app = Flask(__name__)

    # ---------------- SECURITY: RATE LIMITING ----------------
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    # Enable CORS
    CORS(app)

    # ---------------- CONFIGURATION ----------------
    db_url = os.getenv("DATABASE_URL", "sqlite:///database.db")

    # Fix postgres:// issue (Render/Railway)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    # ---------------- EXTENSIONS ----------------
    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)   # ✅ Production migration system

    # ---------------- REGISTER BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(public_bp, url_prefix="/api")

    # ---------------- CORE ROUTES ----------------
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "KaagazSeva Backend is Live 🚀",
            "version": "2.0.0"
        }

    @app.route("/health")
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500

    # ---------------- ERROR HANDLERS ----------------
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
