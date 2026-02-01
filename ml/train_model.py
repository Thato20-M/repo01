"""
Train regression and classification models for academic performance prediction
"""

import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression

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

    def train(self, X, y_next_mark, y_risk):
        self.regressor.fit(X, y_next_mark)
        self.classifier.fit(X, y_risk)

    def save(self, path="models/"):
        joblib.dump(self.regressor, f"{path}/regressor.pkl")
        joblib.dump(self.classifier, f"{path}/classifier.pkl")
