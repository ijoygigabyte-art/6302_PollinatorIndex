Pollination Health Index (PHI) — Multimodal Machine Learning System
Version 1.0 — Prototype → HPC-Scale Training

Overview
This repository contains a multimodal machine learning system that classifies agricultural regions into a Pollination Health Index (PHI) with three categories: LOW, MEDIUM, HIGH. The system integrates satellite imagery, environmental/agricultural tabular data, and scientific text to assess how human activities affect insect pollinators and crop ecosystems. A single configuration flag (SUBSET) allows seamless scaling from a laptop-friendly prototype to full training on university HPC resources.

Motivation
Pollinators support 75% of flowering plants, 35% of global food crops, and $577B in annual agricultural production. Human activities — pesticide use, habitat loss, monoculture farming, and climate disruption — are accelerating pollinator decline. This project provides a data-driven ecological risk assessment tool for researchers, farmers, and policymakers.

Project Goals
- Build an industry-ready multimodal ML pipeline
- Implement 11 required ML models + a Stacking Classifier
- Support prototype and full-scale training with zero code changes
- Produce interpretable outputs: confusion matrices, feature importance, PHI maps
- Enable reproducible research with modular, well-structured code

Datasets
Five public datasets are integrated: GBIF Pollinator Observations, USDA NASS Crops & Pesticides, NASA Landsat/Sentinel-2, NOAA Climate Data, PubMed Abstracts.

Multimodal Feature Engineering
Numeric: StandardScaler (+ PCA).
Images: NDVI (prototype) or ResNet-18 embeddings (HPC).
Text: TF-IDF + sentiment + keyword flags.

Modeling
Trains 11 models including tuned variants, plus a final Stacking Classifier (RF + XGB + GBM → Logistic Regression).

Evaluation
Metrics include accuracy, precision, recall, F1, and confusion matrices. Outputs include ranked model comparison, feature importance, and PHI impact map.

Repository Structure
Refer to project folder layout including config.py, main.py, src modules, data folders, models, and outputs.

Installation
pip install -r requirements.txt

Running the Pipeline
Set SUBSET=True for prototype or SUBSET=False for full HPC training, then run: python main.py

Pipeline Diagram
                 ┌──────────────────────────┐
                 │   Raw Data Sources       │
                 ├──────────────────────────┤
                 │ • GBIF Pollinator Data   │
                 │ • USDA Crops/Pesticides  │
                 │ • NOAA Climate Data      │
                 │ • NASA Landsat/Sentinel  │
                 │ • PubMed Abstracts       │
                 └─────────────┬────────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │   Data Loader (01)       │
                 │  - SUBSET sampling       │
                 │  - Geospatial merging    │
                 └─────────────┬────────────┘
                               │
                               ▼
     ┌──────────────────────────────────────────────────────────┐
     │                Feature Engineering (02–04)               │
     ├──────────────────────────────────────────────────────────┤
     │  Numeric: StandardScaler (+ PCA)                         │
     │  Text: TF-IDF + Sentiment                                │
     │  Images: NDVI (prototype) or ResNet-18 embeddings (HPC)  │
     └─────────────┬───────────────────────────────┬───────────┘
                   │                               │
                   ▼                               ▼
        ┌────────────────┐               ┌──────────────────┐
        │ Numeric Vector │               │ Image Embeddings │
        └────────────────┘               └──────────────────┘
                   │                               │
                   ▼                               ▼
        ┌────────────────┐               ┌──────────────────┐
        │  Text Features │               │  Other Features  │
        └────────────────┘               └──────────────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   ▼
                     ┌──────────────────────────┐
                     │   Unified Feature Matrix  │
                     └───────────────┬──────────┘
                                     │
                                     ▼
                     ┌──────────────────────────┐
                     │   Model Training (05)     │
                     │  11 models + tuned vars   │
                     │  Final Stacking Classifier│
                     └───────────────┬──────────┘
                                     │
                                     ▼
                     ┌──────────────────────────┐
                     │     Evaluation (06)       │
                     │  - Confusion matrices     │
                     │  - F1 ranking table       │
                     │  - Feature importance     │
                     └───────────────┬──────────┘
                                     │
                                     ▼
                     ┌──────────────────────────┐
                     │       Deliverables        │
                     │  Models, charts, reports  │
                     └──────────────────────────┘


License
MIT License (or specify).

Contributions
Pull requests welcome.
