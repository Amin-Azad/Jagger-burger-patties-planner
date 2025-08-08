import math
import streamlit as st

st.set_page_config(page_title="Jagger Burger Patties Planner", page_icon="🍔", layout="centered")

# ---------- Sidebar: Branch settings (editable if HQ changes rules) ----------
st.sidebar.header("⚙️ Branch settings")
reg_pack_size = st.sidebar.number_input("Regular: patties per 2,000 revenue", value=6, min_value=1, step=1)
reg_pack_revenue = st.sidebar.number_input("Regular: revenue unit (kr)", value=2000.0, min_value=1.0, step=100.0)

mini_pack_size = st.sidebar.number_input("Mini: patties per 8,000 revenue", value=10, min_value=1, step=1)
mini_pack_revenue = st.sidebar.number_input("Mini: revenue unit (kr)", value=8000.0, min_value=1.0, step=100.0)

# Weights & trim
reg_piece_g = st.sidebar.number_input("Regular patty weight (g)", value=150, min_value=1, step=5)
mini_piece_g = st.sidebar.number_input("Mini patty weight (g)", value=90, min_value=1, step=5)
waste_per_kg_g = st.sidebar.number_input("Trim/waste per kg raw beef (g)", value=100, min_value=0, step=10)

usable_per_kg_g = 1000 - waste_per_kg_g
reg_per_kg = max(1, usable_per_kg_g // reg_piece_g)
mini_per_kg = max(1, usable_per_kg_g // mini_piece_g)
st.sidebar.caption(f"Yield: {int(reg_per_kg)} regular/kg, {int(mini_per_kg)} mini/kg (usable {usable_per_kg_g} g/kg).")

# ---------- Main UI ----------
st.title("🍔 Jagger Patties Production Calculator")

with st.form("planner"):
    st.markdown("### 1) Sales target")
    col1, col2 = st.columns(2)
    today_budget = col1.number_input("Today’s budget (kr)", min_value=0.0, step=100.0, value=0.0, format="%.0f")
    tomorrow_budget = col2.number_input("Expected revenue until tomorrow cutoff (kr)", min_value=0.0, step=100.0, value=0.0, format="%.0f")

    cutoff_hour = st.select_slider("Tomorrow cutoff time", options=list(range(12, 23)), value=16)
    st.caption(f"Cutoff set to {cutoff_hour}:00 tomorrow.")

    total_target_revenue = today_budget + tomorrow_budget

    st.divider()
    st.markdown("### 2) Current stock")
    c3, c4 = st.columns(2)
    reg_in_stock = c3.number_input("Regular patties left in stock", min_value=0, step=1, value=0.0)
    mini_in_stock = c4.number_input("Mini patties left in stock", min_value=0, step=1, value=0.0)

    submitted = st.form_submit_button("Calculate 💡", use_container_width=True)

if submitted:
    # --- Revenue -> patties (using fixed business rules) ---
    reg_required_total = 0 if reg_pack_revenue <= 0 else math.ceil(total_target_revenue / reg_pack_revenue) * reg_pack_size
    mini_required_total = 0 if mini_pack_revenue <= 0 else math.ceil(total_target_revenue / mini_pack_revenue) * mini_pack_size

    # Subtract stock (can't be negative)
    reg_to_make = max(0, reg_required_total - reg_in_stock)
    mini_to_make = max(0, mini_required_total - mini_in_stock)

    # --- Raw beef required ---
    reg_kg_needed = reg_to_make / reg_per_kg if reg_per_kg else 0
    mini_kg_needed = mini_to_make / mini_per_kg if mini_per_kg else 0

    # Round up to nearest 0.1 kg to avoid shortages
    def round_up(x, step=0.1):
        return math.ceil(x / step) * step if x > 0 else 0.0

    reg_kg_rounded = round_up(reg_kg_needed, 0.1)
    mini_kg_rounded = round_up(mini_kg_needed, 0.1)
    total_kg = reg_kg_rounded + mini_kg_rounded

    def kg_g(kg_float):
        kg = int(kg_float)
        g = int(round((kg_float - kg) * 1000))
        return f"{kg} kg {g} g"

    st.success("Calculation complete.")

    st.markdown("### 📦 Patties to produce")
    a, b = st.columns(2)
    a.metric("Regular patties to make", f"{reg_to_make:,}")
    b.metric("Mini patties to make", f"{mini_to_make:,}")

    st.markdown("### 🥩 Raw beef required")
    st.write(f"- Regular: **{kg_g(reg_kg_rounded)}**")
    st.write(f"- Mini: **{kg_g(mini_kg_rounded)}**")
    st.info(f"**Total raw beef:** {kg_g(total_kg)}")
