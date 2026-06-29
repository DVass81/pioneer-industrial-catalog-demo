from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "demo_workflow.sqlite3"


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_workflow_store() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS field_orders (
                order_number TEXT PRIMARY KEY,
                request_type TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_json TEXT NOT NULL DEFAULT '{}',
                contact_json TEXT NOT NULL DEFAULT '{}',
                created_by TEXT NOT NULL DEFAULT 'Taylor',
                needed_by TEXT NOT NULL DEFAULT '',
                delivery_window TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Standard',
                stage TEXT NOT NULL DEFAULT '',
                delivery_notes TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'New',
                assigned_to TEXT NOT NULL DEFAULT 'Unassigned',
                route TEXT NOT NULL DEFAULT 'Local route',
                dock TEXT NOT NULL DEFAULT 'Main dock',
                subtotal REAL NOT NULL DEFAULT 0,
                line_count INTEGER NOT NULL DEFAULT 0,
                total_items INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS field_order_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL REFERENCES field_orders(order_number) ON DELETE CASCADE,
                product_id TEXT NOT NULL,
                sku TEXT NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                manufacturer TEXT NOT NULL DEFAULT '',
                manufacturer_part_number TEXT NOT NULL DEFAULT '',
                warehouse_location TEXT NOT NULL DEFAULT '',
                lead_time TEXT NOT NULL DEFAULT '',
                available_stock INTEGER NOT NULL DEFAULT 0,
                reorder_point INTEGER NOT NULL DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL NOT NULL DEFAULT 0,
                line_total REAL NOT NULL DEFAULT 0,
                short_quantity INTEGER NOT NULL DEFAULT 0,
                pick_status TEXT NOT NULL DEFAULT 'Ready',
                quote_note TEXT NOT NULL DEFAULT '',
                substitution_preference TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS wms_ticket_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_number TEXT NOT NULL REFERENCES field_orders(order_number) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def _json(value: Any) -> str:
    return json.dumps(value or {}, sort_keys=True)


def _loads(value: str) -> Any:
    try:
        return json.loads(value or "{}")
    except json.JSONDecodeError:
        return {}


def _priority(order: dict) -> str:
    metadata = order.get("order_metadata", {}) or {}
    raw = str(order.get("priority") or metadata.get("priority") or "Standard")
    if "rush" in raw.lower():
        return "Rush"
    if "today" in raw.lower():
        return "Today"
    return "Standard"


def _line_short_quantity(line: dict) -> int:
    if "short_quantity" in line:
        return max(0, int(line.get("short_quantity") or 0))
    available = int(line.get("available_stock", 0) or 0)
    quantity = int(line.get("quantity", 0) or 0)
    return max(0, quantity - available)


def _line_pick_status(line: dict) -> str:
    if line.get("pick_status"):
        return str(line["pick_status"])
    return "Exception" if _line_short_quantity(line) else "Ready"


def save_handoff_order(order: dict, event_type: str = "submitted") -> None:
    init_workflow_store()
    lines = list(order.get("lines", []))
    short_lines = sum(1 for line in lines if _line_short_quantity(line) > 0)
    metadata = order.get("order_metadata", {}) or {}
    order_number = str(order.get("order_number") or order.get("quote_number") or "")
    if not order_number:
        raise ValueError("Order payload needs an order_number or quote_number.")

    status = str(order.get("status") or ("Exception" if short_lines else "New"))
    now = utc_now()
    customer_json = order.get("customer_metadata") or order.get("customer") or {}
    customer_name = str(order.get("customer") or customer_json.get("customer_name") or order.get("customer_name") or "Demo customer")
    contact_json = order.get("contact") or {}
    line_count = int(order.get("line_count") or len(lines))
    total_items = int(order.get("total_items") or sum(int(line.get("quantity", 0) or 0) for line in lines))
    subtotal = float(order.get("subtotal", 0) or 0)

    with connect() as conn:
        existing = conn.execute("SELECT order_number FROM field_orders WHERE order_number = ?", (order_number,)).fetchone()
        created_at = now
        if existing:
            created_at = conn.execute("SELECT created_at FROM field_orders WHERE order_number = ?", (order_number,)).fetchone()["created_at"]
        conn.execute(
            """
            INSERT OR REPLACE INTO field_orders (
                order_number, request_type, customer_name, customer_json, contact_json, created_by,
                needed_by, delivery_window, priority, stage, delivery_notes, status, assigned_to,
                route, dock, subtotal, line_count, total_items, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order_number,
                str(order.get("request_type", "tablet_warehouse_handoff")),
                customer_name,
                _json(customer_json),
                _json(contact_json),
                str(metadata.get("created_by") or order.get("created_by") or "Taylor"),
                str(order.get("needed_by") or metadata.get("needed_by") or ""),
                str(order.get("delivery_window") or metadata.get("delivery_window") or ""),
                _priority(order),
                str(metadata.get("stage") or order.get("stage") or ""),
                str(order.get("delivery_notes") or ""),
                status,
                str(order.get("assigned_to") or "Unassigned"),
                str(order.get("route") or "Local route"),
                str(order.get("dock") or "Main dock"),
                subtotal,
                line_count,
                total_items,
                created_at,
                now,
            ),
        )
        conn.execute("DELETE FROM field_order_lines WHERE order_number = ?", (order_number,))
        for line in lines:
            short_quantity = _line_short_quantity(line)
            conn.execute(
                """
                INSERT INTO field_order_lines (
                    order_number, product_id, sku, name, category, manufacturer, manufacturer_part_number,
                    warehouse_location, lead_time, available_stock, reorder_point, quantity, unit_price,
                    line_total, short_quantity, pick_status, quote_note, substitution_preference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_number,
                    str(line.get("product_id", "")),
                    str(line.get("sku", line.get("product_id", ""))),
                    str(line.get("name", line.get("product_name", line.get("product_id", "")))),
                    str(line.get("category", "")),
                    str(line.get("manufacturer", "")),
                    str(line.get("manufacturer_part_number", "")),
                    str(line.get("warehouse_location", "")),
                    str(line.get("lead_time", "")),
                    int(line.get("available_stock", 0) or 0),
                    int(line.get("reorder_point", 0) or 0),
                    int(line.get("quantity", 0) or 0),
                    float(line.get("unit_price", 0) or 0),
                    float(line.get("line_total", 0) or 0),
                    short_quantity,
                    _line_pick_status(line),
                    str(line.get("quote_note", "")),
                    str(line.get("substitution_preference", "")),
                ),
            )
        conn.execute(
            "INSERT INTO wms_ticket_events (order_number, event_type, message, created_at) VALUES (?, ?, ?, ?)",
            (order_number, event_type, f"{order_number} {event_type}", now),
        )


def list_wms_tickets() -> list[dict]:
    init_workflow_store()
    with connect() as conn:
        order_rows = conn.execute("SELECT * FROM field_orders ORDER BY updated_at DESC").fetchall()
        tickets = []
        for order_row in order_rows:
            line_rows = conn.execute(
                "SELECT * FROM field_order_lines WHERE order_number = ? ORDER BY id",
                (order_row["order_number"],),
            ).fetchall()
            ticket = dict(order_row)
            ticket["customer"] = ticket.pop("customer_name")
            ticket["customer_metadata"] = _loads(ticket.pop("customer_json"))
            ticket["contact"] = _loads(ticket.pop("contact_json"))
            ticket["lines"] = [dict(line) for line in line_rows]
            tickets.append(ticket)
        return tickets


def update_wms_ticket(order_number: str, status: str, assigned_to: str, dock: str) -> None:
    init_workflow_store()
    now = utc_now()
    with connect() as conn:
        conn.execute(
            "UPDATE field_orders SET status = ?, assigned_to = ?, dock = ?, updated_at = ? WHERE order_number = ?",
            (status, assigned_to, dock, now, order_number),
        )
        conn.execute(
            "INSERT INTO wms_ticket_events (order_number, event_type, message, created_at) VALUES (?, ?, ?, ?)",
            (order_number, "status_update", f"Status set to {status}; picker {assigned_to}; dock {dock}", now),
        )


def ticket_count() -> int:
    init_workflow_store()
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS count FROM field_orders").fetchone()["count"])


def recent_events(limit: int = 8) -> list[dict]:
    init_workflow_store()
    with connect() as conn:
        rows = conn.execute(
            "SELECT order_number, event_type, message, created_at FROM wms_ticket_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]