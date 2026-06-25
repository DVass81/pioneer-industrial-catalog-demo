from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


@st.cache_data(show_spinner=False)
def load_products() -> pd.DataFrame:
    products = pd.read_csv(DATA_DIR / "demo_products.csv")
    if "sku" not in products.columns and "SKU / Pioneer part number" in products.columns:
        products["sku"] = products["SKU / Pioneer part number"]
    if "image_url" not in products.columns and "image_ref" in products.columns:
        products["image_url"] = products["image_ref"]
    if "image_url" not in products.columns:
        products["image_url"] = "assets/product_placeholders/industrial-product.svg"
    products["is_icc_supply"] = products["is_icc_supply"].astype(bool)
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
    if "pricing_multiplier" not in customers.columns:
        if "custom_pricing_multiplier" in customers.columns:
            customers["pricing_multiplier"] = customers["custom_pricing_multiplier"]
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
