# Lightweight fallback yield predictor (used if app.py model unavailable)
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

_data = {
    "rainfall":    [100, 200, 150, 300, 250, 400, 350],
    "temperature": [25,  30,  28,  35,  32,  20,  22],
    "soil_quality":[3,   4,   3,   5,   4,   6,   5],
    "yield":       [20,  30,  25,  40,  35,  50,  45],
}
_df = pd.DataFrame(_data)
_model = RandomForestRegressor(n_estimators=50, random_state=42)
_model.fit(_df[["rainfall", "temperature", "soil_quality"]], _df["yield"])


def predict_yield(rainfall, temperature, soil_quality, soil_type=None, crop_type=None):
    """Simple yield prediction from environmental inputs."""
    return _model.predict([[rainfall, temperature, soil_quality]])[0]
