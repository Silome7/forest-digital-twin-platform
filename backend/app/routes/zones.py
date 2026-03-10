from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.zone import Zone
from app.models.zone_status import ZoneStatus
from app.models.zone_metrics import ZoneMetrics
from app.models.zone_alert import ZoneAlert
from app.models.prediction import Prediction

zones_bp = Blueprint('zones', __name__, url_prefix='/api/zones')

# GET all zones
@zones_bp.route('/', methods=['GET'])
@zones_bp.route('', methods=['GET'])
@jwt_required()
def list_zones():
    try:
        zones = Zone.query.all()
        return jsonify({
            'status': 'success',
            'data': [zone.to_dict() for zone in zones]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET single zone
@zones_bp.route('/<int:zone_id>', methods=['GET'])
@jwt_required()
def get_zone(zone_id):
    try:
        zone = Zone.query.get(zone_id)
        if not zone:
            return jsonify({'error': 'Zone not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': zone.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CREATE zone
@zones_bp.route('/', methods=['POST'])
@zones_bp.route('', methods=['POST'])
@jwt_required()
def create_zone():
    try:
        data = request.get_json()
        
        zone = Zone(
            name=data.get('name'),
            forest_id=data.get('forest_id'),
            location=data.get('location'),
            surface=data.get('surface'),
            description=data.get('description'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        db.session.add(zone)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': zone.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# GET zone status
@zones_bp.route('/<int:zone_id>/status', methods=['GET'])
@jwt_required()
def get_zone_status(zone_id):
    try:
        status = ZoneStatus.query.filter_by(zone_id=zone_id).first()
        if not status:
            return jsonify({'error': 'Zone status not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': status.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET zone metrics (série temporelle)
@zones_bp.route('/<int:zone_id>/metrics', methods=['GET'])
@jwt_required()
def get_zone_metrics(zone_id):
    try:
        limit = request.args.get('limit', 30, type=int)
        metrics = ZoneMetrics.query.filter_by(zone_id=zone_id).order_by(
            ZoneMetrics.timestamp.desc()
        ).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'data': [m.to_dict() for m in metrics]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET zone alerts
@zones_bp.route('/<int:zone_id>/alerts', methods=['GET'])
@jwt_required()
def get_zone_alerts(zone_id):
    try:
        alerts = ZoneAlert.query.filter_by(zone_id=zone_id).order_by(
            ZoneAlert.created_at.desc()
        ).all()
        
        return jsonify({
            'status': 'success',
            'data': [a.to_dict() for a in alerts]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# GET zone predictions
@zones_bp.route('/<int:zone_id>/predictions', methods=['GET'])
@jwt_required()
def get_zone_predictions(zone_id):
    try:
        predictions = Prediction.query.filter_by(zone_id=zone_id).order_by(
            Prediction.created_at.desc()
        ).all()
        
        return jsonify({
            'status': 'success',
            'data': [p.to_dict() for p in predictions]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# CREATE zone alert
@zones_bp.route('/<int:zone_id>/alerts', methods=['POST'])
@jwt_required()
def create_zone_alert(zone_id):
    try:
        data = request.get_json()
        
        alert = ZoneAlert(
            zone_id=zone_id,
            alert_type=data.get('alert_type'),
            severity=data.get('severity'),
            title=data.get('title'),
            description=data.get('description'),
            recommended_action=data.get('recommended_action')
        )
        
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': alert.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ACKNOWLEDGE alert
@zones_bp.route('/<int:zone_id>/alerts/<int:alert_id>/ack', methods=['PATCH'])
@jwt_required()
def acknowledge_alert(zone_id, alert_id):
    try:
        alert = ZoneAlert.query.filter_by(id=alert_id, zone_id=zone_id).first()
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.acknowledged = True
        alert.acknowledged_by = request.get_json().get('acknowledged_by', 'agent')
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': alert.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
