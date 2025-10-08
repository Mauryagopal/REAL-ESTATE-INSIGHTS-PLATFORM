
## 📁 Project Folder Structure

```
├── Dataset
│   ├── appartments.csv
│   ├── flats.csv
│   ├── flats_cleaned.csv
│   ├── gurgaon_properties.csv
│   ├── gurgaon_properties_cleaned_v1.csv
│   ├── gurgaon_properties_cleaned_v2.csv
│   ├── gurgaon_properties_missing_value_imputation.csv
│   ├── gurgaon_properties_outlier_treated.csv
│   ├── gurgaon_properties_post_feature_selection.csv
│   ├── gurgaon_properties_post_feature_selection_v2.csv
│   ├── house_cleaned.csv
│   └── houses.csv
├── Notebooks
│   ├── Data_Cleaning_files
│   │   ├── data-preprocessing-flats.ipynb
│   │   ├── data-preprocessing-houses.ipynb
│   │   ├── data-preprocessing-level-2.ipynb
│   │   └── merge-flats-and-house.ipynb
│   ├── EDA
│   │   ├── eda-multivariate-analysis.ipynb
│   │   ├── eda-pandas-profiling.ipynb
│   │   └── eda-univariate-analysis.ipynb
│   ├── Feature_Engineering_files
│   │   ├── feature-engineering.ipynb
│   │   ├── feature-selection-and-feature-engineering.ipynb
│   │   └── feature-selection.ipynb
│   ├── Model_building
│   │   ├── baseline model.ipynb
│   │   ├── final_model.ipynb
│   │   ├── hyperparameter_tunning.ipynb
│   │   └── model-selection.ipynb
│   └── outliers_and_Missing_Value_Handle
│       ├── missing-value-imputation.ipynb
│       └── outlier-treatment.ipynb
├── README.md
├── Saved_Model
│   ├── expected_columns.json
│   ├── expected_columns_with_examples.json
│   └── gurgaon_price_model.joblib
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── analytics_routes.py
│   │   ├── home_routes.py
│   │   ├── insights_routes.py
│   │   ├── prediction_routes.py
│   │   └── recommendation_routes.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   ├── images
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── analytics.html
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── insights.html
│   │   ├── prediction.html
│   │   └── recommendation.html
│   └── utils
│       ├── data_helper.py
│       ├── model_loader.py
│       └── recommendation_engine.py
├── create_flask_structure.py
├── generate_tree.py
├── requirements.txt
└── run.py
```
