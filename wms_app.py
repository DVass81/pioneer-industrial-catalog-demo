import streamlit as st

from modules.data_loader import load_products
from modules.styling import apply_global_styles
from modules.wms import (
    apply_wms_styles,
    init_wms_state,
    render_dashboard,
    render_inventory_control,
    render_pick_queue,
    render_receiving,
    render_wms_sidebar,
)


st.set_page_config(
    page_title="Pioneer WMS | Warehouse Execution",
    page_icon="PIS",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()
apply_wms_styles()


def main() -> None:
    products = load_products()
    init_wms_state(products)
    render_wms_sidebar(products)

    page = st.sidebar.radio(
        "Warehouse workflow",
        ["Command Center", "Pick Queue", "Inventory Control", "Receiving / Replenishment"],
    )

    if page == "Command Center":
        render_dashboard(products)
    elif page == "Pick Queue":
        render_pick_queue()
    elif page == "Inventory Control":
        render_inventory_control(products)
    else:
        render_receiving(products)


if __name__ == "__main__":
    main()