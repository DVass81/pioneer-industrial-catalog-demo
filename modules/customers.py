import streamlit as st

from modules.data_loader import customer_record


def render_customer_selector(customers, expanded: bool = False) -> dict:
    names = customers["customer_name"].tolist()
    if st.session_state.get("selected_customer_name") not in names:
        st.session_state["selected_customer_name"] = names[0]

    container = st.container(border=expanded)
    with container:
        selected = st.selectbox(
            "Demo customer",
            names,
            index=names.index(st.session_state["selected_customer_name"]),
            key="customer_select_box" if expanded else "customer_select_sidebar",
        )
        st.session_state["selected_customer_name"] = selected
        customer = customer_record(customers, selected)

        st.markdown(
            f"""
            <div class="customer-card">
                <strong>{customer['customer_name']}</strong>
                <span>{customer['industry']} | {customer['location']}</span>
                <span>Sales Rep: {customer['assigned_sales_rep']}</span>
                <span>{customer['account_tier']} account | Delivery: {customer['preferred_delivery_day']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if expanded:
            st.write("Frequently ordered categories:", customer["frequently_ordered_categories"])
            st.write("Quote history:", customer["quote_history_placeholder"])
            st.write(f"Pricing multiplier: {customer['pricing_multiplier']:.2f}")
    return customer
