from models import db

class Official(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    start_term = db.Column(db.Date, nullable=False)
    end_term = db.Column(db.Date, nullable=False)
    contact_number = db.Column(db.String(20))
