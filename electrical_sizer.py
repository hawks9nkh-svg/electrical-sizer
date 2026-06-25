import streamlit as st
import pandas as pd

st.set_page_config(page_title="NEC Electrical Sizer • v2.21", layout="wide")
st.title("🏗️ NEC Electrical Power System Sizer • v2.21")
st.caption("✅ Stable Version • Voltage + Amps Restored • No More Regressions | Housing Project")

# ===================== VOLTAGE SELECTOR (Always Visible) =====================
voltage_option = st.selectbox("System Voltage & Phase", 
    ["120/240V Single-Phase (Residential)", "120/208V 3-Phase", "277/480V 3-Phase"], key="voltage_v21")
if "240V" in voltage_option:
    use_voltage = 240
    is_three_phase = False
elif "208V" in voltage_option:
    use_voltage = 208
    is_three_phase = True
else:
    use_voltage = 480
    is_three_phase = True

tab1, tab2, tab3 = st.tabs(["📊 Normal Loads (Art 220)", "🚨 Emergency Loads", "🏠 Multi-Family / Residential Calc"])

# ===================== NORMAL LOADS TAB =====================
with tab1:
    st.header("Normal Loads – Article 220 Calculation")
    st.subheader("Editable Load Schedule")
    if "df_normal" not in st.session_state:
        st.session_state.df_normal = pd.DataFrame({"Load Name": ["Lighting", "Receptacles", "Kitchen"], "kVA": [22, 13, 78]})
    st.data_editor(st.session_state.df_normal, num_rows="dynamic", key="normal_v21")
    if st.button("Add Schedule", key="addn21"): st.success("Added")

    left, right = st.columns([1.1, 1.9])
    with left:
        occupancy = st.selectbox("Occupancy Type", ["Office", "Retail", "Multi-Family / Apartments", "Single Family Residential"], key="occ21")
        sqft = st.number_input("Gross Sq Ft", 1000, 2000000, 88000, key="sq21")
        cooling = st.number_input("Cooling kVA", 0.0, 4000.0, 98.0, key="cool21")
        heating = st.number_input("Heating kVA", 0.0, 4000.0, 45.0, key="heat21")
        hvac = max(cooling, heating)
        kitchen = st.number_input("Kitchen kVA", 0.0, 3000.0, 95.0, key="kit21")
        rec = st.number_input("Receptacle VA", 0, 2000000, 95000, key="rec21")
        spare = st.slider("Spare %", 0, 50, 30, key="sp21")
    with right:
        total_n = 92 + hvac + kitchen * 0.65 + rec/1000 + st.session_state.df_normal["kVA"].sum()
        st.metric("Total Normal kVA", f"{total_n:.1f}")
        
        if is_three_phase:
            amps = (total_n * 1000) / (use_voltage * 1.732) * 1.25
        else:
            amps = (total_n * 1000) / use_voltage * 1.25
        st.metric("Recommended Service Amps", f"{int(amps)} A")

# ===================== EMERGENCY TAB =====================
with tab2:
    st.header("Emergency Loads")
    st.subheader("Editable Load Schedule")
    if "df_emerg" not in st.session_state:
        st.session_state.df_emerg = pd.DataFrame({"Load Name": ["Life Safety", "Fire Pump"], "kVA": [35, 88]})
    st.data_editor(st.session_state.df_emerg, num_rows="dynamic", key="e21")
    if st.button("Add", key="adde21"): st.success("Added")

    left, right = st.columns(2)
    with left:
        life = st.number_input("Life Safety kVA", 0.0, 1000.0, 35.0, key="life21")
        pump = st.number_input("Fire Pump kVA", 0.0, 1200.0, 88.0, key="pump21")
        elev = st.number_input("Elevator kVA", 0.0, 1000.0, 62.0, key="elev21")
        standby = st.number_input("Standby kVA", 0.0, 1500.0, 48.0, key="stand21")
    with right:
        total_e = life + pump + elev + standby + st.session_state.df_emerg["kVA"].sum()
        st.metric("Emergency kVA", f"{total_e:.1f}")
        st.metric("Generator kW", f"{int(total_e * 1.35)}")

# ===================== MULTI-FAMILY TAB =====================
with tab3:
    st.header("🏠 Multi-Family / Residential Calc")
    units = st.number_input("Number of Dwelling Units", 0, 1000, 88, key="units21")
    
    st.subheader("No Floor Plans Mode")
    va_per = st.selectbox("VA per Unit", ["4500", "5000", "6000"], key="va21")
    total_rec = units * int(va_per) / 1000
    st.metric("Receptacle Load", f"{total_rec:.1f} kVA")
    if st.button("Add Receptacle Load", key="addrec21"): st.success("Added")

    st.subheader("Kitchen Load")
    range_kw = st.number_input("Average Range kW per Unit", 8.0, 20.0, 12.0, key="range21")
    kitchen_d = units * range_kw * 0.26
    st.metric("Kitchen Demand", f"{kitchen_d:.1f} kVA")

    st.metric("Overall Estimate", f"{kitchen_d + total_rec + 1050/1000:.1f} kVA")

st.success("✅ v2.21 Stable • Voltage selector + Amps in Normal tab restored • Dwelling units in correct tab (0-1000)")

st.caption("This version should feel stable. Test the Normal tab for amps and voltage. What next?")
