from data_loader import load_data
from lca_engine import calculate_lca_emissions
from ml_model import train_model, predict_missing
from uncertainty import uncertainty_range

def main():
    procurement, logistics, factors = load_data()

    # LCA emissions
    logistics_emissions = calculate_lca_emissions(logistics, factors)

    # ML estimation
    model = train_model(procurement)
    procurement = predict_missing(procurement, model)

    total_procurement_emissions = procurement["emissions_kg"].sum()
    total_scope3 = logistics_emissions + total_procurement_emissions

    low, high = uncertainty_range([total_scope3])

    print("====== Scope 3 Emissions Report ======")
    print(f"Estimated Emissions: {total_scope3:.2f} kg CO2e")
    print(f"Uncertainty Range: {low:.2f} – {high:.2f} kg CO2e")

    procurement.to_csv("data/final_scope3_results.csv", index=False)

if __name__ == "__main__":
    main()