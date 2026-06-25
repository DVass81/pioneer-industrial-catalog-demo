import streamlit as st

from modules.data_loader import customer_record


ACCOUNT_HELP_TEXT = "For account help, quote questions, or rush requests, contact your Pioneer sales representative."
PAYMENT_HELP_TEXT = "Invoices and payment instructions are provided after Pioneer confirms quote pricing and availability."


def _value(customer: dict, key: str, fallback: str = "") -> str:
    value = customer.get(key, fallback)
    if value is None:
        return fallback
    return str(value)


def render_customer_selector(customers, expanded: bool = False) -> dict:
    names = customers["customer_name"].tolist()
    if st.session_state.get("selected_customer_name") not in names:
        st.session_state["selected_customer_name"] = names[0]

    container = st.container(border=expanded)
    with container:
        selected = st.selectbox(
            "Account portal customer",
            names,
            index=names.index(st.session_state["selected_customer_name"]),
            key="customer_select_box" if expanded else "customer_select_sidebar",
        )
        st.session_state["selected_customer_name"] = selected
        customer = customer_record(customers, selected)

        sales_rep = _value(customer, "assigned_sales_rep", "Taylor")
        delivery_day = _value(customer, "preferred_delivery_day", "Scheduled")
        tier = _value(customer, "account_tier", "Demo")
        st.markdown("#### Account Portal")
        st.markdown(
            f"""
            <div class="customer-card">
                <strong>{_value(customer, 'customer_name', 'Demo Customer')}</strong>
                <span>{_value(customer, 'industry', 'Industrial')} | {_value(customer, 'location', 'Regional')}</span>
                <span>Sales Rep: {sales_rep}</span>
                <span>{tier} account | Delivery: {delivery_day}</span>
                <span>Quote pricing shown for this account is estimated until Pioneer confirms it.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(ACCOUNT_HELP_TEXT)
        st.caption(PAYMENT_HELP_TEXT)
        if expanded:
            st.write(
                "Frequently ordered categories:",
                _value(customer, "frequently_ordered_categories", _value(customer, "preferred_categories", "Demo catalog categories")),
            )
            st.write(
                "Quote history:",
                _value(customer, "quote_history_placeholder", _value(customer, "notes", "Demo quote history placeholder")),
            )
            st.write(f"Pricing multiplier: {float(customer.get('pricing_multiplier', 1.0)):.2f}")
            st.info("Pioneer will confirm final price, freight, tax, delivery options, and payment terms before an order is placed.")
    return customer