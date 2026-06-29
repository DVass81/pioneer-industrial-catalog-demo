from __future__ import annotations

from pathlib import Path

import streamlit as st

DESIGN_DIRECTOR_DIR = Path(__file__).resolve().parent.parent / "design-director"

DOCUMENTS = [
    ("README", "README.md", "How to use the internal Design Director workflow."),
    ("Design Principles", "pioneer-design-principles.md", "Visual identity, forbidden moves, and required behaviors."),
    ("System Map", "system-map.md", "How the catalog, tablet app, and WMS connect."),
    ("Design System Template", "design-system-template.md", "Reusable Pioneer tokens, density, status, motion, and accessibility structure."),
    ("Screen Brief Template", "screen-brief-template.md", "Screen-level planning brief for Catalog, Tablet, and WMS work."),
    ("Component Catalog", "component-catalog.md", "Curated Pioneer component patterns and usage rules."),
    ("Codex UI Prompt Template", "codex-ui-prompt-template.md", "Copyable implementation prompt for future screen builds."),
]


def apply_design_director_styles() -> None:
    st.markdown(
        """
        <style>
        .dd-hero {
            border: 1px solid #d9ddd6;
            border-radius: 8px;
            padding: 1.5rem;
            background: linear-gradient(135deg, #252826 0%, #344530 58%, #4c6444 100%);
            color: #ffffff;
            box-shadow: 0 16px 36px rgba(37,40,38,.14);
            margin-bottom: 1rem;
        }
        .dd-hero h1 { color: #ffffff; margin: .25rem 0 .5rem; }
        .dd-hero p { color: #faf7f0; max-width: 900px; }
        .dd-label { display: inline-block; border: 1px solid rgba(238,231,218,.55); border-radius: 999px; padding: .25rem .65rem; color: #eee7da; font-weight: 800; font-size: .78rem; text-transform: uppercase; }
        .dd-card { border: 1px solid #d9ddd6; border-radius: 8px; padding: 1rem; background: #ffffff; min-height: 155px; box-shadow: 0 8px 20px rgba(37,40,38,.06); }
        .dd-card h3 { margin-top: 0; font-size: 1.02rem; }
        .dd-card p { color: #59615b; font-size: .9rem; }
        .dd-workflow { border-left: 5px solid #4c6444; border-radius: 8px; background: #ffffff; padding: 1rem 1.25rem; }
        .dd-copy { border: 1px dashed #4c6444; border-radius: 8px; background: #f8faf7; padding: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _read_doc(filename: str) -> str:
    path = DESIGN_DIRECTOR_DIR / filename
    if not path.exists():
        return f"Missing `{filename}`."
    return path.read_text(encoding="utf-8-sig")


def render_design_director_page(products=None) -> None:
    st.markdown(
        """
        <div class="dd-hero">
            <span class="dd-label">Internal / Dev Only</span>
            <h1>Pioneer Design Director Pipeline</h1>
            <p>Use this planning layer before building major Pioneer catalog, field tablet, or warehouse screens. It keeps the product from drifting into generic SaaS and turns screen ideas into implementation-ready Codex prompts.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if products is not None:
        c1, c2, c3 = st.columns(3)
        c1.metric("Catalog products", f"{len(products):,}")
        c2.metric("Categories", int(products["category"].nunique()) if "category" in products else 0)
        c3.metric("Design scope", "Catalog / Tablet / WMS")

    st.markdown("### Three-Part Pioneer Platform")
    cols = st.columns(3)
    platform_cards = [
        ("Product Catalog", "Customer-facing product visibility, quote/cart flow, product detail, and order status foundation."),
        ("Field Tablet App", "Taylor's field workflow for VMI, replenishment, item lookup, line notes, substitutions, and handoff context."),
        ("WMS / Inventory Control", "Warehouse execution layer for inventory, receiving, pick queues, replenishment, transfers, and exceptions."),
    ]
    for col, (title, body) in zip(cols, platform_cards):
        col.markdown(f'<div class="dd-card"><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

    st.markdown("### Recommended Workflow")
    st.markdown(
        """
        <div class="dd-workflow">
        <ol>
            <li>Choose the system area: Catalog, Field Tablet, or WMS.</li>
            <li>Fill out the screen brief.</li>
            <li>Reference the Pioneer design principles.</li>
            <li>Select component patterns.</li>
            <li>Generate a Codex UI implementation prompt.</li>
            <li>Build the screen.</li>
            <li>Review against the design principles and acceptance criteria.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Pipeline Documents")
    for row_start in range(0, len(DOCUMENTS), 2):
        row_cols = st.columns(2)
        for col, (title, filename, description) in zip(row_cols, DOCUMENTS[row_start : row_start + 2]):
            with col:
                st.markdown(f'<div class="dd-card"><h3>{title}</h3><p>{description}</p><p><code>design-director/{filename}</code></p></div>', unsafe_allow_html=True)
                with st.expander(f"Preview {title}"):
                    st.markdown(_read_doc(filename))

    st.markdown("### Copyable Codex Prompt Starter")
    prompt = """Role: senior industrial product designer + senior frontend engineer.
Context: existing Pioneer 3-part system: Product Catalog, Field Tablet App, and WMS.
Screen to build: [screen name]
System area: [Catalog / Tablet App / WMS]
Business goal: [what Pioneer needs]
User goal: [what the operator/customer/Taylor/warehouse worker needs]
Use design-director/pioneer-design-principles.md and component-catalog.md.
Reuse existing Pioneer visual language. Do not break current routes. Prioritize field usability and operational clarity over decoration. Validate before finishing."""
    st.code(prompt, language="text")
