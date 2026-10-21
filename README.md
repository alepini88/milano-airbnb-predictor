# Milan Airbnb Nightly Price Prediction

**Status: Work in progress — Model 1 completed; further feature development planned.**

## Project overview

This project investigates how well the advertised nightly price of an Airbnb listing in Milan can be estimated from information about the property. The initial goal is to establish a reproducible benchmark using structural listing attributes, then assess whether additional information (particularly location) improves predictive performance.

The project is developed incrementally. **Model 1** covers data exploration, preparation, model comparison, and a final holdout evaluation. Subsequent models are planned but have **not yet been implemented or evaluated**.

**Prediction target:** the advertised nightly price in the source listings data, not the final amount paid by a guest or the price of a completed booking. Prices are analyzed in the numeric units shown in the source file. 

## Data and scope

- **Source:** [Inside Airbnb](https://insideairbnb.com/get-the-data/), Milan listings snapshot, September 2026.
- **Raw dataset:** 25,338 listings and 90 columns.
- **Model 1 population:** `Entire home/apt` and `Private room` listings with a valid, strictly positive nightly price of **1,000 or less**.
- **Modeling sample:** 21,314 listings, comprising 18,877 entire homes/apartments and 2,437 private rooms.
- **Train/test split:** 80% / 20%, stratified by `room_type` (`random_state=42`): 17,051 training observations and 4,263 test observations.

The price ceiling defines the scope of this first experiment. Listings above 1,000 are not assumed to be erroneous. Findings therefore apply to the selected property types and price range, rather than to the entire Milan short-term rental market.

## Completed work: Model 1

### 1. Data understanding and exploratory analysis

The exploratory notebook examines the price distribution, extreme advertised prices, price availability, accommodation types, guest capacity, property categories, and missing structural information. It also examines the free-text bathroom descriptions used to construct two predictors.

The exploration starts from the full dataset. Some descriptive comparisons use the two selected accommodation types **before** the final price filter is applied; the modeling population is defined explicitly in the preparation notebook.

### 2. Data preparation

Model 1 uses seven structural predictors:

| Numeric predictors | Categorical predictors |
| --- | --- |
| `accommodates` | `room_type` |
| `bedrooms` | `property_type` |
| `beds` | `bathroom_type` (derived) |
| `bathrooms_count` (derived) | |

`bathrooms_count` and `bathroom_type` are extracted from `bathrooms_text`. Missing `beds` values are imputed using the median for each accommodation type, with a `beds_missing` indicator added to retain missingness information. Other numeric missing values are filled with training-set medians. Property categories appearing fewer than 30 times in the training data are grouped as `Other`, and categorical variables are one-hot encoded.

Preprocessing is included **inside each model's cross-validation pipeline**, so fitted imputations and category frequencies are learned separately for each training fold. The holdout test set is reserved for final evaluation.

This initial model intentionally excludes geographic coordinates, distance to landmarks, transit accessibility, and amenity features.

### 3. Model comparison

Three approaches were compared using five-fold shuffled cross-validation on the training set. **Mean absolute error (MAE)** is the primary metric, R² is reported as a complementary measure.

| Model | Cross-validation MAE (mean ± SD) | Cross-validation R² (mean ± SD) |
| --- | ---: | ---: |
| Median-price baseline | 79.27 ± 2.58 | -0.067 ± 0.011 |
| Ridge regression | 72.35 ± 2.35 | 0.218 ± 0.033 |
| Histogram gradient boosting | **71.48 ± 2.16** | **0.240 ± 0.023** |

The ± values are standard deviations across the five validation folds, **not** confidence intervals. Histogram gradient boosting was selected because it had the lowest overall cross-validation MAE and the lowest cross-validated MAE within each of the two accommodation types. The difference from Ridge is modest and is not presented as statistically significant.

### 4. Final evaluation

After model selection, histogram gradient boosting was fitted on the full training set and evaluated on the previously held-out test set.

| Test metric | Result |
| --- | ---: |
| MAE | **70.70** |
| R² | **0.227** |
| Entire home/apt MAE (3,776 listings) | 71.88 |
| Private room MAE (487 listings) | 61.55 |

The MAE is measured in the original numeric price units. It is an **average absolute error**, not a guarantee that individual predictions fall within that distance of the observed price. Although the model improves on the median baseline, its error remains substantial. These results come from a random split of one snapshot and do not establish performance on future listings or other time periods.

## Repository structure

```text
.
├── data/
│   └── raw/
│       └── listings.csv.gz       # Source dataset, obtained separately
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_preparation.ipynb
│   └── 03_model_training.ipynb
├── PROJECT_LOG.md               # Methodological decisions and experiment notes
└── README.md
```

The source dataset is not included in this README and may need to be downloaded separately in accordance with its terms of use.

## Reproducing Model 1

1. Obtain the corresponding Milan listings snapshot from Inside Airbnb and place the compressed CSV at `data/raw/listings.csv.gz`. The expected source shape is **25,338 rows × 90 columns**; a different snapshot may produce different results.
2. Use a Python environment with Jupyter, pandas, NumPy, Matplotlib, seaborn, and scikit-learn installed.
3. Open the notebooks from either the repository root or the `notebooks/` directory. The notebooks resolve the dataset path from either location.
4. Run the notebooks in order, restarting the kernel before each complete run:
   - `01_data_understanding.ipynb` — descriptive exploration;
   - `02_data_preparation.ipynb` — modeling sample and preprocessing checks;
   - `03_model_training.ipynb` — cross-validation, model selection, and holdout evaluation.

The notebooks load the source dataset independently; running one does not require variables to remain in memory from another. A pinned dependency file has not yet been finalized, so exact cross-environment reproducibility still requires verification.

## Limitations

- **No location features in Model 1.** Neighborhood and accessibility may explain important price differences that structural attributes alone cannot capture.
- **Restricted population.** Results cover two room types and nightly prices up to 1,000.
- **Snapshot-based evaluation.** A random holdout from one snapshot does not measure performance over time or under market changes.
- **Advertised prices only.** The target does not represent completed transactions or total booking costs.
- **Limited explanatory scope.** Predictive associations should not be interpreted as causal effects on price.

## Next steps

The following work is **planned**, not completed:

1. **Finalize repository reproducibility:** review file organization, document package versions in a dependency file, confirm a clean run from a fresh environment, and update `PROJECT_LOG.md`.
2. **Develop Model 2 with location information:** evaluate latitude/longitude and interpretable location-related features, such as distance to central landmarks or transit, where suitable data are available.
3. **Assess additional listing attributes:** investigate whether selected amenities and other information available when a listing is created improve performance without introducing target leakage.
4. **Compare models consistently:** retain the same evaluation principles, compare new approaches against Model 1 using training-only model selection, and avoid using the original holdout repeatedly for tuning.
5. **Extend error analysis:** examine error patterns across price ranges and accommodation segments, and consider a more realistic temporal or out-of-sample evaluation if suitable data become available.

The purpose of these stages is to test measurable improvements, not to assume that adding features or more complex models will necessarily produce better predictions.

## Data attribution

Listing data are sourced from [Inside Airbnb](https://insideairbnb.com/). Please consult the source for dataset availability, documentation, and applicable usage conditions.





