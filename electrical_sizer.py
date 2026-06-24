import streamlit as st
import pandas as pd

st.set_page_config(page_title="MEP Electrical Sizer", layout="wide")
st.title("🏗️ Electrical Power System Sizer (NEC-Inspired)")

st.sidebar.header("Building Inputs")
occupancy = st.sidebar.selectbox("Occupancy Type", ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel"])
sqft = st.sidebar.number_input("Gross Square Footage", 1000, 500000, 25000)
hvac_kva = st.sidebar.number_input("HVAC Load (kVA) - optional", 0.0, 500.0, 0.0)
kitchen_kva = st.sidebar.number_input("Kitchen / Special Appliance Load (kVA)", 0.0, 500.0, 80.0 if occupancy == "Restaurant" else 0.0)
spare_pct = st.sidebar.slider("Spare Capacity %", 0, 50, 25)

# Calculations
lighting_va_per_sqft = {"Office": 3.5, "Retail": 5.0, "Restaurant": 4.0, "Hospital": 2.0, "School": 3.0, "Warehouse": 1.0, "Hotel": 2.5}
lighting_va = sqft * lighting_va_per_sqft.get(occupancy, 3.0)
general_va = sqft * 1.0
demand_general_kva = (lighting_va + general_va) * 0.8 / 1000

kitchen_contrib = kitchen_kva * 0.75
hvac_contrib = hvac_kva * 1.25
total_kva = demand_general_kva + kitchen_contrib + hvac_contrib

st.header("Results")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Calculated kVA", f"{total_kva:.1f}")
    service_amps = (total_kva * 1000 / (480 * 1.732)) * 1.25 * (1 + spare_pct/100)
    st.metric("Recommended Service (480V example)", f"{int(service_amps/100)*100} A")
with col2:
    emerg_kva = total_kva * 0.2
    st.metric("Emergency Generator (rough)", f"{int(emerg_kva * 1.3):.0f} kW")

st.info("Restaurant kitchen load included. HVAC optional for concept phase. Always verify with full NEC calculations.")

if st.button("Show Load Breakdown"):
    st.dataframe(pd.DataFrame({
        "Component": ["Lighting+General (demand)", "Kitchen", "HVAC", "Total"],
        "kVA": [demand_general_kva, kitchen_contrib, hvac_contrib, total_kva]
    }))