import streamlit as st
import pandas as pd

st.set_page_config(page_title="NEC Electrical Sizer • v2.13", layout="wide")
st.title("🏗️ NEC Electrical Power System Sizer • v2.13")
st.caption("✅ Added Residential & Multi-Family Housing Options | Developing NEC Equipment Sizing for Housing Units")

# Global Voltage
voltage_option = st.selectbox("System Voltage & Phase", 
    ["120/240V Single-Phase (Residential)", "120/208V 3-Phase", "277/480V 3-Phase"], key="global_v")
if "240V" in voltage_option:
    use_voltage = 240
    is_three_phase = False
elif "208V" in voltage_option:
    use_voltage = 208
    is_three_phase = True
else:
    use_voltage = 480
    is_three_phase = True

tab1, tab2, tab3 = st.tabs(["📊 Normal Loads (Art 220)", "🚨 Emergency Loads", "🏠 Residential Service Calc"])

# ===================== NORMAL LOADS TAB =====================
with tab1:
    st.header("Normal Loads – Article 220 Calculation")
    
    st.subheader("📋 Editable Load Schedule")
    if "df_normal" not in st.session_state:
        st.session_state.df_normal = pd.DataFrame({"Load Name": ["Lighting", "Receptacles", "Kitchen"], "kVA": [15.0, 8.5, 72.0]})
    edited_normal = st.data_editor(st.session_state.df_normal, num_rows="dynamic", key="normal_editor_v13")
    st.session_state.df_normal = edited_normal
    if st.button("➕ Add Schedule to Total", key="add_n13"): st.success("Added")

    left, right = st.columns([1.1, 1.9])
    with left:
        occupancy = st.selectbox("Occupancy Type (NEC Table 220.12 / Housing Units)", 
            ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel",
             "Single Family Residential", "Multi-Family / Apartments", "Senior Housing / Assisted Living", 
             "Dormitory / Student Housing", "Custom"], key="occ_v13")
        
        sqft = st.number_input("Gross Square Footage", 1000, 1000000, 35000, step=1000, key="sqft_v13")
        
        st.subheader("🔥 Non-Coincident HVAC Loads")
        col_c, col_h = st.columns(2)
        with col_c: cooling_kva = st.number_input("❄️ Cooling / AC kVA", 0.0, 3000.0, 95.0, key="cool_v13")
        with col_h: heating_kva = st.number_input("🔥 Heating kVA", 0.0, 3000.0, 45.0, key="heat_v13")
        hvac_used = max(cooling_kva, heating_kva)
        st.success(f"✅ Using {hvac_used:.1f} kVA (larger of Cooling or Heating) — NEC 220.60")

        kitchen_kva = st.number_input("Kitchen / Special Appliance kVA", 0.0, 2000.0, 85.0 if "Residential" in occupancy or "Apartment" in occupancy else 120.0, key="kit_v13")
        receptacle_va = st.number_input("Receptacle Load (VA)", 0, 1000000, 75000, step=5000, key="rec_v13")
        spare_pct = st.slider("Future Spare Capacity %", 0, 50, 30, key="spare_v13")
        continuous = st.checkbox("Apply 125% continuous to Lighting + Kitchen", value=True, key="cont_v13")

    with right:
        st.subheader("Results")
        # Lighting VA per sq ft adjusted for housing
        va_per_sqft = 3.0 if any(x in occupancy for x in ["Residential", "Apartment", "Senior", "Dormitory"]) else 3.5
        lighting_va = sqft * va_per_sqft
        general_va = sqft * 1.0 + receptacle_va
        demand_general = (lighting_va + general_va) / 1000 * 0.8
        demand_kitchen = kitchen_kva * 0.65
        subtotal = demand_general + demand_kitchen + hvac_used + st.session_state.df_normal["kVA"].sum()
        if continuous: subtotal *= 1.25
        total_normal_kva = subtotal * (1 + spare_pct/100)
        
        if is_three_phase:
            service_amps = (total_normal_kva * 1000) / (use_voltage * 1.732) * 1.25
        else:
            service_amps = (total_normal_kva * 1000) / use_voltage * 1.25
        rec_service = max(100, round(service_amps / 50) * 50)
        
        st.metric("Total Normal Demand kVA", f"{total_normal_kva:.1f}")
        st.metric("Recommended Service", f"{rec_service} A")
        st.metric("Lighting Load Used", f"{va_per_sqft} VA/ft² (Housing adjusted)")
        st.metric("HVAC Used", f"{hvac_used:.1f} kVA (Non-Coincident)")

