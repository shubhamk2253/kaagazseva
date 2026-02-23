from extensions import db
from datetime import datetime
from uuid import uuid4

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    agent_id = db.Column(db.String(36), db.ForeignKey('agents.id'), nullable=True)
    service_id = db.Column(db.Integer, nullable=False)
    
    status = db.Column(db.String(30), default="pending_payment")
    pincode = db.Column(db.String(10), nullable=False)
    
    # Document keys from S3
    document_url = db.Column(db.String(500), nullable=True)
    
    # Financials
    payment_amount = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(100), nullable=True) # Razorpay ID
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
