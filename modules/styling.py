import streamlit as st


RED = "#B31B1B"
NAVY = "#101722"
INK = "#111111"
STEEL = "#56616F"


def apply_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: #ffffff; color: {INK}; }}
        section[data-testid="stSidebar"] {{ background: {NAVY}; }}
        section[data-testid="stSidebar"] * {{ color: #ffffff; }}
        .sidebar-brand {{ font-size: 1.15rem; font-weight: 900; padding: .75rem 0 1rem; border-bottom: 3px solid {RED}; margin-bottom: 1rem; }}
        .page-kicker {{ color: {RED}; text-transform: uppercase; font-weight: 800; letter-spacing: .08rem; margin-bottom: .25rem; }}
        .hero {{ background: linear-gradient(135deg, {NAVY} 0%, #202734 100%); color: white; padding: 3rem; border-radius: 8px; border-bottom: 6px solid {RED}; margin-bottom: 1.5rem; }}
        .hero h1 {{ color: white; font-size: 3rem; line-height: 1; margin: 0 0 .75rem; }}
        .hero p {{ color: #D9DEE7; font-size: 1.2rem; max-width: 820px; }}
        .service-tile, .customer-card {{ border: 1px solid #E2E5EA; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(16,23,34,.06); }}
        .customer-card span {{ display: block; color: #D9DEE7; font-size: .85rem; margin-top: .2rem; }}
        .product-card {{ border: 1px solid #E0E3E8; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; min-height: 620px; background: #ffffff; box-shadow: 0 10px 28px rgba(16,23,34,.08); }}
        .product-card h3 {{ font-size: 1.05rem; line-height: 1.2; margin: .35rem 0; min-height: 2.6rem; }}
        .product-card p {{ color: {STEEL}; min-height: 4.2rem; font-size: .9rem; }}
        .product-meta {{ color: {STEEL}; font-size: .78rem; text-transform: uppercase; font-weight: 700; }}
        .card-price {{ font-size: 1.35rem; font-weight: 900; margin: .75rem 0; }}
        .card-price span {{ color: {STEEL}; font-size: .85rem; font-weight: 600; }}
        .badge {{ display: inline-block; border-radius: 999px; padding: .25rem .55rem; font-size: .72rem; font-weight: 800; margin-right: .35rem; }}
        .badge-stock {{ background: #E8F7EF; color: #126A38; }}
        .badge-low {{ background: #FFF0E0; color: #9B4A00; }}
        .badge-special {{ background: #F1F2F4; color: #4B5563; }}
        .badge-reorder {{ background: #FFF8D6; color: #725900; }}
        .badge-icc {{ background: {RED}; color: white; }}
        .recommendation-strip {{ background: #FFF5F5; border-left: 5px solid {RED}; padding: .75rem 1rem; border-radius: 6px; margin: 1rem 0; font-weight: 700; }}
        @media (max-width: 900px) {{ .hero {{ padding: 1.5rem; }} .hero h1 {{ font-size: 2rem; }} .product-card {{ min-height: auto; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_home_page(products, customer: dict) -> None:
    icc_count = int(products["is_icc_supply"].sum())
    st.markdown(
        f"""
        <div class="hero">
            <div class="page-kicker">Pioneer Industrial Sales</div>
            <h1>Everything you need... delivered.</h1>
            <p>Browse a working digital catalog built for industrial buyers who need stock visibility,
            account-aware pricing, fast quote requests, and a service team that knows the plant floor.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Demo SKUs", f"{len(products):,}")
    c2.metric("ICC Supplies", icc_count)
    c3.metric("Selected Customer", customer.get("customer_name", "Demo customer"))
    c4.metric("Sales Rep", customer.get("assigned_sales_rep", "Taylor"))

    st.markdown("### We Sell Service.")
    tiles = st.columns(4)
    services = [
        ("Inventory Management", "Stock planning, reorder visibility, and account-specific supply programs."),
        ("24/7 Delivery Service", "Urgent delivery options for line-down and maintenance-critical needs."),
        ("Kitting & Fabrication Services", "Bundled job kits and fabrication support for repeat production work."),
        ("Comprehensive Line of Products", "Packaging, MRO, electrical, safety, abrasives, fasteners, and more."),
    ]
    for tile, (title, body) in zip(tiles, services):
        tile.markdown(f'<div class="service-tile"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)

    if customer.get("customer_name") == "ICC International":
        st.markdown('<div class="recommendation-strip">ICC International profile active: catalog highlights mica, banding tape, safety, abrasives, bearings, hydraulic, and electrical supplies.</div>', unsafe_allow_html=True)


def render_about_page() -> None:
    st.markdown('<div class="page-kicker">About Pioneer Services</div>', unsafe_allow_html=True)
    st.title("Industrial supply backed by service")
    st.write(
        "Pioneer Industrial Sales supports manufacturers, maintenance teams, electrical contractors, "
        "fabricators, and operations leaders with a comprehensive line of products and responsive account service."
    )
    cols = st.columns(3)
    cols[0].markdown("### Inventory Management\nKeep recurring supplies visible, quoted, and ready for reorder.")
    cols[1].markdown("### 24/7 Delivery Service\nSupport for urgent jobs, planned replenishment, and critical-path needs.")
    cols[2].markdown("### Kitting & Fabrication\nOrganized supply kits for repeat workflows and production cells.")
