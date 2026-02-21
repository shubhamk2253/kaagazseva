from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
import random
from datetime import datetime, timedelta
from sqlalchemy import text

# Core modules
from config import JWT_SECRET_KEY
from database import init_db
from models import db

# Route blueprints
from routes.auth_routes import auth_bp
from routes.agent_routes import agent_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.public_roue import public_bp   # keep same name if file is public_roue.py

def create_app():
    app = Flask(__name__)
    CORS(app)

    # ---------------- CONFIG ----------------
    app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB upload limit

    JWTManager(app)

    # ---------------- REGISTER BLUEPRINTS ----------------
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(agent_bp, url_prefix="/api/agent")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(public_bp, url_prefix="/api")

    # ---------------- HOME ROUTE ----------------
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "KaagazSeva Backend is Live 🚀"
        }

    # ---------------- HEALTH CHECK ----------------
    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "service": "backend"
        }

    # ---------------- OTP & SERVICE ROUTES ----------------

    @app.route("/api/send-otp", methods=["POST"])
    def send_otp():
        data = request.json
        mobile = data.get("mobile")

        if not mobile:
            return jsonify({"error": "Mobile required"}), 400

        otp = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        db.session.execute(text("""
            INSERT INTO otp_sessions (mobile, otp_code, expires_at)
            VALUES (:mobile, :otp, :expires_at)
        """), {
            "mobile": mobile,
            "otp": otp,
            "expires_at": expires_at
        })

        db.session.commit()
        print(f"OTP for {mobile}: {otp}")  # For testing only
        return jsonify({"message": "OTP sent"})

    @app.route("/api/verify-otp", methods=["POST"])
    def verify_otp():
        data = request.json
        mobile = data.get("mobile")
        otp = data.get("otp")

        result = db.session.execute(text("""
            SELECT * FROM otp_sessions
            WHERE mobile = :mobile
            AND otp_code = :otp
            AND is_used = FALSE
            AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
        """), {
            "mobile": mobile,
            "otp": otp
        }).fetchone()

        if not result:
            return jsonify({"error": "Invalid or expired OTP"}), 400

        db.session.execute(text("""
            UPDATE otp_sessions
            SET is_used = TRUE
            WHERE id = :id
        """), {"id": result.id})

        user = db.session.execute(text("""
            SELECT * FROM users WHERE mobile = :mobile
        """), {"mobile": mobile}).fetchone()

        if not user:
            db.session.execute(text("""
                INSERT INTO users (id, mobile, role)
                VALUES (gen_random_uuid(), :mobile, 'customer')
            """), {"mobile": mobile})
            db.session.commit()

            user = db.session.execute(text("""
                SELECT * FROM users WHERE mobile = :mobile
            """), {"mobile": mobile}).fetchone()

        access_token = create_access_token(identity=str(user.id))
        db.session.commit()

        return jsonify({
            "message": "Login successful",
            "access_token": access_token
        })

    @app.route("/api/apply-service", methods=["POST"])
    @jwt_required()
    def apply_service():
        user_id = get_jwt_identity()
        # continue with logic
        return jsonify({"message": "Service applied", "user_id": user_id})

    return app

# ---------------- CREATE APP ----------------
app = create_app()

# ✅ Always initialize database (even on Render)
init_db()

# ---------------- RUN SERVER (Local Only) ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
