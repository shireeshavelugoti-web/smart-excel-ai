import os
import pandas as pd
import numpy as np
from backend.models.prediction_models import analyze_dataset_ml, train_ml_model, predict_sample

def test_ml_analysis_and_training(tmp_path):
    # Generate synthetic regression dataset
    np.random.seed(42)
    df = pd.DataFrame({
        "Area": np.random.randint(500, 4000, 100),
        "Bedrooms": np.random.randint(1, 5, 100),
        "Bathrooms": np.random.randint(1, 4, 100),
        "Age": np.random.randint(1, 30, 100),
        "Price": np.random.randint(50, 500, 100)
    })
    
    sample_file = os.path.join(tmp_path, "real_estate.csv")
    df.to_csv(sample_file, index=False)
    
    analysis = analyze_dataset_ml(df)
    
    assert analysis["rows"] == 100
    assert "Price" in analysis["numerical_features"]
    assert "columns" in analysis["correlation"]
    
    # Train Regression Model
    res = train_ml_model(df, target_column="Price", model_name="Random Forest")
    
    assert res["status"] == "trained"
    assert res["task_type"] == "regression"
    assert "r2_score" in res["metrics"]
    assert res["metrics"]["r2_score"] >= 0.0
    
    # Run Prediction
    model_id = res["model_id"]
    sample_input = {
        "Area": 2500,
        "Bedrooms": 3,
        "Bathrooms": 2,
        "Age": 10
    }
    pred = predict_sample(model_id, sample_input)
    assert pred["status"] == "success"
    assert isinstance(pred["prediction"], (int, float))
