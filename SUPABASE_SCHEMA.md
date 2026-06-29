# Supabase Workflow Schema

Use this schema when moving the local demo workflow store from SQLite to Supabase/Postgres.

This data is operational/internal. Do not expose the service role key in browser code. In this Streamlit app, secrets belong in Streamlit Cloud secrets.

```sql
create table if not exists public.field_orders (
    order_number text primary key,
    request_type text not null,
    customer_name text not null,
    customer_json jsonb not null default '{}'::jsonb,
    contact_json jsonb not null default '{}'::jsonb,
    created_by text not null default 'Taylor',
    needed_by text not null default '',
    delivery_window text not null default '',
    priority text not null default 'Standard',
    stage text not null default '',
    delivery_notes text not null default '',
    status text not null default 'New',
    assigned_to text not null default 'Unassigned',
    route text not null default 'Local route',
    dock text not null default 'Main dock',
    subtotal numeric not null default 0,
    line_count integer not null default 0,
    total_items integer not null default 0,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists public.field_order_lines (
    id bigint generated always as identity primary key,
    order_number text not null references public.field_orders(order_number) on delete cascade,
    product_id text not null,
    sku text not null,
    name text not null,
    category text not null default '',
    manufacturer text not null default '',
    manufacturer_part_number text not null default '',
    warehouse_location text not null default '',
    lead_time text not null default '',
    available_stock integer not null default 0,
    reorder_point integer not null default 0,
    quantity integer not null default 0,
    unit_price numeric not null default 0,
    line_total numeric not null default 0,
    short_quantity integer not null default 0,
    pick_status text not null default 'Ready',
    quote_note text not null default '',
    substitution_preference text not null default ''
);

create table if not exists public.wms_ticket_events (
    id bigint generated always as identity primary key,
    order_number text not null references public.field_orders(order_number) on delete cascade,
    event_type text not null,
    message text not null,
    created_at timestamptz not null default now()
);

alter table public.field_orders enable row level security;
alter table public.field_order_lines enable row level security;
alter table public.wms_ticket_events enable row level security;
```

## Demo Access Model

For the Streamlit demo, use server-side Streamlit code with the Supabase service role key stored in Streamlit Secrets. Do not expose this key to a public frontend.

For production, replace broad service-role access with authenticated users and role-specific RLS policies.