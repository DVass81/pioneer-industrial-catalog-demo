import streamlit as st

from modules.data_loader import customer_record


ACCOUNT_HELP_TEXT = "For account help, quote questions, or rush requests, contact your Pioneer sales representative."
PAYMENT_HELP_TEXT = "Invoices and payment instructions are provided after Pioneer confirms quote pricing and availability."
DEFAULT_SALES_REP = "Taylor"
DEFAULT_DELIVERY_DAY = "Scheduled"
DEFAULT_ACCOUNT_TIER = "Demo"


def _value(customer: dict, key: str, fallback: str = "") -> str:
    value = customer.get(key, fallback)
    if value is None:
        return fallback
    return str(value)


def parse_category_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        raw_categories = value
    else:
        raw_categories = str(value).replace("|", ";").split(";")
    return [category.strip() for category in raw_categories if category and category.strip()]


def _pricing_multiplier(customer: dict) -> float:
    raw_multiplier = customer.get("pricing_multiplier")
    if raw_multiplier not in (None, ""):
        try:
            return max(0.01, float(raw_multiplier))
        except (TypeError, ValueError):
            pass

    raw_discount = customer.get("contract_discount", customer.get("discount", 0))
    try:
        discount = float(str(raw_discount).replace("%", "").strip() or 0)
    except (TypeError, ValueError):
        discount = 0
    return max(0.01, round(1 - (discount / 100), 4))


def normalize_customer(customer: dict | None) -> dict:
    normalized = dict(customer or {})
    preferred_categories = parse_category_list(
        normalized.get("preferred_categories")
        or normalized.get("frequently_ordered_categories")
    )
    notes = _value(normalized, "account_notes", _value(normalized, "notes", ""))

    normalized["assigned_sales_rep"] = _value(normalized, "assigned_sales_rep", DEFAULT_SALES_REP)
    normalized["preferred_delivery_day"] = _value(normalized, "preferred_delivery_day", DEFAULT_DELIVERY_DAY)
    normalized["account_tier"] = _value(normalized, "account_tier", DEFAULT_ACCOUNT_TIER)
    normalized["preferred_categories_list"] = preferred_categories
    normalized["preferred_categories"] = ";".join(preferred_categories)
    normalized["frequently_ordered_categories"] = _value(
        normalized,
        "frequently_ordered_categories",
        ";".join(preferred_categories),
    )
    normalized["account_notes"] = notes
    normalized["quote_history_placeholder"] = _value(
        normalized,
        "quote_history_placeholder",
        "No submitted tablet quotes in this demo session yet.",
    )
    normalized["pricing_multiplier"] = _pricing_multiplier(normalized)
    return normalized


def customer_pricing_multiplier(customer: dict | None) -> float:
    return normalize_customer(customer)["pricing_multiplier"]


def customer_tablet_summary(customer: dict | None) -> dict:
    normalized = normalize_customer(customer)
    return {
        "customer_id": _value(normalized, "customer_id", ""),
        "customer_name": _value(normalized, "customer_name", "Demo Customer"),
        "industry": _value(normalized, "industry", "Industrial"),
        "location": _value(normalized, "location", "Regional"),
        "primary_contact": _value(normalized, "primary_contact", ""),
        "email": _value(normalized, "email", ""),
        "phone": _value(normalized, "phone", ""),
        "account_tier": normalized["account_tier"],
        "assigned_sales_rep": normalized["assigned_sales_rep"],
        "preferred_delivery_day": normalized["preferred_delivery_day"],
        "preferred_categories": normalized["preferred_categories_list"],
        "pricing_multiplier": normalized["pricing_multiplier"],
        "account_notes": normalized["account_notes"],
        "payment_terms": _value(normalized, "payment_terms", "Quote confirmation required"),
    }


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
        customer = normalize_customer(customer_record(customers, selected))

        sales_rep = _value(customer, "assigned_sales_rep", DEFAULT_SALES_REP)
        delivery_day = _value(customer, "preferred_delivery_day", DEFAULT_DELIVERY_DAY)
        tier = _value(customer, "account_tier", DEFAULT_ACCOUNT_TIER)
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
                ", ".join(customer["preferred_categories_list"]) or "Demo catalog categories",
            )
            st.write(
                "Quote history:",
                _value(customer, "quote_history_placeholder", "Demo quote history placeholder"),
            )
            st.write(f"Pricing multiplier: {customer['pricing_multiplier']:.2f}")
            st.info("Pioneer will confirm final price, freight, tax, delivery options, and payment terms before an order is placed.")
    return customer
