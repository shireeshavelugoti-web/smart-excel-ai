import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, precision_score, recall_score, f1_score

# In-memory trained model store for session persistence
TRAINED_MODELS_STORE: Dict[str, Dict[str, Any]] = {}

def analyze_dataset_ml(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes statistical metrics, feature correlations, and distributions for ML analysis.
    """
    num_df = df.select_dtypes(include=[np.number])
    corr_matrix = {}
    if not num_df.empty and num_df.shape[1] > 1:
        corr = num_df.corr().fillna(0)
        corr_matrix = {
            "columns": list(corr.columns),
            "values": corr.values.round(3).tolist()
        }
        
    num_cols = num_df.columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    feature_stats = {}
    for col in df.columns:
        if col in num_cols:
            feature_stats[col] = {
                "type": "numerical",
                "mean": round(float(df[col].mean()), 2) if not df[col].isnull().all() else 0,
                "min": round(float(df[col].min()), 2) if not df[col].isnull().all() else 0,
                "max": round(float(df[col].max()), 2) if not df[col].isnull().all() else 0,
                "missing": int(df[col].isnull().sum())
            }
        else:
            feature_stats[col] = {
                "type": "categorical",
                "unique_count": int(df[col].nunique()),
                "top_value": str(df[col].mode()[0]) if not df[col].mode().empty else "N/A",
                "missing": int(df[col].isnull().sum())
            }

    return {
        "rows": len(df),
        "columns": list(df.columns),
        "numerical_features": num_cols,
        "categorical_features": cat_cols,
        "correlation": corr_matrix,
        "feature_stats": feature_stats
    }

def train_ml_model(df: pd.DataFrame, target_column: str, model_name: str = "Random Forest", test_size: float = 0.2) -> Dict[str, Any]:
    """
    Trains a classification or regression pipeline using Scikit-Learn.
    Supported models: Linear Regression, Logistic Regression, Random Forest.
    """
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in dataset.")
        
    # Drop rows where target is missing
    clean_df = df.dropna(subset=[target_column]).copy()
    if len(clean_df) < 10:
        raise ValueError("Dataset must have at least 10 non-null target rows for machine learning.")

    X = clean_df.drop(columns=[target_column])
    y = clean_df[target_column]
    
    # Determine Task Type (Regression vs Classification)
    if pd.api.types.is_numeric_dtype(y) and y.nunique() > 10:
        task_type = "regression"
    else:
        task_type = "classification"
        
    num_features = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_features = X.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Preprocessing Pipelines
    num_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    cat_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_transformer, num_features),
            ('cat', cat_transformer, cat_features)
        ]
    )
    
    # Select Model Estimator
    model_name_clean = model_name.strip().lower()
    if task_type == "regression":
        if "linear" in model_name_clean:
            model = LinearRegression()
            selected_model_title = "Linear Regression"
        else:
            model = RandomForestRegressor(n_estimators=50, random_state=42)
            selected_model_title = "Random Forest Regressor"
    else:
        if "logistic" in model_name_clean:
            model = LogisticRegression(max_iter=500)
            selected_model_title = "Logistic Regression"
        else:
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            selected_model_title = "Random Forest Classifier"

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    pipeline.fit(X_train, y_train)
    
    y_pred = pipeline.predict(X_test)
    
    metrics = {}
    if task_type == "regression":
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))
        metrics = {
            "r2_score": round(max(r2, 0.0), 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "accuracy": f"{round(max(r2, 0.0) * 100, 2)}%"
        }
    else:
        acc = float(accuracy_score(y_test, y_pred))
        metrics = {
            "accuracy": f"{round(acc * 100, 2)}%",
            "accuracy_raw": round(acc, 4),
            "precision": round(float(precision_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            "recall": round(float(recall_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
        }

    # Store trained model session
    model_id = f"model_{target_column}_{model_name_clean}"
    TRAINED_MODELS_STORE[model_id] = {
        "pipeline": pipeline,
        "task_type": task_type,
        "target_column": target_column,
        "model_title": selected_model_title,
        "num_features": num_features,
        "cat_features": cat_features,
        "feature_sample": {col: str(X[col].iloc[0]) for col in X.columns}
    }
    
    return {
        "model_id": model_id,
        "status": "trained",
        "task_type": task_type,
        "target_column": target_column,
        "model_name": selected_model_title,
        "test_size": test_size,
        "training_samples": len(X_train),
        "testing_samples": len(X_test),
        "metrics": metrics,
        "features": list(X.columns),
        "num_features": num_features,
        "cat_features": cat_features
    }

def predict_sample(model_id: str, input_features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates prediction using stored trained ML pipeline.
    """
    if model_id not in TRAINED_MODELS_STORE:
        raise ValueError(f"Model ID '{model_id}' not found. Please train a model first.")
        
    model_data = TRAINED_MODELS_STORE[model_id]
    pipeline = model_data["pipeline"]
    
    input_df = pd.DataFrame([input_features])
    pred = pipeline.predict(input_df)[0]
    
    prediction_val = round(float(pred), 2) if isinstance(pred, (int, float, np.number)) else str(pred)
    
    return {
        "status": "success",
        "model_id": model_id,
        "model_title": model_data["model_title"],
        "target_column": model_data["target_column"],
        "prediction": prediction_val,
        "input_features": input_features
    }
