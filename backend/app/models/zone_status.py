from app import db
from datetime import datetime

class ZoneStatus(db.Model):
    __tablename__ = 'zone_statuses'

    id = db.Column(db.Integer, primary_key=True)
    
    # Zone
    zone_id = db.Column(
        db.Integer,
        db.ForeignKey('zones.id'),
        nullable=False,
        unique=True  # Une seule status par zone
    )
    
    # Santé
    health_score = db.Column(db.Float)  # 0-100
    status = db.Column(db.String(50), default='unknown')  # healthy/stressed/critical
    risk_level = db.Column(db.String(50))  # low/medium/high/critical
    
    # Détails
    temperature_avg = db.Column(db.Float)
    humidity_avg = db.Column(db.Float)
    air_quality_index = db.Column(db.Float)
    sensor_coverage = db.Column(db.Float)  # % de couverture
    
    # Confiance
    confidence_score = db.Column(db.Float)  # 0-1
    
    # Timestamps
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sensor_reading = db.Column(db.DateTime)
    
    # Relationships
    zone = db.relationship('Zone', backref='status', uselist=False)
    
    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "health_score": self.health_score,
            "status": self.status,
            "risk_level": self.risk_level,
            "temperature_avg": self.temperature_avg,
            "humidity_avg": self.humidity_avg,
            "air_quality_index": self.air_quality_index,
            "sensor_coverage": self.sensor_coverage,
            "confidence_score": self.confidence_score,
            "updated_at": self.updated_at.isoformat(),
            "last_sensor_reading": self.last_sensor_reading.isoformat() if self.last_sensor_reading else None
        }
    
    def __repr__(self):
        return f"<ZoneStatus {self.zone_id}: {self.status}>"
