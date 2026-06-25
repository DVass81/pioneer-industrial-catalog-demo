from __future__ import annotations

from html import escape

import streamlit as st

try:
    from modules.cart import add_to_cart, effective_price
except ImportError:
    def effective_price(row, customer: dict) -> float:
        base = float(row.get("customer_specific_price", row.get("price", 0)) or 0)
        multiplier = float(customer.get("pricing_multiplier", 1.0))
        return round(base * multiplier, 2)

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


def _customer_price(value, customer: dict) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        pass

    customer_name = str(customer.get("customer_name", "")).strip()
    for part in str(value).split(";"):
        if "=" not in part:
            continue
        name, price = part.split("=", 1)
        if name.strip() == customer_name:
            try:
                return float(price.strip())
            except ValueError:
                return None
    return None


def prepare_catalog_products(products, customer: dict):
    prepared = products.copy()
    if "sku" not in prepared.columns and "SKU / Pioneer part number" in prepared.columns:
        prepared["sku"] = prepared["SKU / Pioneer part number"]
    if "image_url" not in prepared.columns and "image_ref" in prepared.columns:
        prepared["image_url"] = prepared["image_ref"]
    if "customer_specific_price" in prepared.columns:
        prepared["customer_specific_price"] = prepared["customer_specific_price"].apply(lambda value: _customer_price(value, customer))
    if "customer_specific_price" not in prepared.columns or prepared["customer_specific_price"].isna().all():
        prepared["customer_specific_price"] = prepared["price"]
    else:
        prepared["customer_specific_price"] = prepared["customer_specific_price"].fillna(prepared["price"])
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


def filter_products(products, search, category, subcategory, in_stock_only, icc_only):
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
    if icc_only:
        filtered = filtered.loc[filtered["is_icc_supply"]]
    return filtered


def sort_products(products, sort_by):
    if sort_by == "Stock":
        return products.sort_values(["quantity_in_stock", "_catalog_relevance", "product_name"], ascending=[False, False, True])
    if sort_by == "Price":
        return products.sort_values(["price", "product_name"], ascending=[True, True])
    if sort_by == "Category":
        return products.sort_values(["category", "subcategory", "product_name"])
    if "_catalog_relevance" in products.columns and products["_catalog_relevance"].sum() > 0:
        return products.sort_values(
            ["_catalog_relevance", "quantity_in_stock", "product_name"],
            ascending=[False, False, True],
        )
    return products.sort_values(["is_icc_supply", "quantity_in_stock", "product_name"], ascending=[False, False, True])


def render_catalog_page(products, customer: dict) -> None:
    products = prepare_catalog_products(products, customer)
    st.markdown('<div class="page-kicker">Industrial Catalog</div>', unsafe_allow_html=True)
    st.title("Find the supplies that keep the line moving")

    with st.container(border=True):
        top = st.columns([3, 1.4, 1.4, 1.2])
        search = top[0].text_input("Search products, SKU, manufacturer part, category, tags")
        category_options = ["All"] + sorted(products["category"].unique().tolist())
        category = top[1].selectbox("Category", category_options)
        sub_source = products if category == "All" else products.loc[products["category"] == category]
        subcategory = top[2].selectbox("Subcategory", ["All"] + sorted(sub_source["subcategory"].unique().tolist()))
        sort_by = top[3].selectbox("Sort by", ["Relevance", "Stock", "Price", "Category"])
        toggles = st.columns([1, 1, 4])
        in_stock_only = toggles[0].toggle("In-stock only")
        icc_only = toggles[1].toggle("ICC supplies")

    filtered = sort_products(filter_products(products, search, category, subcategory, in_stock_only, icc_only), sort_by)

    if customer["customer_name"] == "ICC International" and not icc_only:
        st.markdown('<div class="recommendation-strip">ICC International recommended supplies are highlighted with red tags.</div>', unsafe_allow_html=True)

    st.caption(f"{len(filtered)} products found")
    render_product_grid(filtered, customer)
    render_product_detail_modal(products, customer)


