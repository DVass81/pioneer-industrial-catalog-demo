from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PRODUCT_IMAGE_DIR = ROOT / "assets" / "product_images" / "real"


CATEGORY_IMAGE_MAP = {
    "Packaging": "assets/product_placeholders/packaging.svg",
    "Power Transmission": "assets/product_placeholders/power_transmission.svg",
    "MRO Facilities & Maintenance": "assets/product_placeholders/mro_facilities_and_maintenance.svg",
    "Electrical": "assets/product_placeholders/electrical.svg",
    "Hoses, Tubes & Pipes": "assets/product_placeholders/hoses_tubes_and_pipes.svg",
    "Janitorial & Safety": "assets/product_placeholders/janitorial_and_safety.svg",
    "Adhesives, Sealants & Tapes": "assets/product_placeholders/adhesives_sealants_and_tapes.svg",
    "Fasteners & Hardware": "assets/product_placeholders/fasteners_and_hardware.svg",
    "Material Handling": "assets/product_placeholders/material_handling.svg",
    "Office Supplies": "assets/product_placeholders/office_supplies.svg",
    "Pneumatics & Hydraulics": "assets/product_placeholders/pneumatics_and_hydraulics.svg",
    "Paints & Painting Supplies": "assets/product_placeholders/paints_and_painting_supplies.svg",
    "Welding & Fabrication": "assets/product_placeholders/welding_and_fabrication.svg",
    "Abrasives & Cutting": "assets/product_placeholders/abrasives_and_cutting.svg",
    "Bearings & Motion Control": "assets/product_placeholders/bearings_and_motion_control.svg",
    "Abrasives & Grinding": "assets/product_placeholders/abrasives_and_cutting.svg",
    "Cutting Tools": "assets/product_placeholders/abrasives_and_cutting.svg",
    "Electrical & Wire Management": "assets/product_placeholders/electrical.svg",
    "Fasteners & Anchors": "assets/product_placeholders/fasteners_and_hardware.svg",
    "Hydraulics & Pneumatics": "assets/product_placeholders/pneumatics_and_hydraulics.svg",
    "Industrial Hardware": "assets/product_placeholders/fasteners_and_hardware.svg",
    "MRO Chemicals & Lubricants": "assets/product_placeholders/mro_facilities_and_maintenance.svg",
    "Measuring & Layout": "assets/product_placeholders/material_handling.svg",
    "PPE & Safety": "assets/product_placeholders/janitorial_and_safety.svg",
    "Packaging & Shipping": "assets/product_placeholders/packaging.svg",
    "Pipe, Valves & Fittings": "assets/product_placeholders/hoses_tubes_and_pipes.svg",
    "Power Tool Accessories": "assets/product_placeholders/power_transmission.svg",
    "Shop Supplies & Janitorial": "assets/product_placeholders/janitorial_and_safety.svg",
    "Welding & Gas Supplies": "assets/product_placeholders/welding_and_fabrication.svg",
}


def _category_image(category: str) -> str:
    return CATEGORY_IMAGE_MAP.get(str(category), "assets/product_placeholders/industrial-product.svg")


def _existing_image_path(row: pd.Series) -> str:
    image_url = str(row.get("image_url") or row.get("image_ref") or "")
    if image_url and not image_url.startswith(("http://", "https://")) and (ROOT / image_url).exists():
        return image_url

    product_id = str(row.get("product_id", "")).lower()
    matches = sorted(PRODUCT_IMAGE_DIR.glob(f"{product_id}*.jpg"))
    if matches:
        return matches[0].relative_to(ROOT).as_posix()

    return _category_image(str(row.get("category", "")))


@st.cache_data(show_spinner=False)
def load_products() -> pd.DataFrame:
    products = pd.read_csv(DATA_DIR / "demo_products.csv")
    if "sku" not in products.columns and "SKU / Pioneer part number" in products.columns:
        products["sku"] = products["SKU / Pioneer part number"]
    if "image_url" not in products.columns and "image_ref" in products.columns:
        products["image_url"] = products["image_ref"]
    if "image_url" not in products.columns:
        products["image_url"] = products["category"].map(_category_image)
    generic_image = "assets/product_placeholders/industrial-product.svg"
    products.loc[products["image_url"].astype(str).str.endswith("industrial-product.svg"), "image_url"] = products["category"].map(_category_image)
    products["image_url"] = products.apply(_existing_image_path, axis=1)
    products["is_icc_supply"] = products["is_icc_supply"].astype(str).str.strip().str.lower().isin(["true", "1", "yes", "y"])
    products["price"] = products["price"].astype(float)
    if "customer_specific_price" not in products.columns:
        products["customer_specific_price"] = products["price"]
    products["customer_specific_price"] = pd.to_numeric(
        products["customer_specific_price"], errors="coerce"
    ).fillna(products["price"])
    products["quantity_in_stock"] = products["quantity_in_stock"].astype(int)
    products["reorder_point"] = products["reorder_point"].astype(int)
    return products


@st.cache_data(show_spinner=False)
def load_customers() -> pd.DataFrame:
    customers = pd.read_csv(DATA_DIR / "demo_customers.csv")
    customers["assigned_sales_rep"] = customers.get("assigned_sales_rep", "Taylor")
    customers["preferred_delivery_day"] = customers.get("preferred_delivery_day", "Scheduled")
    if "frequently_ordered_categories" not in customers.columns:
        customers["frequently_ordered_categories"] = customers.get("preferred_categories", "Demo catalog categories")
    if "quote_history_placeholder" not in customers.columns:
        customers["quote_history_placeholder"] = customers.get("notes", "Demo quote history placeholder")

    if "pricing_multiplier" not in customers.columns:
        if "custom_pricing_multiplier" in customers.columns:
            customers["pricing_multiplier"] = customers["custom_pricing_multiplier"]
        elif "contract_discount" in customers.columns:
            discount = (
                customers["contract_discount"]
                .astype(str)
                .str.replace("%", "", regex=False)
                .pipe(pd.to_numeric, errors="coerce")
                .fillna(0)
            )
            customers["pricing_multiplier"] = 1 - (discount / 100)
        elif "discount" in customers.columns:
            discount = pd.to_numeric(customers["discount"], errors="coerce").fillna(0)
            customers["pricing_multiplier"] = 1 - (discount / 100)
        else:
            customers["pricing_multiplier"] = 1.0
    customers["pricing_multiplier"] = customers["pricing_multiplier"].astype(float)
    return customers


def customer_record(customers: pd.DataFrame, name: str) -> dict:
    row = customers.loc[customers["customer_name"] == name]
    if row.empty:
        return customers.iloc[0].to_dict()
    return row.iloc[0].to_dict()
