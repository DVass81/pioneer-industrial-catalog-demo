# Pioneer Three-System Demo Guide

This demo is built as three Streamlit apps from one shared repository. They are separate deployed apps, but they use the same Pioneer branding, shared product/customer data, and compatible handoff structures.

## The Three Systems

### 1. Public Catalog

Entrypoint: `app.py`

Purpose: public-facing product browsing and quote request.

What it shows:

- Pioneer brand and service positioning.
- Product catalog browsing by category and search.
- Product detail pages with SKU, manufacturer part number, stock, lead time, bin/location, and image.
- Quote cart and public quote request confirmation.

Demo URL locally:

```powershell
streamlit run app.py --server.port 8501
```

Streamlit Cloud main file:

```text
app.py
```

### 2. Taylor Field Tablet

Entrypoint: `tablet_app.py`

Purpose: rep-facing workflow for Taylor during account visits, counter conversations, or guided replenishment.

What it shows:

- Demo customer selection.
- Account profile, payment terms, preferred categories, and customer notes.
- Account-aware recommendations and product lookup.
- Field quote/order builder with customer pricing, line notes, substitution preferences, needed-by date, and delivery window.
- Warehouse handoff preview that mirrors the future WMS ticket payload.

Demo URL locally:

```powershell
streamlit run tablet_app.py --server.port 8502
```

Streamlit Cloud main file:

```text
tablet_app.py
```

### 3. WMS / Warehouse Execution

Entrypoint: `wms_app.py`

Purpose: internal warehouse workflow for pull tickets, picking, stock exceptions, and replenishment visibility.

What it shows:

- Command center with open tickets, exceptions, staged tickets, and reorder-risk SKUs.
- Pick queue with ticket status, picker assignment, dock/route note, bin, SKU, quantity, on-hand stock, shortage, lead time, substitution preference, and line notes.
- Inventory control view for stock, bins, and reorder risk.
- Receiving/replenishment workbench with suggested buy quantities.

Demo URL locally:

```powershell
streamlit run wms_app.py --server.port 8504
```

Streamlit Cloud main file:

```text
wms_app.py
```

## Recommended Demo Flow

1. Start with the public catalog.
   Show how a customer can browse inventory, inspect product details, and submit a quote request without seeing private account data.

2. Move to Taylor's tablet app.
   Select `ICC International`, show account context, add a few recommended products, add a line note, choose a substitution preference, set a needed-by date, and send the order to warehouse preview.

3. Move to the WMS app.
   Click **Refresh queue**, open the command center, then the pick queue. Show how Taylor's submitted order appears alongside existing tickets, and how warehouse users see ticket priority, bin locations, stock exceptions, substitutions, and delivery notes.

4. Close with the system story.
   The catalog creates customer demand, Taylor's tablet captures account-specific field demand, and the WMS turns confirmed demand into warehouse work.

## How The Apps Work Together Today

The apps currently share:

- One GitHub repository.
- One Streamlit dependency set in `requirements.txt`.
- Shared Pioneer styling from `modules/styling.py`.
- Shared product data from `data/demo_products.csv`.
- Shared customer data for the tablet workflow from `data/demo_customers.csv`.
- A local shared workflow store at `data/demo_workflow.sqlite3`.
- A compatible handoff shape between the tablet order builder and the WMS ticket model.

When Taylor submits a field order from the tablet app, it is written to the shared workflow store. The WMS reads from the same store, so the order appears as a pull ticket after refreshing the WMS queue. WMS status, picker, and dock/route changes are written back as ticket events.

Important cloud note: separate Streamlit Cloud apps do not share local files or `st.session_state`. The SQLite store makes the local demo feel live. For deployed cross-app persistence, move the same tables to Supabase/Postgres or another hosted database.

## Shared Workflow Store

The local demo store uses these records:

- `field_orders`: order number, customer, contact, needed-by date, delivery window, notes, status, picker, route, dock, totals, and timestamps.
- `field_order_lines`: order number, product ID, SKU, product name, quantity, unit price, bin, lead time, stock, substitution preference, and line note.
- `wms_ticket_events`: order number, status changes, picker assignment, dock/route notes, submission events, and seed events.

## Next Integration Step

To make the deployed Streamlit Cloud apps share live tickets, connect `modules/workflow_store.py` to a hosted database. Supabase/Postgres is the natural next choice because the current SQLite schema already maps cleanly to Postgres tables.

## Streamlit Cloud Setup

Create three separate Streamlit Cloud apps from the same GitHub repository:

| System | Main file | Audience |
| --- | --- | --- |
| Public Catalog | `app.py` | Customers / public demo |
| Taylor Field Tablet | `tablet_app.py` | Sales rep / guided account demo |
| WMS | `wms_app.py` | Warehouse / internal operations demo |

Keep the design director app local/internal unless intentionally showing the planning pipeline.