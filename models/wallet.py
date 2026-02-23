from extensions import db
from datetime import datetime
from uuid import uuid4

class WalletTransaction(db.Model):
    __tablename__ = 'wallet_transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    agent_id = db.Column(db.String(36), db.ForeignKey('agents.id'), nullable=False)
    application_id = db.Column(db.String(36), db.ForeignKey('applications.id'), nullable=True)
    
    transaction_type = db.Column(db.String(20)) # CREDIT (Earnings), DEBIT (Payout)
    amount = db.Column(db.Float, nullable=False)
    running_balance = db.Column(db.Float, nullable=False) # Balance AFTER this txn
    
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
