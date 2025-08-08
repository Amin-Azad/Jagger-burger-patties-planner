import streamlit as st
import math

# --- Hide GitHub icon, header and footer ---
hide_github = """
    <style>
    #MainMenu, footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_github, unsafe_allow_html=True)

# --- Jagger Logo ---
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://jagger.dk/wp-content/uploads/JAGGER-Logo.svg" width="200"/>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Title ---
st.markdown("<h1 style='text-align: center;'>🍔 Jagger Burger Patties Calculator</h1>", unsafe_allow_html=True)

# --- Settings (hidden in expander) ---
with st.expander("⚙️ Branch Settings", expanded=False):
    st.markdown("Adjust only if your branch has different sales Behaviour.")

    reg_pack_revenue = st.number_input("Revenue from 6 regular patties (kr)", value=2000.0)
    mini_pack_revenue = st.number_input("Revenue from 10 mini patties (kr)", value=8000.0)

    reg_patty_weight = st.number_input("Regular patty weight (g)", value=150)
    mini_patty_weight = st.number_input("Mini patty weight (g)", value=90)

    reg_per_kg = st.number_input("Regular patties per 1kg raw (incl. waste)", value=6)
    mini_per_kg = st.number_input("Mini patties per 1kg raw (incl. waste)", value=10)

# --- Section: Sales Target ---
st.markdown("### 1) Sales Target")
today_budget = st.number_input("Today’s expected sales (kr)", min_value=0)
tomorrow_cutoff = st.number_input("Tomorrow's Budget until cutoff hour(kr)", min_value=0)
cutoff_time = st.slider("Cutoff time tomorrow", min_value=12, max_value=22, value=16)

total_budget = today_budget + tomorrow_cutoff
st.caption(f"Total budget: {int(total_budget)} kr — cutoff set to {cutoff_time}:00 tomorrow.")

# --- Section: Current Stock ---
st.markdown("### 2) Current Stock")
reg_in_stock = st.number_input("Regular patties in stock", min_value=0)
mini_in_stock = st.number_input("Mini patties in stock", min_value=0)

# --- Calculation button ---
# Center and resize Calculate button
st.markdown("""
    <style>
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
        width: 50%;
        background-color: #FF5722;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# The Calculate button
submitted = st.button("💡 Calculate")


if submitted:
    st.success("Calculation complete.")


    # Calculate total patties required
    reg_required_total = (total_budget / reg_pack_revenue) * 6
    mini_required_total = (total_budget / mini_pack_revenue) * 10

    # Round up to whole numbers
    reg_to_make = max(0, math.ceil(reg_required_total - reg_in_stock))
    mini_to_make = max(0, math.ceil(mini_required_total - mini_in_stock))

    # Calculate raw beef required
    reg_kg = reg_to_make / reg_per_kg if reg_per_kg else 0
    mini_kg = mini_to_make / mini_per_kg if mini_per_kg else 0

    def to_kg_g(kg_float):
        kg = int(kg_float)
        g = int((kg_float - kg) * 1000)
        return f"{kg} kg {g} g"

    # --- Output ---
    st.markdown("## 📦 Patties to produce")
    col1, col2 = st.columns(2)
    col1.metric("Regular patties to make", reg_to_make)
    col2.metric("Mini patties to make", mini_to_make)

    st.markdown("## 🥩 Raw beef required")
    st.write(f"• Regular: **{to_kg_g(reg_kg)}**")
    st.write(f"• Mini: **{to_kg_g(mini_kg)}**")
    st.info(f"**Total raw beef: {to_kg_g(reg_kg + mini_kg)}**")

    st.markdown("### Notes")
    st.markdown("- Yields are based on patty weights and waste.")
    st.markdown("- Adjust 'Branch Settings' if needed for specific locations.")
