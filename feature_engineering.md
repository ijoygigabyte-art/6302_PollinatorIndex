# Feature Engineering Definitions

This document outlines the raw data features extracted from the downloaded datasets, and the engineered features required for building the Pollinator Index and conducting related spatial/temporal analysis.

## 1. USGS Pesticide National Synthesis Project (PNSP)
**Source**: `usgs_pesticides_dfw.csv`
**Granularity**: County-level, Annual (1992–2023)

### Raw Features
- **`compound`**: The specific pesticide active ingredient (filtered for pollinator-relevant compounds).
- **`year`**: The year of the pesticide use estimate.
- **`county_fips` / `county`**: The FIPS code and name of the DFW county.
- **`epest_low_kg`**: The conservative estimate of pesticide use (in kg) based primarily on surveyed farm data.
- **`epest_high_kg`**: The upper-bound estimate of pesticide use (in kg) including extrapolated use where survey data is missing.

### Engineered Features Needed
- **Total Pesticide Burden**: Aggregation of `epest_low_kg` across all reported compounds per county per year to represent the total pollinator pesticide burden.
- **Pesticide Hazard Index (PHI)**: Uses `epest_low_kg` as the primary foundational variable. By dividing the total kg of pesticide by the total agricultural/cultivated land area in the county (merged from NLCD), we can calculate an application rate or hazard intensity metric.

---

## 2. GBIF Pollinator Occurrences
**Source**: `gbif_occurrences_dfw.csv`
**Granularity**: Individual occurrence records (Point data)

### Raw Features
- **`gbifID`**: Unique identifier for the occurrence record.
- **Taxonomy (`order`, `family`, `genus`, `species`)**: Identification of the observed organism (e.g., bees, butterflies, moths, hoverflies).
- **Location (`decimalLatitude`, `decimalLongitude`, `county`)**: Precise geospatial coordinates and county of the observation.
- **Date (`year`, `month`, `day`)**: Temporal information of the observation.
- **`individualCount`**: Number of individuals observed (when available).
- **`coordinateUncertaintyInMeters`**: Precision of the spatial coordinates.

### Engineered Features Needed
- **Species Richness**: Count of unique species observed per spatial unit (e.g., county or uniform grid cell) per year/month.
- **Occurrence Density**: Count of total observations per spatial unit per given timeframe.
- **Pollinator Presence**: Binary indicators tracking the presence/absence of specific key pollinator families (e.g., *Apidae*, *Syrphidae*) at given locations.

---

## 3. NLCD Land Cover (NASA/Landsat)
**Source**: `nlcd_<year>_dfw.tif`
**Granularity**: 30m resolution Raster (Geospatial)

### Raw Features
- **Pixel Values (Class Codes)**: Integer values corresponding to the NLCD legend. Key categories include:
  - `21-24`: Developed Areas (varying intensity)
  - `41-43`: Forested Areas
  - `71`: Grassland/Herbaceous (Key Pollinator Habitat)
  - `81`: Pasture/Hay (Semi-natural Habitat)
  - `82`: Cultivated Crops (Key variable for pesticide application)

### Engineered Features Needed
- **Habitat Availability Fraction**: Proportion of a spatial extent (e.g., a county, or a localized buffer radius around an occurrence point) that consists of pollinator-friendly land cover (`71`, `81`, `41-43`).
- **Agricultural Intensity Fraction**: Proportion of the area classified as Cultivated Crops (`82`). This is essential for normalizing the county-level USGS pesticide mass into an application rate.
- **Urbanization Index**: Proportion of developed/impervious classes (`21-24`), representing habitat loss and urban stress.

---

## Data Integration & Modeling Plan

To build the final analytical dataset (the feature matrix), these sources must be integrated:
1. **Spatial Join**: Overlay **GBIF occurrences** with **NLCD Land Cover** to extract the surrounding land cover proportions (e.g., within a 1km or 5km buffer) for each observation point.
2. **Agricultural Normalization**: Calculate the total hectares of Cultivated Crops (`82`) within each county using **NLCD** data for the corresponding year.
3. **Hazard Rate Calculation**: Merge the **USGS Pesticide** kg estimates with the county-level agricultural area to compute an estimated application density (kg / hectare of crop).
4. **Final Matrix**: Combine the localized habitat availability, agricultural intensity, and pesticide hazard rate with the pollinator occurrence/richness metrics to model the impacts over space and time.

