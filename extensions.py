from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate

# Initialize extensions without an app context initially
# This allows them to be imported into Models and Services safely
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()

# Standardized SQLAlchemy configuration for Supabase/Postgres
# This ensures we use the modern engine features
db.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
