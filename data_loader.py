import pandas as pd

def load_data():
    procurement = pd.read_csv("data/procurement.csv")
    logistics = pd.read_csv("data/logistics.csv")
    factors = pd.read_csv("data/emission_factors.csv")
    return procurement, logistics, factors