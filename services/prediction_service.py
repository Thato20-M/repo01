# services/prediction_service.py

from ml.feature_engineering import build_features
from ml.predictor import AcademicPredictor


predictor = AcademicPredictor()


def predict_module_performance(df):
    if df.empty:
        return None

    features = build_features(df)
    return predictor.predict(features)
