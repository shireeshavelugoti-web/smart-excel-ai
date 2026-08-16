import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import IsolationForest

def detect_outliers_isolation_forest(df: pd.DataFrame, contamination: float = 0.05) -> List[Dict[str, Any]]:
    """
    Uses Scikit-Learn IsolationForest to detect numerical multivariate outliers.
    Returns list of outlier dictionaries with row index, feature values, and anomaly scores.
    """
    num_df = df.select_dtypes(include=[np.number]).dropna()
    if num_df.empty or len(num_df) < 5:
        return []
    
    model = IsolationForest(contamination=contamination, random_state=42)
    num_df_copy = num_df.copy()
    preds = model.fit_predict(num_df_copy)
    scores = model.decision_function(num_df_copy)
    
    outliers = []
    for idx, (pred, score) in enumerate(zip(preds, scores)):
        if pred == -1:
            row_idx = int(num_df_copy.index[idx])
            outliers.append({
                "row_index": row_idx + 1, # 1-based index for UI
                "dataframe_index": row_idx,
                "anomaly_score": round(float(score), 4),
                "features": df.loc[row_idx, num_df.columns].to_dict()
            })
            
    return outliers
