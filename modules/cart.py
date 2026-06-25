from __future__ import annotations

import streamlit as st


FINAL_PRICING_NOTE = "Final pricing confirmed by Pioneer sales representative."
PIONEER_CONTACT_TEXT = "Questions or rush needs? Contact your Pioneer sales representative or Pioneer Industrial Sales for help."
PAYMENT_TEXT = "Payment is completed after Pioneer confirms pricing, availability, freight, and delivery details."
CONFIRMATION_TEXT = (
    "Your quote request has been sent to Pioneer Industrial Sales. A customer service representative "
    "will contact you with confirmed pricing, delivery options, and payment instructions."
)


def _row_value(row, *keys, default=None):
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return default


def effective_price(row, customer: dict) -> float:
    base = float(_row_value(row, "customer_specific_price", "price", default=0) or 0)
    multiplier = float(customer.get("pricing_multiplier", customer.get("discount_multiplier", 1.0)) or 1.0)
    return round(base * multiplier, 2)


def add_to_cart(product_id: str, quantity: int) -> None:
    quantity = max(1, int(quantity))
    cart = st.session_state.setdefault("cart", {})
    cart[product_id] = cart.get(product_id, 0) + quantity
    st.toast("Added to quote cart", icon="OK")


def cart_lines(products, customer: dict) -> list[dict]:
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
                "quantity": int(quantity),
                "unit_price": unit_price,
                "line_total": round(unit_price * int(quantity), 2),
            }
        )
    return lines


def cart_subtotal(products, customer: dict) -> float:
    return round(sum(line["line_total"] for line in cart_lines(products, customer)), 2)


def render_quote_sidebar(products, customer: dict) -> None:
    lines = cart_lines(products, customer)
    st.markdown("### Quote Cart")
    st.caption(customer.get("customer_name", "Selected customer"))
    if not lines:
        st.caption("No products selected yet. Add catalog items to build a Pioneer quote request.")
        st.info(PIONEER_CONTACT_TEXT)
        return

    total_items = sum(line["quantity"] for line in lines)
    subtotal = cart_subtotal(products, customer)
    st.metric("Items in quote cart", total_items)
    st.metric("Estimated subtotal", f"${subtotal:,.2f}")
    with st.expander("Cart preview", expanded=True):
        for line in lines[:4]:
            st.markdown(
                f"**{line['quantity']} x {line['name']}**  \n"
                f"`{line['sku']}` | ${line['line_total']:,.2f}"
            )
        if len(lines) > 4:
            st.caption(f"+ {len(lines) - 4} more line item(s)")
    st.caption(FINAL_PRICING_NOTE)
    st.caption(PAYMENT_TEXT)
    if st.button("Submit Quote Request", use_container_width=True, key="sidebar_submit"):
        submit_quote(products, customer)
        st.rerun()


def render_quote_cart_page(products, customer: dict) -> None:
    st.markdown('<div class="page-kicker">Quote Cart</div>', unsafe_allow_html=True)
    st.title("Build a Pioneer quote request")
    st.caption(f"Selected customer: {customer.get('customer_name', 'Demo customer')}")

    lines = cart_lines(products, customer)
    if not lines:
        st.info("Your quote cart is empty. Add products from the catalog to start a Pioneer quote request.")
        st.caption(PIONEER_CONTACT_TEXT)
        return

    st.caption("Adjust quantities before submitting. Pioneer will confirm price, delivery, and payment details.")
    for line in lines:
        with st.container(border=True):
            cols = st.columns([4, 1.2, 1.2, 1])
            cols[0].markdown(f"**{line['name']}**  \n`{line['sku']}`")
            new_qty = cols[1].number_input(
                "Qty",
                min_value=1,
                value=line["quantity"],
                step=1,
                key=f"cart_qty_{line['product_id']}",
            )
            st.session_state["cart"][line["product_id"]] = int(new_qty)
            updated_line_total = round(line["unit_price"] * int(new_qty), 2)
            cols[2].markdown(f"**${line['unit_price']:,.2f} ea.**  \n${updated_line_total:,.2f}")
            if cols[3].button("Remove", key=f"remove_{line['product_id']}"):
                st.session_state["cart"].pop(line["product_id"], None)
                st.rerun()

    st.markdown(f"## Estimated subtotal: ${cart_subtotal(products, customer):,.2f}")
    st.caption(FINAL_PRICING_NOTE)
    st.caption(PAYMENT_TEXT)
    cols = st.columns(2)
    if cols[0].button("Submit Quote Request", type="primary", use_container_width=True, key="cart_submit"):
        submit_quote(products, customer)
        st.rerun()
    cols[1].info("Pioneer will follow up with confirmed pricing, payment instructions, and delivery options.")


def submit_quote(products, customer: dict) -> str:
    if not st.session_state.get("cart"):
        return ""
    quote_number = f"PIS-QR-{st.session_state.get('quote_counter', 1001)}"
    st.session_state["quote_counter"] = st.session_state.get("quote_counter", 1001) + 1
    st.session_state.setdefault("quote_requests", []).append(
        {
            "quote_number": quote_number,
            "customer": customer.get("customer_name", "Demo customer"),
            "lines": cart_lines(products, customer),
            "subtotal": cart_subtotal(products, customer),
        }
    )
    st.session_state["cart"] = {}
    st.session_state["last_quote_number"] = quote_number
    return quote_number


def render_request_quote_page(products, customer: dict) -> None:
    st.markdown('<div class="page-kicker">Request Quote</div>', unsafe_allow_html=True)
    st.title("Submit a quote request")

    if st.session_state.get("last_quote_number"):
        st.success(CONFIRMATION_TEXT)
        st.markdown(f"### Quote request number: `{st.session_state['last_quote_number']}`")
        st.caption(PIONEER_CONTACT_TEXT)
    else:
        st.info("Review your cart and submit when ready.")

    render_quote_cart_page(products, customer)