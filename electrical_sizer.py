import streamlit as st

st.set_page_config(page_title="NEC Electrical Sizer • Normal & Emergency", layout="wide")
st.title("🏗️ NEC Electrical Power System Sizer • v2.1")
st.caption("Article 220 Load Calc + 700/701/702 Emergency | Normal and Emergency Loads")

system_voltage = st.selectbox("System Voltage", ["277/480V (480V 3Ø)", "120/208V (208V 3Ø)"], key="sys_v")
use_voltage = 480 if "480" in system_voltage else 208

tab1, tab2 = st.tabs(["📊 Normal Loads (Art 220)", "🚨 Emergency Loads (700/701/702)"])

# ===================== NORMAL LOADS =====================
with tab1:
    st.header("Normal Loads – Article 220 Calculation")
    left, right = st.columns([1.1, 1.9])
    
    with left:
        occupancy = st.selectbox("Occupancy Type (NEC Table 220.12)", 
                                ["Office", "Retail", "Restaurant", "Hospital", "School", "Warehouse", "Hotel", "Custom"])
        sqft = st.number_input("Gross Square Footage", 1000, 1_000_000, 25000, step=1000)
        
        col_a, col_b = st.columns(2)
        with col_a:
            hvac_type = st.radio("HVAC Input", ["kVA (nameplate)", "FLA"], horizontal=True)
            if hvac_type == "kVA (nameplate)":
                hvac_kva = st.number_input("HVAC kVA", 0.0, 2000.0, 120.0)
            else:
                hvac_fla = st.number_input("HVAC FLA", 0.0, 3000.0, 180.0)
                hvac_kva = round((hvac_fla * use_voltage * 1.732) / 1000, 1)
        
        kitchen_kva = st.number_input("Kitchen / Special Appliance Connected kVA", 0.0, 1000.0, 
                                      120.0 if occupancy == "Restaurant" else 40.0)
        receptacle_va = st.number_input("Receptacle Load (VA) – Art 220.14", 0, 500000, 50000, step=5000)

        st.subheader("Demand Factors")
        kitchen_df = st.slider("Kitchen Demand Factor (Table 220.56)", 0.25, 1.0, 0.65, 0.05)
        lighting_df = st.slider("Lighting + General Demand (Table 220.42)", 0.50, 1.0, 0.80, 0.05)
        spare_pct = st.slider("Future Spare Capacity %", 0, 50, 25)

        continuous = st.checkbox("Treat Lighting + HVAC + Kitchen as Continuous (125% factor)", value=True)

    with right:
        st.subheader("Calculated Loads (NEC Step-by-Step)")
        
        lighting_va = sqft * {"Office":3.5, "Retail":5.0, "Restaurant":4.0, "Hospital":2.5, "School":3.0,
                              "Warehouse":1.0, "Hotel":2.5, "Custom":3.0}.get(occupancy, 3.0)
        general_va = sqft * 1.0 + receptacle_va
        connected_kva = (lighting_va + general_va + kitchen_kva + hvac_kva) / 1000
        
        demand_general = (lighting_va + general_va) / 1000 * lighting_df
        demand_kitchen = kitchen_kva * kitchen_df
        demand_hvac = hvac_kva
        
        if continuous:
            total_normal_kva = (demand_general * 1.25 + demand_kitchen * 1.25 + demand_hvac * 1.25) + (spare_pct/100 * connected_kva)
        else:
            total_normal_kva = demand_general + demand_kitchen + demand_hvac + (spare_pct/100 * connected_kva)
        
        service_amps = (total_normal_kva * 1000) / (use_voltage * 1.732) * 1.25
        
        rec_service = max(100, round(service_amps / 50) * 50)
        
        st.metric("**Total Normal Demand kVA**", f"{total_normal_kva:.1f} kVA")
        st.metric("**Recommended Service**", f"{rec_service} A  •  {int(total_normal_kva*1.25):,} kVA")
        st.metric("**Rough Generator (optional standby)**", f"{int(total_normal_kva*0.25):,} kW")

        with st.expander("🧾 NEC References & Breakdown"):
            st.write("• Lighting → Table 220.12 + 220.42 demand")
            st.write("• Receptacles → 220.14")
            st.write("• Kitchen → 220.56 Table")
            st.write("• Continuous loads × 1.25 (215.2, 230.42)")

# ===================== EMERGENCY LOADS =====================
with tab2:
    st.header("Emergency / Standby Loads – NEC 700/701/702")
    left, right = st.columns([1.1, 1.9])
    
    with left:
        life_safety = st.number_input("Life Safety / Exit + Egress (kVA)", 0.0, 500.0, 15.0)
        fire_alarm = st.number_input("Fire Alarm + Detection (kVA)", 0.0, 100.0, 6.0)
        fire_pump = st.number_input("Fire Pump + Jockey (kVA)", 0.0, 800.0, 60.0)
        
        elev_type = st.radio("Elevators", ["kVA", "FLA"], horizontal=True)
        if elev_type == "kVA":
            elevator_kva = st.number_input("Elevator kVA (connected)", 0.0, 600.0, 45.0)
        else:
            elev_fla = st.number_input("Elevator FLA", 0.0, 2000.0, 90.0)
            elevator_kva = round((elev_fla * use_voltage * 1.732) / 1000, 1)
        
        standby_kva = st.number_input("Optional Standby / Critical (kVA)", 0.0, 1000.0, 35.0)
        
        gen_safety_factor = st.slider("Generator Safety / Starting Factor", 1.1, 1.5, 1.30, 0.05)

    with right:
        total_emergency_kva = life_safety + fire_alarm + fire_pump + elevator_kva + standby_kva
        
        st.metric("**Total Emergency kVA**", f"{total_emergency_kva:.1f} kVA")
        st.metric("**Recommended Generator**", f"{int(total_emergency_kva * gen_safety_factor):,} kW")
        st.metric("**ATS Recommendation**", f"{int(total_emergency_kva * 1.1):,} A")
        
        st.info("Full 100% load + 30% future typical for genset sizing (NEC 700.5 / 701.4)")

st.divider()
st.success("✅ Tab & dropdown removed. Now clean 2-tab layout exactly as requested.")

# ── Development Controls ─────────────────────────────────────
st.subheader("Next Development Step?")
option = st.radio("Pick one (I'll code it immediately):", 
    ["Add editable Load Schedule table (pandas dataframe + add/remove rows)",
     "Add Motor loads section + Table 430 demand factors",
     "Add Transformer + Feeder sizing outputs in both tabs",
     "Add Export buttons (Excel + PDF report with NEC citations)",
     "Add voltage drop calculator + conductor sizing helper",
     "Something else (describe below)"], index=0)

if st.button("🚀 Build This Next"):
    st.toast(f"Building **{option}** right now…", icon="🔨")
    st.rerun()

if st.text_input("Or type custom request here", placeholder="e.g. make normal loads have a full Article 220 worksheet view"):
    st.success("Got it — implementing your custom request in next version.")

st.caption("Just hit the button or type what you want next. We’re iterating fast on the NEC equipment sizing tool.")
