from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.zone import Zone
from app.models.zone_status import ZoneStatus
from app.models.zone_metrics import ZoneMetrics
from app.models.zone_alert import ZoneAlert
from app.models.prediction import Prediction
from app.services.alert_service import calculate_fire_risk, analyze_and_alert

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

# GET zones as GeoJSON (pour la carte)
@zones_bp.route('/geojson', methods=['GET'])
@jwt_required()
def get_zones_geojson():
    try:
        zones = Zone.query.all()
        features = [z.to_geojson_feature() for z in zones]
        return jsonify({
            "type": "FeatureCollection",
            "features": features
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# GET historique zone (Sprint 2 — graphiques)
@zones_bp.route('/<int:zone_id>/history', methods=['GET'])
@jwt_required()
def get_zone_history(zone_id):
    try:
        # Paramètres optionnels
        period = request.args.get('period', '1y')  # 1m, 3m, 6m, 1y, 2y
        granularity = request.args.get('granularity', 'weekly')  # daily, weekly, monthly

        from datetime import datetime, timedelta
        from sqlalchemy import func

        now = datetime.utcnow()
        period_map = {
            '1m': now - timedelta(days=30),
            '3m': now - timedelta(days=90),
            '6m': now - timedelta(days=180),
            '1y': now - timedelta(days=365),
            '2y': now - timedelta(days=730),
            'all': datetime(2020, 1, 1)
        }
        start_date = period_map.get(period, datetime(2020, 1, 1))

        # Agréger selon granularité
        if granularity == 'daily':
            trunc = func.date_trunc('day', ZoneMetrics.timestamp)
        elif granularity == 'weekly':
            trunc = func.date_trunc('week', ZoneMetrics.timestamp)
        else:
            trunc = func.date_trunc('month', ZoneMetrics.timestamp)

        results = db.session.query(
            trunc.label('period'),
            func.avg(ZoneMetrics.avg_ndvi).label('avg_ndvi'),
            func.avg(ZoneMetrics.avg_temperature).label('avg_temperature'),
            func.avg(ZoneMetrics.avg_humidity).label('avg_humidity'),
            func.avg(ZoneMetrics.fire_risk_score).label('fire_risk_score'),
            func.avg(ZoneMetrics.health_index).label('health_index'),
            func.count(ZoneMetrics.id).label('count')
        ).filter(
            ZoneMetrics.zone_id == zone_id,
            ZoneMetrics.timestamp >= start_date
        ).group_by(trunc).order_by(trunc).all()

        data = [{
            "date": r.period.strftime('%Y-%m-%d'),
            "avg_ndvi": round(float(r.avg_ndvi), 4) if r.avg_ndvi else None,
            "avg_temperature": round(float(r.avg_temperature), 1) if r.avg_temperature else None,
            "avg_humidity": round(float(r.avg_humidity), 1) if r.avg_humidity else None,
            "fire_risk_score": round(float(r.fire_risk_score), 2) if r.fire_risk_score else None,
            "health_index": round(float(r.health_index), 1) if r.health_index else None,
            "count": r.count
        } for r in results]

        return jsonify({
            'status': 'success',
            'zone_id': zone_id,
            'period': period,
            'granularity': granularity,
            'data_points': len(data),
            'data': data
        }), 200
        

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@zones_bp.route('/<int:zone_id>/analyze', methods=['POST'])
@jwt_required()
def analyze_zone_risk(zone_id):
    try:
        result = analyze_and_alert(zone_id)
        return jsonify({"status": "success", "data": result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500