---

## 5. Feature Relationships to Final Target (PHI Score)

The final predicting label is the **Pollination Health Index (PHI) Class** (`0=LOW`, `1=MEDIUM`, `2=HIGH`), representing the overall health of the pollinator ecosystem in a given area. The engineered features detailed below serve as the primary predictors to map human activities to this index:

### Core Predictors & Expected Relationships

- **`pollination_health_class` (Target)**
  - **Description**: The synthesized target variable derived from a combination of high biological activity (species richness) and low chemical stress (pesticide hazard).

- **`county_fips` & `year`**
  - **Description**: Spatiotemporal Identifying Features tracking DFW counties from 2010 to 2023.
  - **Relationship**: Captures baseline unobserved heterogeneities (e.g., regional variations or overall time trends) and allows for robust spatial cross-validation.

- **`habitat_availability_fraction`**
  - **Description**: Scaled percentage (0 to 1) representing the fraction of pollinator-friendly landscape.
  - **Relationship**: *Positive driver*. Higher fractions provide natural foraging and nesting resources, pushing the PHI score toward `HIGH`.

- **`agricultural_intensity_fraction`**
  - **Description**: Scaled percentage (0 to 1) representing the footprint of cultivated crops.
  - **Relationship**: *Stressor multiplier*. Intensive monoculture lacks varied floral resources. High values typically correlate with lower PHI scores unless mitigated by pesticide-free regimes.

- **`urbanization_index`**
  - **Description**: Scaled percentage (0 to 1) representing developed or impervious land.
  - **Relationship**: *Negative driver*. Higher indices cause habitat fragmentation and increase urban environmental stress, likely pushing the PHI score toward `LOW`.

- **`total_pesticide_burden_kg`**
  - **Description**: Synthesized total mass of synthesized pesticide applied.
  - **Relationship**: Represents the absolute raw chemical pressure acting on the local ecosystem.

- **`pesticide_hazard_index`**
  - **Description**: A critical calculated ratio that normalizes the absolute pesticide burden by the total available agricultural area.
  - **Relationship**: *Key localized stressor*. High hazard scores act as chemical bottlenecks, substantially depressing biological indicators and strongly driving the prediction toward a `LOW` PHI.

- **`species_richness` & `occurrence_density`**
  - **Description**: Simulated continuous counts of unique species and overall observation traffic.
  - **Relationship**: *Direct biological indicators*. They form the foundational ground truth of health. Regions with high density are near-guaranteed to fall into a `HIGH` PHI class.

- **`apidae_presence` & `syrphidae_presence`**
  - **Description**: Binary occurrence indicators (`0` or `1`) tracking indicator taxa (Bees and Hoverflies).
  - **Relationship**: *Sentinel markers*. The presence of these taxa highlights ecosystem resilience. Absence often signals acute toxicity or extreme habitat loss (correlating with `LOW` PHI).

---

## 6. Feature Computation Methodologies

The specific programmatic steps to aggregate the engineered features from the raw data files are defined below:

### From `gbif_occurrences_dfw.csv` (Biological Indicators)
- **`species_richness`**: Group all GBIF rows by `county` and `year`, then count the number of unique values in the `species` column for that group. Multiple sightings of the same species only count as 1.
- **`occurrence_density`**: Group similarly by `county` and `year`, but return the total number of rows. Each row is one observation event.
- **`apidae_presence` / `syrphidae_presence`**: Group by `county` and `year` and check if the keyword "Apidae" or "Syrphidae" respectively appears in the `family` column. Map to `1` if present, otherwise `0`.

### From `usgs_pesticides_dfw.csv` (Chemical Stressors)
- **`total_pesticide_burden_kg`**: Filter down to a single `county` and `year`, then compute the sum of all `epest_low_kg` values across every single `compound` row. This represents the total localized chemical weight applied.
- **`pesticide_hazard_index`** *(Cross-file Calculation)*: Retrieve the total cropland area (`hectares`) for the county-year from the NLCD dataset. Divide the `total_pesticide_burden_kg` by this cultivated area to yield the absolute application rate (`kg/ha`).

