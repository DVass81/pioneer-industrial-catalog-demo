# Streamlit Cloud Deployment Checklist

The repository has been pushed to GitHub:

```text
https://github.com/DVass81/pioneer-industrial-catalog-demo
```

Create three separate Streamlit Cloud apps from that same repository.

## App 1: Public Catalog

- Repository: `DVass81/pioneer-industrial-catalog-demo`
- Branch: `main`
- Main file path: `app.py`
- Suggested app name: `pioneer-industrial-catalog`
- Audience: public/customer-facing catalog demo

## App 2: Taylor Field Tablet

- Repository: `DVass81/pioneer-industrial-catalog-demo`
- Branch: `main`
- Main file path: `tablet_app.py`
- Suggested app name: `pioneer-taylor-tablet`
- Audience: sales rep / account visit workflow

## App 3: WMS

- Repository: `DVass81/pioneer-industrial-catalog-demo`
- Branch: `main`
- Main file path: `wms_app.py`
- Suggested app name: `pioneer-wms`
- Audience: warehouse / internal operations workflow

## Steps In Streamlit Cloud

1. Open Streamlit Cloud.
2. Select **Create app** or **New app**.
3. Choose **Deploy from existing repo**.
4. Pick the GitHub repo above.
5. Choose branch `main`.
6. Enter the main file path for the system you are deploying.
7. Add the shared persistence secrets below to each app.
8. Deploy.
9. Repeat for the other two systems.

## Shared Persistence Secrets

Local demo handoff uses SQLite at `data/demo_workflow.sqlite3`. Streamlit Cloud apps do not share local files, so all three cloud apps need the same Pioneer Supabase secrets.

Add these secrets to all three Streamlit apps:

```toml
SUPABASE_URL = "https://dujcsbzqznucqpuyjsdy.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR-SERVICE-ROLE-KEY"
WORKFLOW_BACKEND = "supabase"
```

Keep these values in Streamlit Secrets only. Do not commit them to GitHub.

## Pioneer Supabase Project

- Project name: `Pioneer Industrial Demo`
- Project ref: `dujcsbzqznucqpuyjsdy`
- Region: `us-east-2`
- Separate from: `CBS Intelligence Pilot`
- Database tables: `field_orders`, `field_order_lines`, `wms_ticket_events`

## Taylor Demo Cloud Check

After all three apps are deployed:

1. Open the tablet app and submit a test ICC International field order.
2. Open the WMS app and click **Refresh queue**.
3. Confirm the submitted order appears as a pull ticket.
4. Change the ticket status and picker in WMS.
5. Confirm the WMS command center shows the new event in recent ticket activity.