import math
import datetime as dt
import streamlit as st

st.set_page_config(page_title="Burger Patties Planner", page_icon="🍔", layout="centered")

# ---------- Sidebar: Branch settings (editable) ----------
st.sidebar.header("⚙️ Branch Settings (edit as needed)")

# Revenue model (packs → revenue)
reg_pack_size = st.sidebar.number_input("Regular: patties per pack", value=6, min_value=1, step=1)
reg_pack_revenue = st.sidebar.number_input("Regular: revenue per pack", value=2000.0, min_value=0.0, step=100.0)

mini_pack_size = st.sidebar.number_input("Mini: patties per pack", value=10, min_value=1, step=1)
mini_pack_revenue = st.sidebar.number_input("Mini: revenue per pack", value=8000.0, min_value=0.0, step=100.0)

# Meat weights / yield
reg_piece_g = st.sidebar.number_input("Regular patty weight (g)", value=150, min_value=1, step=5)
mini_piece_g = st.sidebar.number_input("Mini patty weight (g)", value=90, min_value=1, step=5)
waste_per_kg_g = st.sidebar.number_input("Trim/waste per kg raw beef (g)", value=100, min_value=0, step=10)

# Derived: patties per kg based on weight & waste (assumes 1000 g raw -> 1000 - waste usable)
usable_per_kg_g = 1000 - waste_per_kg_g
reg_per_kg = max(1, math.floor(usable_per_kg_g / reg_piece_g))
mini_per_kg = max(1, math.floor(usable_per_kg_g / mini_piece_g))

st.sidebar.caption(
    f"📦 Derived yield: {reg_per_kg} regular/kg, {mini_per_kg} mini/kg "
    f"(from {usable_per_kg_g} g usable per kg)."
)

# Target split method
st.sidebar.subheader("How to split the revenue target?")
split_method = st.sidebar.radio(
    "Choose one:",
    ["Single total revenue + split %", "Enter revenue targets per type"],
    index=0
)
reg_share = 0.5
reg_target_rev = 0.0
mini_target_rev = 0.0

# ---------- Main UI ----------
st.title("🍔 Patties Production Calculator")

with st.form("planner"):
    st.markdown("### 1) Sales targets")
    col1, col2 = st.columns(2)

    today_budget = col1.number_input("Today’s budget (revenue)", min_value=0.0, step=100.0, value=16000.0, format="%.0f")
    tomorrow_budget = col2.number_input("Expected revenue until tomorrow cutoff", min_value=0.0, step=100.0, value=0.0, format="%.0f")

    cutoff_hour = st.select_slider("Tomorrow cutoff time", options=list(range(12, 23)), value=16)
    st.caption(f"Cutoff set to {cutoff_hour}:00 tomorrow.")

    total_target_revenue = today_budget + tomorrow_budget

    st.divider()
    if split_method == "Single total revenue + split %":
        reg_share = st.slider("Regular share of total revenue (%)", min_value=0, max_value=100, value=50, step=5) / 100.0
        reg_target_rev = total_target_revenue * reg_share
        mini_target_rev = total_target_revenue - reg_target_rev
    else:
        colr, colm = st.columns(2)
        reg_target_rev = colr.number_input("Revenue target from Regular", min_value=0.0, step=100.0, value=total_target_revenue/2, format="%.0f")
        mini_target_rev = colm.number_input("Revenue target from Mini", min_value=0.0, step=100.0, value=total_target_revenue/2, format="%.0f")

    st.markdown("### 2) Current stock")
    col3, col4 = st.columns(2)
    reg_in_stock = col3.number_input("Regular patties left in stock", min_value=0, step=1, value=16)
    mini_in_stock = col4.number_input("Mini patties left in stock", min_value=0, step=1, value=20)

    submitted = st.form_submit_button("Calculate 💡", use_container_width=True)

if submitted:
    # Revenue per patty (from pack model)
    reg_rev_per_patty = reg_pack_revenue / reg_pack_size if reg_pack_size else 0
    mini_rev_per_patty = mini_pack_revenue / mini_pack_size if mini_pack_size else 0

    # Required patties to hit revenue targets (round up)
    reg_required_total = math.ceil(reg_target_rev / reg_rev_per_patty) if reg_rev_per_patty > 0 else 0
    mini_required_total = math.ceil(mini_target_rev / mini_rev_per_patty) if mini_rev_per_patty > 0 else 0

    # Net to produce (can’t go negative)
    reg_to_make = max(0, reg_required_total - reg_in_stock)
    mini_to_make = max(0, mini_required_total - mini_in_stock)

    # Raw beef required (by kg) — round up to cover whole patties
    reg_kg_needed = reg_to_make / reg_per_kg
    mini_kg_needed = mini_to_make / mini_per_kg

    # Optionally round up to nearest 0.1 kg for practicality
    round_up_to = 0.1  # kg
    def round_up(x, step): return math.ceil(x / step) * step if x > 0 else 0.0

    reg_kg_rounded = round_up(reg_kg_needed, round_up_to)
    mini_kg_rounded = round_up(mini_kg_needed, round_up_to)
    total_kg = reg_kg_rounded + mini_kg_rounded

    # Pretty kg + g formatter
    def kg_g(kg_float):
        kg = int(kg_float)
        g = int(round((kg_float - kg) * 1000))
        return f"{kg} kg {g} g"

    st.success("Calculation complete.")

    st.markdown("### 📦 Patties to produce")
    colA, colB = st.columns(2)
    colA.metric("Regular patties to make", f"{reg_to_make:,}")
    colB.metric("Mini patties to make", f"{mini_to_make:,}")

    st.markdown("### 🥩 Raw beef required")
    st.write(f"- Regular: **{kg_g(reg_kg_rounded)}** (before trimming)")
    st.write(f"- Mini: **{kg_g(mini_kg_rounded)}** (before trimming)")
    st.info(f"**Total raw beef:** {kg_g(total_kg)}")

    st.markdown("### Notes")
    st.write(
        "- Yields are derived from patty weights and the selected waste per kg.\n"
        "- You can change pack sizes and revenue per pack in the sidebar (varies by branch).\n"
        "- Rounds meat up to the nearest 0.1 kg to avoid shortages."
    )

# Footer
st.caption(
    "Built for mobile: use the sidebar for branch-specific settings. "
    "Adjust any numbers and re-calc anytime."
)
