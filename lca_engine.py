def calculate_lca_emissions(logistics, factors):
    emissions = []

    for _, row in logistics.iterrows():
        factor = factors[factors["activity"] == row["mode"]]["emission_factor"].values[0]
        emission = row["distance_km"] * row["weight_tons"] * factor
        emissions.append(emission)

    return sum(emissions)