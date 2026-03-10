from flask import Blueprint, jsonify
from sqlalchemy import func
from app import db
from app.models import Sensor, Alert, SensorData 

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    # Exemple de logique : compter les capteurs et alertes
    total_sensors = Sensor.query.count()
    active_sensors = Sensor.query.filter_by(is_active=True).count()
    critical_alerts = Alert.query.filter_by(severity='critical').count()
    data_points = db.session.query(func.count(SensorData.id)).scalar() or 0  

    return jsonify({
        'totalSensors': total_sensors,
        'activeSensors': active_sensors,
        'criticalAlerts': critical_alerts,
        'dataPoints': data_points
    })

@dashboard_bp.route('/environmental', methods=['GET'])
def get_environmental_data():
    # Exemple de logique : retourner des données environnementales simulées
    return jsonify({
        'temperature': [22.5, 23.0, 22.8],  # Données simulées
        'humidity': [45, 47, 46],
        'airQuality': [35, 38, 36]
    })
