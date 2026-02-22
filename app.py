from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from sqlalchemy import text

# Core internal modules
from config import JWT_SECRET_KEY
from database import init_db
from models import db

# Route blueprints
from routes.auth_routes import auth_bp
from routes.agent_routes import agent_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.public_routes import public_bp

def create_app():
    app = Flask(__name__)
    
    # Enable CORS
    CORS(app)

    # ---------------- CONFIGURATION ----------------
    # Unified Database: Fixed for Heroku/Render/Railway (Postgres vs PostgreSQL)
    db_url = os.getenv("DATABASE_URL", "sqlite:///database.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    # Initialize extensions
    db.init_app(app)
    JWTManager(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(public_bp, url_prefix="/api")

    # ---------------- CORE SYSTEM ROUTES ----------------
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "KaagazSeva Backend is Live 🚀",
            "version": "1.0.1"
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

# ---------------- APPLICATION STARTUP ----------------
app = create_app()

with app.app_context():
    db.create_all()
    init_db()

if __name__ == "__main__":
    # Get port from environment
    port = int(os.getenv("PORT", 5000))
    # Check if we are in development mode
    debug_mode = os.getenv("FLASK_ENV") == "development"
    # Run app
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
