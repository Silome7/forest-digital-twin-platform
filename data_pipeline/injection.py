import pandas as pd
from sqlalchemy import create_engine, text
from geoalchemy2 import Geometry
import json

# Connexion à ta DB (ajuste les credentials selon ton docker-compose)
engine = create_engine('postgresql://user:password@localhost:5432/dtdb')

def seed_sprint_1():
    # 1. Créer la Zone 'Rif Forest' avec son polygone
    # Coordonnées approximatives d'une parcelle du Rif
    polygon_wkt = "POLYGON((-4.05 35.15, -3.95 35.15, -3.95 35.25, -4.05 35.25, -4.05 35.15))"
    
    with engine.connect() as conn:
        # On insère la zone si elle n'existe pas
        conn.execute(text("""
            INSERT INTO zones (id, name, forest_name, geometry, surface_hectares)
            VALUES ('rif_forest', 'Parcelle Nord Rif', 'Rif Forest', 
                    ST_GeomFromText(:wkt, 4326), 1200)
            ON CONFLICT (id) DO NOTHING;
        """), {"wkt": polygon_wkt})
        conn.commit()

    # 2. Charger le Master Dataset
    df = pd.read_csv('data/processed/master_dataset.csv')
    
    # 3. Préparer les données pour la table 'sensor_data' ou 'zone_metrics'
    # On va mapper tes colonnes CSV aux colonnes de ta DB
    df['zone_id'] = 'rif_forest'
    
    # Injection massive via Pandas (très rapide)
    # Assure-toi que les noms de colonnes correspondent à ta table ZoneMetrics
    df.to_sql('zone_metrics', engine, if_exists='append', index=False)
    
    print("✅ Sprint 1 : Données spatialisées et injectées avec succès !")

if __name__ == "__main__":
    seed_sprint_1()