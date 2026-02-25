import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import numpy as np
import joblib
import os

def train_model(procurement):

    # Remove rows where emissions are missing
    known = procurement.dropna()

    X = known[["spend_usd"]]
    y = known["emissions_kg"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict on test data
    y_pred = model.predict(X_test)

    # Evaluate model
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    print("\nModel Performance:")
    print("R2 Score:", round(r2, 4))
    print("MAE:", round(mae, 2))
    print("RMSE:", round(rmse, 2))

    # Save model
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/scope3_model.pkl")

    return model