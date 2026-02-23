from extensions import db
from datetime import datetime

class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    is_verified = db.Column(db.Boolean, default=False)
    service_radius = db.Column(db.Integer, default=10) # in KM
    base_pincode = db.Column(db.String(10), nullable=False)
    
    # Financial tracking
    total_earnings = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    
    # Constraints
    max_workload = db.Column(db.Integer, default=5)
    current_workload = db.Column(db.Integer, default=0)

    # Relationships
    wallet_records = db.relationship('WalletTransaction', backref='agent', lazy=True)
    assigned_applications = db.relationship('Application', backref='assigned_agent', lazy=True)