### From `nlcd_<year>_dfw.tif` (Environmental Drivers)
- **`habitat_availability_fraction`**: Clip the NLCD raster to the relevant county boundary. Count all pixels with class codes `41, 42, 43` (forest), `71` (grassland), and `81` (pasture). Divide this target count by the total pixel count within the county.
- **`agricultural_intensity_fraction`**: Follows the same methodology, but targets only pixels with class code `82` (Cultivated Crops). 
- **`urbanization_index`**: Follows the same methodology, but targets pixels with class codes `21, 22, 23, 24` (developed land at any intensity). Expect significant geographic variance across the DFW footprint (e.g., Dallas/Tarrant vs. Ellis/Denton).



****
species_richness — from gbif_occurrences_dfw.csv
Group all GBIF rows by county and year, then count how many unique values appear in the species column for that group. One county in one year might have 200 sighting records, but if they're all the same 34 species, the richness is 34. This is a direct biological indicator — it forms part of the ground truth of ecosystem health. Counties with high species richness are near-guaranteed to land in the HIGH PHI class.
occurrence_density — from gbif_occurrences_dfw.csv
Same grouping as above, but instead of counting unique species, just count the total number of rows. Every row is one observation event, so this is simply how many times any pollinator was recorded in that county that year. Like species richness, this is a direct biological signal — high density strongly pushes the prediction toward HIGH PHI.
apidae_present / syrphidae_present — from gbif_occurrences_dfw.csv
Group by county and year, then check whether the word "Apidae" (or "Syrphidae") ever appears in the family column for that group. If it does at least once, the value is 1. If not, 0. These families act as sentinel markers — their presence signals ecosystem resilience, while their absence often points to acute toxicity or severe habitat loss, both of which correlate with LOW PHI.
total_pesticide_burden_kg — from usgs_pesticides_dfw.csv
Filter to one county and one year, then add up all the epest_low_kg values across every compound row. So if Dallas in 2016 has 30 compound rows, you sum all 30 kg values into a single number. This represents the absolute raw chemical pressure on the local ecosystem — it tells you how much total pesticide mass was applied, before accounting for how much farmland it was spread across.
pesticide_hazard_index — from usgs_pesticides_dfw.csv + NLCD raster
This is the one cross-dataset calculation. First get total_pesticide_burden_kg for the county-year from the USGS file. Then compute the total cropland hectares in that county from the NLCD raster (explained below). Divide kg by hectares to get kg/ha. This is the key localized stressor in the model — a county might have modest total kg but tiny farmland, making the application rate extremely intense. High values act as a chemical bottleneck that strongly drives predictions toward LOW PHI.
habitat_availability_frac — from nlcd_<year>_dfw.tif
Clip the NLCD raster to the county boundary. Count all pixels with class codes 41, 42, 43 (forest), 71 (grassland), and 81 (pasture). Divide by the total pixel count in the county. The result is the fraction of the county that is pollinator-friendly habitat. This is a positive driver — higher fractions mean more natural foraging and nesting resources, pushing the PHI score toward HIGH.
agricultural_intensity_frac — from nlcd_<year>_dfw.tif
Same process, but only count pixels with class code 82 (Cultivated Crops). Divide by total county pixels. This is also the denominator you use to compute the pesticide hazard index above — multiply this fraction by the county's total area in hectares to get cropland hectares. This acts as a stressor multiplier: intensive monoculture lacks varied floral resources, so high values typically correlate with lower PHI unless the pesticide hazard index is also low.
urbanization_index — from nlcd_<year>_dfw.tif
Same process again, but count pixels with codes 21, 22, 23, and 24 (developed land at any intensity). Divide by total county pixels. This is a negative driver — higher values mean more habitat fragmentation and urban environmental stress, pushing the PHI score toward LOW. For DFW, expect Dallas and Tarrant to dominate on this feature while Ellis and Denton sit much lower.