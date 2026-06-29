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
7. Deploy.
8. Repeat for the other two systems.

## Secrets For Shared Cloud Persistence

Local demo handoff uses SQLite at `data/demo_workflow.sqlite3`. Streamlit Cloud apps do not share local files, so hosted persistence needs database secrets.

When Supabase/Postgres is ready, add these secrets to all three Streamlit apps:

```toml
SUPABASE_URL = "https://dujcsbzqznucqpuyjsdy.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "YOUR-SERVICE-ROLE-KEY"
WORKFLOW_BACKEND = "supabase"
```

Keep these values in Streamlit Secrets only. Do not commit them to GitHub.

## Pioneer Supabase Project

- Project name: Pioneer Industrial Demo (separate from CBS Intelligence Pilot)
- Project ref: dujcsbzqznucqpuyjsdy 
- Region: us-east-2 
- Database tables created: ield_orders, ield_order_lines, wms_ticket_events 