def render_product_grid(products, customer: dict) -> None:
    if products.empty:
        st.warning("No products match the current filters.")
        return

    for chunk_start in range(0, len(products), 3):
        cols = st.columns(3)
        for col, (_, row) in zip(cols, products.iloc[chunk_start : chunk_start + 3].iterrows()):
            render_product_card(col, row, customer)


def render_product_card(col, row, customer: dict) -> None:
    badge_text, badge_class = stock_badge(row)
    price = effective_price(row, customer)
    product_id = row["product_id"]
    in_stock = int(row["quantity_in_stock"]) > 0
    with col:
        st.markdown('<div class="product-card">', unsafe_allow_html=True)
        st.image(row["image_url"], use_container_width=True)
        icc_tag = '<span class="badge badge-icc">ICC</span>' if bool(row["is_icc_supply"]) else ""
        st.markdown(
            f"""
            <div class="product-meta">{escape(str(row['manufacturer']))} | {escape(str(row['sku']))}</div>
            <h3>{escape(str(row['product_name']))}</h3>
            <div><span class="{badge_class}">{escape(badge_text)}</span>{icc_tag}</div>
            <p>{escape(str(row['description']))}</p>
            <div class="card-price">${price:,.2f} <span>/{escape(str(row['unit_of_measure']))}</span></div>
            """,
            unsafe_allow_html=True,
        )
        max_qty = max(1, int(row["quantity_in_stock"]))
        qty = st.number_input(
            "Qty",
            min_value=1,
            max_value=max_qty,
            value=1,
            step=1,
            key=f"qty_{product_id}",
            disabled=not in_stock,
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


def render_product_detail_content(row, customer: dict, key_prefix: str = "detail") -> None:
    product_id = row["product_id"]
    in_stock = int(row["quantity_in_stock"]) > 0
    cols = st.columns([1, 1.2])
    with cols[0]:
        st.image(row["image_url"], use_container_width=True)
    with cols[1]:
        badge_text, badge_class = stock_badge(row)
        st.markdown(f'<span class="{badge_class}">{escape(badge_text)}</span>', unsafe_allow_html=True)
        st.title(row["product_name"])
        st.caption(f"{row['manufacturer']} | SKU {row['sku']} | MPN {row['manufacturer_part_number']}")
        st.write(row["description"])
        st.markdown(f"### ${effective_price(row, customer):,.2f} / {row['unit_of_measure']}")
        qty = st.number_input(
            "Quantity",
            min_value=1,
            max_value=max(1, int(row["quantity_in_stock"])),
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
        st.divider()
        st.write("Specs:", row["specs"])
        st.write("Lead time:", row["lead_time"])
        st.write("Warehouse:", row["warehouse_location"])
        st.write("Stock:", int(row["quantity_in_stock"]))


def render_product_detail_modal(products, customer: dict) -> None:
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
            render_product_detail_content(row, customer, key_prefix="modal_detail")
            if st.button("Close", key=f"modal_close_{row['product_id']}"):
                st.session_state.pop(DETAIL_MODAL_KEY, None)
                st.rerun()

        detail_dialog()
        return

    with st.expander("Product details", expanded=True):
        render_product_detail_content(row, customer, key_prefix="modal_detail")
        if st.button("Close details", key=f"modal_close_{row['product_id']}"):
            st.session_state.pop(DETAIL_MODAL_KEY, None)
            st.rerun()


def render_product_detail_page(products, customer: dict) -> None:
    products = prepare_catalog_products(products, customer)
    product_id = st.session_state.get("selected_product_id")
    if not product_id:
        product_id = products.iloc[0]["product_id"]
    row = _detail_row(products, product_id)
    if row is None:
        st.warning("Select a product from the catalog to view details.")
        return

    st.markdown('<div class="page-kicker">Product Detail</div>', unsafe_allow_html=True)
    render_product_detail_content(row, customer, key_prefix="detail_page")
