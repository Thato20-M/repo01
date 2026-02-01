import joblib
import os

class AcademicPredictor:
    def __init__(self, model_path="models"):
        self.regressor = joblib.load(os.path.join(model_path, "regressor.pkl"))
        self.classifier = joblib.load(os.path.join(model_path, "classifier.pkl"))

    def predict(self, features_df):
        return {
            "next_mark": float(self.regressor.predict(features_df)[0]),
            "risk_prob": float(self.classifier.predict_proba(features_df)[0][1])
        }

