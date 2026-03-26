"""
pollination_project/config.py
=============================
Master configuration file for the Pollination Health Index (PHI) Project.
Controls the scale of the pipeline (Laptop vs. HPC) and all shared constants.
"""

import os

# ── ENVIRONMENT SWITCH ────────────────────────────────────────────────────────
# Set SUBSET = True for local prototype (laptop).
# Set SUBSET = False for full-scale training (University HPC).
SUBSET = True

# ── DIRECTORY STRUCTURE ───────────────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
SUBSET_DATA_DIR = os.path.join(DATA_DIR, "subset")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

MODELS_DIR = os.path.join(ROOT_DIR, "models", "saved")
OUTPUTS_DIR = os.path.join(ROOT_DIR, "outputs")
CONFUSION_DIR = os.path.join(OUTPUTS_DIR, "confusion_matrices")

# Create directories if they don't exist
for d in [SUBSET_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, CONFUSION_DIR]:
    os.makedirs(d, exist_ok=True)

# ── SCALABLE PARAMETERS (controlled by SUBSET) ──────────────────────────────
# number of trees in ensembles (RF, XGB, etc.)
N_ESTIMATORS = 50 if SUBSET else 500

# Whether to run the ResNet-18 CNN feature extractor
# Prototype uses NDVI statistics as a proxy on local machines.
USE_CNN = not SUBSET

# Max features for TF-IDF Vectorizer
TEXT_FEATURES = 100 if SUBSET else 500

# Limit number of satellite images processed
IMAGE_LIMIT = 50 if SUBSET else None

# Number of parallel jobs (-1 uses all cores)
N_JOBS = 1 if SUBSET else -1

# Number of folds for Cross-Validation
CV_FOLDS = 3 if SUBSET else 5

# ── SPATIAL & DATA ALIGNMENT ──────────────────────────────────────────────────
# H3 Resolution level (6 or 7 recommended for regional analysis)
H3_RESOLUTION = 6

# ── PHI LABEL CONSTRUCTION ────────────────────────────────────────────────────
# Weights for the PHI Score calculation
PHI_WEIGHTS = {
    'pollinator_sightings': 0.35,
    'ndvi': 0.25,
    'pesticide_intensity': 0.20,  # Contribution is (1 - intensity)
    'research_sentiment': 0.20
}

# Thresholds for classification
PHI_THRESHOLDS = {
    'HIGH': 0.66,
    'MEDIUM': 0.33,
    'LOW': 0.00
}

# ── SEED ──────────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
