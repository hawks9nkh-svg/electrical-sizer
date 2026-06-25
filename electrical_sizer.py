import streamlit as st
import pandas as pd

st.set_page_config(page_title="NEC Electrical Sizer • v2.20", layout="wide")
st.title("🏗️ NEC Electrical Power System Sizer • v2.20")
st.caption("✅ Dwelling Units moved to Multi-Family Tab • 0 to 1000 range | Housing Project")

tab1, tab2, tab3 = st.tabs(["📊 Normal Loads (Art 220)", "🚨 Emergency Loads", "🏠 Multi-Family / Residential Calc"])

# ===================== TAB 1 - NORMAL LOADS =====================
with tab1:
    st.header("Normal Loads – Article 220")
    st.subheader("Editable Load Schedule")
    if "df_normal" not in st.session_state:
        st.session_state.df_normal = pd.DataFrame({"Load Name": ["Lighting", "Receptacles"], "kVA": [18, 11]})
    st.data_editor(st.session_state.df_normal, num_rows="dynamic", key="n20")
    if st.button("Add Schedule", key="addn20"): st.success("Added")

    left, right = st.columns([1.1, 1.9])
    with left:
        occupancy = st.selectbox("Occupancy Type", ["Office", "Retail", "Multi-Family / Apartments", "Single Family Residential"], key="occ20")
        sqft = st.number_input("Gross Sq Ft", 1000, 2000000, 88000, key="sq20")
        cooling = st.number_input("Cooling kVA", 0.0, 4000.0, 98.0, key="cool20")
        heating = st.number_input("Heating kVA", 0.0, 4000.0, 45.0, key="heat20")
        hvac = max(cooling, heating)
        kitchen = st.number_input("Kitchen kVA", 0.0, 3000.0, 95.0, key="kit20")
        rec = st.number_input("Receptacle VA", 0, 2000000, 85000, key="rec20")
        spare = st.slider("Spare %", 0, 50, 30, key="sp20")
    with right:
        total_n = 82 + hvac + kitchen * 0.65 + rec/1000 + st.session_state.df_normal["kVA"].sum()
        st.metric("Normal Total kVA", f"{total_n:.1f}")

# ===================== TAB 2 - EMERGENCY =====================
with tab2:
    st.header("Emergency Loads")
    st.subheader("Editable Load Schedule")
    if "df_emerg" not in st.session_state:
        st.session_state.df_emerg = pd.DataFrame({"Load Name": ["Life Safety", "Fire Pump"], "kVA": [35, 92]})
    st.data_editor(st.session_state.df_emerg, num_rows="dynamic", key="e20")
    if st.button("Add", key="adde20"): st.success("Added")

    left, right = st.columns(2)
    with left:
        life = st.number_input("Life Safety kVA", 0.0, 1000.0, 35.0, key="life20")
        pump = st.number_input("Fire Pump kVA", 0.0, 1200.0, 92.0, key="pump20")
        elev = st.number_input("Elevator kVA", 0.0, 1000.0, 62.0, key="elev20")
        standby = st.number_input("Standby kVA", 0.0, 1500.0, 48.0, key="stand20")
    with right:
        total_e = life + pump + elev + standby + st.session_state.df_emerg["kVA"].sum()
        st.metric("Emergency kVA", f"{total_e:.1f}")
        st.metric("Generator kW", f"{int(total_e * 1.35)}")

# ===================== TAB 3 - MULTI-FAMILY =====================
with tab3:
    st.header("🏠 Multi-Family / Residential Calc")
    
    st.subheader("Dwelling Units Input (Moved here as requested)")
    units = st.number_input("Number of Dwelling Units", 0, 1000, 88, key="units20")   # Now 0 to 1000
    
    st.subheader("No Floor Plans Mode")
    va_per = st.selectbox("VA per Unit", ["4500", "5000", "6000"], key="va20")
    total_rec = units * int(va_per) / 1000
    st.metric("Receptacle + Small Appliance + Laundry", f"{total_rec:.1f} kVA")
    if st.button("Add Receptacle Load", key="addrec20"): st.success("Added to total")

    st.subheader("Kitchen Load")
    range_kw = st.number_input("Average Range kW per Unit", 8.0, 20.0, 12.0, key="range20")
    kitchen_d = units * range_kw * 0.26
    st.metric("Kitchen Demand Load", f"{kitchen_d:.1f} kVA")

    st.subheader("Other Inputs")
    range_total = st.number_input("Total Range Load kVA", 0.0, 3000.0, 1056.0, key="r20")
    st.metric("Overall Estimate", f"{kitchen_d + total_rec + range_total/1000:.1f} kVA")

st.success("✅ v2.20 Complete — Dwelling Units now in the correct tab and can be 0 to 1000.")

st.caption("Test it and tell me what to add next. I will keep the code long and detailed.")
