import streamlit as st


PIONEER_GREEN = "#4c6444"
PIONEER_GREEN_DARK = "#344530"
CHARCOAL = "#252826"
INK = "#171a18"
STEEL = "#59615b"
GRAPHITE = "#343936"
ASH = "#d9ddd6"
MIST = "#f5f6f3"
WARM_NEUTRAL = "#eee7da"
WARM_NEUTRAL_LIGHT = "#faf7f0"
SUCCESS = "#2f6a42"
CAUTION = "#8a5a19"


def apply_global_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{ background: {MIST}; color: {INK}; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3, h4 {{ color: {CHARCOAL}; letter-spacing: 0; }}
        p, li, label, .stMarkdown {{ color: {INK}; }}
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {CHARCOAL} 0%, {PIONEER_GREEN_DARK} 100%);
            border-right: 1px solid rgba(255,255,255,.08);
        }}
        section[data-testid="stSidebar"] * {{ color: #ffffff; }}
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] .stCaptionContainer {{ color: rgba(255,255,255,.78); }}
        section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.18); }}
        .sidebar-brand {{
            position: relative;
            font-size: 1.04rem;
            font-weight: 900;
            line-height: 1.12;
            padding: 1rem 0 1.15rem 3rem;
            border-bottom: 1px solid rgba(238,231,218,.38);
            margin-bottom: 1rem;
            letter-spacing: .02rem;
        }}
        .sidebar-brand::before {{
            content: "P";
            position: absolute;
            left: 0;
            top: .78rem;
            width: 2.25rem;
            height: 2.25rem;
            display: grid;
            place-items: center;
            border: 2px solid {WARM_NEUTRAL};
            background: {PIONEER_GREEN};
            color: #ffffff;
            font-weight: 900;
            font-size: 1.15rem;
        }}
        .sidebar-brand::after {{
            content: "We Sell Service.";
            display: block;
            margin-top: .32rem;
            color: {WARM_NEUTRAL};
            font-size: .72rem;
            font-weight: 800;
            letter-spacing: .08rem;
            text-transform: uppercase;
        }}
        .page-kicker {{ color: {PIONEER_GREEN}; text-transform: uppercase; font-weight: 800; letter-spacing: .08rem; margin-bottom: .25rem; }}
        .hero {{
            background:
                linear-gradient(135deg, rgba(37,40,38,.96) 0%, rgba(52,69,48,.95) 58%, rgba(76,100,68,.92) 100%),
                linear-gradient(90deg, rgba(238,231,218,.18), rgba(238,231,218,0));
            color: white;
            padding: 3rem;
            border-radius: 8px;
            border: 1px solid rgba(238,231,218,.28);
            border-bottom: 6px solid {PIONEER_GREEN};
            margin-bottom: 1.5rem;
            box-shadow: 0 16px 36px rgba(37,40,38,.14);
        }}
        .hero h1 {{ color: white; font-size: 3rem; line-height: 1; margin: 0 0 .75rem; }}
        .hero p {{ color: {WARM_NEUTRAL_LIGHT}; font-size: 1.2rem; max-width: 820px; }}
        .service-tile, .customer-card {{ border: 1px solid {ASH}; border-radius: 8px; padding: 1rem; background: #ffffff; box-shadow: 0 8px 20px rgba(37,40,38,.06); }}
        .service-tile h4 {{ border-left: 4px solid {PIONEER_GREEN}; padding-left: .65rem; }}
        .customer-card span {{ display: block; color: {STEEL}; font-size: .85rem; margin-top: .2rem; }}
        .product-card {{ border: 1px solid {ASH}; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; min-height: 620px; background: #ffffff; box-shadow: 0 10px 28px rgba(37,40,38,.08); }}
        .product-card h3 {{ font-size: 1.05rem; line-height: 1.2; margin: .35rem 0; min-height: 2.6rem; }}
        .product-card p {{ color: {STEEL}; min-height: 4.2rem; font-size: .9rem; }}
        .product-meta {{ color: {STEEL}; font-size: .78rem; text-transform: uppercase; font-weight: 700; }}
        .card-price {{ font-size: 1.35rem; font-weight: 900; margin: .75rem 0; }}
        .card-price span {{ color: {STEEL}; font-size: .85rem; font-weight: 600; }}
        .badge {{ display: inline-block; border-radius: 999px; padding: .25rem .55rem; font-size: .72rem; font-weight: 800; margin-right: .35rem; }}
        .badge-stock {{ background: #e8f1e5; color: {SUCCESS}; }}
        .badge-low {{ background: #f7ead6; color: {CAUTION}; }}
        .badge-special {{ background: #eef0ec; color: {GRAPHITE}; }}
        .badge-reorder {{ background: #f6efcf; color: #685519; }}
        .badge-icc {{ background: {PIONEER_GREEN}; color: white; }}
        .recommendation-strip {{ background: {WARM_NEUTRAL_LIGHT}; border-left: 5px solid {PIONEER_GREEN}; padding: .75rem 1rem; border-radius: 6px; margin: 1rem 0; font-weight: 700; color: {CHARCOAL}; }}
        div[data-testid="stMetric"] {{
            background: #ffffff;
            border: 1px solid {ASH};
            border-radius: 8px;
            padding: .85rem 1rem;
            box-shadow: 0 8px 20px rgba(37,40,38,.05);
        }}
        .stButton > button {{
            border-radius: 6px;
            border-color: {PIONEER_GREEN};
            color: {PIONEER_GREEN};
            font-weight: 800;
        }}
        .stButton > button:hover {{
            border-color: {PIONEER_GREEN_DARK};
            color: {PIONEER_GREEN_DARK};
            background: #edf3ea;
        }}
        .stButton > button[kind="primary"] {{
            background: {PIONEER_GREEN};
            border-color: {PIONEER_GREEN};
            color: #ffffff;
        }}
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
            <h1>Everything you need, delivered.</h1>
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
