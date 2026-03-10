from flask import Blueprint, jsonify
from app import db
from app.models import Sensor # adapte selon tes modèles
from sqlalchemy import func
from app.models import Sensor, Alert, SensorData 
dashboarduser_bp = Blueprint('dashboarduser', __name__, url_prefix='/dashboarduser')

@dashboarduser_bp.route('/environmental', methods=['GET'])
def get_user_environmental_data():
    # Exemple : on retourne uniquement certaines données adaptées à l’utilisateur
    # Ici je simplifie par rapport à ton dashboard admin
    return jsonify({
        'temperature': [22.5, 23.0, 22.8],
        'humidity': [45, 47, 46],
        'soilHumidity': [30, 32, 31],
        'soilPH': [6.5, 6.7, 6.6]
    })

@dashboarduser_bp.route('/stats', methods=['GET'])
def get_user_stats():
    # Exemple : stats simplifiées pour l’utilisateur
    total_sensors = Sensor.query.count()
    data_points = db.session.query(func.count(SensorData.id)).scalar() or 0

    return jsonify({
        'totalSensors': total_sensors,
        'dataPoints': data_points
    })
