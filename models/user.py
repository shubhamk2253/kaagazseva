from extensions import db
from datetime import datetime
from uuid import uuid4

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    phone = db.Column(db.String(15), unique=True, nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False) # admin, agent, customer
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
