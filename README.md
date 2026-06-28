# Pioneer Industrial Sales Public Catalog

This repository contains the Pioneer Industrial Sales Streamlit catalog. Phase 1 is scoped as a public-facing product catalog that helps visitors browse industrial supply categories, inspect product details, and start a quote request with lightweight, approved demo product data.

The public site should not expose customer-specific accounts, pricing, order history, or demo customer workflows. Demo customers are reserved for the Stage 2 tablet-mode vision, where sales reps can use account-aware views during guided customer conversations.

## Repository Files

- `requirements.txt`: Python packages needed by the Streamlit app.
- `.streamlit/config.toml`: Pioneer-aligned Streamlit UI theme defaults.
- `.gitignore`: Local Python, Streamlit secret, editor, and build artifacts to keep out of Git.
- `README.md`: Setup, run, deployment, product vision, and QC notes.
- `assets/`: Logo and demo product imagery.
- `data/`: Approved sample product data, plus Stage 2-only demo customer data when needed for tablet-mode work.
- `modules/`: Streamlit page, catalog, cart, data loading, and styling modules.

## Product Direction

### Phase 1: Public Catalog

Phase 1 is the public Pioneer Industrial Sales catalog experience:

- Open catalog browsing without authentication.
- Product search, category filtering, stock/lead-time context, product details, and quote-cart flow.
- Public brand presentation for Pioneer services and industrial supply categories.
- Sample or approved product data only.
- No public customer selector, customer-specific pricing, contract terms, account notes, quote history, or private customer records.

### Stage 2+: Rep Tablet Mode

Stage 2 and later can add a tablet-friendly sales-rep workflow for in-person walkthroughs:

- Demo customer selector for guided selling and training.
- Account-aware recommendations, preferred categories, quote history placeholders, and negotiated-pricing examples.
- Customer-context views optimized for tablet use during field visits, counter conversations, or trade-show demos.
- Clear separation from the public catalog so customer-style demo data does not appear on the public site.

## Local Setup

Use Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If your machine uses `py` instead of `python`, replace `python` with `py` in the commands above.

## Run Locally

Start the app from the repository root:

```powershell
streamlit run app.py
```

If the app entry file uses a different name, replace `app.py` with the correct Streamlit file.

## Upload to GitHub

From the repository root:

```powershell
git status
git add README.md requirements.txt .gitignore .streamlit/config.toml
git commit -m "Add Streamlit deployment files"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

If the remote already exists, update it with:

```powershell
git remote set-url origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

## Deploy to Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Select **New app**.
4. Choose the GitHub repository and branch.
5. Set the main file path, usually `app.py`.
6. Confirm that `requirements.txt` is detected.
7. Deploy the app.

If the app needs private keys or credentials later, add them in Streamlit Cloud under **App settings > Secrets**. Do not commit `.streamlit/secrets.toml`.

## Public Demo Instructions

Use the deployed Streamlit URL to review the Phase 1 public catalog experience.

Recommended presenter path:

1. Open the app in a fresh browser window.
2. Start on **Home** and frame Phase 1 as the public Pioneer inventory and quote request website.
3. Open **Product Catalog** and show that products are organized by category, not dumped into one long SKU list.
4. Select **Fasteners & Anchors** to demonstrate product-type browsing, then narrow with the product type filter if useful.
5. Open a product detail view and call out the SKU, manufacturer part number, stock, lead time, bin/location, and product image.
6. Add the item to the quote cart, then open **Quote Cart** to adjust quantity or remove the line.
7. Open **Request Quote**, enter sample contact details, and submit to show the `PIS-QR-####` confirmation flow.
8. End by explaining that Pioneer confirms final pricing, availability, delivery, and payment instructions after the request.

Keep the walkthrough practical and buyer-focused: category browse, product detail, quote cart, request quote. Avoid presenting customer-specific accounts or Taylor's field tablet workflow in Phase 1.
Before sharing externally, confirm the URL, product data, brand copy, and public-facing demo script with the project owner. Do not present demo customer accounts on the public site; those belong to the Stage 2 tablet-mode workflow.

## Brand and Theme Notes

The rebuilt Pioneer demo uses a light Streamlit shell with olive green, charcoal, black-green ink, and warm neutral accents:

- Primary action/accent: `#4C6444`
- Sidebar and hero dark green: `#344530`
- Main text: `#171914`
- Secondary background: `#F4F2EC`
- App logo asset: `assets/pioneer_logo.png`

Keep `.streamlit/config.toml` aligned with the app-level CSS in `modules/styling.py` so Streamlit widgets, buttons, sidebar behavior, and the custom page styling feel like one brand system.

## Photo QA Status

Phase 1.5 includes a repeatable photo audit for demo readiness:

```powershell
python scripts\audit_product_photos.py
```

The audit writes `data/product_photo_review_queue.csv`, which tracks product images that still need exact-photo replacement or cleaner attribution. Current known review categories are:

- Remote image refs: product currently displays a Replit-imported image URL instead of a local cleared asset.
- Similar-photo matches: product has a local real image, but the image is only a close visual stand-in.
- Missing direct source URL: product image renders locally, but the attribution row needs a cleaner original source URL/license record.

The live catalog can be rebuilt from Replit reference data with:

```powershell
python scripts\\convert_replit_catalog.py
```

The current Replit-derived catalog uses remote image URLs from the published Replit app for internal demo comparison. Before an external/customer demo, replace those remote images with local cleared or generated demo visuals.

Do not use automated keyword-only image replacements for the final customer demo unless the image title/source clearly matches the product type. Bad image matches are worse than leaving a known review item in the queue.

## Demo Data Note

This catalog should use synthetic, anonymized, or approved sample data only. Do not upload real customer data, private credentials, internal exports, or personally identifiable information unless the project owner has explicitly approved that data for the intended environment.

For Phase 1 public catalog releases, keep customer-specific demo data out of the public experience. Demo customer profiles, negotiated-pricing examples, quote-history placeholders, and account-aware recommendations are reserved for Stage 2+ tablet mode.

## QC Checks Before Final

Run these checks before handing off the repository or deployment:

- `git status` shows only the intended files changed.
- `pip install -r requirements.txt` completes in a clean virtual environment.
- `streamlit run app.py` starts successfully from the repository root.
- The app loads locally without uncaught Streamlit errors.
- The Pioneer logo loads from `assets/pioneer_logo.png`.
- Streamlit theme colors match the Pioneer brand notes above.
- All visible controls, filters, links, and charts work with demo data.
- Phase 1 public navigation does not expose demo customer accounts, customer-specific pricing, private account notes, or quote history.
- Any demo customer selector or account-aware workflow is clearly treated as Stage 2+ tablet-mode work, not the public catalog.
- The deployed Streamlit Cloud app builds successfully from GitHub.
- The deployed app opens in an incognito/private browser window.
- No secrets, tokens, local paths, customer data, or private files are committed.
- `.streamlit/secrets.toml`, `.env`, virtual environments, caches, and editor files are ignored.
- README setup and deployment commands match the final repository structure.
