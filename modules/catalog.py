from __future__ import annotations

from html import escape

import streamlit as st

try:
    from modules.cart import add_to_cart
except ImportError:
    def add_to_cart(product_id: str, quantity: int) -> None:
        quantity = max(1, int(quantity))
        cart = st.session_state.setdefault("cart", {})
        cart[product_id] = cart.get(product_id, 0) + quantity
        st.toast("Added to quote cart")


DETAIL_MODAL_KEY = "catalog_detail_modal_product_id"
SEARCH_FIELDS = [
    "product_name",
    "sku",
    "manufacturer_part_number",
    "category",
    "subcategory",
    "tags",
]

def apply_catalog_styles() -> None:
    st.markdown(
        """
        <style>
        .catalog-summary { display: flex; align-items: center; justify-content: space-between; gap: .75rem; margin: .85rem 0 .65rem; padding: .65rem .8rem; border: 1px solid #E2E5EA; border-radius: 8px; background: #F8FAFC; }
        .catalog-summary strong { color: #101722; font-size: 1rem; }
        .catalog-summary span { color: #56616F; font-size: .82rem; font-weight: 700; text-transform: uppercase; }
        .catalog-filter-note { color: #56616F; font-size: .83rem; margin-top: -.3rem; }
        .product-card { position: relative; min-height: 570px; padding: .8rem; border-color: #D8DDE5; box-shadow: 0 8px 18px rgba(16,23,34,.07); }
        .product-card img { border: 1px solid #ECEFF3; border-radius: 6px; background: #F6F8FA; }
        .product-card h3 { margin: .25rem 0 .3rem; min-height: 2.45rem; font-size: 1rem; }
        .product-card p { margin: .45rem 0 .55rem; min-height: 3.55rem; font-size: .84rem; line-height: 1.35; }
        .product-meta { display: flex; align-items: center; justify-content: space-between; gap: .45rem; margin-top: .65rem; color: #56616F; font-size: .72rem; }
        .product-meta span { overflow-wrap: anywhere; }
        .product-badges { margin: .35rem 0 .3rem; min-height: 1.55rem; }
        .product-spec-strip { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .4rem; margin: .55rem 0; }
        .product-spec { border: 1px solid #E7EAF0; border-radius: 6px; padding: .42rem .5rem; background: #FBFCFE; }
        .product-spec label { display: block; margin-bottom: .1rem; color: #687386; font-size: .66rem; font-weight: 800; text-transform: uppercase; }
        .product-spec span { color: #101722; font-size: .78rem; font-weight: 800; overflow-wrap: anywhere; }
        .badge { border: 1px solid transparent; letter-spacing: .01rem; }
        .badge-stock { border-color: #BFEAD0; }
        .badge-low { border-color: #FFD6A8; }
        .badge-special { border-color: #D9DEE7; }
        .badge-reorder { border-color: #F2E49A; }
        .badge-featured { box-shadow: inset 0 -1px 0 rgba(0,0,0,.18); }
        .detail-shell { border: 1px solid #E0E3E8; border-radius: 8px; padding: 1rem; background: #FFFFFF; box-shadow: 0 8px 20px rgba(16,23,34,.06); }
        .detail-title { margin: .35rem 0 .25rem; font-size: 1.55rem; line-height: 1.1; font-weight: 900; color: #101722; }
        .detail-subtitle { color: #56616F; font-size: .85rem; font-weight: 700; }
        .detail-description { color: #2E3744; margin: .8rem 0; line-height: 1.45; }
        .detail-spec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .5rem; margin-top: .9rem; }
        .detail-spec { border: 1px solid #E7EAF0; border-radius: 6px; padding: .65rem; background: #FBFCFE; }
        .detail-spec label { display: block; color: #687386; font-size: .7rem; font-weight: 900; text-transform: uppercase; margin-bottom: .15rem; }
        .detail-spec span { color: #101722; font-weight: 800; overflow-wrap: anywhere; }
        @media (max-width: 900px) { .catalog-summary { align-items: flex-start; flex-direction: column; } .product-card { min-height: auto; } .detail-spec-grid { grid-template-columns: 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

def prepare_catalog_products(products, customer: dict | None = None):
    prepared = products.copy()
    if "sku" not in prepared.columns and "SKU / Pioneer part number" in prepared.columns:
        prepared["sku"] = prepared["SKU / Pioneer part number"]
    if "image_url" not in prepared.columns and "image_ref" in prepared.columns:
        prepared["image_url"] = prepared["image_ref"]
    return prepared


def stock_badge(row) -> tuple[str, str]:
    qty = int(row["quantity_in_stock"])
    reorder = int(row["reorder_point"])
    if qty <= 0:
        return "Special Order", "badge badge-special"
    if qty <= reorder:
        return "Low Stock", "badge badge-low"
    if qty <= reorder * 2:
        return "Reorder Soon", "badge badge-reorder"
    return "In Stock", "badge badge-stock"


def _field_text(row, field: str) -> str:
    value = row.get(field, "")
    if value is None:
        return ""
    return str(value)


def _search_haystack(products):
    haystack = products[SEARCH_FIELDS[0]].astype(str)
    for field in SEARCH_FIELDS[1:]:
        haystack = haystack + " " + products[field].astype(str)
    return haystack.str.lower()


def _relevance_score(row, search: str) -> int:
    if not search:
        return 0

    query = search.lower().strip()
    terms = [term for term in query.split() if term]
    weighted_fields = [
        ("product_name", 10),
        ("sku", 9),
        ("manufacturer_part_number", 9),
        ("category", 4),
        ("subcategory", 3),
        ("tags", 3),
    ]

    score = 0
    for term in terms:
        for field, weight in weighted_fields:
            if term in _field_text(row, field).lower():
                score += weight

    if query in _field_text(row, "product_name").lower():
        score += 12
    if query in {
        _field_text(row, "sku").lower(),
        _field_text(row, "manufacturer_part_number").lower(),
    }:
        score += 20
    return score


def filter_products(products, search, category, subcategory, in_stock_only, featured_only):
    filtered = products.copy()
    filtered["_catalog_relevance"] = 0
    if search:
        needle = search.lower().strip()
        haystack = _search_haystack(filtered)
        filtered = filtered.loc[haystack.str.contains(needle, regex=False)]
        filtered = filtered.copy()
        filtered["_catalog_relevance"] = filtered.apply(lambda row: _relevance_score(row, needle), axis=1)
    if category != "All":
        filtered = filtered.loc[filtered["category"] == category]
    if subcategory != "All":
        filtered = filtered.loc[filtered["subcategory"] == subcategory]
    if in_stock_only:
        filtered = filtered.loc[filtered["quantity_in_stock"] > 0]
    if featured_only:
        filtered = filtered.loc[filtered["is_icc_supply"]]
    return filtered


def sort_products(products, sort_by):
    if sort_by == "Stock":
        return products.sort_values(["quantity_in_stock", "_catalog_relevance", "product_name"], ascending=[False, False, True])
    if sort_by == "Category":
        return products.sort_values(["category", "subcategory", "product_name"])
    if "_catalog_relevance" in products.columns and products["_catalog_relevance"].sum() > 0:
        return products.sort_values(
            ["_catalog_relevance", "quantity_in_stock", "product_name"],
            ascending=[False, False, True],
        )
    return products.sort_values(["is_icc_supply", "quantity_in_stock", "product_name"], ascending=[False, False, True])


def render_catalog_page(products, customer: dict | None = None) -> None:
    apply_catalog_styles()
    products = prepare_catalog_products(products)
    st.markdown('<div class="page-kicker">Industrial Catalog</div>', unsafe_allow_html=True)
    st.title("Find the supplies that keep the line moving")

    with st.container(border=True):
        top = st.columns([2.6, 1.35, 1.35, 1.1])
        search = top[0].text_input("Search catalog", placeholder="Product, SKU, MPN, category, tag")
        category_options = ["All"] + sorted(products["category"].unique().tolist())
        category = top[1].selectbox("Category", category_options)
        sub_source = products if category == "All" else products.loc[products["category"] == category]
        subcategory = top[2].selectbox("Subcategory", ["All"] + sorted(sub_source["subcategory"].unique().tolist()))
        sort_by = top[3].selectbox("Sort by", ["Relevance", "Stock", "Category"])
        toggles = st.columns([1.1, 1.1, 3.8])
        in_stock_only = toggles[0].toggle("In-stock only")
        featured_only = toggles[1].toggle("Featured")
        toggles[2].markdown(
            '<div class="catalog-filter-note">Use filters together for fast reorder, sourcing, and quote-building workflows.</div>',
            unsafe_allow_html=True,
        )

    filtered = sort_products(filter_products(products, search, category, subcategory, in_stock_only, featured_only), sort_by)

    st.markdown(
        f"""
        <div class="catalog-summary">
            <strong>{len(filtered):,} products found</strong>
            <span>{escape(category)} / {escape(subcategory)} / Sorted by {escape(sort_by)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_product_grid(filtered)
    render_product_detail_modal(products)


def render_product_grid(products, customer: dict | None = None) -> None:
    if products.empty:
        st.warning("No products match the current filters.")
        return

    for chunk_start in range(0, len(products), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, products.iloc[chunk_start : chunk_start + 3].iterrows()):
            render_product_card(col, row)


def render_product_card(col, row, customer: dict | None = None) -> None:
    badge_text, badge_class = stock_badge(row)
    product_id = row["product_id"]
    in_stock = int(row["quantity_in_stock"]) > 0
    stock_qty = int(row["quantity_in_stock"])
    reorder_point = int(row["reorder_point"])
    lead_time = escape(str(row["lead_time"]))
    warehouse = escape(str(row["warehouse_location"]))
    with col:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(row["image_url"], use_container_width=True)
        featured_tag = '<span class="badge badge-featured">Featured</span>' if bool(row["is_icc_supply"]) else ""
        st.markdown(
            f"""
            <div class="product-meta">
                <span>{escape(str(row['manufacturer']))}</span>
                <span>SKU {escape(str(row['sku']))}</span>
            </div>
            <h3>{escape(str(row['product_name']))}</h3>
            <div class="product-badges"><span class="{badge_class}">{escape(badge_text)}</span>{featured_tag}</div>
            <p>{escape(str(row['description']))}</p>
            <div class="product-spec-strip">
                <div class="product-spec"><label>MPN</label><span>{escape(str(row['manufacturer_part_number']))}</span></div>
                <div class="product-spec"><label>Stock</label><span>{stock_qty:,} on hand</span></div>
                <div class="product-spec"><label>Lead</label><span>{lead_time}</span></div>
                <div class="product-spec"><label>Bin</label><span>{warehouse}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        max_qty = max(1, stock_qty)
        qty = st.number_input(
            "Qty",
            min_value=1,
            max_value=max_qty,
            value=1,
            step=1,
            key=f"qty_{product_id}",
            disabled=not in_stock,
            help=f"Reorder point: {reorder_point:,}",
        )
        bcols = st.columns(2)
        if bcols[0].button("Add", key=f"add_{product_id}", use_container_width=True, disabled=not in_stock):
            add_to_cart(product_id, qty)
        if bcols[1].button("Details", key=f"detail_{product_id}", use_container_width=True):
            st.session_state["selected_product_id"] = product_id
            st.session_state[DETAIL_MODAL_KEY] = product_id
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
def _detail_row(products, product_id):
    row = products.loc[products["product_id"] == product_id]
    if row.empty:
        return None
    return row.iloc[0]


def render_product_detail_content(row, customer: dict | None = None, key_prefix: str = "detail") -> None:
    product_id = row["product_id"]
    in_stock = int(row["quantity_in_stock"]) > 0
    badge_text, badge_class = stock_badge(row)
    featured_tag = '<span class="badge badge-featured">Featured</span>' if bool(row["is_icc_supply"]) else ""
    stock_qty = int(row["quantity_in_stock"])
    cols = st.columns([1, 1.2])
    with cols[0]:
        st.image(row["image_url"], use_container_width=True)
    with cols[1]:
        st.markdown(
            f"""
            <div class="detail-shell">
                <div class="product-badges"><span class="{badge_class}">{escape(badge_text)}</span>{featured_tag}</div>
                <div class="detail-title">{escape(str(row['product_name']))}</div>
                <div class="detail-subtitle">{escape(str(row['manufacturer']))} | SKU {escape(str(row['sku']))} | MPN {escape(str(row['manufacturer_part_number']))}</div>
                <div class="detail-description">{escape(str(row['description']))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(1, stock_qty),
            value=1,
            step=1,
            key=f"{key_prefix}_qty_{product_id}",
            disabled=not in_stock,
        )
        if st.button(
            "Add to quote cart",
            type="primary",
            key=f"{key_prefix}_add_{product_id}",
            disabled=not in_stock,
        ):
            add_to_cart(product_id, qty)
    st.markdown(
        f"""
        <div class="detail-spec-grid">
            <div class="detail-spec"><label>Specs</label><span>{escape(str(row['specs']))}</span></div>
            <div class="detail-spec"><label>Lead time</label><span>{escape(str(row['lead_time']))}</span></div>
            <div class="detail-spec"><label>Warehouse</label><span>{escape(str(row['warehouse_location']))}</span></div>
            <div class="detail-spec"><label>Available stock</label><span>{stock_qty:,}</span></div>
            <div class="detail-spec"><label>Reorder point</label><span>{int(row['reorder_point']):,}</span></div>
            <div class="detail-spec"><label>Category</label><span>{escape(str(row['category']))} / {escape(str(row['subcategory']))}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_product_detail_modal(products, customer: dict | None = None) -> None:
    product_id = st.session_state.get(DETAIL_MODAL_KEY)
    if not product_id:
        return

    row = _detail_row(products, product_id)
    if row is None:
        st.session_state.pop(DETAIL_MODAL_KEY, None)
        return

    if hasattr(st, "dialog"):

        @st.dialog("Product details")
        def detail_dialog() -> None:
            render_product_detail_content(row, key_prefix="modal_detail")
            if st.button("Close", key=f"modal_close_{row['product_id']}"):
                st.session_state.pop(DETAIL_MODAL_KEY, None)
                st.rerun()

        detail_dialog()
        return

    with st.expander("Product details", expanded=True):
        render_product_detail_content(row, key_prefix="modal_detail")
        if st.button("Close details", key=f"modal_close_{row['product_id']}"):
            st.session_state.pop(DETAIL_MODAL_KEY, None)
            st.rerun()


def render_product_detail_page(products, customer: dict | None = None) -> None:
    apply_catalog_styles()
    products = prepare_catalog_products(products)
    product_id = st.session_state.get("selected_product_id")
    if not product_id:
        product_id = products.iloc[0]["product_id"]
    row = _detail_row(products, product_id)
    if row is None:
        st.warning("Select a product from the catalog to view details.")
        return

    st.markdown('<div class="page-kicker">Product Detail</div>', unsafe_allow_html=True)
    render_product_detail_content(row, key_prefix="detail_page")


