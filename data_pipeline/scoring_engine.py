"""
Scoring Engine — Alertes Intelligentes
Analyse les données historiques et déclenche des alertes
"""
import os
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

DATABASE_URL = "postgresql://postgres:password@localhost:5432/DTDB"
engine = create_engine(DATABASE_URL)

# ============================================================
# RÈGLES DE SCORING
# ============================================================
RULES = [
    {
        "name": "Risque Incendie Critique",
        "alert_type": "Fire",
        "severity": "Critical",
        "condition": lambda r: r['avg_temperature'] > 35 and r['avg_ndvi'] < 0.35,
        "title": "🔴 RISQUE INCENDIE CRITIQUE",
        "description": lambda r: f"Température {r['avg_temperature']:.1f}°C + NDVI {r['avg_ndvi']:.3f} — Risque incendie imminent.",
        "action": "Déployer équipes immédiatement. Interdire l'accès à la zone."
    },
    {
        "name": "Risque Incendie Élevé",
        "alert_type": "Fire",
        "severity": "High",
        "condition": lambda r: r['avg_temperature'] > 28 and r['avg_ndvi'] < 0.48,
        "title": "🟠 RISQUE INCENDIE ÉLEVÉ",
        "description": lambda r: f"Température {r['avg_temperature']:.1f}°C + NDVI {r['avg_ndvi']:.3f} — Conditions favorables aux incendies.",
        "action": "Augmenter la fréquence des rondes."
    },
    {
        "name": "Stress Hydrique",
        "alert_type": "Health",
        "severity": "High",
        "condition": lambda r: r['avg_humidity'] < 25 and r['avg_temperature'] > 28,
        "title": "🟠 STRESS HYDRIQUE DÉTECTÉ",
        "description": lambda r: f"Humidité {r['avg_humidity']:.1f}% + Température {r['avg_temperature']:.1f}°C — Sécheresse sévère.",
        "action": "Activer protocole d'irrigation d'urgence."
    },
    {
        "name": "Stress Végétatif",
        "alert_type": "Health",
        "severity": "Warning",
        "condition": lambda r: r['avg_ndvi'] < 0.50 and r['avg_temperature'] > 25,
        "title": "🟡 STRESS VÉGÉTATIF ESTIVAL",
        "description": lambda r: f"NDVI {r['avg_ndvi']:.3f} avec chaleur {r['avg_temperature']:.1f}°C — Stress hydrique modéré.",
        "action": "Surveiller l'évolution hebdomadaire."
    },
]

def run_scoring(zone_id: int = 5):
    print("=" * 60)
    print("🧠 SCORING ENGINE — ANALYSE INTELLIGENTE")
    print("=" * 60)

    # Charger les données historiques
    df = pd.read_sql(f"""
        SELECT timestamp, avg_temperature, avg_humidity, avg_ndvi,
               fire_risk_score, health_index
        FROM zone_metrics
        WHERE zone_id = {zone_id}
        ORDER BY timestamp
    """, engine)

    print(f"📊 {len(df)} mesures analysées pour zone {zone_id}")

    alerts_generated = []
    alerts_inserted = 0

    with engine.connect() as conn:
        # Supprimer les anciennes alertes auto-générées pour cette zone
        conn.execute(text("""
            DELETE FROM zone_alerts 
            WHERE zone_id = :zone_id 
            AND acknowledged_by = 'scoring_engine'
        """), {"zone_id": zone_id})
        conn.commit()

        for _, row in df.iterrows():
            for rule in RULES:
                try:
                    if rule["condition"](row):
                        alert = {
                            "zone_id": zone_id,
                            "alert_type": rule["alert_type"],
                            "severity": rule["severity"],
                            "title": rule["title"],
                            "description": rule["description"](row),
                            "recommended_action": rule["action"],
                            "timestamp": row['timestamp'],
                        }
                        alerts_generated.append(alert)
                except Exception:
                    continue

        print(f"⚠️  {len(alerts_generated)} alertes détectées dans l'historique")

        # Insérer les alertes significatives (échantillon représentatif)
        # On garde max 50 alertes pour ne pas surcharger
        if alerts_generated:
            # Garder les plus récentes + les Critical
            critical = [a for a in alerts_generated if a['severity'] == 'Critical']
            high = [a for a in alerts_generated if a['severity'] == 'High']
            warning = [a for a in alerts_generated if a['severity'] == 'Warning']

            # Mix représentatif
            selected = critical[-20:] + high[-15:] + warning[-10:]
            selected = sorted(selected, key=lambda x: x['timestamp'])[-50:]

            for alert in selected:
                conn.execute(text("""
                    INSERT INTO zone_alerts 
                        (zone_id, alert_type, severity, title, description, 
                         recommended_action, acknowledged, acknowledged_by, created_at)
                    VALUES 
                        (:zone_id, :alert_type, :severity, :title, :description,
                         :recommended_action, false, 'scoring_engine', :created_at)
                """), {
                    "zone_id": alert["zone_id"],
                    "alert_type": alert["alert_type"],
                    "severity": alert["severity"],
                    "title": alert["title"],
                    "description": alert["description"],
                    "recommended_action": alert["recommended_action"],
                    "created_at": alert["timestamp"],
                })
                alerts_inserted += 1

            conn.commit()

    # Résumé
    print(f"\n✅ {alerts_inserted} alertes insérées en base")
    print(f"\n📊 Répartition des alertes détectées :")
    print(f"   🔴 Critical : {len([a for a in alerts_generated if a['severity'] == 'Critical'])}")
    print(f"   🟠 High     : {len([a for a in alerts_generated if a['severity'] == 'High'])}")
    print(f"   🟡 Warning  : {len([a for a in alerts_generated if a['severity'] == 'Warning'])}")

    # Stats intéressantes pour la soutenance
    critical_periods = [a for a in alerts_generated if a['severity'] == 'Critical']
    if critical_periods:
        print(f"\n🔴 Périodes critiques détectées :")
        for a in critical_periods[:5]:
            print(f"   {a['timestamp'].strftime('%Y-%m-%d')} — {a['title']}")

    return alerts_generated

if __name__ == "__main__":
    alerts = run_scoring(zone_id=5)
    print("\n✅ Scoring Engine terminé !")