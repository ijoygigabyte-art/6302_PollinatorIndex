"""
Synthetic Data Generator for Pollination Health Index (PHI) Project
===================================================================
Generates realistic synthetic datasets matching the official schemas of:
  1. GBIF Pollinator Observations (Darwin Core standard)
  2. USDA NASS QuickStats Crop & Pesticide Data
  3. NOAA GHCN-Daily Climate Data (long format)
  4. PubMed Abstracts (XML/API-style fields)
  5. NASA Landsat/Sentinel-2 Satellite Images (NDVI .npy arrays)
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "satellite_images"), exist_ok=True)

np.random.seed(42)  # Reproducibility
print("Starting synthetic data generation...\n")


# ══════════════════════════════════════════════════════════════════════════════
# 1. GBIF Pollinator Observations  (Darwin Core Standard)
#    Real schema: https://dwc.tdwg.org/terms/
# ══════════════════════════════════════════════════════════════════════════════
NUM_GBIF = 2000

# Realistic pollinator species with taxonomy
species_data = [
    # (scientificName, kingdom, phylum, class, order, family, genus, species)
    ("Apis mellifera", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Apidae", "Apis", "mellifera"),
    ("Bombus impatiens", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Apidae", "Bombus", "impatiens"),
    ("Bombus terrestris", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Apidae", "Bombus", "terrestris"),
    ("Danaus plexippus", "Animalia", "Arthropoda", "Insecta", "Lepidoptera", "Nymphalidae", "Danaus", "plexippus"),
    ("Vanessa cardui", "Animalia", "Arthropoda", "Insecta", "Lepidoptera", "Nymphalidae", "Vanessa", "cardui"),
    ("Megachile rotundata", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Megachilidae", "Megachile", "rotundata"),
    ("Osmia lignaria", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Megachilidae", "Osmia", "lignaria"),
    ("Xylocopa virginica", "Animalia", "Arthropoda", "Insecta", "Hymenoptera", "Apidae", "Xylocopa", "virginica"),
]

us_states = [
    "Alabama", "Arizona", "California", "Colorado", "Florida", "Georgia",
    "Illinois", "Indiana", "Iowa", "Kansas", "Minnesota", "Missouri",
    "Nebraska", "New York", "North Carolina", "Ohio", "Oregon", "Pennsylvania",
    "South Dakota", "Texas", "Virginia", "Washington", "Wisconsin"
]

species_idx = np.random.randint(0, len(species_data), NUM_GBIF)
event_dates = [(datetime(2020, 1, 1) + timedelta(days=int(d))).strftime('%Y-%m-%d')
               for d in np.random.randint(0, 1460, NUM_GBIF)]

lats = np.random.uniform(24.5, 48.5, NUM_GBIF).round(6)
lons = np.random.uniform(-124.5, -67.0, NUM_GBIF).round(6)

gbif_data = pd.DataFrame({
    'gbifID': np.arange(1000000001, 1000000001 + NUM_GBIF),
    'occurrenceID': [f"urn:catalog:POLL:{i}" for i in range(NUM_GBIF)],
    'basisOfRecord': np.random.choice(['HUMAN_OBSERVATION', 'PRESERVED_SPECIMEN', 'MACHINE_OBSERVATION'], NUM_GBIF, p=[0.7, 0.2, 0.1]),
    'scientificName': [species_data[i][0] for i in species_idx],
    'kingdom': [species_data[i][1] for i in species_idx],
    'phylum': [species_data[i][2] for i in species_idx],
    'class': [species_data[i][3] for i in species_idx],
    'order': [species_data[i][4] for i in species_idx],
    'family': [species_data[i][5] for i in species_idx],
    'genus': [species_data[i][6] for i in species_idx],
    'species': [f"{species_data[i][6]} {species_data[i][7]}" for i in species_idx],
    'taxonRank': ['SPECIES'] * NUM_GBIF,
    'individualCount': np.random.choice([1, 2, 3, 5, 10, 25, 50], NUM_GBIF, p=[0.4, 0.2, 0.15, 0.1, 0.08, 0.05, 0.02]),
    'eventDate': event_dates,
    'year': [int(d[:4]) for d in event_dates],
    'month': [int(d[5:7]) for d in event_dates],
    'day': [int(d[8:10]) for d in event_dates],
    'decimalLatitude': lats,
    'decimalLongitude': lons,
    'coordinateUncertaintyInMeters': np.random.choice([10, 50, 100, 500, 1000], NUM_GBIF),
    'countryCode': ['US'] * NUM_GBIF,
    'stateProvince': np.random.choice(us_states, NUM_GBIF),
    'occurrenceStatus': ['PRESENT'] * NUM_GBIF,
    'license': np.random.choice(['CC0_1_0', 'CC_BY_4_0', 'CC_BY_NC_4_0'], NUM_GBIF),
})

gbif_data.to_csv(os.path.join(OUTPUT_DIR, 'gbif_pollinators.csv'), index=False)
print(f"✓ gbif_pollinators.csv  ({NUM_GBIF} rows, {len(gbif_data.columns)} cols)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. USDA NASS QuickStats Crop & Pesticide Data
#    Real schema: https://quickstats.nass.usda.gov/api  (~39 columns)
# ══════════════════════════════════════════════════════════════════════════════
NUM_USDA = 1000

state_info = {
    'CA': ('CALIFORNIA', '06'), 'TX': ('TEXAS', '48'), 'IA': ('IOWA', '19'),
    'IL': ('ILLINOIS', '17'), 'MN': ('MINNESOTA', '27'), 'NE': ('NEBRASKA', '31'),
    'IN': ('INDIANA', '18'), 'OH': ('OHIO', '39'), 'SD': ('SOUTH DAKOTA', '46'),
    'ND': ('NORTH DAKOTA', '38'), 'KS': ('KANSAS', '20'), 'WI': ('WISCONSIN', '55'),
}

commodities = ['CORN', 'SOYBEANS', 'WHEAT', 'ALMONDS', 'COTTON']
stat_categories = [
    ('YIELD', 'BU / ACRE'),
    ('AREA HARVESTED', 'ACRES'),
    ('PRODUCTION', 'BU'),
    ('APPLICATIONS', 'LB'),
    ('TREATED', 'ACRES'),
]

state_keys = list(state_info.keys())
chosen_states = np.random.choice(state_keys, NUM_USDA)
chosen_commodities = np.random.choice(commodities, NUM_USDA)
chosen_stat_idx = np.random.randint(0, len(stat_categories), NUM_USDA)

county_names = [f"COUNTY {np.random.randint(1, 100):03d}" for _ in range(NUM_USDA)]
county_codes = [f"{np.random.randint(1, 200):03d}" for _ in range(NUM_USDA)]

short_descs = []
for i in range(NUM_USDA):
    cat, unit = stat_categories[chosen_stat_idx[i]]
    short_descs.append(f"{chosen_commodities[i]} - {cat}, MEASURED IN {unit}")

usda_data = pd.DataFrame({
    'source_desc': np.random.choice(['SURVEY', 'CENSUS'], NUM_USDA, p=[0.8, 0.2]),
    'sector_desc': ['CROPS'] * NUM_USDA,
    'group_desc': ['FIELD CROPS'] * NUM_USDA,
    'commodity_desc': chosen_commodities,
    'class_desc': ['ALL CLASSES'] * NUM_USDA,
    'prodn_practice_desc': ['ALL PRODUCTION PRACTICES'] * NUM_USDA,
    'util_practice_desc': ['ALL UTILIZATION PRACTICES'] * NUM_USDA,
    'statisticcat_desc': [stat_categories[i][0] for i in chosen_stat_idx],
    'unit_desc': [stat_categories[i][1] for i in chosen_stat_idx],
    'short_desc': short_descs,
    'domain_desc': np.random.choice(['TOTAL', 'CHEMICAL, INSECTICIDE', 'CHEMICAL, HERBICIDE'], NUM_USDA),
    'domaincat_desc': ['NOT SPECIFIED'] * NUM_USDA,
    'agg_level_desc': np.random.choice(['STATE', 'COUNTY'], NUM_USDA, p=[0.4, 0.6]),
    'state_alpha': chosen_states,
    'state_name': [state_info[s][0] for s in chosen_states],
    'state_ansi': [state_info[s][1] for s in chosen_states],
    'county_name': county_names,
    'county_code': county_codes,
    'asd_desc': ['CENTRAL'] * NUM_USDA,
    'year': np.random.choice([2018, 2019, 2020, 2021, 2022, 2023], NUM_USDA),
    'freq_desc': np.random.choice(['ANNUAL', 'SEASON'], NUM_USDA, p=[0.9, 0.1]),
    'reference_period_desc': np.random.choice(['YEAR', 'JAN', 'APR', 'JUL', 'OCT'], NUM_USDA),
    'begin_code': [0] * NUM_USDA,
    'end_code': [0] * NUM_USDA,
    'Value': np.random.uniform(0.5, 250.0, NUM_USDA).round(2),
    'CV_%': np.random.uniform(1.0, 30.0, NUM_USDA).round(1),
})

usda_data.to_csv(os.path.join(OUTPUT_DIR, 'usda_nass_crops.csv'), index=False)
print(f"✓ usda_nass_crops.csv   ({NUM_USDA} rows, {len(usda_data.columns)} cols)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. NOAA GHCN-Daily Climate Data  (LONG FORMAT)
#    Real schema: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt
#    Columns: ID, DATE, ELEMENT, DATA_VALUE, M_FLAG, Q_FLAG, S_FLAG, OBS_TIME
#    + separate stations metadata file
# ══════════════════════════════════════════════════════════════════════════════
NUM_STATIONS = 20
NUM_NOAA_DAYS = 500  # days per station subset

# Generate realistic station IDs (11-char: country code + network + station number)
station_ids = [f"USW00{np.random.randint(10000, 99999)}" for _ in range(NUM_STATIONS)]
station_lats = np.random.uniform(24.5, 48.5, NUM_STATIONS).round(4)
station_lons = np.random.uniform(-124.5, -67.0, NUM_STATIONS).round(4)
station_elevs = np.random.uniform(5.0, 2500.0, NUM_STATIONS).round(1)
station_names = [f"STATION_{i:02d}" for i in range(NUM_STATIONS)]

# Generate stations metadata file (ghcnd-stations.txt format)
stations_meta = pd.DataFrame({
    'ID': station_ids,
    'LATITUDE': station_lats,
    'LONGITUDE': station_lons,
    'ELEVATION': station_elevs,
    'STATE': np.random.choice(state_keys, NUM_STATIONS),
    'NAME': station_names,
})
stations_meta.to_csv(os.path.join(OUTPUT_DIR, 'noaa_stations.csv'), index=False)

# Generate daily observations in LONG FORMAT
elements = ['PRCP', 'TMAX', 'TMIN', 'SNOW', 'SNWD']
rows = []
for sid in station_ids:
    n_days = np.random.randint(NUM_NOAA_DAYS // 2, NUM_NOAA_DAYS)
    dates_int = [(datetime(2020, 1, 1) + timedelta(days=int(d))).strftime('%Y%m%d')
                 for d in sorted(np.random.choice(1460, n_days, replace=False))]
    for date_str in dates_int:
        for elem in np.random.choice(elements, size=np.random.randint(2, 5), replace=False):
            if elem == 'PRCP':
                val = int(np.random.exponential(30))        # tenths of mm
            elif elem in ('TMAX', 'TMIN'):
                base = 200 if elem == 'TMAX' else 50       # tenths of °C
                val = int(np.random.normal(base, 80))
            elif elem == 'SNOW':
                val = int(max(0, np.random.exponential(10)))  # mm
            else:  # SNWD
                val = int(max(0, np.random.exponential(20)))  # mm

            rows.append({
                'ID': sid,
                'DATE': date_str,
                'ELEMENT': elem,
                'DATA_VALUE': val,
                'M_FLAG': '',
                'Q_FLAG': '',
                'S_FLAG': np.random.choice(['W', 'X', 'N', '7', 'K']),
                'OBS_TIME': np.random.choice(['0700', '0800', '1700', '1800', '']),
            })

noaa_data = pd.DataFrame(rows)
noaa_data.to_csv(os.path.join(OUTPUT_DIR, 'noaa_climate.csv'), index=False)
print(f"✓ noaa_climate.csv      ({len(noaa_data)} rows, {len(noaa_data.columns)} cols — long format)")
print(f"✓ noaa_stations.csv     ({NUM_STATIONS} stations metadata)")


# ══════════════════════════════════════════════════════════════════════════════
# 4. PubMed Abstracts  (XML/API-style fields)
#    Real fields: PMID, ArticleTitle, AbstractText, Authors, DOI,
#                 Journal, PubDate_Year, PubDate_Month
# ══════════════════════════════════════════════════════════════════════════════
NUM_PUBMED = 500

abstract_templates = [
    "This study evaluates the impact of {chemical} exposure on {species} colonies across {region}. Results indicate a {pct}% decline in colony health metrics over the study period.",
    "Habitat fragmentation in {region} leads to reduced genetic diversity in native {species} populations. We analyzed {n} sampling sites over {years} years.",
    "Climate change shifts the phenology of flowering plants in {region}, disrupting {species} pollination networks. Mean bloom date advanced by {days} days per decade.",
    "Residues of {chemical} found in pollen samples correlate with increased mortality in {species}. Lethal dose thresholds were exceeded in {pct}% of tested fields.",
    "Urban gardens in {region} provide crucial refuge for {species} amidst surrounding agricultural monocultures. Species richness was {n}x higher in garden plots.",
    "Long-term monitoring of {species} populations in {region} reveals significant population declines linked to {chemical} application rates. We recommend immediate policy intervention.",
    "A meta-analysis of {n} studies spanning {years} years demonstrates that {chemical} negatively affects {species} foraging behavior and navigation abilities.",
    "Field trials in {region} show that integrated pest management reduces {species} mortality by {pct}% compared to conventional {chemical} application schedules.",
]
chemicals = ["neonicotinoid", "imidacloprid", "clothianidin", "thiamethoxam", "organophosphate", "glyphosate"]
species_names = ["Apis mellifera", "Bombus impatiens", "Bombus terrestris", "Osmia lignaria", "Megachile rotundata", "native bumblebee"]
regions = ["Midwest US", "Central Valley CA", "Great Plains", "Eastern Seaboard", "Pacific Northwest", "Southern US"]

titles = [
    "Pesticide Impact on Honeybee Colony Health",
    "Genetic Diversity of Pollinators in Fragmented Habitats",
    "Phenological Shifts in Plant-Pollinator Networks Under Climate Change",
    "Sublethal Neonicotinoid Effects on Solitary Bees",
    "Urban Pollinator Conservation: A Garden Ecology Study",
    "Long-Term Trends in Pollinator Abundance and Pesticide Use",
    "Meta-Analysis of Pesticide Effects on Bee Foraging Behavior",
    "Integrated Pest Management Benefits for Pollinator Health",
]
journals = [
    "Journal of Applied Ecology", "Environmental Science & Technology",
    "Ecology Letters", "PNAS", "Nature Ecology & Evolution",
    "Agriculture, Ecosystems & Environment", "Science of the Total Environment",
]
author_names = [
    "Smith J", "Johnson A", "Williams R", "Brown M", "Jones K",
    "Garcia L", "Martinez C", "Anderson T", "Taylor S", "Thomas D",
    "Wilson P", "Moore H", "Jackson B", "Martin F", "Lee W",
]

generated_abstracts = []
for _ in range(NUM_PUBMED):
    tmpl = np.random.choice(abstract_templates)
    text = tmpl.format(
        chemical=np.random.choice(chemicals),
        species=np.random.choice(species_names),
        region=np.random.choice(regions),
        pct=np.random.randint(5, 65),
        n=np.random.randint(10, 500),
        years=np.random.randint(3, 20),
        days=np.random.randint(2, 12),
    )
    generated_abstracts.append(text)

pub_years = np.random.choice(range(2010, 2025), NUM_PUBMED)
pub_months = np.random.choice(range(1, 13), NUM_PUBMED)

# Generate author lists (2-5 authors per paper)
author_lists = []
for _ in range(NUM_PUBMED):
    n_auth = np.random.randint(2, 6)
    auths = ", ".join(np.random.choice(author_names, n_auth, replace=False))
    author_lists.append(auths)

pubmed_data = pd.DataFrame({
    'PMID': np.arange(30000001, 30000001 + NUM_PUBMED),
    'ArticleTitle': np.random.choice(titles, NUM_PUBMED),
    'AbstractText': generated_abstracts,
    'Authors': author_lists,
    'DOI': [f"10.1{np.random.randint(1000, 9999)}/pollinator.{np.random.randint(2010, 2025)}.{np.random.randint(1000, 9999)}" for _ in range(NUM_PUBMED)],
    'Journal': np.random.choice(journals, NUM_PUBMED),
    'PubDate_Year': pub_years,
    'PubDate_Month': pub_months,
})

pubmed_data.to_csv(os.path.join(OUTPUT_DIR, 'pubmed_abstracts.csv'), index=False)
print(f"✓ pubmed_abstracts.csv  ({NUM_PUBMED} rows, {len(pubmed_data.columns)} cols)")


# ══════════════════════════════════════════════════════════════════════════════
# 5. NASA Landsat / Sentinel-2 Satellite Images (synthetic NDVI arrays)
#    Real data: GeoTIFF multi-band; for prototype we store NDVI as .npy
# ══════════════════════════════════════════════════════════════════════════════
NUM_IMAGES = 50
sat_dir = os.path.join(OUTPUT_DIR, "satellite_images")

for i in range(NUM_IMAGES):
    # NDVI ranges from -1.0 to 1.0; realistic agricultural values cluster 0.2–0.8
    ndvi = np.clip(np.random.normal(0.45, 0.2, (64, 64)), -1.0, 1.0).astype(np.float32)
    np.save(os.path.join(sat_dir, f"sat_image_{i:03d}.npy"), ndvi)

print(f"✓ satellite_images/     ({NUM_IMAGES} .npy files, 64×64 float32)")
print("\n✅ All synthetic data generated successfully!")
