from app import db
from datetime import datetime

class ZoneAlert(db.Model):
    __tablename__ = 'zone_alerts'

    id = db.Column(db.Integer, primary_key=True)
    
    zone_id = db.Column(
        db.Integer,
        db.ForeignKey('zones.id'),
        nullable=False
    )
    
    # Type d'alerte
    alert_type = db.Column(db.String(50), nullable=False)  # fire, drought, disease, etc
    severity = db.Column(db.String(50), nullable=False)  # low/medium/high/critical
    
    # Message
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Action recommandée
    recommended_action = db.Column(db.Text)
    
    # Pour qui?
    send_to_agents = db.Column(db.Boolean, default=True)
    
    # État
    acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime)
    acknowledged_by = db.Column(db.String(100))  # agent qui a confirmé
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Relationships
    zone = db.relationship('Zone', backref='alerts')
    
    def to_dict(self):
        return {
            "id": self.id,
            "zone_id": self.zone_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "recommended_action": self.recommended_action,
            "send_to_agents": self.send_to_agents,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f"<ZoneAlert {self.alert_type} - Zone {self.zone_id}>"
