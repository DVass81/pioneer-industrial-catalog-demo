import streamlit as st

from modules.cart import render_quote_cart_page, render_quote_sidebar, render_request_quote_page
from modules.catalog import render_catalog_page, render_product_detail_page
from modules.customers import render_customer_selector
from modules.data_loader import load_customers, load_products
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
        "selected_customer_name": "ICC International",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()
products = load_products()
customers = load_customers()

with st.sidebar:
    st.markdown('<div class="sidebar-brand">Pioneer Industrial Sales</div>', unsafe_allow_html=True)
    selected_customer = render_customer_selector(customers)
    st.divider()
    page = st.radio(
        "Navigate",
        [
            "Home",
            "Product Catalog",
            "Product Detail",
            "Quote Cart",
            "Request Quote",
            "Customer Login",
            "About Pioneer Services",
        ],
        label_visibility="collapsed",
    )
    st.divider()
    render_quote_sidebar(products, selected_customer)

if page == "Home":
    render_home_page(products, selected_customer)
elif page == "Product Catalog":
    render_catalog_page(products, selected_customer)
elif page == "Product Detail":
    render_product_detail_page(products, selected_customer)
elif page == "Quote Cart":
    render_quote_cart_page(products, selected_customer)
elif page == "Request Quote":
    render_request_quote_page(products, selected_customer)
elif page == "Customer Login":
    st.markdown('<div class="page-kicker">Demo Customer Portal</div>', unsafe_allow_html=True)
    st.title("Customer Login / Demo Customer Selector")
    st.info("This demo uses customer profiles instead of live authentication.")
    render_customer_selector(customers, expanded=True)
elif page == "About Pioneer Services":
    render_about_page()
