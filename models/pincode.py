from extensions import db

class Pincode(db.Model):
    __tablename__ = 'pincodes'
    pincode = db.Column(db.String(10), primary_key=True)
    state_id = db.Column(db.Integer, db.ForeignKey('states.id'), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_serviceable = db.Column(db.Boolean, default=True)
