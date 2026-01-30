"""
Train regression and classification models for academic performance prediction
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


class AcademicModelTrainer:
    def __init__(self):
        self.regressor = Pipeline([
            ("scaler", StandardScaler()),
            ("model", LinearRegression())
        ])

        self.classifier = Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression())
        ])

    def train(self, X: pd.DataFrame, y_next_mark: pd.Series, y_risk: pd.Series):
        self.regressor.fit(X, y_next_mark)
        self.classifier.fit(X, y_risk)

    def save(self, path="models/"):
        joblib.dump(self.regressor, f"{path}regressor.pkl")
        joblib.dump(self.classifier, f"{path}classifier.pkl")


import pandas as pd

def build_training_set(feature_rows: list):
    """
    feature_rows: list of dicts with keys:
    - features (DataFrame row)
    - next_mark (float)
    """

    X = pd.concat([row["features"] for row in feature_rows])
    y_next = pd.Series([row["next_mark"] for row in feature_rows])

    # Risk label: next mark < 50
    y_risk = (y_next < 50).astype(int)

    return X, y_next, y_risk

import os
import joblib

class AcademicPredictor:
    def __init__(self, model_path="models/"):
        self.regressor = joblib.load(os.path.join(model_path, "regressor.pkl"))
        self.classifier = joblib.load(os.path.join(model_path, "classifier.pkl"))

    def predict(self, features_df):
        next_mark = self.regressor.predict(features_df)[0]
        risk_prob = self.classifier.predict_proba(features_df)[0][1]

        return {
            "next_mark": next_mark,
            "risk_prob": risk_prob
        }
