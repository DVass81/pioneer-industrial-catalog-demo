from __future__ import annotations

from datetime import date
from html import escape

import pandas as pd
import streamlit as st

from modules.data_loader import load_customers, load_products
from modules.styling import apply_global_styles


CATEGORY_MAP = {
    "PPE & Safety": "Safety Supplies",
    "Electrical & Wire Management": "Electrical",
    "Fasteners & Anchors": "Fasteners",
    "MRO Chemicals & Lubricants": "Lubricants",
    "Pipe, Valves & Fittings": "MRO Supplies",
    "Hydraulics & Pneumatics": "Power Transmission",
    "Abrasives & Grinding": "Abrasives",
    "Welding & Gas Supplies": "MRO Supplies",
    "Industrial Hardware": "Fasteners",
    "Packaging & Shipping": "Material Handling",
    "Measuring & Layout": "MRO Supplies",
    "Cutting Tools": "Cutting Tools",
    "Material Handling": "Material Handling",
}


st.set_page_config(
    page_title="Taylor Field Tablet | Pioneer Industrial Sales",
    page_icon="PIS",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()


def apply_tablet_styles() -> None:
    st.markdown(
        """
        <style>
        .tablet-shell { padding-bottom: 1rem; }
        .tablet-hero { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); }
        .tablet-kpi { border: 1px solid #d9ddd6; border-radius: 8px; padding: .85rem; background: #ffffff; min-height: 108px; }
        .tablet-kpi label { display: block; color: #59615b; font-size: .72rem; font-weight: 900; text-transform: uppercase; }
        .tablet-kpi strong { display: block; color: #252826; font-size: 1.25rem; margin-top: .2rem; }
        .tablet-card { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); margin-bottom: .75rem; }
        .tablet-card h3 { margin: 0 0 .4rem; }
        .tablet-pill { display: inline-block; border: 1px solid #d9ddd6; border-radius: 999px; padding: .25rem .55rem; margin: .15rem .2rem .15rem 0; background: #f5f6f3; color: #252826; font-size: .78rem; font-weight: 800; }
        .tablet-product { border: 1px solid #e3e6df; border-radius: 8px; padding: .85rem; background: #ffffff; min-height: 265px; }
        .tablet-product h4 { margin: .3rem 0; font-size: 1rem; line-height: 1.2; }
        .tablet-product p { min-height: 3.2rem; color: #59615b; font-size: .84rem; }
        .handoff-box { border-left: 5px solid #4c6444; border-radius: 8px; padding: 1rem; background: #f4f7f2; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "cart": {},
        "quote_counter": 2001,
        "tablet_orders": [],
        "selected_customer_name": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def money(value: float) -> str:
    return f"${float(value):,.2f}"


def parse_discount(customer: dict) -> float:
    raw = str(customer.get("contract_discount", "0")).replace("%", "").strip()
    try:
        return max(0.0, min(float(raw), 80.0)) / 100
    except ValueError:
        return 0.0


def account_price(row, customer: dict) -> float:
    discount = parse_discount(customer)
    price = float(row.get("price", 0) or 0)
    return round(price * (1 - discount), 2)


def account_price_label(row, customer: dict) -> str:
    price = float(row.get("price", 0) or 0)
    if price <= 0:
        return "Quote required"
    return money(account_price(row, customer))


def add_to_tablet_cart(product_id: str, quantity: int) -> None:
    quantity = max(1, int(quantity))
    cart = st.session_state.setdefault("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    st.toast("Added to Taylor's field order", icon="OK")


def preferred_categories(customer: dict, available_categories: list[str]) -> list[str]:
    raw = str(customer.get("preferred_categories", ""))
    mapped: list[str] = []
    for item in [part.strip() for part in raw.split(";") if part.strip()]:
        category = CATEGORY_MAP.get(item, item)
        if category in available_categories and category not in mapped:
            mapped.append(category)
    return mapped or available_categories[:4]


def customer_selector(customers: pd.DataFrame) -> dict:
    names = customers["customer_name"].tolist()
    if st.session_state.get("selected_customer_name") not in names:
        st.session_state["selected_customer_name"] = names[0]
    selected = st.sidebar.selectbox(
        "Customer account",
        names,
        index=names.index(st.session_state["selected_customer_name"]),
    )
    st.session_state["selected_customer_name"] = selected
    return customers.loc[customers["customer_name"] == selected].iloc[0].to_dict()


def cart_lines_for_customer(products: pd.DataFrame, customer: dict) -> list[dict]:
    lines = []
    for product_id, quantity in st.session_state.get("cart", {}).items():
        match = products.loc[products["product_id"] == product_id]
        if match.empty:
            continue
        row = match.iloc[0]
        unit_price = account_price(row, customer)
        lines.append(
            {
                "product_id": product_id,
                "sku": row.get("sku", row.get("SKU / Pioneer part number", product_id)),
                "name": row.get("product_name", product_id),
                "quantity": int(quantity),
                "unit_price": unit_price,
                "line_total": round(unit_price * int(quantity), 2),
            }
        )
    return lines


def customer_subtotal(products: pd.DataFrame, customer: dict) -> float:
    return round(sum(line["line_total"] for line in cart_lines_for_customer(products, customer)), 2)


def render_sidebar(customer: dict, products: pd.DataFrame) -> None:
    st.sidebar.image("assets/pioneer_logo.png", width="stretch")
    st.sidebar.markdown('<div class="sidebar-brand">Taylor Field Tablet</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**{customer['customer_name']}**")
    st.sidebar.caption(f"{customer['industry']} | {customer['location']}")
    st.sidebar.caption(f"Contact: {customer['primary_contact']} | {customer['phone']}")
    st.sidebar.divider()
    st.sidebar.metric("Quote lines", len(st.session_state.get("cart", {})))
    st.sidebar.metric("Account subtotal", money(customer_subtotal(products, customer)))
    st.sidebar.caption("Account pricing is demo-estimated until Pioneer confirms final quote.")


def render_dashboard(customer: dict, products: pd.DataFrame) -> None:
    categories = sorted(products["category"].unique().tolist())
    prefs = preferred_categories(customer, categories)
    st.markdown('<div class="page-kicker">Taylor Field Tablet</div>', unsafe_allow_html=True)
    st.title(f"{customer['customer_name']} field visit")
    st.markdown(
        f"""
        <div class="tablet-hero">
            <strong>{escape(customer['primary_contact'])}</strong> | {escape(customer['email'])} | {escape(customer['phone'])}<br>
            {escape(customer['account_tier'])} account | {escape(customer['payment_terms'])} | Credit limit {escape(str(customer['credit_limit']))}<br>
            {escape(customer['notes'])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpis = st.columns(4)
    kpis[0].markdown(f'<div class="tablet-kpi"><label>Sales rep</label><strong>Taylor</strong></div>', unsafe_allow_html=True)
    kpis[1].markdown(f'<div class="tablet-kpi"><label>Contract discount</label><strong>{escape(str(customer.get("contract_discount", "0%")))}</strong></div>', unsafe_allow_html=True)
    kpis[2].markdown(f'<div class="tablet-kpi"><label>Preferred categories</label><strong>{len(prefs)}</strong></div>', unsafe_allow_html=True)
    kpis[3].markdown(f'<div class="tablet-kpi"><label>Catalog products</label><strong>{len(products)}</strong></div>', unsafe_allow_html=True)

    st.markdown("### Account focus")
    st.markdown("".join(f'<span class="tablet-pill">{escape(category)}</span>' for category in prefs), unsafe_allow_html=True)

    st.markdown("### Recommended for this visit")
    recommended = products.loc[products["category"].isin(prefs)].sort_values(["is_icc_supply", "quantity_in_stock"], ascending=[False, False]).head(6)
    render_product_tiles(recommended, customer, key_prefix="rec")


def render_product_tiles(rows: pd.DataFrame, customer: dict, key_prefix: str) -> None:
    if rows.empty:
        st.info("No matching products for this filter.")
        return
    for chunk_start in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, rows.iloc[chunk_start : chunk_start + 3].iterrows()):
            with col:
                image_ref = str(row.get("image_ref") or row.get("image_url") or "")
                if image_ref:
                    st.image(image_ref, width="stretch")
                st.markdown(
                    f"""
                    <div class="tablet-product">
                        <span class="tablet-pill">{escape(str(row['category']))}</span>
                        <h4>{escape(str(row['product_name']))}</h4>
                        <p>{escape(str(row['description']))}</p>
                        <strong>{escape(str(row['sku']))}</strong><br>
                        Stock: {int(row['quantity_in_stock']):,} | Account price: {account_price_label(row, customer)}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                qty = st.number_input("Qty", min_value=1, value=1, step=1, key=f"{key_prefix}_qty_{row['product_id']}")
                if st.button("Add", key=f"{key_prefix}_add_{row['product_id']}", width="stretch"):
                    add_to_tablet_cart(row["product_id"], qty)


def render_lookup(customer: dict, products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Field Product Lookup</div>', unsafe_allow_html=True)
    st.title("Find and add products")
    categories = ["All"] + sorted(products["category"].unique().tolist())
    c1, c2, c3 = st.columns([2.2, 1.2, 1])
    search = c1.text_input("Search", placeholder="SKU, product, category, manufacturer")
    category = c2.selectbox("Category", categories)
    in_stock = c3.toggle("In stock")
    filtered = products.copy()
    if search:
        haystack = (
            filtered["product_name"].astype(str) + " " + filtered["sku"].astype(str) + " " + filtered["category"].astype(str) + " " + filtered["manufacturer"].astype(str)
        ).str.lower()
        filtered = filtered.loc[haystack.str.contains(search.lower(), regex=False)]
    if category != "All":
        filtered = filtered.loc[filtered["category"] == category]
    if in_stock:
        filtered = filtered.loc[filtered["quantity_in_stock"] > 0]
    st.caption(f"{len(filtered)} products found")
    render_product_tiles(filtered.head(24), customer, key_prefix="lookup")


def render_order_builder(customer: dict, products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Field Quote / Order Builder</div>', unsafe_allow_html=True)
    st.title("Prepare customer quote")
    lines = cart_lines_for_customer(products, customer)
    if not lines:
        st.info("No products added yet. Use Dashboard recommendations or Product Lookup to build the order.")
        return
    for line in lines:
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{line['name']}**  \n`{line['sku']}`")
            new_qty = cols[1].number_input("Qty", min_value=1, value=line["quantity"], key=f"tablet_cart_qty_{line['product_id']}")
            st.session_state["cart"][line["product_id"]] = int(new_qty)
            cols[2].markdown(f"**{money(line['unit_price'])}**  \n{money(line['unit_price'] * int(new_qty))}")
            if cols[3].button("Remove", key=f"tablet_remove_{line['product_id']}"):
                st.session_state["cart"].pop(line["product_id"], None)
                st.rerun()
    st.markdown(f"### Account estimated subtotal: {money(customer_subtotal(products, customer))}")

    with st.form("tablet_handoff_form"):
        st.markdown("### Delivery and warehouse handoff")
        c1, c2 = st.columns(2)
        needed_by = c1.date_input("Needed by", value=date.today())
        delivery_window = c2.selectbox("Delivery window", ["Next route", "Morning", "Afternoon", "Will call", "Rush review"])
        delivery_notes = st.text_area("Field notes", placeholder="Dock notes, substitutions, customer urgency, Taylor observations.")
        submit = st.form_submit_button("Send to warehouse preview", type="primary", width="stretch")
    if submit:
        order_number = f"PIS-FIELD-{st.session_state.get('quote_counter', 2001)}"
        st.session_state["quote_counter"] = st.session_state.get("quote_counter", 2001) + 1
        st.session_state.setdefault("tablet_orders", []).append(
            {
                "order_number": order_number,
                "customer": customer["customer_name"],
                "lines": cart_lines_for_customer(products, customer),
                "subtotal": customer_subtotal(products, customer),
                "needed_by": str(needed_by),
                "delivery_window": delivery_window,
                "delivery_notes": delivery_notes,
            }
        )
        st.session_state["cart"] = {}
        st.success(f"Created warehouse handoff preview {order_number}")
        st.rerun()


def render_handoff(products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Stage 3 Preview</div>', unsafe_allow_html=True)
    st.title("Warehouse handoff preview")
    orders = st.session_state.get("tablet_orders", [])
    if not orders:
        st.info("No field orders submitted yet. Create one from the Order Builder to preview WMS handoff.")
        return
    for order in reversed(orders):
        st.markdown(
            f"""
            <div class="handoff-box">
                <h3>{escape(order['order_number'])}</h3>
                <strong>{escape(order['customer'])}</strong> | Needed by {escape(order['needed_by'])} | {escape(order['delivery_window'])}<br>
                Pull ticket status: Ready for Stage 3 WMS build
            </div>
            """,
            unsafe_allow_html=True,
        )
        for line in order["lines"]:
            st.markdown(f"- `{line['sku']}` {line['quantity']} x {line['name']}")
        st.caption(order.get("delivery_notes", ""))


def main() -> None:
    apply_tablet_styles()
    init_state()
    products = load_products()
    customers = load_customers()
    customer = customer_selector(customers)
    render_sidebar(customer, products)

    page = st.sidebar.radio(
        "Tablet workflow",
        ["Dashboard", "Product Lookup", "Order Builder", "Warehouse Handoff"],
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    st.sidebar.caption("Stage 2 demo only. No live ERP, payment, or warehouse integration yet.")

    if page == "Dashboard":
        render_dashboard(customer, products)
    elif page == "Product Lookup":
        render_lookup(customer, products)
    elif page == "Order Builder":
        render_order_builder(customer, products)
    else:
        render_handoff(products)


if __name__ == "__main__":
    main()


