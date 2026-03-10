"""from app import db

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
        return f"<Zone {self.name}>"""
        
        

from app import db
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import json

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
    geometry = db.Column(Geometry(geometry_type='POLYGON', srid=4326))

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

    def to_geojson_feature(self):
        geom = None
        if self.geometry is not None:
            shape = to_shape(self.geometry)
            geom = json.loads(json.dumps(shape.__geo_interface__))
        return {
            "type": "Feature",
            "properties": {
                "id": self.id,
                "name": self.name,
                "location": self.location,
                "surface": self.surface,
            },
            "geometry": geom
        }

    def __repr__(self):
        return f"<Zone {self.name}>"
