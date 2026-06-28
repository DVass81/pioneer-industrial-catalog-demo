from __future__ import annotations

from datetime import date

import streamlit as st

from modules.customers import customer_pricing_multiplier, customer_tablet_summary


FINAL_PRICING_NOTE = "Final pricing confirmed by Pioneer sales representative."
PIONEER_CONTACT_TEXT = "Questions or rush needs? Call Pioneer Industrial Sales so the team can help confirm options."
PAYMENT_TEXT = "Payment is completed after Pioneer confirms pricing, availability, freight, and delivery details."
CONFIRMATION_TEXT = (
    "Your quote request has been sent to Pioneer Industrial Sales. A customer service representative "
    "will contact you with confirmed pricing, delivery options, and payment instructions."
)
PUBLIC_PRICE_MULTIPLIER = 1.0


def _row_value(row, *keys, default=None):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def effective_price(row, customer: dict | None = None) -> float:
    base_price = float(_row_value(row, "price", "customer_specific_price", default=0) or 0)
    multiplier = customer_pricing_multiplier(customer) if customer else PUBLIC_PRICE_MULTIPLIER
    return round(base_price * multiplier, 2)


def add_to_cart(product_id: str, quantity: int) -> None:
    quantity = max(1, int(quantity))
    cart = st.session_state.setdefault("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    st.toast("Added to quote cart", icon="OK")


def cart_lines(products, customer: dict | None = None) -> list[dict]:
    lines = []
    for product_id, quantity in st.session_state.get("cart", {}).items():
        match = products.loc[products["product_id"] == product_id]
        if match.empty:
            continue
        row = match.iloc[0]
        unit_price = effective_price(row, customer)
        lines.append(
            {
                "product_id": product_id,
                "sku": _row_value(row, "sku", "SKU / Pioneer part number", default=product_id),
                "name": _row_value(row, "product_name", "name", default=product_id),
                "category": _row_value(row, "category", default=""),
                "subcategory": _row_value(row, "subcategory", default=""),
                "quantity": int(quantity),
                "unit_price": unit_price,
                "line_total": round(unit_price * int(quantity), 2),
            }
        )
    return lines


def cart_subtotal(products, customer: dict | None = None) -> float:
    return round(sum(line["line_total"] for line in cart_lines(products, customer)), 2)


def build_quote_snapshot(
    products,
    contact_details: dict | None = None,
    customer: dict | None = None,
    request_type: str = "quote",
    order_metadata: dict | None = None,
) -> dict:
    lines = cart_lines(products, customer)
    subtotal = round(sum(line["line_total"] for line in lines), 2)
    snapshot = {
        "request_type": request_type,
        "contact": contact_details or {},
        "order_metadata": order_metadata or {},
        "lines": lines,
        "subtotal": subtotal,
        "line_count": len(lines),
        "total_items": sum(line["quantity"] for line in lines),
        "final_pricing_note": FINAL_PRICING_NOTE,
    }
    if customer:
        snapshot["customer"] = customer_tablet_summary(customer)
    return snapshot


def build_warehouse_handoff_preview(
    products,
    quote_number: str,
    customer: dict | None = None,
    delivery_notes: str = "",
    contact_details: dict | None = None,
    order_metadata: dict | None = None,
) -> dict:
    snapshot = build_quote_snapshot(
        products,
        contact_details=contact_details,
        customer=customer,
        request_type="warehouse_handoff_preview",
        order_metadata=order_metadata,
    )
    customer_summary = snapshot.get("customer", {})
    contact = snapshot.get("contact", {})
    metadata = snapshot.get("order_metadata", {})
    return {
        "quote_number": quote_number,
        "customer_name": customer_summary.get("customer_name", "Public quote request"),
        "assigned_sales_rep": customer_summary.get("assigned_sales_rep", "Taylor"),
        "customer": customer_summary,
        "contact": contact,
        "order_metadata": metadata,
        "needed_by": metadata.get("needed_by") or contact.get("needed_by_date", ""),
        "delivery_window": metadata.get("delivery_window", ""),
        "delivery_notes": delivery_notes,
        "pull_ticket_status": "Preview only - Stage 3 WMS will create the pull ticket.",
        "warehouse_notes": [
            "Confirm stock before pick release.",
            "Validate freight, tax, and delivery route before customer payment.",
        ],
        "lines": snapshot["lines"],
        "line_count": snapshot["line_count"],
        "total_items": snapshot["total_items"],
        "subtotal": snapshot["subtotal"],
        "final_pricing_note": snapshot["final_pricing_note"],
    }


def render_quote_sidebar(products) -> None:
    lines = cart_lines(products)
    st.markdown("### Quote Cart")
    if not lines:
        st.caption("No products selected yet. Add catalog items to build a Pioneer quote request.")
        st.info(PIONEER_CONTACT_TEXT)
        return

    total_items = sum(line["quantity"] for line in lines)
    subtotal = cart_subtotal(products)
    st.metric("Items in quote cart", total_items)
    st.metric("Estimated subtotal", f"${subtotal:,.2f}")
    with st.expander("Cart preview", expanded=True):
        for line in lines[:4]:
            st.markdown(f"**{line['quantity']} x {line['name']}**  \n`{line['sku']}` | ${line['line_total']:,.2f}")
        if len(lines) > 4:
            st.caption(f"+ {len(lines) - 4} more line item(s)")
    st.caption(FINAL_PRICING_NOTE)
    st.caption(PAYMENT_TEXT)


def render_quote_cart_page(products) -> None:
    st.markdown('<div class="page-kicker">Quote Cart</div>', unsafe_allow_html=True)
    st.title("Build a Pioneer quote request")
    lines = cart_lines(products)
    if not lines:
        st.info("Your quote cart is empty. Add products from the catalog to start a Pioneer quote request.")
        st.caption(PIONEER_CONTACT_TEXT)
        return

    st.caption("Adjust quantities before submitting. Pioneer will confirm price, delivery, and payment details.")
    for line in lines:
        with st.container(border=True):
            cols = st.columns([4, 1.2, 1.2, 1])
            cols[0].markdown(f"**{line['name']}**  \n`{line['sku']}`")
            new_qty = cols[1].number_input("Qty", min_value=1, value=line["quantity"], step=1, key=f"cart_qty_{line['product_id']}")
            st.session_state["cart"][line["product_id"]] = int(new_qty)
            updated_line_total = round(line["unit_price"] * int(new_qty), 2)
            cols[2].markdown(f"**${line['unit_price']:,.2f} ea.**  \n${updated_line_total:,.2f}")
            if cols[3].button("Remove", key=f"remove_{line['product_id']}"):
                st.session_state["cart"].pop(line["product_id"], None)
                st.rerun()

    st.markdown(f"## Estimated subtotal: ${cart_subtotal(products):,.2f}")
    st.caption(FINAL_PRICING_NOTE)
    st.caption(PAYMENT_TEXT)


def _contact_form() -> dict | None:
    with st.form("public_quote_request_form"):
        st.markdown("### Contact and delivery details")
        cols = st.columns(2)
        company = cols[0].text_input("Company name *")
        contact = cols[1].text_input("Contact name *")
        email = cols[0].text_input("Email *")
        phone = cols[1].text_input("Phone *")
        needed_by_date = cols[0].date_input("Needed-by date", value=date.today())
        delivery_notes = st.text_area("Delivery notes", placeholder="Receiving hours, dock notes, delivery address, or rush timing.")
        quote_notes = st.text_area("Quote notes", placeholder="Anything Pioneer should know before confirming pricing and availability.")
        submitted = st.form_submit_button("Submit Quote Request", type="primary", width='stretch')
    if not submitted:
        return None
    missing = [label for label, value in [("company name", company), ("contact name", contact), ("email", email), ("phone", phone)] if not str(value).strip()]
    if missing:
        st.error("Please enter " + ", ".join(missing) + ".")
        return None
    return {
        "company_name": company.strip(),
        "contact_name": contact.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
        "needed_by_date": str(needed_by_date),
        "delivery_notes": delivery_notes.strip(),
        "quote_notes": quote_notes.strip(),
    }


def submit_quote(products, contact_details: dict, customer: dict | None = None) -> str:
    if not st.session_state.get("cart"):
        return ""
    quote_number = f"PIS-QR-{st.session_state.get('quote_counter', 1001)}"
    st.session_state["quote_counter"] = st.session_state.get("quote_counter", 1001) + 1
    quote_request = build_quote_snapshot(products, contact_details, customer)
    quote_request["quote_number"] = quote_number
    st.session_state.setdefault("quote_requests", []).append(quote_request)
    st.session_state["cart"] = {}
    st.session_state["last_quote_number"] = quote_number
    return quote_number


def render_request_quote_page(products) -> None:
    st.markdown('<div class="page-kicker">Request Quote</div>', unsafe_allow_html=True)
    st.title("Submit a quote request")
    if st.session_state.get("last_quote_number"):
        st.success(CONFIRMATION_TEXT)
        st.markdown(f"### Quote request number: `{st.session_state['last_quote_number']}`")
        st.caption(PIONEER_CONTACT_TEXT)

    lines = cart_lines(products)
    if not lines:
        st.info("Your quote cart is empty. Add catalog products before submitting a quote request.")
        return

    st.markdown(f"### Quote cart subtotal: ${cart_subtotal(products):,.2f}")
    st.caption(FINAL_PRICING_NOTE)
    details = _contact_form()
    if details:
        submit_quote(products, details)
        st.rerun()
