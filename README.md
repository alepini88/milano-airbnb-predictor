# Milan Airbnb Nightly Price Prediction

**Status: Work in progress — structural and geographic models completed; amenity-based feature development planned.**

## Project overview

This project investigates how well the advertised nightly price of an Airbnb listing in Milan can be predicted from property characteristics. It follows an incremental approach: establish a structural-feature benchmark (**Model 1**), measure the contribution of geographic information (**Model 2**), and then investigate additional listing attributes.

**Prediction target:** the advertised nightly price in the source listings data, not the final amount paid by a guest or a completed transaction. All errors are reported in the original numeric price units; the currency has not been independently verified.

## Data and scope

- **Source:** [Inside Airbnb](https://insideairbnb.com/get-the-data/), Milan listings snapshot, September 2026.
- **Raw dataset:** 25,338 listings and 90 columns.
- **Modeling population:** `Entire home/apt` and `Private room` listings with a valid, strictly positive advertised nightly price of **1,000 or less**.
- **Final sample:** 21,314 listings (18,877 entire homes/apartments; 2,437 private rooms).
- **Train/test split:** 80% / 20%, stratified by `room_type`, `random_state=42` (17,051 training; 4,263 test observations).

The price ceiling is a scope decision, not an assertion that higher prices are invalid. Results therefore do not describe all Milan short-term rental listings.

## Modeling approach

### Model 1 — Structural features

Exploratory analysis examined prices, accommodation types, capacity, property categories, missing data, and free-text bathroom descriptions. The initial model uses seven predictors:

| Numeric | Categorical |
| --- | --- |
| `accommodates` | `room_type` |
| `bedrooms` | `property_type` |
| `beds` | `bathroom_type` (derived) |
| `bathrooms_count` (derived) | |

`bathrooms_count` and `bathroom_type` are extracted from `bathrooms_text`. Missing `beds` values are imputed by room-type median with a `beds_missing` indicator; other numeric values use training-set medians. Rare `property_type` categories (fewer than 30 training observations) are grouped as `Other`, and categorical predictors are one-hot encoded.

Three approaches were compared using shuffled five-fold cross-validation on the training set:

| Approach | CV MAE (mean ± SD) | CV R² (mean ± SD) |
| --- | ---: | ---: |
| Median-price baseline | 79.27 ± 2.58 | -0.067 ± 0.011 |
| Ridge regression | 72.35 ± 2.35 | 0.218 ± 0.033 |
| Histogram gradient boosting | **71.48 ± 2.16** | **0.240 ± 0.023** |

Histogram gradient boosting was selected based on cross-validation MAE. On the held-out test set, **Model 1 achieved MAE 70.70 and R² 0.227**. Its test MAE was 71.88 for entire homes/apartments (3,776 observations) and 61.55 for private rooms (487 observations).

### Model 2 — Geographic features

The geographic extension retains the seven structural predictors and evaluates four location variables:

- `latitude` and `longitude`;
- `neighbourhood_cleansed` (87 neighborhoods in the modeling data);
- `distance_duomo_km`, calculated using the Haversine distance to Milan's Duomo (45.4642, 9.1916).

Five feature configurations were evaluated with the same histogram gradient boosting settings and five-fold cross-validation protocol:

| Feature configuration | CV MAE (mean ± SD) | CV R² (mean ± SD) |
| --- | ---: | ---: |
| Structural Baseline | 71.48 ± 2.16 | 0.240 ± 0.023 |
| Distance | 62.03 ± 1.81 | 0.377 ± 0.037 |
| Coordinates | 60.79 ± 1.96 | 0.395 ± 0.037 |
| Neighbourhood | 62.80 ± 2.08 | 0.365 ± 0.031 |
| All Geographic | **60.71 ± 1.73** | 0.395 ± 0.037 |

**Coordinates** was selected for Model 2: it uses only `latitude` and `longitude` alongside the structural predictors, while its mean CV MAE is just 0.082 higher than the more complex All Geographic configuration. The All Geographic advantage was observed in three of five validation folds; the small difference is not treated as evidence of a meaningful performance gain.

### Held-out test comparison

| Metric | Model 1 — Structural | Model 2 — Coordinates |
| --- | ---: | ---: |
| MAE | 70.70 | **61.09** |
| R² | 0.227 | **0.368** |

Model 2 reduced test MAE by **9.61 (13.6%)** and increased R² by **0.141** relative to the recorded Model 1 results. The same filtering and split parameters were used, although exact listing-level test membership has not been independently verified across notebooks.

**Evaluation discipline:** preprocessing and learned transformations are fitted within each cross-validation fold, preventing training/validation leakage. Feature configurations were selected using training-set cross-validation; the selected Model 2 was then evaluated on the holdout. The ± figures above are fold standard deviations, not confidence intervals.

## Repository structure

```text
.
├── data/
│   └── raw/
│       └── listings.csv.gz       # Local source data; not committed
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_preparation.ipynb
│   ├── 03_model_training.ipynb
│   ├── 05_geographic_data_preparation.ipynb
│   └── 06_geographic_model_training.ipynb
├── PROJECT_LOG.md               # Methodological decisions and experiment notes
└── README.md
```

The tree lists the confirmed notebook filenames relevant to these two models; check the repository for any additional files. The raw dataset must be obtained separately and should not be uploaded to GitHub.

## Reproducing the analysis

1. Obtain the corresponding Milan snapshot from [Inside Airbnb](https://insideairbnb.com/get-the-data/) and place `listings.csv.gz` at `data/raw/listings.csv.gz`. The expected raw shape is **25,338 × 90**; other snapshots may yield different results.
2. Set up Python with Jupyter, pandas, NumPy, SciPy, Matplotlib, seaborn, and scikit-learn.
3. Run the notebooks in numerical order, restarting the kernel before a complete run. Each modeling notebook loads the source data independently; variables do not need to persist between notebooks.
4. Consult `03_model_training.ipynb` for Model 1 and `05_geographic_data_preparation.ipynb` / `06_geographic_model_training.ipynb` for the geographic extension.

Notebook 06 has been rerun from start to finish without execution errors in the development environment. A pinned dependency file and a clean-environment reproducibility check are still outstanding.

## Limitations

- **Restricted population:** only two accommodation types and advertised nightly prices up to 1,000 are modeled.
- **Unverified currency:** numeric price units are used without assigning a monetary denomination.
- **Snapshot-based validation:** random splitting of one snapshot does not establish performance on future listings or across market conditions.
- **Comparison caveat:** identical filtering and random-split settings do not independently prove identical listing-level holdout membership across Model 1 and Model 2.
- **Predictive, not causal:** location and property associations do not establish causal price effects. The target also excludes fees and completed booking outcomes.
- **Remaining error:** Model 2 improves predictive accuracy but still leaves substantial unexplained variation.

## Next steps

1. **Investigate amenities (Model 3):** inspect the raw amenity field, define usable features, and assess their incremental predictive value without target leakage.
2. **Preserve evaluation discipline:** compare amenity configurations using training-only cross-validation, avoid repeated test-driven tuning, and establish a consistent holdout comparison.
3. **Improve reproducibility and documentation:** record dependency versions, validate a clean-environment run, review repository organization, and update `PROJECT_LOG.md`.
4. **Extend diagnostics:** assess error patterns by price range and accommodation type; consider temporal or genuinely out-of-sample validation if suitable data become available.

## Data attribution

Listing data are sourced from [Inside Airbnb](https://insideairbnb.com/). Consult the source for dataset availability, documentation, and applicable usage conditions.
