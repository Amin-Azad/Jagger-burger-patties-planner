import math
import streamlit as st

st.set_page_config(page_title="Jagger Burger Patties Planner", page_icon="🍔", layout="centered")

# Hide GitHub icon (top-right)
hide_github = """
    <style>
    #MainMenu, footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_github, unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("⚙️ Branch Settings")
reg_pack_size = st.sidebar.number_input("Regular: patties per 2000 revenue", value=6, min_value=1)
reg_pack_revenue = st.sidebar.number_input("Regular: revenue base (kr)", value=2000.0, min_value=1.0)

mini_pack_size = st.sidebar.number_input("Mini: patties per 8000 revenue", value=10, min_value=1)
mini_pack_revenue = st.sidebar.number_input("Mini: revenue base (kr)", value=8000.0, min_value=1.0)

reg_piece_g = st.sidebar.number_input("Regular patty weight (g)", value=150, min_value=1)
mini_piece_g = st.sidebar.number_input("Mini patty weight (g)", value=90, min_value=1)
waste_per_kg_g = st.sidebar.number_input("Waste per kg raw beef (g)", value=100, min_value=0)

usable_per_kg_g = 1000 - waste_per_kg_g
reg_per_kg = max(1, usable_per_kg_g // reg_piece_g)
mini_per_kg = max(1, usable_per_kg_g // mini_piece_g)
st.sidebar.caption(f"Yield: {int(reg_per_kg)} regular/kg, {int(mini_per_kg)} mini/kg")

# ---------- Main UI ----------
st.markdown("## 🍔 Jagger Burger Patties Calculator")

with st.form("planner"):
    st.markdown("### 1) Sales Target")
    col1, col2 = st.columns(2)
    today_budget = col1.number_input("Today’s expected revenue (kr)", value=0.0, step=100.0, format="%.0f")
    tomorrow_budget = col2.number_input("Tomorrow until cutoff (kr)", value=0.0, step=100.0, format="%.0f")
    total_target_revenue = today_budget + tomorrow_budget

    cutoff_hour = st.select_slider("Cutoff time tomorrow", options=list(range(12, 23)), value=16)
    st.caption(f"Total budget: {total_target_revenue:.0f} kr — cutoff set to {cutoff_hour}:00 tomorrow.")

    st.divider()
    st.markdown("### 2) Current Stock")
    c3, c4 = st.columns(2)
    reg_in_stock = c3.number_input("Regular patties in stock", min_value=0, step=1, value=0)
    mini_in_stock = c4.number_input("Mini patties in stock", min_value=0, step=1, value=0)

    submitted = st.form_submit_button("Calculate 💡", use_container_width=True)

if submitted:
    # 🧮 Main Calculation
    reg_required_total = math.ceil((total_target_revenue / reg_pack_revenue) * reg_pack_size)
    mini_required_total = math.ceil((total_target_revenue / mini_pack_revenue) * mini_pack_size)

    reg_to_make = max(0, reg_required_total - reg_in_stock)
    mini_to_make = max(0, mini_required_total - mini_in_stock)

    reg_kg_needed = reg_to_make / reg_per_kg if reg_per_kg else 0
    mini_kg_needed = mini_to_make / mini_per_kg if mini_per_kg else 0

    def round_up(x, step=0.1):
        return math.ceil(x / step) * step

    reg_kg_rounded = round_up(reg_kg_needed)
    mini_kg_rounded = round_up(mini_kg_needed)
    total_kg = reg_kg_rounded + mini_kg_rounded

    def kg_g(kg_float):
        kg = int(kg_float)
        g = int(round((kg_float - kg) * 1000))
        return f"{kg} kg {g} g"

    # ✅ Output
    st.success("Calculation complete.")

    st.markdown("### 📦 Patties to produce")
    a, b = st.columns(2)
    a.metric("Regular patties to make", f"{reg_to_make:,}")
    b.metric("Mini patties to make", f"{mini_to_make:,}")

    st.markdown("### 🥩 Raw beef required")
    st.write(f"- Regular: **{kg_g(reg_kg_rounded)}**")
    st.write(f"- Mini: **{kg_g(mini_kg_rounded)}**")
    st.info(f"**Total raw beef:** {kg_g(total_kg)}")
