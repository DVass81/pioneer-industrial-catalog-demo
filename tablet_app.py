from __future__ import annotations

import base64
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.cart import effective_price
from modules.data_loader import load_customers, load_products
from modules.styling import apply_global_styles
from modules.workflow_store import init_workflow_store, save_handoff_order


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

SUBSTITUTION_PREFERENCES = [
    "Use closest stocked equivalent",
    "Call customer before substituting",
    "No substitutions",
]

ROOT = Path(__file__).resolve().parent
IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
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
        .tablet-hero-grid { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(240px, .8fr); gap: .9rem; align-items: stretch; }
        .tablet-hero h3 { margin: 0 0 .35rem; color: #252826; font-size: 1.05rem; }
        .tablet-hero p { margin: .2rem 0; color: #59615b; line-height: 1.35; }
        .tablet-account-strip { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .55rem; margin-top: .8rem; }
        .tablet-account-fact { border: 1px solid #e3e6df; border-radius: 8px; padding: .65rem; background: #f8faf7; }
        .tablet-account-fact label { display: block; color: #59615b; font-size: .68rem; font-weight: 900; text-transform: uppercase; }
        .tablet-account-fact strong { display: block; margin-top: .15rem; color: #252826; font-size: .98rem; line-height: 1.2; overflow-wrap: anywhere; }
        .tablet-kpi { border: 1px solid #d9ddd6; border-radius: 8px; padding: .85rem; background: #ffffff; min-height: 108px; }
        .tablet-kpi label { display: block; color: #59615b; font-size: .72rem; font-weight: 900; text-transform: uppercase; }
        .tablet-kpi strong { display: block; color: #252826; font-size: 1.25rem; margin-top: .2rem; }
        .tablet-kpi small { display: block; margin-top: .2rem; color: #59615b; line-height: 1.25; }
        .tablet-card { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); margin-bottom: .75rem; }
        .tablet-card h3 { margin: 0 0 .4rem; }
        .tablet-pill { display: inline-block; border: 1px solid #d9ddd6; border-radius: 999px; padding: .25rem .55rem; margin: .15rem .2rem .15rem 0; background: #f5f6f3; color: #252826; font-size: .78rem; font-weight: 800; }
        .tablet-product { border: 1px solid #e3e6df; border-radius: 8px; padding: .85rem; background: #ffffff; min-height: 265px; }
        .tablet-product-image { width: 100%; aspect-ratio: 4 / 3; border: 1px solid #e3e6df; border-radius: 8px; background: #f8faf7; display: flex; align-items: center; justify-content: center; overflow: hidden; margin-bottom: .7rem; }
        .tablet-product-image img { width: 100%; height: 100%; object-fit: contain; display: block; padding: .45rem; }
        .tablet-product h4 { margin: .3rem 0; font-size: 1rem; line-height: 1.2; }
        .tablet-product p { min-height: 3.2rem; color: #59615b; font-size: .84rem; }
        .tablet-product-meta { color: #59615b; font-size: .86rem; line-height: 1.35; }
        .tablet-product-meta strong { color: #252826; }
        .tablet-detail { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); margin: .85rem 0 1rem; }
        .tablet-detail-grid { display: grid; grid-template-columns: minmax(220px, .75fr) minmax(0, 1.25fr); gap: 1rem; align-items: start; }
        .tablet-detail-image { width: 100%; aspect-ratio: 4 / 3; border: 1px solid #e3e6df; border-radius: 8px; background: #f8faf7; display: flex; align-items: center; justify-content: center; overflow: hidden; }
        .tablet-detail-image img { width: 100%; height: 100%; object-fit: contain; display: block; padding: .65rem; }
        .tablet-detail h3 { margin: .35rem 0 .45rem; color: #252826; line-height: 1.2; }
        .tablet-detail p { color: #59615b; line-height: 1.45; margin: .45rem 0; }
        .tablet-detail-facts { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .55rem; margin-top: .75rem; }
        .tablet-detail-fact { border: 1px solid #e3e6df; border-radius: 8px; padding: .6rem; background: #f8faf7; }
        .tablet-detail-fact label { display: block; color: #59615b; font-size: .68rem; font-weight: 900; text-transform: uppercase; }
        .tablet-detail-fact strong { display: block; color: #252826; margin-top: .15rem; line-height: 1.2; overflow-wrap: anywhere; }
        .visit-prep { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); }
        .visit-prep h3 { margin: 0 0 .35rem; }
        .visit-prep p { margin: 0 0 .35rem; color: #59615b; }
        .handoff-box { border-left: 5px solid #4c6444; border-radius: 8px; padding: 1rem; background: #f4f7f2; }
        @media (max-width: 900px) {
            .tablet-hero-grid, .tablet-account-strip, .tablet-detail-grid, .tablet-detail-facts { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "cart": {},
        "cart_line_details": {},
        "quote_counter": 2001,
        "tablet_orders": [],
        "selected_customer_name": None,
        "selected_product_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def money(value: float) -> str:
    return f"${float(value):,.2f}"


def customer_field(customer: dict, key: str, fallback: str = "Not provided") -> str:
    value = customer.get(key, fallback)
    if pd.isna(value) or str(value).strip() == "":
        return fallback
    return str(value)


def credit_limit_label(customer: dict) -> str:
    raw = customer.get("credit_limit", "")
    try:
        return money(float(raw))
    except (TypeError, ValueError):
        return str(raw) if str(raw).strip() else "Not provided"


@st.cache_data(show_spinner=False)
def image_src(image_ref: str) -> str:
    if image_ref.startswith(("http://", "https://", "data:")):
        return image_ref
    image_path = (ROOT / image_ref).resolve()
    try:
        image_path.relative_to(ROOT)
    except ValueError:
        return ""
    if not image_path.exists() or not image_path.is_file():
        return ""
    mime_type = IMAGE_MIME_TYPES.get(image_path.suffix.lower(), "image/png")
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"




def account_price(row, customer: dict) -> float:
    return effective_price(row, customer)


def account_price_label(row, customer: dict) -> str:
    price = float(row.get("price", 0) or 0)
    if price <= 0:
        return "Quote required"
    return money(account_price(row, customer))


def add_to_tablet_cart(product_id: str, quantity: int) -> None:
    quantity = max(1, int(quantity))
    cart = st.session_state.setdefault("cart", {})
    details = st.session_state.setdefault("cart_line_details", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    details.setdefault(
        product_id,
        {
            "quote_note": "",
            "substitution_preference": SUBSTITUTION_PREFERENCES[0],
        },
    )
    st.toast("Added to Taylor's field order")


def clear_cart_line_detail(product_id: str) -> None:
    st.session_state.setdefault("cart_line_details", {}).pop(product_id, None)
    st.session_state.pop(f"tablet_line_note_{product_id}", None)
    st.session_state.pop(f"tablet_line_substitution_{product_id}", None)

def product_image_html(row, css_class: str, empty_label: str = "No product image") -> str:
    image_ref = str(row.get("image_url") or row.get("image_ref") or "")
    src = image_src(image_ref) if image_ref else ""
    if not src:
        return f'<div class="{css_class}">{escape(empty_label)}</div>'
    product_name = escape(str(row.get("product_name", "Product image")))
    return f'<div class="{css_class}"><img src="{escape(src)}" alt="{product_name}"></div>'


def product_fact(label: str, value: object) -> str:
    text = str(value).strip() if value is not None else ""
    return (
        '<div class="tablet-detail-fact">'
        f'<label>{escape(label)}</label>'
        f'<strong>{escape(text or "Not provided")}</strong>'
        '</div>'
    )


def render_selected_product_detail(products: pd.DataFrame, customer: dict, key_prefix: str) -> None:
    product_id = st.session_state.get("selected_product_id")
    if not product_id:
        return

    match = products.loc[products["product_id"] == product_id]
    if match.empty:
        st.session_state["selected_product_id"] = None
        st.info("That product is no longer available in the current catalog.")
        return

    row = match.iloc[0]
    stock = max(0, int(row.get("quantity_in_stock", 0) or 0))
    price_label = account_price_label(row, customer)
    facts = "".join(
        [
            product_fact("SKU", row.get("sku", row.get("SKU / Pioneer part number", product_id))),
            product_fact("Manufacturer", row.get("manufacturer", "")),
            product_fact("Category", row.get("category", "")),
            product_fact("Stock", f"{stock:,} on hand" if stock > 0 else "Out of stock"),
            product_fact("Account price", price_label),
            product_fact("Mfr part", row.get("manufacturer_part_number", "")),
        ]
    )
    st.markdown(
        f"""
        <div class="tablet-detail">
            <div class="tablet-detail-grid">
                {product_image_html(row, "tablet-detail-image")}
                <div>
                    <span class="tablet-pill">{escape(str(row.get('category', 'Product')))}</span>
                    <h3>{escape(str(row.get('product_name', product_id)))}</h3>
                    <p>{escape(str(row.get('description', 'No description available.')))}</p>
                    <div class="tablet-detail-facts">{facts}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    detail_cols = st.columns([1, 1, 2])
    qty = detail_cols[0].number_input(
        "Quantity",
        min_value=1,
        max_value=max(1, stock),
        value=1,
        step=1,
        key=f"{key_prefix}_detail_qty_{product_id}",
        disabled=stock <= 0,
    )
    if detail_cols[1].button("Add to cart", key=f"{key_prefix}_detail_add_{product_id}", width="stretch", disabled=stock <= 0):
        add_to_tablet_cart(str(product_id), qty)
    if detail_cols[2].button("Close details", key=f"{key_prefix}_detail_close_{product_id}"):
        st.session_state["selected_product_id"] = None
        st.rerun()


def preferred_categories(customer: dict, available_categories: list[str]) -> list[str]:
    raw = str(customer.get("preferred_categories", ""))
    mapped: list[str] = []
    for item in [part.strip() for part in raw.split(";") if part.strip()]:
        category = CATEGORY_MAP.get(item, item)
        if category in available_categories and category not in mapped:
            mapped.append(category)
    return mapped or available_categories[:4]



def reset_tablet_cart_for_customer(customer: dict) -> None:
    customer_id = customer_field(customer, "customer_id", customer_field(customer, "customer_name"))
    active_customer_id = st.session_state.get("active_cart_customer_id")
    if active_customer_id is None:
        st.session_state["active_cart_customer_id"] = customer_id
        return
    if active_customer_id != customer_id:
        st.session_state["cart"] = {}
        st.session_state["cart_line_details"] = {}
        st.session_state["selected_product_id"] = None
        st.session_state["active_cart_customer_id"] = customer_id
        st.toast("Started a fresh tablet cart for this customer")
def customer_selector(customers: pd.DataFrame) -> dict:
    names = customers["customer_name"].tolist()
    if not names:
        st.error("No Stage 2 customer records are available.")
        st.stop()
    if st.session_state.get("selected_customer_name") not in names:
        st.session_state["selected_customer_name"] = names[0]
    selected = st.sidebar.selectbox(
        "Customer account",
        names,
        index=names.index(st.session_state["selected_customer_name"]),
    )
    st.session_state["selected_customer_name"] = selected
    customer = customers.loc[customers["customer_name"] == selected].iloc[0].to_dict()
    reset_tablet_cart_for_customer(customer)
    return customer


def cart_lines_for_customer(products: pd.DataFrame, customer: dict) -> list[dict]:
    lines = []
    line_details = st.session_state.setdefault("cart_line_details", {})
    for product_id, quantity in st.session_state.get("cart", {}).items():
        match = products.loc[products["product_id"] == product_id]
        if match.empty:
            continue
        row = match.iloc[0]
        unit_price = account_price(row, customer)
        details = line_details.setdefault(
            product_id,
            {
                "quote_note": "",
                "substitution_preference": SUBSTITUTION_PREFERENCES[0],
            },
        )
        lines.append(
            {
                "product_id": product_id,
                "sku": row.get("sku", row.get("SKU / Pioneer part number", product_id)),
                "name": row.get("product_name", product_id),
                "category": row.get("category", ""),
                "manufacturer": row.get("manufacturer", ""),
                "manufacturer_part_number": row.get("manufacturer_part_number", ""),
                "warehouse_location": row.get("warehouse_location", ""),
                "lead_time": row.get("lead_time", ""),
                "available_stock": int(row.get("quantity_in_stock", 0) or 0),
                "reorder_point": int(row.get("reorder_point", 0) or 0),
                "quantity": int(quantity),
                "unit_price": unit_price,
                "line_total": round(unit_price * int(quantity), 2),
                "quote_note": str(details.get("quote_note", "")).strip(),
                "substitution_preference": details.get("substitution_preference", SUBSTITUTION_PREFERENCES[0]),
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
    account_notes = customer_field(customer, "account_notes", customer_field(customer, "notes"))
    quote_history = customer_field(customer, "quote_history_placeholder", "Review recent quote activity with the customer.")
    delivery_day = customer_field(customer, "preferred_delivery_day", "Scheduled")
    st.markdown('<div class="page-kicker">Taylor Field Tablet</div>', unsafe_allow_html=True)
    st.title(f"{customer['customer_name']} field visit")
    st.markdown(
        f"""
        <div class="tablet-hero">
            <div class="tablet-hero-grid">
                <div>
                    <h3>{escape(customer_field(customer, "primary_contact"))}</h3>
                    <p>{escape(customer_field(customer, "email"))} | {escape(customer_field(customer, "phone"))}</p>
                    <p>{escape(account_notes)}</p>
                </div>
                <div>
                    <h3>Account summary</h3>
                    <p><strong>{escape(customer_field(customer, "account_tier"))}</strong> account</p>
                    <p>{escape(customer_field(customer, "payment_terms"))} | Credit limit {escape(credit_limit_label(customer))}</p>
                    <p>Preferred delivery: {escape(delivery_day)}</p>
                </div>
            </div>
            <div class="tablet-account-strip">
                <div class="tablet-account-fact"><label>Location</label><strong>{escape(customer_field(customer, "location"))}</strong></div>
                <div class="tablet-account-fact"><label>Industry</label><strong>{escape(customer_field(customer, "industry"))}</strong></div>
                <div class="tablet-account-fact"><label>Recent context</label><strong>{escape(quote_history)}</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    kpis = st.columns(4)
    kpis[0].markdown('<div class="tablet-kpi"><label>Sales rep</label><strong>Taylor</strong><small>Field visit owner</small></div>', unsafe_allow_html=True)
    kpis[1].markdown(f'<div class="tablet-kpi"><label>Contract discount</label><strong>{escape(str(customer.get("contract_discount", "0%")))}</strong><small>Applied in account pricing</small></div>', unsafe_allow_html=True)
    kpis[2].markdown(f'<div class="tablet-kpi"><label>Preferred categories</label><strong>{len(prefs)}</strong><small>{escape(", ".join(prefs[:2]))}</small></div>', unsafe_allow_html=True)
    in_stock_count = len(products.loc[products["quantity_in_stock"] > 0])
    kpis[3].markdown(f'<div class="tablet-kpi"><label>Catalog products</label><strong>{len(products)}</strong><small>{in_stock_count} in stock</small></div>', unsafe_allow_html=True)

    st.markdown("### Account focus")
    st.markdown("".join(f'<span class="tablet-pill">{escape(category)}</span>' for category in prefs), unsafe_allow_html=True)

    st.markdown(
        """
        <div class="visit-prep">
            <h3>Visit prep</h3>
            <p>Use this quick field check before building the quote.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    prep_key = customer_field(customer, "customer_id", customer_field(customer, "customer_name"))
    prep_cols = st.columns(3)
    prep_cols[0].checkbox("Confirm replenishment priorities", key=f"prep_priorities_{prep_key}")
    prep_cols[1].checkbox("Verify delivery window", key=f"prep_delivery_{prep_key}")
    prep_cols[2].checkbox("Capture substitution notes", key=f"prep_subs_{prep_key}")

    st.markdown("### Recommended for this visit")
    recommended = products.loc[products["category"].isin(prefs)].sort_values(["is_icc_supply", "quantity_in_stock"], ascending=[False, False]).head(6)
    render_selected_product_detail(products, customer, key_prefix="rec")
    render_product_tiles(recommended, customer, key_prefix="rec")


def render_product_tiles(rows: pd.DataFrame, customer: dict, key_prefix: str) -> None:
    if rows.empty:
        st.info("No matching products for this filter.")
        return
    for chunk_start in range(0, len(rows), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, rows.iloc[chunk_start : chunk_start + 3].iterrows()):
            with col:
                image_markup = product_image_html(row, "tablet-product-image", empty_label="")
                st.markdown(
                    f"""
                    <div class="tablet-product">
                        {image_markup}
                        <span class="tablet-pill">{escape(str(row['category']))}</span>
                        <h4>{escape(str(row['product_name']))}</h4>
                        <p>{escape(str(row['description']))}</p>
                        <div class="tablet-product-meta">
                            <strong>{escape(str(row['sku']))}</strong><br>
                            Stock: {int(row['quantity_in_stock']):,}<br>
                            Account price: <strong>{account_price_label(row, customer)}</strong>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                stock = max(0, int(row["quantity_in_stock"]))
                qty = st.number_input("Qty", min_value=1, max_value=max(1, stock), value=1, step=1, key=f"{key_prefix}_qty_{row['product_id']}", disabled=stock <= 0)
                action_cols = st.columns([1, 1])
                if action_cols[0].button("View details", key=f"{key_prefix}_view_{row['product_id']}", width="stretch"):
                    st.session_state["selected_product_id"] = row["product_id"]
                    st.rerun()
                if action_cols[1].button("Add", key=f"{key_prefix}_add_{row['product_id']}", width="stretch", disabled=stock <= 0):
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
    render_selected_product_detail(products, customer, key_prefix="lookup")
    render_product_tiles(filtered.head(24), customer, key_prefix="lookup")


def tablet_customer_handoff(customer: dict) -> dict:
    return {
        "customer_name": customer.get("customer_name", "Demo customer"),
        "customer_id": customer.get("customer_id", ""),
        "industry": customer.get("industry", ""),
        "location": customer.get("location", ""),
        "account_tier": customer.get("account_tier", ""),
        "payment_terms": customer.get("payment_terms", ""),
        "credit_limit": customer.get("credit_limit", ""),
        "assigned_sales_rep": customer.get("assigned_sales_rep", "Taylor"),
        "notes": customer.get("notes", ""),
    }


def tablet_contact_handoff(customer: dict) -> dict:
    return {
        "primary_contact": customer.get("primary_contact", ""),
        "email": customer.get("email", ""),
        "phone": customer.get("phone", ""),
    }


def build_tablet_handoff_order(
    order_number: str,
    customer: dict,
    lines: list[dict],
    needed_by: date,
    delivery_window: str,
    delivery_notes: str,
) -> dict:
    subtotal = round(sum(line["line_total"] for line in lines), 2)
    total_items = sum(line["quantity"] for line in lines)
    rush_review = delivery_window == "Rush review" or needed_by <= date.today()
    return {
        "order_number": order_number,
        "request_type": "tablet_warehouse_handoff_preview",
        "customer": customer.get("customer_name", "Demo customer"),
        "customer_metadata": tablet_customer_handoff(customer),
        "contact": tablet_contact_handoff(customer),
        "order_metadata": {
            "created_by": "Taylor",
            "needed_by": str(needed_by),
            "delivery_window": delivery_window,
            "priority": "Rush review" if rush_review else "Standard route planning",
            "stage": "Stage 2 tablet preview",
        },
        "lines": lines,
        "subtotal": subtotal,
        "line_count": len(lines),
        "total_items": total_items,
        "needed_by": str(needed_by),
        "delivery_window": delivery_window,
        "delivery_notes": delivery_notes.strip(),
        "pull_ticket_status": "Ready for Stage 3 WMS build",
        "warehouse_checklist": [
            "Confirm on-hand stock and substitutions.",
            "Validate route, freight, tax, and payment terms.",
            "Create WMS pull ticket after Pioneer confirmation.",
        ],
    }


def render_order_builder(customer: dict, products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Field Quote / Order Builder</div>', unsafe_allow_html=True)
    st.title("Prepare customer quote")
    if st.session_state.get("last_tablet_order_number"):
        st.success(f"Created warehouse handoff preview {st.session_state['last_tablet_order_number']}.")
    lines = cart_lines_for_customer(products, customer)
    if not lines:
        st.info("No products added yet. Use Dashboard recommendations or Product Lookup to build the order.")
        return
    line_details = st.session_state.setdefault("cart_line_details", {})
    for line in lines:
        product_id = line["product_id"]
        details = line_details.setdefault(
            product_id,
            {
                "quote_note": "",
                "substitution_preference": SUBSTITUTION_PREFERENCES[0],
            },
        )
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(f"**{line['name']}**  \n`{line['sku']}`")
            stock_match = products.loc[products["product_id"] == product_id]
            available_stock = int(stock_match.iloc[0]["quantity_in_stock"]) if not stock_match.empty else line["quantity"]
            new_qty = cols[1].number_input("Qty", min_value=1, max_value=max(1, available_stock), value=min(line["quantity"], max(1, available_stock)), key=f"tablet_cart_qty_{product_id}")
            st.session_state["cart"][product_id] = int(new_qty)
            cols[2].markdown(f"**{money(line['unit_price'])}**  \n{money(line['unit_price'] * int(new_qty))}")
            if cols[3].button("Remove", key=f"tablet_remove_{product_id}"):
                st.session_state["cart"].pop(product_id, None)
                clear_cart_line_detail(product_id)
                st.rerun()
            detail_cols = st.columns([2, 1])
            note_key = f"tablet_line_note_{product_id}"
            st.session_state.setdefault(note_key, str(details.get("quote_note", "")))
            note = detail_cols[0].text_area(
                "Line note",
                placeholder="Quote note for warehouse or customer follow-up.",
                key=note_key,
                height=80,
            )
            current_preference = details.get("substitution_preference", SUBSTITUTION_PREFERENCES[0])
            if current_preference not in SUBSTITUTION_PREFERENCES:
                current_preference = SUBSTITUTION_PREFERENCES[0]
            substitution_key = f"tablet_line_substitution_{product_id}"
            st.session_state.setdefault(substitution_key, current_preference)
            substitution = detail_cols[1].selectbox(
                "Substitution",
                SUBSTITUTION_PREFERENCES,
                key=substitution_key,
            )
            line_details[product_id] = {
                "quote_note": note,
                "substitution_preference": substitution,
            }
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
        submitted_lines = cart_lines_for_customer(products, customer)
        handoff_order = build_tablet_handoff_order(
            order_number,
            customer,
            submitted_lines,
            needed_by,
            delivery_window,
            delivery_notes,
        )
        st.session_state.setdefault("tablet_orders", []).append(handoff_order)
        st.session_state["last_tablet_order_number"] = order_number
        st.session_state["cart"] = {}
        st.session_state["cart_line_details"] = {}
        st.success(f"Created warehouse handoff preview {order_number} and added it to the WMS queue.")
        st.rerun()


def render_handoff(products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Stage 3 Preview</div>', unsafe_allow_html=True)
    st.title("Warehouse handoff preview")
    orders = st.session_state.get("tablet_orders", [])
    if not orders:
        st.info("No field orders submitted yet. Create one from the Order Builder to preview WMS handoff.")
        return
    st.caption(f"{len(orders)} session handoff preview(s) preserved for this tablet visit.")
    for order in reversed(orders):
        customer_metadata = order.get("customer_metadata", {})
        contact = order.get("contact", {})
        order_metadata = order.get("order_metadata", {})
        st.markdown(
            f"""
            <div class="handoff-box">
                <h3>{escape(order['order_number'])}</h3>
                <strong>{escape(order.get('customer', customer_metadata.get('customer_name', 'Demo customer')))}</strong> | Needed by {escape(order.get('needed_by', order_metadata.get('needed_by', '')))} | {escape(order.get('delivery_window', order_metadata.get('delivery_window', '')))}<br>
                Pull ticket status: {escape(order.get('pull_ticket_status', 'Ready for Stage 3 WMS build'))}
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lines", order.get("line_count", len(order.get("lines", []))))
        c2.metric("Pieces", order.get("total_items", sum(line.get("quantity", 0) for line in order.get("lines", []))))
        c3.metric("Subtotal", money(order.get("subtotal", 0)))
        c4.metric("Priority", order_metadata.get("priority", "Standard"))

        st.markdown(
            f"**Contact:** {escape(str(contact.get('primary_contact', '')))} | "
            f"{escape(str(contact.get('email', '')))} | {escape(str(contact.get('phone', '')))}"
        )
        st.caption(
            "Account: "
            f"{customer_metadata.get('account_tier', '')} | "
            f"{customer_metadata.get('payment_terms', '')} | "
            f"Credit limit {customer_metadata.get('credit_limit', '')}"
        )

        line_rows = [
            {
                "SKU": line.get("sku", ""),
                "Product": line.get("name", ""),
                "Category": line.get("category", ""),
                "Mfr Part": line.get("manufacturer_part_number", ""),
                "Bin": line.get("warehouse_location", ""),
                "Lead Time": line.get("lead_time", ""),
                "Qty": line.get("quantity", 0),
                "Unit": money(line.get("unit_price", 0)),
                "Line total": money(line.get("line_total", 0)),
                "Substitution": line.get("substitution_preference", ""),
                "Line note": line.get("quote_note", ""),
            }
            for line in order.get("lines", [])
        ]
        if line_rows:
            st.dataframe(line_rows, width="stretch", hide_index=True)

        checklist = order.get("warehouse_checklist", [])
        if checklist:
            st.markdown("**Warehouse checklist**")
            for item in checklist:
                st.markdown(f"- {escape(str(item))}")
        if order.get("delivery_notes"):
            st.caption(f"Field notes: {order['delivery_notes']}")


def main() -> None:
    apply_tablet_styles()
    init_workflow_store()
    init_state()
    products = load_products()
    customers = load_customers()
    customer = customer_selector(customers)
    render_sidebar(customer, products)

    page = st.sidebar.radio(
        "Tablet workflow",
        ["Dashboard", "Product Lookup", "Order Builder", "Warehouse Handoff"],
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
