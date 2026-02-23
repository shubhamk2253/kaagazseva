from flask import Flask
from config import Config
from extensions import db, jwt, cors, migrate
from core.responses import error_response
from infrastructure.logging import setup_logging

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1. Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # 2. Setup Logging (Infrastructure Layer)
    setup_logging(app)

    # 3. Register Blueprints (Route Layer)
    from routes.auth_routes import auth_bp
    from routes.customer_routes import customer_bp
    from routes.agent_routes import agent_bp
    from routes.admin_routes import admin_bp
    from routes.payment_routes import payment_bp
    from routes.public_routes import public_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(customer_bp, url_prefix='/api/customer')
    app.register_blueprint(agent_bp, url_prefix='/api/agent')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')
    app.register_blueprint(public_bp, url_prefix='/api/public')

    # 4. Global Error Handler (The Safety Net)
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Captures any unhandled error and returns a clean JSON response."""
        app.logger.error(f"Unhandled Exception: {str(e)}")
        return error_response(
            message="An internal server error occurred", 
            status_code=500
        )

    # 5. Health Check for Render
    @app.route('/health')
    def health_check():
        return {
            "status": "healthy", 
            "service": "kaagazseva-backend",
            "version": "1.0.0"
        }, 200

    return app

# For Render/Gunicorn to pick up the app instance
app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
