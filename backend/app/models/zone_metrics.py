from app import db
from datetime import datetime

class ZoneMetrics(db.Model):
    __tablename__ = 'zone_metrics'

    id = db.Column(db.Integer, primary_key=True)
    
    zone_id = db.Column(
        db.Integer,
        db.ForeignKey('zones.id'),
        nullable=False
    )
    
    # Timestamp pour série temporelle
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Métriques agrégées
    avg_temperature = db.Column(db.Float)
    avg_humidity = db.Column(db.Float)
    avg_air_quality = db.Column(db.Float)
    
    # Végétation (NDVI)
    avg_ndvi = db.Column(db.Float)  # Normalized Difference Vegetation Index
    ndvi_trend = db.Column(db.String(50))  # increasing/stable/decreasing
    
    # Couverture capteurs
    active_sensors = db.Column(db.Integer)
    total_sensors = db.Column(db.Integer)
    coverage_percent = db.Column(db.Float)
    
    # Qualité données
    data_quality = db.Column(db.Float)  # 0-1
    
    # Relationships
    zone = db.relationship('Zone', backref='metrics')
    
    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "timestamp": self.timestamp.isoformat(),
            "avg_temperature": self.avg_temperature,
            "avg_humidity": self.avg_humidity,
            "avg_air_quality": self.avg_air_quality,
            "avg_ndvi": self.avg_ndvi,
            "ndvi_trend": self.ndvi_trend,
            "active_sensors": self.active_sensors,
            "total_sensors": self.total_sensors,
            "coverage_percent": self.coverage_percent,
            "data_quality": self.data_quality
        }
    
    def __repr__(self):
        return f"<ZoneMetrics {self.zone_id} at {self.timestamp}>"
