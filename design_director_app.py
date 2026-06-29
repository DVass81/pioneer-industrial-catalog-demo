import streamlit as st

from modules.data_loader import load_products
from modules.design_director import apply_design_director_styles, render_design_director_page
from modules.styling import apply_global_styles


st.set_page_config(
    page_title="Design Director | Pioneer Industrial Sales",
    page_icon="PIS",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
apply_design_director_styles()

products = load_products()

with st.sidebar:
    st.image("assets/pioneer_logo.png", width="stretch")
    st.markdown('<div class="sidebar-brand">Design Director</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="quote-panel"><h4>Internal / Dev Only</h4><p>Planning foundation for Pioneer catalog, tablet, and WMS screens.</p></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.caption("Run separately from the public catalog. Do not deploy as the customer-facing app.")

render_design_director_page(products)
