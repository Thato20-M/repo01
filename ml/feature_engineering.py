import pandas as pd

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts assessment marks into ML features
    """
    features = {
        "avg_mark": df["Mark"].mean(),
        "last_mark": df["Mark"].iloc[-1],
        "trend": df["Mark"].iloc[-1] - df["Mark"].iloc[0],
        "num_assessments": len(df),
        "weight_sum": df["Weight"].sum()
    }

    return pd.DataFrame([features])
