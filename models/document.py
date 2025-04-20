from datetime import datetime
from models import db

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    resident = db.relationship('Resident', backref=db.backref('documents', lazy=True))
    document_type = db.Column(db.String(50), nullable=False)
    issue_date = db.Column(db.Date, default=datetime.utcnow)
    purpose = db.Column(db.String(200))
