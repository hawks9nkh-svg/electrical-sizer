import streamlit as st
import pandas as pd

st.set_page_config(page_title="MEP Electrical Sizer", layout="wide")
st.title("🏗️ Electrical Power System Sizer (NEC-Inspired)")

system_voltage = st.selectbox("System Voltage", ["277/480V (480V 3P)", "120/208V (208V 3P)"])
use_voltage = 480 if "480" in system_voltage else 208

tab1, tab2 = st.tabs(["Normal Loads", "Emergency Loads"])

with tab1:
    st.header("Normal Loads")
    left, right = st.columns([1, 2])
    with left:
        occupancy = st.selectbox("Occupancy Type", ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel"])
        sqft = st.number_input("Gross Square Footage", 1000, 500000, 25000)
        hvac_type = st.radio("HVAC Input Type", ["kVA", "FLA"])
        if hvac_type == "kVA":
            hvac_kva = st.number_input("HVAC Load (kVA nameplate)", 0.0, 500.0, 0.0)
        else:
            hvac_fla = st.number_input("HVAC FLA", 0.0, 1000.0, 0.0)
            hvac_kva = (hvac_fla * use_voltage * 1.732) / 1000
        kitchen_kva = st.number_input("Kitchen / Special Appliance Load (kVA nameplate)", 0.0, 500.0, 80.0 if occupancy == "Restaurant" else 0.0)

        st.subheader("Demand Factors")
        kitchen_demand_factor = st.number_input("Kitchen Demand Factor", 0.5, 1.0, 0.75, step=0.05)
        hvac_demand_factor = st.number_input("HVAC Demand Factor", 1.0, 1.5, 1.25, step=0.05)
        spare_pct = st.slider("Spare Capacity %", 0, 50, 25)

    with right:
        st.header("Results")
        lighting_va_per_sqft = {"Office": 3.5, "Retail": 5.0, "Restaurant": 4.0, "Hospital": 2.0, "School": 3.0, "Warehouse": 1.0, "Hotel": 2.5}
        lighting_va = sqft * lighting_va_per_sqft.get(occupancy, 3.0)
        general_va = sqft * 1.0
        demand_general_kva = (lighting_va + general_va) * 0.8 / 1000

        kitchen_demand_kva = kitchen_kva * kitchen_demand_factor
        hvac_demand_kva = hvac_kva * hvac_demand_factor if 'hvac_kva' in locals() else 0
        total_normal_kva = demand_general_kva + kitchen_demand_kva + hvac_demand_kva

        service_amps = (total_normal_kva * 1000 / (use_voltage * 1.732)) * 1.25 * (1 + spare_pct/100)
        recommended_service = max(100, round(service_amps / 50) * 50)

        st.metric("Normal Total Demand kVA", f"{total_normal_kva:.1f}")
        st.metric(f"Recommended Service ({use_voltage}V example)", f"{recommended_service} A")
        st.metric("Emergency Generator (rough)", f"{int(total_normal_kva * 0.2 * 1.3):.0f} kW")

with tab2:
    st.header("Emergency Loads")
    left, right = st.columns([1, 2])
    with left:
        life_safety_kva = st.number_input("Life Safety (kVA)", 0.0, 500.0, 10.0)
        fire_alarm_kva = st.number_input("Fire Alarm (kVA)", 0.0, 100.0, 5.0)
        fire_pump_kva = st.number_input("Fire Pump (kVA)", 0.0, 500.0, 50.0)
        elev_type = st.radio("Elevators Input Type", ["kVA", "FLA"])
        if elev_type == "kVA":
            elevator_kva = st.number_input("Elevators (kVA)", 0.0, 500.0, 0.0)
        else:
            elevator_fla = st.number_input("Elevators FLA", 0.0, 1000.0, 0.0)
            elevator_kva = (elevator_fla * use_voltage * 1.732) / 1000
        standby_kva = st.number_input("Standby Loads (kVA)", 0.0, 500.0, 20.0)
    with right:
        total_emergency_kva = life_safety_kva + fire_alarm_kva + fire_pump_kva + elevator_kva + standby_kva
        st.metric("Emergency Total kVA", f"{total_emergency_kva:.1f}")
        st.metric("Recommended Emergency Generator", f"{int(total_emergency_kva * 1.3):.0f} kW")

st.info("System voltage selected at top. All inputs on left, results on right per tab.")

if st.button("Show Breakdown"):
    st.dataframe(pd.DataFrame({
        "Component": ["Normal General", "Kitchen", "HVAC", "Life Safety", "Fire Alarm", "Fire Pump", "Elevators", "Standby"],
        "kVA": [demand_general_kva, kitchen_demand_kva, hvac_demand_kva, life_safety_kva, fire_alarm_kva, fire_pump_kva, elevator_kva, standby_kva]
    }))
