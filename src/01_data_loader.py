"""
pollination_project/src/01_data_loader.py
=========================================
Loads and aligns all 5 datasets spatially (using H3 hexagons) and temporally.
Outputs a merged DataFrame ready for feature engineering.
"""

import sys
import os
import pandas as pd
import numpy as np
import h3
from glob import glob

# Add root to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def get_h3_index(lat, lon):
    """Calculates H3 hex index for a given coordinate at configured resolution."""
    return h3.latlng_to_cell(lat, lon, config.H3_RESOLUTION)

def load_gbif():
    """Loads GBIF data and aggregates by H3/Year/Month."""
    print("Loading GBIF Dataset...")
    df = pd.read_csv(os.path.join(config.RAW_DATA_DIR, 'gbif_pollinators.csv'))
    
    if config.SUBSET:
        df = df.head(config.IMAGE_LIMIT * 40 if config.IMAGE_LIMIT else 2000)

    # Assign H3 indices
    df['h3_index'] = df.apply(lambda r: get_h3_index(r['decimalLatitude'], r['decimalLongitude']), axis=1)
    
    # Simple aggregations
    agg_df = df.groupby(['h3_index', 'year', 'month']).agg({
        'gbifID': 'count',
        'individualCount': 'sum',
        'scientificName': 'nunique'
    }).reset_index()
    
    agg_df.columns = ['h3_index', 'year', 'month', 'obs_count', 'total_pollinators', 'species_richness']
    return agg_df

def load_usda():
    """Loads USDA data. Since USDA is at county level, we simulate centroids for alignment."""
    print("Loading USDA Dataset...")
    df = pd.read_csv(os.path.join(config.RAW_DATA_DIR, 'usda_nass_crops.csv'))
    
    # In a real scenario, we would use a county-to-h3 mapping.
    # For this prototype, we'll assign each specific county/state combo a stable centroid.
    np.random.seed(config.RANDOM_STATE)
    counties = df[['state_alpha', 'county_name']].drop_duplicates()
    
    # Approximate US bounding box for synthetic centroids
    counties['lat'] = np.random.uniform(25, 48, len(counties))
    counties['lon'] = np.random.uniform(-120, -70, len(counties))
    counties['h3_index'] = counties.apply(lambda r: get_h3_index(r['lat'], r['lon']), axis=1)
    
    df = df.merge(counties[['state_alpha', 'county_name', 'h3_index']], on=['state_alpha', 'county_name'])
    
    # Aggregate yield and pesticide signals
    agg_df = df.groupby(['h3_index', 'year']).agg({
        'Value': 'mean'
    }).reset_index()
    agg_df.columns = ['h3_index', 'year', 'avg_crop_val']
    return agg_df

def load_noaa():
    """Loads NOAA climate data and joins with station locations for H3 alignment."""
    print("Loading NOAA Dataset...")
    df = pd.read_csv(os.path.join(config.RAW_DATA_DIR, 'noaa_climate.csv'))
    stations = pd.read_csv(os.path.join(config.RAW_DATA_DIR, 'noaa_stations.csv'))
    
    # Assign H3 to stations
    stations['h3_index'] = stations.apply(lambda r: get_h3_index(r['LATITUDE'], r['LONGITUDE']), axis=1)
    
    # Join climate data to stations
    df = df.merge(stations[['ID', 'h3_index']], on='ID')
    
    # Parse date YYYYMMDD
    df['year'] = (df['DATE'] // 10000).astype(int)
    df['month'] = ((df['DATE'] % 10000) // 100).astype(int)
    
    # Pivot elements (TMAX, TMIN, PRCP) to columns
    pivot_df = df.pivot_table(
        index=['h3_index', 'year', 'month'],
        columns='ELEMENT',
        values='DATA_VALUE',
        aggfunc='mean'
    ).reset_index().fillna(0)
    
    return pivot_df

def load_pubmed():
    """Loads PubMed abstracts. Broadcasts them as regional keywords."""
    print("Loading PubMed Dataset...")
    df = pd.read_csv(os.path.join(config.RAW_DATA_DIR, 'pubmed_abstracts.csv'))
    
    # Since PubMed isn't strictly spatial, we'll aggregate by Year/Month
    # to provide temporal research context features.
    agg_df = df.groupby(['PubDate_Year', 'PubDate_Month']).agg({
        'AbstractText': lambda x: " ".join(x.astype(str))
    }).reset_index()
    agg_df.columns = ['year', 'month', 'merged_abstracts']
    return agg_df

def load_nasa_metadata():
    """Simulates/loads metadata linking NASA image files to H3/Time."""
    print("Linking Satellite Images...")
    image_files = sorted(glob(os.path.join(config.RAW_DATA_DIR, 'satellite_images', '*.npy')))
    
    if config.SUBSET and config.IMAGE_LIMIT:
        image_files = image_files[:config.IMAGE_LIMIT]
        
    # Create synthetic spatial-temporal metadata for these image files
    np.random.seed(config.RANDOM_STATE)
    data = []
    for f in image_files:
        lat = np.random.uniform(25, 48)
        lon = np.random.uniform(-120, -70)
        year = np.random.choice([2020, 2021, 2022, 2023])
        month = np.random.randint(1, 13)
        data.append({
            'image_path': f,
            'h3_index': get_h3_index(lat, lon),
            'year': year,
            'month': month
        })
    return pd.DataFrame(data)

def run_pipeline():
    """Loads all, joins, and saves to processed."""
    print("Starting Data Loading Pipeline...")
    
    gbif = load_gbif()
    usda = load_usda()
    noaa = load_noaa()
    pubmed = load_pubmed()
    nasa = load_nasa_metadata()
    
    # Join strategy: Start with GBIF sightings as the primary spatial grid
    master_df = gbif.merge(noaa, on=['h3_index', 'year', 'month'], how='left')
    master_df = master_df.merge(usda, on=['h3_index', 'year'], how='left')  # USDA is annual
    master_df = master_df.merge(pubmed, on=['year', 'month'], how='left')  # PubMed broad temporal
    master_df = master_df.merge(nasa, on=['h3_index', 'year', 'month'], how='left')
    
    # Fill missing values
    master_df = master_df.fillna(0)
    
    # Save processed dataframe
    save_path = os.path.join(config.PROCESSED_DATA_DIR, 'merged_space_time_grid.csv')
    master_df.to_csv(save_path, index=False)
    
    print(f"\n✅ Alignment Complete! Shape: {master_df.shape}")
    print(f"Saved to: {save_path}")
    return master_df

if __name__ == "__main__":
    run_pipeline()
