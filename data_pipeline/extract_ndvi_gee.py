"""
Extraction NDVI réel Sentinel-2 via Google Earth Engine
Zone : Rif Forest, Maroc (Chefchaouen)
Période : 2020-2026
"""
import ee
import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 60)
print("EXTRACTION NDVI SENTINEL-2 — RIF FOREST")
print("=" * 60)

# Init GEE
ee.Initialize(project='forest-digital-twin')

# Polygone exact de la Parcelle Nord-Rif A1
RIF_POLYGON = ee.Geometry.Polygon([[
    [-5.30, 35.10],
    [-5.10, 35.10],
    [-5.10, 35.30],
    [-5.30, 35.30],
    [-5.30, 35.10]
]])

def get_ndvi_collection(start_date, end_date):
    """Récupère collection Sentinel-2 avec NDVI calculé"""
    
    def add_ndvi(image):
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)
    
    def mask_clouds(image):
        qa = image.select('QA60')
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(
                     qa.bitwiseAnd(1 << 11).eq(0))
        return image.updateMask(cloud_mask)
    
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(RIF_POLYGON)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(mask_clouds)
        .map(add_ndvi))
    
    return collection

def extract_ndvi_timeseries():
    """Extrait la série temporelle NDVI par période de 16 jours"""
    
    results = []
    
    # Années à extraire
    years = range(2020, 2027)
    
    for year in years:
        print(f"\n  📡 Extraction {year}...")
        
        start = f'{year}-01-01'
        end = f'{year}-12-31' if year < 2026 else '2026-03-03'
        
        collection = get_ndvi_collection(start, end)
        
        # Réduire par intervalle de 16 jours (cycle Sentinel-2)
        def reduce_region(image):
            stats = image.select('NDVI').reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=RIF_POLYGON,
                scale=10,  # résolution 10m Sentinel-2
                maxPixels=1e9
            )
            return ee.Feature(None, {
                'date': image.date().format('YYYY-MM-dd'),
                'ndvi': stats.get('NDVI'),
                'cloud_pct': image.get('CLOUDY_PIXEL_PERCENTAGE')
            })
        
        features = collection.map(reduce_region)
        
        try:
            # Récupérer les données
            data = features.getInfo()
            
            for f in data['features']:
                props = f['properties']
                if props.get('ndvi') is not None:
                    results.append({
                        'date': props['date'],
                        'ndvi': round(float(props['ndvi']), 4),
                        'cloud_pct': props.get('cloud_pct', 0),
                        'source': 'Sentinel-2_GEE_Real'
                    })
            
            print(f"  ✅ {year} : {len([f for f in data['features'] if f['properties'].get('ndvi')])} images valides")
            
        except Exception as e:
            print(f"  ⚠️  {year} erreur: {e}")
    
    return results

# Lancer l'extraction
print("\n🚀 Démarrage extraction (peut prendre 2-5 minutes)...")
ndvi_results = extract_ndvi_timeseries()

if not ndvi_results:
    print("❌ Aucune donnée extraite")
    exit(1)

# Créer DataFrame NDVI
df_ndvi = pd.DataFrame(ndvi_results)
df_ndvi['date'] = pd.to_datetime(df_ndvi['date'])
df_ndvi = df_ndvi.sort_values('date').reset_index(drop=True)

print(f"\n✅ {len(df_ndvi)} mesures NDVI réelles extraites")
print(f"   Période : {df_ndvi['date'].min().date()} → {df_ndvi['date'].max().date()}")
print(f"   NDVI moyen : {df_ndvi['ndvi'].mean():.4f}")
print(f"   NDVI min/max : {df_ndvi['ndvi'].min():.4f} / {df_ndvi['ndvi'].max():.4f}")

# Charger météo existante (déjà dans master_dataset)
print("\n📊 Fusion avec météo Open-Meteo existante...")
df_master = pd.read_csv('data/processed/master_dataset.csv')
df_master['date'] = pd.to_datetime(df_master['date'])

# Remplacer le NDVI simulé par le vrai
df_master = df_master.drop(columns=['ndvi', 'ndvi_rolling_7d', 'ndvi_change'], errors='ignore')

# Merge avec vrai NDVI
df_merged = df_master.merge(df_ndvi[['date', 'ndvi']], on='date', how='left')

# Interpoler les jours sans image satellite (nuages, etc.)
df_merged['ndvi'] = df_merged['ndvi'].interpolate(method='linear')
df_merged['ndvi'] = df_merged['ndvi'].fillna(method='bfill').fillna(method='ffill')

# Recalculer features dérivées
df_merged['ndvi_rolling_7d'] = df_merged['ndvi'].rolling(7, min_periods=1).mean()
df_merged['ndvi_change'] = df_merged['ndvi'].diff()

# Sauvegarder
import os
os.makedirs('data/processed', exist_ok=True)
df_merged.to_csv('data/processed/master_dataset.csv', index=False)

# Sauvegarder aussi le NDVI brut GEE pour référence
df_ndvi.to_csv('data/processed/ndvi_sentinel2_real.csv', index=False)

print(f"\n✅ Master dataset mis à jour avec NDVI réel Sentinel-2 !")
print(f"   Lignes : {len(df_merged)}")
print(f"   NDVI NaN restants : {df_merged['ndvi'].isna().sum()}")
print(f"\n📁 Fichiers sauvegardés :")
print(f"   data/processed/master_dataset.csv (mis à jour)")
print(f"   data/processed/ndvi_sentinel2_real.csv (NDVI brut)") 