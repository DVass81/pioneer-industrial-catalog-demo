from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    import streamlit as st
except Exception:  # pragma: no cover - lets non-Streamlit scripts use env vars only.
    st = None


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "demo_workflow.sqlite3"
SUPABASE_TABLE_ORDERS = "field_orders"
SUPABASE_TABLE_LINES = "field_order_lines"
SUPABASE_TABLE_EVENTS = "wms_ticket_events"


def utc_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _config_value(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value:
        return value
    if st is None:
        return default
    try:
        value = st.secrets.get(name, default)
    except Exception:
        return default
    return str(value or default)


def workflow_backend() -> str:
    return _config_value("WORKFLOW_BACKEND", "sqlite").strip().lower() or "sqlite"


def using_supabase() -> bool:
    return workflow_backend() == "supabase"


@lru_cache(maxsize=1)
def _supabase_client():
    url = _config_value("SUPABASE_URL").strip()
    key = _config_value("SUPABASE_SERVICE_ROLE_KEY").strip()
    if not url or not key:
        raise RuntimeError(
            "WORKFLOW_BACKEND is set to 'supabase', but SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY are not both configured in Streamlit Secrets."
        )
    try:
        from supabase import create_client
    except ImportError as exc:
        raise RuntimeError("The 'supabase' package is required for WORKFLOW_BACKEND='supabase'.") from exc
    return create_client(url, key)


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_workflow_store() -> None:
    if using_supabase():
        _supabase_client()
        return
    _init_sqlite_store()


def _init_sqlite_store() -> None:
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


def _loads(value: Any) -> Any:
    if isinstance(value, dict):
        return value
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


def _order_record(order: dict, lines: list[dict], status: str, now: str, created_at: str | None = None) -> dict:
    metadata = order.get("order_metadata", {}) or {}
    customer_payload = order.get("customer_metadata") if isinstance(order.get("customer_metadata"), dict) else {}
    if not customer_payload and isinstance(order.get("customer"), dict):
        customer_payload = order["customer"]
    contact_payload = order.get("contact") if isinstance(order.get("contact"), dict) else {}
    customer_name = str(order.get("customer_name") or customer_payload.get("customer_name") or order.get("customer") or "Demo customer")
    return {
        "order_number": str(order.get("order_number") or order.get("quote_number") or ""),
        "request_type": str(order.get("request_type", "tablet_warehouse_handoff")),
        "customer_name": customer_name,
        "customer_json": customer_payload if using_supabase() else _json(customer_payload),
        "contact_json": contact_payload if using_supabase() else _json(contact_payload),
        "created_by": str(metadata.get("created_by") or order.get("created_by") or "Taylor"),
        "needed_by": str(order.get("needed_by") or metadata.get("needed_by") or ""),
        "delivery_window": str(order.get("delivery_window") or metadata.get("delivery_window") or ""),
        "priority": _priority(order),
        "stage": str(metadata.get("stage") or order.get("stage") or ""),
        "delivery_notes": str(order.get("delivery_notes") or ""),
        "status": status,
        "assigned_to": str(order.get("assigned_to") or "Unassigned"),
        "route": str(order.get("route") or "Local route"),
        "dock": str(order.get("dock") or "Main dock"),
        "subtotal": float(order.get("subtotal", 0) or 0),
        "line_count": int(order.get("line_count") or len(lines)),
        "total_items": int(order.get("total_items") or sum(int(line.get("quantity", 0) or 0) for line in lines)),
        "created_at": created_at or now,
        "updated_at": now,
    }


def _line_record(order_number: str, line: dict) -> dict:
    short_quantity = _line_short_quantity(line)
    return {
        "order_number": order_number,
        "product_id": str(line.get("product_id", "")),
        "sku": str(line.get("sku", line.get("product_id", ""))),
        "name": str(line.get("name", line.get("product_name", line.get("product_id", "")))),
        "category": str(line.get("category", "")),
        "manufacturer": str(line.get("manufacturer", "")),
        "manufacturer_part_number": str(line.get("manufacturer_part_number", "")),
        "warehouse_location": str(line.get("warehouse_location", "")),
        "lead_time": str(line.get("lead_time", "")),
        "available_stock": int(line.get("available_stock", 0) or 0),
        "reorder_point": int(line.get("reorder_point", 0) or 0),
        "quantity": int(line.get("quantity", 0) or 0),
        "unit_price": float(line.get("unit_price", 0) or 0),
        "line_total": float(line.get("line_total", 0) or 0),
        "short_quantity": short_quantity,
        "pick_status": _line_pick_status(line),
        "quote_note": str(line.get("quote_note", "")),
        "substitution_preference": str(line.get("substitution_preference", "")),
    }


def save_handoff_order(order: dict, event_type: str = "submitted") -> None:
    if using_supabase():
        _save_handoff_order_supabase(order, event_type)
    else:
        _save_handoff_order_sqlite(order, event_type)


def _save_handoff_order_sqlite(order: dict, event_type: str) -> None:
    _init_sqlite_store()
    lines = list(order.get("lines", []))
    short_lines = sum(1 for line in lines if _line_short_quantity(line) > 0)
    order_number = str(order.get("order_number") or order.get("quote_number") or "")
    if not order_number:
        raise ValueError("Order payload needs an order_number or quote_number.")

    status = str(order.get("status") or ("Exception" if short_lines else "New"))
    now = utc_now()
    with connect() as conn:
        existing = conn.execute("SELECT created_at FROM field_orders WHERE order_number = ?", (order_number,)).fetchone()
        created_at = existing["created_at"] if existing else now
        record = _order_record(order, lines, status, now, created_at)
        conn.execute(
            """
            INSERT OR REPLACE INTO field_orders (
                order_number, request_type, customer_name, customer_json, contact_json, created_by,
                needed_by, delivery_window, priority, stage, delivery_notes, status, assigned_to,
                route, dock, subtotal, line_count, total_items, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(record[column] for column in [
                "order_number", "request_type", "customer_name", "customer_json", "contact_json", "created_by",
                "needed_by", "delivery_window", "priority", "stage", "delivery_notes", "status", "assigned_to",
                "route", "dock", "subtotal", "line_count", "total_items", "created_at", "updated_at",
            ]),
        )
        conn.execute("DELETE FROM field_order_lines WHERE order_number = ?", (order_number,))
        for line in lines:
            line_record = _line_record(order_number, line)
            conn.execute(
                """
                INSERT INTO field_order_lines (
                    order_number, product_id, sku, name, category, manufacturer, manufacturer_part_number,
                    warehouse_location, lead_time, available_stock, reorder_point, quantity, unit_price,
                    line_total, short_quantity, pick_status, quote_note, substitution_preference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(line_record[column] for column in [
                    "order_number", "product_id", "sku", "name", "category", "manufacturer", "manufacturer_part_number",
                    "warehouse_location", "lead_time", "available_stock", "reorder_point", "quantity", "unit_price",
                    "line_total", "short_quantity", "pick_status", "quote_note", "substitution_preference",
                ]),
            )
        conn.execute(
            "INSERT INTO wms_ticket_events (order_number, event_type, message, created_at) VALUES (?, ?, ?, ?)",
            (order_number, event_type, f"{order_number} {event_type}", now),
        )


def _save_handoff_order_supabase(order: dict, event_type: str) -> None:
    client = _supabase_client()
    lines = list(order.get("lines", []))
    short_lines = sum(1 for line in lines if _line_short_quantity(line) > 0)
    order_number = str(order.get("order_number") or order.get("quote_number") or "")
    if not order_number:
        raise ValueError("Order payload needs an order_number or quote_number.")

    status = str(order.get("status") or ("Exception" if short_lines else "New"))
    now = utc_now()
    existing = client.table(SUPABASE_TABLE_ORDERS).select("created_at").eq("order_number", order_number).limit(1).execute().data
    created_at = existing[0]["created_at"] if existing else now
    client.table(SUPABASE_TABLE_ORDERS).upsert(_order_record(order, lines, status, now, created_at), on_conflict="order_number").execute()
    client.table(SUPABASE_TABLE_LINES).delete().eq("order_number", order_number).execute()
    line_records = [_line_record(order_number, line) for line in lines]
    if line_records:
        client.table(SUPABASE_TABLE_LINES).insert(line_records).execute()
    client.table(SUPABASE_TABLE_EVENTS).insert(
        {"order_number": order_number, "event_type": event_type, "message": f"{order_number} {event_type}", "created_at": now}
    ).execute()


def list_wms_tickets() -> list[dict]:
    return _list_wms_tickets_supabase() if using_supabase() else _list_wms_tickets_sqlite()


def _ticket_from_order(order_row: dict, line_rows: list[dict]) -> dict:
    ticket = dict(order_row)
    ticket["customer"] = ticket.pop("customer_name")
    ticket["customer_metadata"] = _loads(ticket.pop("customer_json"))
    ticket["contact"] = _loads(ticket.pop("contact_json"))
    ticket["lines"] = [dict(line) for line in line_rows]
    return ticket


def _list_wms_tickets_sqlite() -> list[dict]:
    _init_sqlite_store()
    with connect() as conn:
        order_rows = conn.execute("SELECT * FROM field_orders ORDER BY updated_at DESC").fetchall()
        tickets = []
        for order_row in order_rows:
            line_rows = conn.execute(
                "SELECT * FROM field_order_lines WHERE order_number = ? ORDER BY id",
                (order_row["order_number"],),
            ).fetchall()
            tickets.append(_ticket_from_order(dict(order_row), [dict(line) for line in line_rows]))
        return tickets


def _list_wms_tickets_supabase() -> list[dict]:
    client = _supabase_client()
    order_rows = client.table(SUPABASE_TABLE_ORDERS).select("*").order("updated_at", desc=True).execute().data or []
    tickets = []
    for order_row in order_rows:
        line_rows = (
            client.table(SUPABASE_TABLE_LINES)
            .select("*")
            .eq("order_number", order_row["order_number"])
            .order("id")
            .execute()
            .data
            or []
        )
        tickets.append(_ticket_from_order(order_row, line_rows))
    return tickets


def update_wms_ticket(order_number: str, status: str, assigned_to: str, dock: str) -> None:
    if using_supabase():
        _update_wms_ticket_supabase(order_number, status, assigned_to, dock)
    else:
        _update_wms_ticket_sqlite(order_number, status, assigned_to, dock)


def _update_wms_ticket_sqlite(order_number: str, status: str, assigned_to: str, dock: str) -> None:
    _init_sqlite_store()
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


def _update_wms_ticket_supabase(order_number: str, status: str, assigned_to: str, dock: str) -> None:
    client = _supabase_client()
    now = utc_now()
    client.table(SUPABASE_TABLE_ORDERS).update(
        {"status": status, "assigned_to": assigned_to, "dock": dock, "updated_at": now}
    ).eq("order_number", order_number).execute()
    client.table(SUPABASE_TABLE_EVENTS).insert(
        {
            "order_number": order_number,
            "event_type": "status_update",
            "message": f"Status set to {status}; picker {assigned_to}; dock {dock}",
            "created_at": now,
        }
    ).execute()


def ticket_count() -> int:
    return _ticket_count_supabase() if using_supabase() else _ticket_count_sqlite()


def _ticket_count_sqlite() -> int:
    _init_sqlite_store()
    with connect() as conn:
        return int(conn.execute("SELECT COUNT(*) AS count FROM field_orders").fetchone()["count"])


def _ticket_count_supabase() -> int:
    client = _supabase_client()
    response = client.table(SUPABASE_TABLE_ORDERS).select("order_number", count="exact").limit(1).execute()
    return int(response.count or 0)


def recent_events(limit: int = 8) -> list[dict]:
    return _recent_events_supabase(limit) if using_supabase() else _recent_events_sqlite(limit)


def _recent_events_sqlite(limit: int = 8) -> list[dict]:
    _init_sqlite_store()
    with connect() as conn:
        rows = conn.execute(
            "SELECT order_number, event_type, message, created_at FROM wms_ticket_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def _recent_events_supabase(limit: int = 8) -> list[dict]:
    client = _supabase_client()
    rows = (
        client.table(SUPABASE_TABLE_EVENTS)
        .select("order_number,event_type,message,created_at")
        .order("id", desc=True)
        .limit(limit)
        .execute()
        .data
        or []
    )
    return [dict(row) for row in rows]