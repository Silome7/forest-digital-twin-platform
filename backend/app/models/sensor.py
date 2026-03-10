from app import db

class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    battery_level = db.Column(db.Integer, nullable=True, default=100)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)

    # Relation vers Zone
    zone_id = db.Column(db.Integer, db.ForeignKey('zones.id'), nullable=True)
    zone = db.relationship('Zone', back_populates='sensors')

    # Relation vers SensorData
    data = db.relationship(
        "SensorData",
        back_populates="sensor",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Sensor {self.name} ({self.type})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "unit": self.unit,
            "status": self.status,
            "battery_level": self.battery_level,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }
