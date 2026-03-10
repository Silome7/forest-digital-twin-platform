from app import db

class Forest(db.Model):
    __tablename__ = 'forests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    surface = db.Column(db.Float)
    description = db.Column(db.Text)

    # Relation vers Zone
    zones = db.relationship('Zone', back_populates='forest', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Forest {self.name}>"
