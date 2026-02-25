import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(page_title="Carbon Intelligence Platform", layout="wide")

# Clean Dark Theme
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
}

h1, h2, h3 {
    color: #E6F2FF;
}

div[data-testid="metric-container"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Carbon Intelligence & Sustainability Platform")

# ---------------------------------------------------
# CORE FUNCTIONS
# ---------------------------------------------------

def calculate_lca(logistics, factors):
    emissions = []
    for _, row in logistics.iterrows():
        factor = factors[factors["activity"] == row["mode"]]["emission_factor"].values[0]
        emission = row["distance_km"] * row["weight_tons"] * factor
        emissions.append(emission)
    return sum(emissions)


def train_and_predict(procurement):
    known = procurement.dropna()
    X = known[["spend_usd"]]
    y = known["emissions_kg"]

    model = LinearRegression()
    model.fit(X, y)

    missing = procurement[procurement["emissions_kg"].isna()]

    if not missing.empty:
        predictions = model.predict(missing[["spend_usd"]])
        procurement.loc[procurement["emissions_kg"].isna(), "emissions_kg"] = predictions

    return procurement


def bootstrap_uncertainty(value):
    samples = []
    for _ in range(1000):
        noise = np.random.normal(0, value * 0.05)
        samples.append(value + noise)
    return np.percentile(samples, 5), np.percentile(samples, 95)


def calculate_carbon_score(total_emissions, max_reference):
    score = max(0, 100 - (total_emissions / max_reference) * 100)
    score = round(score, 1)

    if score >= 80:
        rating = "Excellent 🟢"
    elif score >= 60:
        rating = "Good 🟢"
    elif score >= 40:
        rating = "Moderate 🟡"
    elif score >= 20:
        rating = "High 🔴"
    else:
        rating = "Critical 🔴"

    return score, rating


def reduction_suggestions(score, entity_type="Personal"):
    if score >= 80:
        return ["Maintain current sustainable practices.",
                "Consider investing in renewable energy.",
                "Support climate-positive initiatives."]
    elif score >= 60:
        return ["Reduce energy consumption.",
                "Shift to public transport or EV.",
                "Reduce meat consumption."]
    elif score >= 40:
        return ["Switch to renewable electricity.",
                "Optimize travel frequency.",
                "Improve energy efficiency."]
    else:
        if entity_type == "Company":
            return ["Conduct supplier ESG audit.",
                    "Optimize logistics routes.",
                    "Adopt science-based emission targets.",
                    "Invest in carbon capture or offsets."]
        else:
            return ["Significantly reduce flights.",
                    "Adopt plant-based diet.",
                    "Install rooftop solar.",
                    "Offset emissions through verified programs."]


# ---------------------------------------------------
# CREATE TABS
# ---------------------------------------------------

tab1, tab2 = st.tabs(["🏢 Company Scope 3", "👤 Personal Footprint"])


# ===================================================
# TAB 1 — COMPANY
# ===================================================

with tab1:

    st.header("🏢 Company Scope 3 Emissions Estimator")

    col1, col2, col3 = st.columns(3)

    with col1:
        procurement_file = st.file_uploader("Upload Procurement CSV", type=["csv"])

    with col2:
        logistics_file = st.file_uploader("Upload Logistics CSV", type=["csv"])

    with col3:
        factors_file = st.file_uploader("Upload Emission Factors CSV", type=["csv"])

    if procurement_file and logistics_file and factors_file:

        procurement = pd.read_csv(procurement_file)
        logistics = pd.read_csv(logistics_file)
        factors = pd.read_csv(factors_file)

        logistics_emissions = calculate_lca(logistics, factors)
        procurement = train_and_predict(procurement)
        procurement_emissions = procurement["emissions_kg"].sum()

        total_scope3 = logistics_emissions + procurement_emissions
        low, high = bootstrap_uncertainty(total_scope3)

        st.subheader("📊 Scope 3 Results")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Emissions (kg CO2e)", f"{total_scope3:,.2f}")
        c2.metric("Lower Bound", f"{low:,.2f}")
        c3.metric("Upper Bound", f"{high:,.2f}")

        # Company Score
        score, rating = calculate_carbon_score(total_scope3, max_reference=100000)

        st.markdown("### 🎯 Company Carbon Score")
        s1, s2 = st.columns(2)
        s1.metric("Score (0-100)", score)
        s2.metric("Rating", rating)

        # Reduction Suggestions
        st.markdown("### 📉 Recommended Actions")
        suggestions = reduction_suggestions(score, entity_type="Company")
        for suggestion in suggestions:
            st.write(f"- {suggestion}")

    else:
        st.info("Upload all required CSV files to calculate company emissions.")


# ===================================================
# TAB 2 — PERSONAL
# ===================================================

with tab2:

    st.header("👤 Personal Carbon Footprint Calculator")

    col1, col2 = st.columns(2)

    with col1:
        electricity = st.number_input("Monthly Electricity (kWh)", 0.0, 2000.0, 150.0)
        lpg = st.number_input("Monthly LPG (kg)", 0.0, 50.0, 10.0)
        car_km = st.number_input("Car Travel per Month (km)", 0.0, 5000.0, 300.0)

    with col2:
        flights = st.number_input("Flights per Year", 0, 50, 2)
        diet = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])

    if st.button("Calculate Personal Footprint"):

        EF_ELECTRICITY = 0.82
        EF_LPG = 3.0
        EF_CAR = 0.192
        EF_FLIGHT = 150

        DIET_FACTORS = {
            "Vegetarian": 1.5,
            "Non-Vegetarian": 2.5,
            "Vegan": 1.2
        }

        electricity_emissions = electricity * 12 * EF_ELECTRICITY
        lpg_emissions = lpg * 12 * EF_LPG
        car_emissions = car_km * 12 * EF_CAR
        flight_emissions = flights * EF_FLIGHT
        diet_emissions = DIET_FACTORS[diet] * 1000

        total_personal = (
            electricity_emissions +
            lpg_emissions +
            car_emissions +
            flight_emissions +
            diet_emissions
        )

        lower = total_personal * 0.9
        upper = total_personal * 1.1

        p1, p2, p3 = st.columns(3)
        p1.metric("Total Emissions (kg CO2e)", f"{total_personal:,.2f}")
        p2.metric("Lower Estimate", f"{lower:,.2f}")
        p3.metric("Upper Estimate", f"{upper:,.2f}")

        # Carbon Score
        score, rating = calculate_carbon_score(total_personal, max_reference=15000)

        st.markdown("### 🎯 Your Carbon Score")
        s1, s2 = st.columns(2)
        s1.metric("Score (0-100)", score)
        s2.metric("Rating", rating)

        # Tree Offset
        TREE_ABSORPTION = 21
        trees_needed = int(np.ceil(total_personal / TREE_ABSORPTION))
        st.success(f"🌳 You need approximately {trees_needed:,} trees per year to offset your emissions.")

        # Reduction Suggestions
        st.markdown("### 📉 How You Can Improve")
        suggestions = reduction_suggestions(score, entity_type="Personal")
        for suggestion in suggestions:
            st.write(f"- {suggestion}")

        # Breakdown Chart
        breakdown = {
            "Electricity": electricity_emissions,
            "LPG": lpg_emissions,
            "Car Travel": car_emissions,
            "Flights": flight_emissions,
            "Diet": diet_emissions
        }

        breakdown_df = pd.DataFrame(
            breakdown.items(),
            columns=["Category", "Emissions (kg CO2e)"]
        )

        fig = px.bar(
            breakdown_df,
            x="Category",
            y="Emissions (kg CO2e)",
            color="Category",
            text_auto=True,
            title="Personal Emissions Breakdown"
        )

        fig.update_layout(template="plotly_dark", title_x=0.5, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)