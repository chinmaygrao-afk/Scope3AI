import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

def train_model(procurement):
    known = procurement.dropna()
    X = known[["spend_usd"]]
    y = known["emissions_kg"]

    model = LinearRegression()
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/scope3_model.pkl")
    return model

def predict_missing(procurement, model):
    missing = procurement[procurement["emissions_kg"].isna()]
    if missing.empty:
        return procurement

    predictions = model.predict(missing[["spend_usd"]])
    procurement.loc[procurement["emissions_kg"].isna(), "emissions_kg"] = predictions
    return procurement