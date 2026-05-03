import pandas as pd
import numpy as np
import joblib
import lightgbm as lgb
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

# Config
SEED = 123
MODEL_PATH = "model.joblib"

selected_features = [
    'ORGANIZATION_TYPE', 'EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3',
    'INST_DPD_LATE_MEAN', 'AMT_CREDIT', 'INST_AMT_PAYMENT_SUM', 'AMT_ANNUITY',
    'DAYS_EMPLOYED', 'POS_CNT_INSTALMENT_FUTURE_MEAN', 'AMT_GOODS_PRICE',
    'INST_DBD_MEAN', 'BURO_DAYS_CREDIT_MAX', 'PREV_CNT_PAYMENT_MEAN',
    'BURO_DAYS_CREDIT_ENDDATE_MAX', 'OCCUPATION_TYPE', 'DAYS_ID_PUBLISH',
    'CC_CNT_DRAWINGS_ATM_CURRENT_MEAN', 'OWN_CAR_AGE', 'CODE_GENDER'
]

def export():
    # In a real scenario, we would load the 'train_final.csv'
    print("Loading data...")
    try:
        # Check if train_final.csv exists (from Polars merge)
        if os.path.exists("Data/train_final.csv"):
            df = pd.read_csv("Data/train_final.csv")
        else:
            df = pd.read_csv("Data/application_train.csv")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Keep only available selected features
    available_features = [c for c in selected_features if c in df.columns]
    X = df[available_features]
    y = df['TARGET']

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()

    # Preprocessing
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    onehot_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='undefined')),
        ('hot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', onehot_transformer, categorical_features)
    ])

    # Best model params from notebook
    best_params = {
        'n_estimators': 200,
        'learning_rate': 0.05,
        'num_leaves': 31,
        'max_depth': -1,
        'min_child_samples': 20,
        'class_weight': 'balanced',
        'random_state': SEED,
        'n_jobs': -1
    }

    model = lgb.LGBMClassifier(**best_params)

    full_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])

    print("Training model...")
    full_pipeline.fit(X, y)

    print(f"Saving model to {MODEL_PATH}...")
    joblib.dump(full_pipeline, MODEL_PATH)
    print("Export complete.")

if __name__ == "__main__":
    import os
    export()