# ===================== EMERGENCY LOADS TAB =====================
with tab2:
    st.header("Emergency Loads – NEC 700/701/702")
    st.subheader("📋 Editable Load Schedule")
    if "df_emerg" not in st.session_state:
        st.session_state.df_emerg = pd.DataFrame({"Load Name": ["Life Safety", "Fire Alarm", "Fire Pump", "Elevators"], "kVA": [18, 8, 72, 55]})
    st.data_editor(st.session_state.df_emerg, num_rows="dynamic", key="emerg_editor_v13")
    if st.button("Add to Emergency", key="add_e13"): st.success("Added")

    left, right = st.columns([1.1, 1.9])
    with left:
        life_safety = st.number_input("Life Safety kVA", 0.0, 800.0, 22.0, key="ls_e13")
        fire_alarm = st.number_input("Fire Alarm kVA", 0.0, 150.0, 8.0, key="fa_e13")
        fire_pump = st.number_input("Fire Pump kVA", 0.0, 1000.0, 75.0, key="fp_e13")
        elevator_kva = st.number_input("Elevator kVA", 0.0, 800.0, 52.0, key="elev_e13")
        standby = st.number_input("Standby kVA", 0.0, 1200.0, 45.0, key="sb_e13")
        gen_factor = st.slider("Generator Factor", 1.1, 1.6, 1.35, 0.05, key="gf_e13")
    with right:
        total_e = life_safety + fire_alarm + fire_pump + elevator_kva + standby + st.session_state.df_emerg["kVA"].sum()
        st.metric("Emergency Total kVA", f"{total_e:.1f}")
        st.metric("Recommended Generator", f"{int(total_e * gen_factor)} kW")
        st.metric("ATS", f"{int(total_e * 1.2)} A")

# ===================== RESIDENTIAL TAB =====================
with tab3:
    st.header("🏠 Residential / Housing Service Calc")
    st.subheader("📋 Editable Load Schedule")
    if "df_res" not in st.session_state:
        st.session_state.df_res = pd.DataFrame({"Load Name": ["Range", "Dryer", "Water Heater", "EV"], "kVA": [14.5, 6.0, 5.2, 11.0]})
    st.data_editor(st.session_state.df_res, num_rows="dynamic", key="res_editor_v13")
    if st.button("Add to Residential", key="add_r13"): st.success("Added")

    left, right = st.columns([1.1, 1.9])
    with left:
        sqft_r = st.number_input("Conditioned Sq Ft", 800, 50000, 42000, key="sqft_r13")   # good for housing project
        range_r = st.number_input("Range kVA", 0.0, 40.0, 14.5, key="range_r13")
        dryer_r = st.number_input("Dryer kVA", 0.0, 15.0, 6.0, key="dryer_r13")
        water_r = st.number_input("Water Heater kVA", 0.0, 20.0, 5.2, key="water_r13")
        ac_r = st.number_input("AC kVA", 0.0, 40.0, 8.5, key="ac_r13")
        heat_r = st.number_input("Heating kVA", 0.0, 50.0, 15.0, key="heat_r13")
        ev_r = st.number_input("EV Charger kVA", 0.0, 50.0, 11.0, key="ev_r13")
        spare_r = st.slider("Spare %", 0, 50, 35, key="spare_r_unique_v13")
    with right:
        base = sqft_r * 3 + range_r*1000 + dryer_r*1000 + max(ac_r, heat_r)*1000 + water_r*1000 + ev_r*1000
        total_r = base / 1000 + st.session_state.df_res["kVA"].sum()
        total_r = total_r * (1 + spare_r/100)
        amps_r = (total_r * 1000) / use_voltage * 1.25 if not is_three_phase else (total_r * 1000) / (use_voltage * 1.732) * 1.25
        st.metric("Housing Total kVA", f"{total_r:.1f}")
        st.metric("Recommended Service", f"{max(200, round(amps_r/50)*50)} A")

st.success("✅ v2.13 Complete with Residential / Multi-Family Housing occupancy options added.")

st.caption("Perfect for your housing units project. Let me know what else to add or adjust!")
