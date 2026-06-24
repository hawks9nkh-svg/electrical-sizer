import streamlit as st
import pandas as pd

st.set_page_config(page_title="MEP Electrical Sizer", layout="wide")
st.title("🏗️ Electrical Power System Sizer (NEC-Inspired)")

tab1, tab2 = st.tabs(["Normal Loads", "Emergency Loads"])

with tab1:
    st.header("Normal Loads")
    col1, col2 = st.columns(2)
    with col1:
        occupancy = st.selectbox("Occupancy Type", ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel"])
        sqft = st.number_input("Gross Square Footage", 1000, 500000, 25000)
        hvac_input_type = st.radio("HVAC Input Type", ["kVA", "FLA"])
        if hvac_input_type == "kVA":
            hvac_kva = st.number_input("HVAC Load (kVA nameplate)", 0.0, 500.0, 0.0)
        else:
            hvac_fla = st.number_input("HVAC FLA (Full Load Amps)", 0.0, 1000.0, 0.0)
            voltage = st.selectbox("System Voltage", [480, 208])
            hvac_kva = (hvac_fla * voltage * 1.732) / 1000 if voltage == 480 else (hvac_fla * voltage * 1.732) / 1000 * 0.577  # rough
        kitchen_kva = st.number_input("Kitchen / Special Appliance Load (kVA nameplate)", 0.0, 500.0, 80.0 if occupancy == "Restaurant" else 0.0)
    with col2:
        st.header("Demand Factors")
        kitchen_demand_factor = st.number_input("Kitchen Demand Factor", 0.5, 1.0, 0.75, step=0.05)
        hvac_demand_factor = st.number_input("HVAC Demand Factor", 1.0, 1.5, 1.25, step=0.05)
        spare_pct = st.slider("Spare Capacity %", 0, 50, 25)

with tab2:
    st.header("Emergency Loads")
    life_safety_kva = st.number_input("Life Safety (kVA)", 0.0, 500.0, 10.0)
    elevator_fla = st.number_input("Elevators FLA (total)", 0.0, 1000.0, 0.0)
    standby_kva = st.number_input("Standby Loads (kVA)", 0.0, 500.0, 20.0)
    emergency_demand_factor = st.number_input("Emergency Demand Factor", 0.8, 1.0, 1.0, step=0.05)

# Normal calculations
lighting_va_per_sqft = {"Office": 3.5, "Retail": 5.0, "Restaurant": 4.0, "Hospital": 2.0, "School": 3.0, "Warehouse": 1.0, "Hotel": 2.5}
lighting_va = sqft * lighting_va_per_sqft.get(occupancy, 3.0)
general_va = sqft * 1.0
demand_general_kva = (lighting_va + general_va) * 0.8 / 1000
kitchen_demand_kva = kitchen_kva * kitchen_demand_factor
hvac_demand_kva = hvac_kva * hvac_demand_factor if 'hvac_kva' in locals() else 0
total_normal_k
