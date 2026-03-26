# Review Report: Prompt 1 & 2 Implementation

## What This Project Does (Plain English)

This project builds a **Pollination Health Index** — a system that looks at data about bees, crops, weather, satellite images, and scientific research papers, then uses machine learning to classify whether a region's pollinator health is **LOW**, **MEDIUM**, or **HIGH**.

The first two steps (Prompts 1 & 2) set up the project's **control panel** and the **data merging engine**.

---

## Prompt 1: Configuration ([config.py](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/config.py)) — ✅ Correct

### What It Does
Think of [config.py](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/config.py) as the project's **control panel with a single master switch**. When you flip the switch (`SUBSET = True`), the entire system runs in "laptop mode" — small data, fast results, perfect for testing. Flip it to `False`, and it runs on the university's powerful computers with full-scale data.

### What the Code Controls

| Setting | Laptop Mode (`True`) | HPC Mode (`False`) | Purpose |
|---------|---------------------|---------------------|---------|
| `N_ESTIMATORS` | 50 trees | 500 trees | How many "decision trees" each ML model uses |
| `USE_CNN` | Off (NDVI stats) | On (ResNet-18) | Simple image analysis vs. deep learning |
| `TEXT_FEATURES` | 100 words | 500 words | How many keywords to extract from research papers |
| `IMAGE_LIMIT` | 50 images | All images | How many satellite images to process |
| `N_JOBS` | 1 core | All cores | How much of the computer's power to use |
| `CV_FOLDS` | 3 folds | 5 folds | How rigorously to validate each model |

### PHI Scoring Formula
The code defines how the final health score is calculated — a weighted average of four factors:
- **Pollinator sightings (35%)** — How many bees/butterflies were observed
- **NDVI vegetation index (25%)** — How green/healthy the land is (from satellite)
- **Pesticide intensity (20%)** — How much pesticide is used (inverted — less is better)
- **Research sentiment (20%)** — What scientists are saying in published studies

### Verdict
> [!TIP]
> **Well implemented.** All PRD requirements for the config file are met. Directory auto-creation, scaling parameters, PHI weights, and thresholds are all correctly coded.

---

## Prompt 2: Data Loader ([src/01_data_loader.py](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/src/01_data_loader.py)) — ⚠️ Mostly Correct (Minor Issues)

### What It Does
This is the **data merging engine**. It takes 5 completely different datasets that each describe the world differently, and stitches them together onto a **common map grid** using hexagonal tiles (like a honeycomb laid over the US). This way, for any given hex tile in any given month, we know: how many pollinators were sighted, what the weather was, what crops were grown, what scientists published, and what the satellite saw.

### How the 5 Datasets Are Handled

| Dataset | What It Contains | How It's Aligned |
|---------|-----------------|------------------|
| **GBIF** (pollinators) | Bee/butterfly sightings with GPS coordinates | Each sighting's lat/lon → mapped to a hex tile. Aggregated by tile + year + month |
| **USDA** (crops) | Crop yields and pesticide data by county | Each county gets a synthetic GPS point → mapped to hex tile. Aggregated by tile + year |
| **NOAA** (weather) | Daily temperature and precipitation from weather stations | Each station's lat/lon → mapped to hex tile. Pivoted so TMAX, TMIN, PRCP become columns |
| **PubMed** (research) | Scientific paper abstracts about pollinators | No location data — joined by year + month only (applied equally across all regions) |
| **NASA** (satellite) | 64×64 NDVI vegetation images | Each image gets synthetic coordinates → mapped to hex tile + year + month |

### Merge Strategy
The code uses GBIF (pollinator sightings) as the **anchor dataset** — every row starts as a pollinator observation. Then it layers on weather, crop data, research text, and satellite images by matching on hex tile and time period.

### Output Verified
The merged file [merged_space_time_grid.csv](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/data/processed/merged_space_time_grid.csv) has:
- **2,001 rows** (one header + 2,000 data rows)
- **14 columns**: [h3_index](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/src/01_data_loader.py#19-22), `year`, `month`, `obs_count`, `total_pollinators`, `species_richness`, `PRCP`, `SNOW`, `SNWD`, `TMAX`, `TMIN`, `avg_crop_val`, `merged_abstracts`, `image_path`

### Issues Found

> [!WARNING]
> **Issue 1: Most satellite images are not linked.** The `image_path` column is `0` for almost all rows. This happens because the random hex tiles assigned to images almost never match the random hex tiles from GBIF sightings. This is expected with synthetic data — in a real scenario with overlapping geographic coverage, there would be more matches.

> [!NOTE]
> **Issue 2: NOAA adds extra columns.** The climate data brings in `SNOW` and `SNWD` (snow depth) columns alongside `PRCP`, `TMAX`, `TMIN`. These are bonus features from the GHCN-Daily dataset — they won't cause errors but aren't mentioned in the PRD. They could be useful or dropped later.

> [!NOTE]
> **Issue 3: Most climate/crop values are 0.** Because the hex tiles from different datasets rarely overlap (each dataset generates random coordinates independently), left joins produce mostly zeros. Again, this is a synthetic data artifact, not a code bug.

### Verdict
> [!TIP]
> **The code logic is correct.** The H3 hexagonal alignment, temporal joins, and aggregation strategy all follow the PRD. The sparse matches are expected behavior with independently-generated synthetic data.

---

## Summary Scorecard

| Aspect | Status | Notes |
|--------|--------|-------|
| [config.py](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/config.py) structure | ✅ Pass | All required settings present |
| SUBSET scaling logic | ✅ Pass | Correctly toggles all parameters |
| PHI score formula | ✅ Pass | Weights sum to 1.0, thresholds are correct |
| H3 spatial indexing | ✅ Pass | Uses correct v4 syntax (`latlng_to_cell`) |
| 5-dataset loading | ✅ Pass | All 5 datasets loaded with appropriate logic |
| Merge strategy | ✅ Pass | Left joins preserve all GBIF rows |
| Output file produced | ✅ Pass | [merged_space_time_grid.csv](file:///f:/MASTERS/SEM2/6302ASDS/Final_Project/data/processed/merged_space_time_grid.csv) exists with expected shape |
| Data sparsity | ⚠️ Note | Expected with synthetic data — not a code defect |

---

## What Comes Next (Prompt 3)
The next step is **Feature Engineering** — transforming this raw merged grid into numbers that machine learning models can actually learn from:
- Scale numeric columns (temperature, precipitation) to comparable ranges
- Extract statistics from satellite images (average greenness, variation)
- Convert research paper text into numeric word-frequency vectors (TF-IDF)
- Calculate the final PHI score and label each row as LOW / MEDIUM / HIGH
