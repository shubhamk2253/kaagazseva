from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# Core modules
from config import JWT_SECRET_KEY
from database import init_db

# Route blueprints
from routes.auth_routes import auth_bp
from routes.agent_routes import agent_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.public_roue import public_bp   # FIXED NAME

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------- CONFIG ----------------
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    JWTManager(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(public_bp, url_prefix="/api")

    # ---------------- HEALTH CHECK ----------------
    @app.route("/health")
    def health():
        return {"status": "ok", "service": "kaagazseva-backend"}

    return app


# ---------------- RUN SERVER ----------------
app = create_app()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
