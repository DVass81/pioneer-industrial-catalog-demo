import streamlit as st

from modules.cart import render_quote_cart_page, render_quote_sidebar, render_request_quote_page
from modules.catalog import render_catalog_page, render_product_detail_page
from modules.data_loader import load_products
from modules.styling import apply_global_styles, render_about_page, render_home_page


st.set_page_config(
    page_title="Pioneer Industrial Sales Catalog",
    page_icon="PIS",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


def init_session_state() -> None:
    defaults = {
        "cart": {},
        "quote_requests": [],
        "quote_counter": 1001,
        "selected_product_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()
products = load_products()

with st.sidebar:
    st.image("assets/pioneer_logo.png", width='stretch')
    st.markdown('<div class="sidebar-brand">Pioneer Industrial Sales</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="quote-panel"><h4>We Sell Service.</h4><p>Browse Pioneer inventory, build a quote cart, and send a request for confirmed pricing and delivery.</p></div>',
        unsafe_allow_html=True,
    )
    st.divider()
    page = st.radio(
        "Navigate",
        [
            "Home",
            "Product Catalog",
            "Product Detail",
            "Quote Cart",
            "Request Quote",
            "About Pioneer Services",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    render_quote_sidebar(products)

if page == "Home":
    render_home_page(products)
elif page == "Product Catalog":
    render_catalog_page(products)
elif page == "Product Detail":
    render_product_detail_page(products)
elif page == "Quote Cart":
    render_quote_cart_page(products)
elif page == "Request Quote":
    render_request_quote_page(products)
elif page == "About Pioneer Services":
    render_about_page()
