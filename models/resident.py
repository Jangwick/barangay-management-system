from datetime import datetime
from models import db

class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    birth_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships to Blotter records
    # Blotters where this resident is the complainant
    blotters_as_complainant = db.relationship(
        'Blotter', 
        foreign_keys='Blotter.complainant_resident_id', 
        backref='complainant_resident_info', 
        lazy=True
    )
    # Blotters where this resident is the respondent
    blotters_as_respondent = db.relationship(
        'Blotter', 
        foreign_keys='Blotter.respondent_resident_id', 
        backref='respondent_resident_info', 
        lazy=True
    )

    def get_absolute_url(self):
        """
        Returns the absolute URL for this resident instance.
        This can be used in templates to link to a resident's detail page.
        Assumes a route like '/residents/<resident_id>' exists.
        """
        return f"/residents/{self.id}"
