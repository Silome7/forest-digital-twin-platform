from app import db
from datetime import datetime

class SHAPExplanation(db.Model):
    __tablename__ = 'shap_explanations'

    id = db.Column(db.Integer, primary_key=True)

    prediction_id = db.Column(
        db.Integer,
        db.ForeignKey('predictions.id'),
        nullable=False
    )

    shap_values = db.Column(db.JSON)
    base_value = db.Column(db.Float)

    explanation_text = db.Column(db.Text)
    recommendation = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    prediction = db.relationship(
        'Prediction',
        backref='shap_explanations'
    )

    def to_dict(self):
        return {
            "id": self.id,
            "prediction_id": self.prediction_id,
            "shap_values": self.shap_values,
            "base_value": self.base_value,
            "explanation_text": self.explanation_text,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat()
        }

    def __repr__(self):
        return f"<SHAPExplanation {self.prediction_id}>"
