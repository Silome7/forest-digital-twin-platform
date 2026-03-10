from app import db
from datetime import datetime

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)

    # IMPORTANT : centré zone
    zone_id = db.Column(
        db.Integer,
        db.ForeignKey('zones.id'),
        nullable=False
    )

    model_type = db.Column(db.String(50), nullable=False)
    model_version = db.Column(db.String(50))

    risk_score = db.Column(db.Float)  # ex: 0.85
    prediction_class = db.Column(db.String(50))  # low/medium/high
    confidence_score = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    forecast_date = db.Column(db.DateTime)

    # Relationships
    zone = db.relationship('Zone', backref='predictions')

    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "model_type": self.model_type,
            "model_version": self.model_version,
            "risk_score": self.risk_score,
            "prediction_class": self.prediction_class,
            "confidence_score": self.confidence_score,
            "created_at": self.created_at.isoformat(),
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None
        }

    def __repr__(self):
        return f"<Prediction {self.model_type} - Zone {self.zone_id}>"
