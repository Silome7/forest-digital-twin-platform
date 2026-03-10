from app import db

class Zone(db.Model):
    __tablename__ = 'zones'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    forest_id = db.Column(db.Integer, db.ForeignKey('forests.id'), nullable=False)
    location = db.Column(db.String(200))
    surface = db.Column(db.Float)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relations
    forest = db.relationship('Forest', back_populates='zones')
    sensors = db.relationship('Sensor', back_populates='zone', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "forest_id": self.forest_id,
            "location": self.location,
            "surface": self.surface,
            "description": self.description,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

    def __repr__(self):
        return f"<Zone {self.name}>"
