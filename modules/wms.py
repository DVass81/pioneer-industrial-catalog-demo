from __future__ import annotations

from datetime import date, timedelta
from html import escape

import pandas as pd
import streamlit as st

from modules.cart import effective_price
from modules.workflow_store import (
    init_workflow_store,
    list_wms_tickets,
    recent_events,
    save_handoff_order,
    ticket_count,
    update_wms_ticket,
)


WMS_STATUSES = ["New", "Released", "Picking", "Staged", "Exception", "Ready for delivery"]
PRIORITY_ORDER = {"Rush": 0, "Today": 1, "Standard": 2}


def money(value: float) -> str:
    return f"${float(value):,.2f}"


def apply_wms_styles() -> None:
    st.markdown(
        """
        <style>
        .wms-workbench { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); margin-bottom: .9rem; }
        .wms-ticket { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); margin-bottom: .85rem; }
        .wms-ticket h3 { margin: 0 0 .3rem; font-size: 1.05rem; }
        .wms-ticket-meta { color: #59615b; font-size: .88rem; line-height: 1.35; }
        .wms-badge { display: inline-block; border-radius: 999px; padding: .22rem .55rem; margin: .1rem .25rem .1rem 0; font-size: .72rem; font-weight: 900; }
        .wms-badge-rush { background: #f7ead6; color: #8a5a19; }
        .wms-badge-standard { background: #eef0ec; color: #343936; }
        .wms-badge-ready { background: #e8f1e5; color: #2f6a42; }
        .wms-badge-exception { background: #fbe1dc; color: #8a2d1d; }
        .wms-line-note { border-left: 4px solid #4c6444; border-radius: 6px; padding: .55rem .7rem; background: #f8faf7; margin: .4rem 0; color: #252826; }
        @media (max-width: 900px) { .wms-ticket { padding: .8rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _product_lookup(products: pd.DataFrame, product_id: str) -> dict:
    match = products.loc[products["product_id"] == product_id]
    if match.empty:
        return {}
    return match.iloc[0].to_dict()


def build_wms_line(
    products: pd.DataFrame,
    product_id: str,
    quantity: int,
    note: str = "",
    substitution: str = "Use closest stocked equivalent",
) -> dict:
    row = _product_lookup(products, product_id)
    unit_price = effective_price(row) if row else 0
    available = int(row.get("quantity_in_stock", 0) or 0)
    reorder_point = int(row.get("reorder_point", 0) or 0)
    short = max(0, int(quantity) - available)
    return {
        "product_id": product_id,
        "sku": row.get("sku", row.get("SKU / Pioneer part number", product_id)),
        "name": row.get("product_name", product_id),
        "category": row.get("category", ""),
        "manufacturer": row.get("manufacturer", ""),
        "manufacturer_part_number": row.get("manufacturer_part_number", ""),
        "warehouse_location": row.get("warehouse_location", ""),
        "lead_time": row.get("lead_time", ""),
        "available_stock": available,
        "reorder_point": reorder_point,
        "quantity": int(quantity),
        "unit_price": unit_price,
        "line_total": round(unit_price * int(quantity), 2),
        "short_quantity": short,
        "pick_status": "Exception" if short else "Ready",
        "quote_note": note,
        "substitution_preference": substitution,
    }


def _ticket(ticket_id: str, customer: str, priority: str, needed_by: date, delivery_window: str, lines: list[dict], notes: str) -> dict:
    short_lines = sum(1 for line in lines if line["short_quantity"] > 0)
    status = "Exception" if short_lines else "New"
    return {
        "order_number": ticket_id,
        "request_type": "seeded_wms_demo_ticket",
        "customer": customer,
        "customer_metadata": {"customer_name": customer},
        "contact": {},
        "order_metadata": {
            "created_by": "WMS demo seed",
            "needed_by": str(needed_by),
            "delivery_window": delivery_window,
            "priority": priority,
            "stage": "Stage 3 WMS demo",
        },
        "needed_by": str(needed_by),
        "delivery_window": delivery_window,
        "priority": priority,
        "status": status,
        "assigned_to": "Unassigned",
        "route": "Local route",
        "dock": "Main dock",
        "delivery_notes": notes,
        "lines": lines,
        "line_count": len(lines),
        "total_items": sum(line["quantity"] for line in lines),
        "subtotal": round(sum(line["line_total"] for line in lines), 2),
    }


@st.cache_data(show_spinner=False)
def seed_wms_tickets(products: pd.DataFrame) -> list[dict]:
    today = date.today()
    return [
        _ticket(
            "PIS-WMS-3001",
            "ICC International",
            "Rush",
            today,
            "Will call",
            [
                build_wms_line(products, "RPL-0024", 12, "Customer asked for respirator substitution call before pick."),
                build_wms_line(products, "RPL-0006", 18),
                build_wms_line(products, "RPL-0089", 6),
            ],
            "Taylor flagged as jobsite replenishment. Hold at counter when staged.",
        ),
        _ticket(
            "PIS-WMS-3002",
            "Liberty Manufacturing",
            "Today",
            today + timedelta(days=1),
            "Morning route",
            [
                build_wms_line(products, "RPL-0003", 4),
                build_wms_line(products, "RPL-0095", 3),
            ],
            "Deliver to receiving door 2.",
        ),
        _ticket(
            "PIS-WMS-3003",
            "Smoky Mountain Fabrication",
            "Standard",
            today + timedelta(days=3),
            "Next route",
            [
                build_wms_line(products, "RPL-0004", 2, "Quote required item. Confirm before release.", "Call customer before substituting"),
                build_wms_line(products, "RPL-0090", 8),
            ],
            "Combine with next scheduled route if fully picked.",
        ),
    ]


def sync_tickets() -> list[dict]:
    tickets = list_wms_tickets()
    st.session_state["wms_tickets"] = tickets
    return tickets


def init_wms_state(products: pd.DataFrame) -> None:
    init_workflow_store()
    if ticket_count() == 0:
        for ticket in seed_wms_tickets(products):
            save_handoff_order(ticket, event_type="seeded")
    sync_tickets()
    st.session_state.setdefault("wms_activity", [])


def status_badge(status: str, priority: str = "Standard") -> str:
    if status == "Exception":
        css = "wms-badge wms-badge-exception"
    elif status in {"Staged", "Ready for delivery"}:
        css = "wms-badge wms-badge-ready"
    elif priority == "Rush":
        css = "wms-badge wms-badge-rush"
    else:
        css = "wms-badge wms-badge-standard"
    return f'<span class="{css}">{escape(status)}</span>'


def filtered_tickets() -> list[dict]:
    tickets = sync_tickets()
    return sorted(tickets, key=lambda ticket: (PRIORITY_ORDER.get(ticket["priority"], 9), ticket["needed_by"], ticket["order_number"]))


def render_wms_sidebar(products: pd.DataFrame) -> None:
    tickets = sync_tickets()
    open_tickets = [ticket for ticket in tickets if ticket["status"] != "Ready for delivery"]
    exception_count = sum(1 for ticket in open_tickets if ticket["status"] == "Exception")
    low_stock = int((products["quantity_in_stock"] <= products["reorder_point"]).sum())
    st.sidebar.image("assets/pioneer_logo.png", width="stretch")
    st.sidebar.markdown('<div class="sidebar-brand">Pioneer WMS</div>', unsafe_allow_html=True)
    st.sidebar.metric("Open tickets", len(open_tickets))
    st.sidebar.metric("Exceptions", exception_count)
    st.sidebar.metric("Reorder alerts", low_stock)
    if st.sidebar.button("Refresh queue", width="stretch"):
        sync_tickets()
        st.rerun()
    st.sidebar.caption("Stage 3 demo uses the shared local workflow store. Streamlit Cloud needs an external database for cross-app persistence.")


def render_dashboard(products: pd.DataFrame) -> None:
    tickets = sync_tickets()
    open_tickets = [ticket for ticket in tickets if ticket["status"] != "Ready for delivery"]
    exception_count = sum(1 for ticket in open_tickets if ticket["status"] == "Exception")
    staged_count = sum(1 for ticket in tickets if ticket["status"] in {"Staged", "Ready for delivery"})
    low_stock = products.loc[products["quantity_in_stock"] <= products["reorder_point"]]

    st.markdown('<div class="page-kicker">Warehouse Execution</div>', unsafe_allow_html=True)
    st.title("WMS command center")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open pull tickets", len(open_tickets))
    c2.metric("Exception tickets", exception_count)
    c3.metric("Staged / ready", staged_count)
    c4.metric("Low-stock SKUs", len(low_stock))

    st.markdown(
        """
        <div class="wms-workbench">
            <h3>Today</h3>
            <p>Release clean tickets, work stock exceptions, stage completed orders, and keep reorder-risk items visible before the route leaves.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    queue_rows = [
        {
            "Ticket": ticket["order_number"],
            "Customer": ticket["customer"],
            "Priority": ticket["priority"],
            "Status": ticket["status"],
            "Needed by": ticket["needed_by"],
            "Lines": ticket["line_count"],
            "Pieces": ticket["total_items"],
        }
        for ticket in filtered_tickets()[:8]
    ]
    st.dataframe(queue_rows, width="stretch", hide_index=True)

    events = recent_events()
    if events:
        st.markdown("### Recent ticket activity")
        st.dataframe(
            [
                {
                    "Time": event["created_at"],
                    "Ticket": event["order_number"],
                    "Event": event["event_type"],
                    "Message": event["message"],
                }
                for event in events
            ],
            width="stretch",
            hide_index=True,
        )


def render_pick_queue() -> None:
    st.markdown('<div class="page-kicker">Pick Queue</div>', unsafe_allow_html=True)
    st.title("Pull tickets")
    status_filter = st.multiselect("Status", WMS_STATUSES, default=["New", "Released", "Picking", "Exception"])
    search = st.text_input("Search tickets", placeholder="Ticket, customer, SKU, product")
    tickets = filtered_tickets()
    if status_filter:
        tickets = [ticket for ticket in tickets if ticket["status"] in status_filter]
    if search:
        needle = search.lower()
        tickets = [
            ticket
            for ticket in tickets
            if needle in (ticket["order_number"] + " " + ticket["customer"] + " " + " ".join(line["sku"] + " " + line["name"] for line in ticket["lines"])).lower()
        ]

    for ticket in tickets:
        render_ticket(ticket)
    if not tickets:
        st.info("No tickets match the current filters.")


def render_ticket(ticket: dict) -> None:
    st.markdown(
        f"""
        <div class="wms-ticket">
            <h3>{escape(ticket["order_number"])} | {escape(ticket["customer"])}</h3>
            <div>{status_badge(ticket["status"], ticket["priority"])}<span class="wms-badge wms-badge-standard">{escape(ticket["priority"])}</span></div>
            <div class="wms-ticket-meta">Needed by {escape(ticket["needed_by"])} | {escape(ticket["delivery_window"])} | {ticket["line_count"]} lines | {ticket["total_items"]} pieces | {escape(ticket["route"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1.1, 1.1, 2])
    picker_options = ["Unassigned", "Taylor", "Warehouse A", "Warehouse B", "Counter"]
    current_status = ticket["status"] if ticket["status"] in WMS_STATUSES else "New"
    new_status = c1.selectbox("Status", WMS_STATUSES, index=WMS_STATUSES.index(current_status), key=f"wms_status_{ticket['order_number']}")
    current_picker = ticket.get("assigned_to", "Unassigned")
    if current_picker not in picker_options:
        current_picker = "Unassigned"
    assignee = c2.selectbox("Picker", picker_options, index=picker_options.index(current_picker), key=f"wms_picker_{ticket['order_number']}")
    dock_note = c3.text_input("Dock / route note", value=ticket.get("dock", ""), key=f"wms_dock_{ticket['order_number']}")
    if new_status != ticket["status"] or assignee != ticket.get("assigned_to") or dock_note != ticket.get("dock"):
        update_wms_ticket(ticket["order_number"], new_status, assignee, dock_note)
        ticket["status"] = new_status
        ticket["assigned_to"] = assignee
        ticket["dock"] = dock_note
        st.session_state["wms_activity"].append(f"{ticket['order_number']} updated to {new_status}")

    rows = [
        {
            "Pick": line["pick_status"],
            "Bin": line["warehouse_location"],
            "SKU": line["sku"],
            "Product": line["name"],
            "Qty": line["quantity"],
            "On hand": line["available_stock"],
            "Short": line["short_quantity"],
            "Lead time": line["lead_time"],
            "Substitution": line["substitution_preference"],
        }
        for line in ticket["lines"]
    ]
    st.dataframe(rows, width="stretch", hide_index=True)
    for line in ticket["lines"]:
        if line.get("quote_note") or line.get("short_quantity"):
            note = line.get("quote_note") or "Stock exception requires buyer review."
            st.markdown(f'<div class="wms-line-note"><strong>{escape(line["sku"])}</strong>: {escape(note)}</div>', unsafe_allow_html=True)
    if ticket.get("delivery_notes"):
        st.caption(f"Field notes: {ticket['delivery_notes']}")


def render_inventory_control(products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Inventory Control</div>', unsafe_allow_html=True)
    st.title("Stock, bins, and reorder risk")
    categories = ["All"] + sorted(products["category"].dropna().astype(str).unique())
    c1, c2, c3 = st.columns([1.4, 1, 1])
    search = c1.text_input("Search inventory", placeholder="SKU, product, bin, manufacturer")
    category = c2.selectbox("Category", categories)
    risk_only = c3.toggle("Reorder risk only", value=True)

    filtered = products.copy()
    if category != "All":
        filtered = filtered.loc[filtered["category"] == category]
    if risk_only:
        filtered = filtered.loc[filtered["quantity_in_stock"] <= filtered["reorder_point"]]
    if search:
        haystack = (
            filtered["product_name"].astype(str)
            + " "
            + filtered["sku"].astype(str)
            + " "
            + filtered["warehouse_location"].astype(str)
            + " "
            + filtered["manufacturer"].astype(str)
        ).str.lower()
        filtered = filtered.loc[haystack.str.contains(search.lower(), regex=False)]

    rows = filtered.assign(
        status=filtered.apply(lambda row: "Reorder" if int(row["quantity_in_stock"]) <= int(row["reorder_point"]) else "OK", axis=1),
        gap=filtered["quantity_in_stock"] - filtered["reorder_point"],
    )[
        ["sku", "product_name", "category", "warehouse_location", "quantity_in_stock", "reorder_point", "gap", "lead_time", "status"]
    ].rename(
        columns={
            "sku": "SKU",
            "product_name": "Product",
            "category": "Category",
            "warehouse_location": "Bin",
            "quantity_in_stock": "On hand",
            "reorder_point": "Reorder point",
            "gap": "Stock gap",
            "lead_time": "Lead time",
            "status": "Status",
        }
    )
    st.caption(f"{len(rows)} SKU(s)")
    st.dataframe(rows, width="stretch", hide_index=True)


def render_receiving(products: pd.DataFrame) -> None:
    st.markdown('<div class="page-kicker">Receiving / Replenishment</div>', unsafe_allow_html=True)
    st.title("Inbound and replenishment workbench")
    low_stock = products.loc[products["quantity_in_stock"] <= products["reorder_point"]].copy()
    low_stock["suggested_order_qty"] = (low_stock["reorder_point"] * 2 - low_stock["quantity_in_stock"]).clip(lower=1)
    c1, c2, c3 = st.columns(3)
    c1.metric("Reorder candidates", len(low_stock))
    c2.metric("Fastest lead time", str(low_stock["lead_time"].iloc[0]) if not low_stock.empty else "None")
    c3.metric("Open exceptions", sum(1 for ticket in sync_tickets() if ticket["status"] == "Exception"))

    rows = low_stock.head(30)[
        ["sku", "product_name", "warehouse_location", "quantity_in_stock", "reorder_point", "suggested_order_qty", "lead_time"]
    ].rename(
        columns={
            "sku": "SKU",
            "product_name": "Product",
            "warehouse_location": "Bin",
            "quantity_in_stock": "On hand",
            "reorder_point": "Reorder point",
            "suggested_order_qty": "Suggested buy",
            "lead_time": "Lead time",
        }
    )
    st.dataframe(rows, width="stretch", hide_index=True)
    st.caption("Receiving is demo-mode only. Future build should persist receipts, lot/bin moves, cycle counts, and purchasing handoffs.")