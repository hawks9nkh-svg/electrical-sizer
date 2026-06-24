import streamlit as st
import pandas as pd

st.set_page_config(page_title="MEP Electrical Sizer", layout="wide")
st.title("🏗️ Electrical Power System Sizer (NEC-Inspired)")

st.sidebar.header("Building Inputs")
occupancy = st.sidebar.selectbox("Occupancy Type", ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel"])
sqft = st.sidebar.number_input("Gross Square Footage", 1000, 500000, 25000)
hvac_kva = st.sidebar.number_input("HVAC Load (kVA nameplate)", 0.0, 500.0, 0.0)
kitchen_kva = st.sidebar.number_input("Kitchen / Special Appliance Load (kVA nameplate)", 0.0, 500.0, 80.0 if occupancy == "Restaurant" else 0.0)

st.sidebar.header("Demand Factors (editable)")
kitchen_demand_factor = st.sidebar.number_input("Kitchen Demand Factor", 0.5, 1.0, 0.75, step=0.05)
hvac_demand_factor = st.sidebar.number_input("HVAC Demand Factor (continuous)", 1.0, 1.5, 1.25, step=0.05)
spare_pct = st.sidebar.slider("Spare Capacity %", 0, 50, 25)

# Calculations
lighting_va_per_sqft = {"Office": 3.5, "Retail": 5.0, "Restaurant": 4.0, "Hospital": 2.0, "School": 3.0, "Warehouse": 1.0, "Hotel": 2.5}
lighting_va = sqft * lighting_va_per_sqft.get(occupancy, 3.0)
general_va = sqft * 1.0
demand_general_kva = (lighting_va + general_va) * 0.8 / 1000

kitchen_demand_kva = kitchen_kva * kitchen_demand_factor
hvac_demand_kva = hvac_kva * hvac_demand_factor
total_demand_kva = demand_general_kva + kitchen_demand_kva + hvac_demand_kva

# Service amps rounded to nearest 50A, min 100A
service_amps = (total_demand_kva * 1000 / (480 * 1.732)) * 1.25 * (1 + spare_pct/100)
recommended_service = max(100, round(service_amps / 50) * 50)

st.header("Results")
col1, col2 = st.columns(2)
with col1:
    st.metric("General Lighting + Receptacles (demand)", f"{demand_general_kva:.1f} kVA")
    st.metric("Kitchen Demand kVA", f"{kitchen_demand_kva:.1f} kVA")
    st.metric("HVAC Demand kVA", f"{hvac_demand_kva:.1f} kVA")
    st.metric("**Total Demand kVA**", f"{total_demand_kva:.1f}")
with col2:
    st.metric("Recommended Service (480V example)", f"{recommended_service} A")
    emerg_kva = total_demand_kva * 0.2
    st.metric("Emergency Generator (rough)", f"{int(emerg_kva * 1.3):.0f} kW")

st.info("Demand factors are editable on the left. Restaurant kitchen load included. Always verify with full NEC calculations.")

if st.button("Show Load Breakdown"):
    st.dataframe(pd.DataFrame({
        "Component": ["General (demand)", "Kitchen Demand", "HVAC Demand", "Total Demand"],
        "kVA": [demand_general_kva, kitchen_demand_kva, hvac_demand_kva, total_demand_kva]
    }))
