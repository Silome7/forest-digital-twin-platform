from app import db
from app.models.zone_metrics import ZoneMetrics
from app.models.zone_alert import ZoneAlert
from datetime import datetime

def calculate_fire_risk(ndvi, temp, humidity):
    """Score de risque incendie — scientifiquement cohérent"""
    score = 0
    
    # NDVI (état de la végétation)
    if ndvi < 0.3:   score += 40  # Végétation très inflammable
    elif ndvi < 0.4: score += 25
    elif ndvi < 0.5: score += 10
    
    # Température
    if temp > 35:   score += 30  # Canicule
    elif temp > 30: score += 20
    elif temp > 25: score += 10
    
    # Humidité
    if humidity < 20:  score += 30  # Air très sec
    elif humidity < 30: score += 20
    elif humidity < 40: score += 10
    
    return min(score, 100)

def get_severity(score):
    if score >= 70:  return "Critical"
    if score >= 50:  return "High"
    if score >= 30:  return "Warning"
    return "Info"

def analyze_and_alert(zone_id: int):
    """Analyse la dernière mesure et crée une alerte si nécessaire"""
    last_m = ZoneMetrics.query.filter_by(zone_id=zone_id)\
                .order_by(ZoneMetrics.timestamp.desc()).first()
    
    if not last_m:
        return {"error": "Pas de données"}, 404

    score = calculate_fire_risk(
        last_m.avg_ndvi or 0.5,
        last_m.avg_temperature or 20,
        last_m.avg_humidity or 60
    )
    severity = get_severity(score)
    alert_created = False

    if score >= 30:
        # Vérifier qu'on n'a pas déjà une alerte récente non acquittée
        existing = ZoneAlert.query.filter_by(
            zone_id=zone_id,
            acknowledged=False,
            acknowledged_by='auto_scoring'
        ).order_by(ZoneAlert.created_at.desc()).first()

        if not existing:
            alert = ZoneAlert(
                zone_id=zone_id,
                alert_type="Fire" if score >= 50 else "Health",
                severity=severity,
                title=f"{'🔴' if severity=='Critical' else '🟠' if severity=='High' else '🟡'} Score Risque : {score}/100",
                description=(
                    f"NDVI={last_m.avg_ndvi:.3f} | "
                    f"Temp={last_m.avg_temperature:.1f}°C | "
                    f"Humidité={last_m.avg_humidity:.1f}%"
                ),
                recommended_action=(
                    "Déployer équipes immédiatement." if severity == "Critical"
                    else "Augmenter surveillance." if severity == "High"
                    else "Surveiller l'évolution."
                ),
                acknowledged=False,
                acknowledged_by='auto_scoring',
                created_at=datetime.utcnow()
            )
            db.session.add(alert)
            db.session.commit()
            alert_created = True

    return {
        "risk_score": score,
        "severity": severity,
        "ndvi": last_m.avg_ndvi,
        "temperature": last_m.avg_temperature,
        "humidity": last_m.avg_humidity,
        "alert_created": alert_created
    }