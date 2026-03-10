import pandas as pd
from sqlalchemy import create_engine, text
import numpy as np

# Configuration de la connexion (ajuste si nécessaire)
engine = create_engine('postgresql://postgres:password@localhost:5432/DTDB')

def run_injection():
    print("🚀 Démarrage de l'injection Sprint 1...")
    
    # 1. Charger le Master Dataset
    df = pd.read_csv('/home/lonkou/Forest-digital-twin/data/processed/master_dataset.csv')
    df['date'] = pd.to_datetime(df['date'])
    # Remplacer les NaN (comme ndvi_change sur la 1ère ligne) par 0
    df = df.replace({np.nan: 0})

    with engine.connect() as conn:
        # 2. Créer la Forêt "Rif Forest"
        conn.execute(text("""
            INSERT INTO forests (name, location, surface, description)
            VALUES ('Rif Forest', 'Nord du Maroc', 50000, 'Écosystème forestier du Rif')
            ON CONFLICT DO NOTHING;
        """))
        
        forest_id = conn.execute(text("SELECT id FROM forests WHERE name='Rif Forest'")).scalar()

        # 3. Créer la Zone avec Géométrie (Polygone autour de Chefchaouen/Rif)
        # On définit un carré représentatif pour la démo
        polygon_wkt = "POLYGON((-5.30 35.10, -5.10 35.10, -5.10 35.30, -5.30 35.30, -5.30 35.10))"
        
        conn.execute(text("""
            INSERT INTO zones (name, forest_id, geometry)
            VALUES ('Parcelle Nord-Rif A1', :f_id, ST_GeomFromText(:wkt, 4326))
            ON CONFLICT DO NOTHING;
        """), {"f_id": forest_id, "wkt": polygon_wkt})
        
        zone_id = conn.execute(text("SELECT id FROM zones WHERE name='Parcelle Nord-Rif A1'")).scalar()
        conn.commit()

        print(f"🌲 Forêt ID: {forest_id} | Zone ID: {zone_id} créées.")

        # 4. Préparer les données pour 'zone_metrics'
        # On mappe les colonnes du CSV vers tes colonnes DB réelles (\d zone_metrics)
        df_metrics = pd.DataFrame({
            'zone_id': zone_id,
            'timestamp': df['date'],
            'avg_temperature': df['temperature'],
            'avg_humidity': df['humidity'],
            'avg_ndvi': df['ndvi'],
            'ndvi_trend': 'Stable', # Valeur par défaut
            'active_sensors': 10,
            'total_sensors': 10,
            'coverage_percent': 100.0,
            'data_quality': 0.95,
            # Nouvelles colonnes ajoutées au Sprint 1
            'fire_risk_score': (df['temperature'] * 0.4) + ((100 - df['humidity']) * 0.6), # Score simple pour débuter
            'health_index': df['ndvi'] * 100
        })

        # 5. Injection massive
        print(f"📊 Injection de {len(df_metrics)} mesures historiques...")
        df_metrics.to_sql('zone_metrics', engine, if_exists='append', index=False)
        
        # 6. Mettre à jour 'zone_statuses'
        last_row = df_metrics.iloc[-1]
        conn.execute(text("""
            INSERT INTO zone_statuses (zone_id, health_score, status, risk_level, temperature_avg, humidity_avg, updated_at)
            VALUES (:z_id, :h_score, 'Active', 'Normal', :temp, :hum, :now)
            ON CONFLICT (zone_id) DO UPDATE SET
                health_score = EXCLUDED.health_score,
                temperature_avg = EXCLUDED.temperature_avg,
                humidity_avg = EXCLUDED.humidity_avg,
                updated_at = EXCLUDED.updated_at;
        """), {
            "z_id": int(zone_id),
            "h_score": float(last_row['health_index']),
            "temp": float(last_row['avg_temperature']),
            "hum": float(last_row['avg_humidity']),
            "now": last_row['timestamp'].to_pydatetime()
        })
        conn.commit()

    print("✅ Sprint 1 VALIDÉ : Base de données prête et peuplée !")

if __name__ == "__main__":
    run_injection()