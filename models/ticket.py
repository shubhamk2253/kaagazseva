class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    application_id = db.Column(db.String(36), db.ForeignKey('applications.id'))
    
    subject = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="open") # open, resolved, closed
    priority = db.Column(db.String(10), default="medium")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
