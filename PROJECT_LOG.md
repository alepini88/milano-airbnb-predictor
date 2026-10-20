# Project Log — Milan Airbnb Nightly Price Prediction

**Status:** Work in progress. Model 1 completed; further experiments planned.  
**Dataset:** Inside Airbnb, Milan, September 2026 listings snapshot.

## Project objective

Predict advertised nightly listing prices using a reproducible baseline and progressively richer features. Model 1 deliberately uses structural property attributes only. The target is the numeric price parsed from the source `price` field (displayed with `$`); the underlying currency has not been independently verified.

## Model 1 — Scope and data decisions

- Raw source: **25,338 rows, 90 columns**.
- Included room types: `Entire home/apt` and `Private room`.
- Included prices: successfully parsed, **strictly greater than 0 and at most 1,000**. This threshold defines the study population; higher prices are not automatically treated as errors.
- Resulting population: **21,314 listings** — **18,877 entire homes/apartments** and **2,437 private rooms**.
- Split: 80% training / 20% holdout, stratified by `room_type`, `random_state=42`.
- Training: **17,051** listings (15,101 entire homes/apartments; 1,950 private rooms).
- Test: **4,263** listings (3,776 entire homes/apartments; 487 private rooms).
- The test set is reserved for final model evaluation; cross-validation and model selection use training data only.

## Structural predictors and feature engineering

Seven initial predictors:

- Numeric: `accommodates`, `bedrooms`, `beds`, `bathrooms_count`.
- Categorical: `room_type`, `property_type`, `bathroom_type`.

`bathrooms_count` and `bathroom_type` are extracted from `bathrooms_text` using fixed text-parsing rules. Half-bath descriptions are represented as 0.5 bathrooms. Bathroom privacy categories are `private`, `shared`, `unspecified`, and `missing`.

Missing-data decisions:

- Retain `bedrooms=0` (plausible studio apartments).
- Impute missing `beds` using training-fold medians by `room_type`, with a global median fallback; add `beds_missing` indicator.
- Impute remaining numeric missing values using training-fold medians.
- Group `property_type` levels with fewer than **30** training-fold examples into `Other`; map unseen categories to `Other`.
- One-hot encode categorical variables with `handle_unknown="ignore"`.

The training preprocessing check produced **26 transformed features**. Learned preprocessing is fitted within each model's cross-validation pipeline to avoid information leakage. Model 1 excludes location, proximity to transit and amenities.

## Model comparison

Evaluation: five-fold `KFold(n_splits=5, shuffle=True, random_state=42)` on training data. Primary metric: MAE; secondary metric: R². Reported ± values are standard deviations across validation folds, not confidence intervals.

| Model | CV MAE (mean ± SD) | CV R² (mean ± SD) |
| --- | ---: | ---: |
| Median baseline (`DummyRegressor`) | 79.27 ± 2.58 | -0.067 ± 0.011 |
| `Ridge(alpha=1.0)` | 72.35 ± 2.35 | 0.218 ± 0.033 |
| `HistGradientBoostingRegressor(max_iter=200, learning_rate=0.05, max_leaf_nodes=15, random_state=42)` | **71.48 ± 2.16** | **0.240 ± 0.023** |

Out-of-fold MAE by accommodation type:

| Room type | Training listings | Ridge | HistGradientBoosting |
| --- | ---: | ---: | ---: |
| Entire home/apt | 15,101 | 73.67 | 72.94 |
| Private room | 1,950 | 62.14 | 60.16 |

**Selection:** HistGradientBoosting has the lowest overall cross-validated MAE and lower MAE in both accommodation groups. The improvement over Ridge is modest; no statistical significance claim is made.

## Final holdout evaluation

HistGradientBoosting was fitted on all training data after model selection, then evaluated on the holdout set.

| Metric | Holdout result |
| --- | ---: |
| Overall MAE | **70.70** |
| Overall R² | **0.227** |
| Entire home/apt MAE (3,776 test listings) | 71.88 |
| Private room MAE (487 test listings) | 61.55 |

The error is measured in the original numeric price units and remains substantial. This is a random holdout from a single snapshot, not a temporal or external validation. The prediction target is an advertised nightly price, not a completed transaction price.

## Notebook review and repository preparation

- `01_data_understanding.ipynb`: EDA and distinctions between exploratory subsets and the final modeling population; feature-selection rationale documented.
- `02_data_preparation.ipynb`: strictly positive price filter; explicit explanation of training-only preprocessing and fold-level refitting.
- `03_model_training.ipynb`: consistent population filter, baseline and model comparison, out-of-fold group analysis, and final test evaluation.
- English, impersonal Markdown documentation intended for public reading.
- README documents the project as work in progress.
- Repository package includes notebook files, dependency list, and `.gitignore`; source data excluded.

**Verification status:** The notebook code has been syntax-checked and the user reported successful execution in VS Code. A full clean-environment run of the packaged repository has **not** been independently verified. Dependency versions are not pinned; the environment must be recorded before claiming exact reproducibility across machines.

## Planned next steps

1. Verify a clean run of all three notebooks in the packaged folder layout, using the matching raw snapshot.
2. Record tested package versions and consider pinning them for reproducibility.
3. Develop Model 2 with geographical information (e.g., coordinates and interpretable distance features); compare against Model 1 using a consistent validation design.
4. Explore amenity-related predictors and inspect error patterns by price range and accommodation type.
5. Document whether additional features improve generalization; avoid selecting features or tuning based on repeated test-set inspection.
