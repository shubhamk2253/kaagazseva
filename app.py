from flask import Flask
from config import Config
from extensions import db, jwt, cors, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints (We will create these next)
    # from routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "kaagazseva-backend"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
