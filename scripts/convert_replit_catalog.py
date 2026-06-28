from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = ROOT / "data" / "replit_reference"
PRODUCTS_IN = REFERENCE_DIR / "products.csv"
CATEGORIES_IN = REFERENCE_DIR / "categories.csv"
PRODUCTS_OUT = ROOT / "data" / "demo_products.csv"
SOURCES_OUT = ROOT / "data" / "product_image_sources.csv"

PRODUCT_FIELDS = [
    "product_id",
    "SKU / Pioneer part number",
    "manufacturer",
    "manufacturer_part_number",
    "product_name",
    "category",
    "subcategory",
    "description",
    "specs",
    "unit_of_measure",
    "quantity_in_stock",
    "reorder_point",
    "price",
    "customer_specific_price",
    "image_ref",
    "lead_time",
    "warehouse_location",
    "is_icc_supply",
    "tags",
    "safety_stock_status",
]

SOURCE_FIELDS = [
    "product_id",
    "product_name",
    "image_ref",
    "source_url",
    "source_page",
    "search_query",
    "license",
    "license_url",
    "creator",
    "source",
    "title",
    "retrieved_date",
]

SUBCATEGORY_RULES = [
    ("Bearings", "tapered", "Tapered Roller Bearings"),
    ("Bearings", "spherical", "Spherical Roller Bearings"),
    ("Bearings", "cylindrical", "Cylindrical Roller Bearings"),
    ("Bearings", "ball bearing", "Ball Bearings"),
    ("Power Transmission", "v-belt", "V-Belts"),
    ("Power Transmission", "belt", "Belts"),
    ("Power Transmission", "sheave", "Sheaves"),
    ("Power Transmission", "sprocket", "Sprockets"),
    ("Power Transmission", "coupling", "Couplings"),
    ("Abrasives", "flap", "Flap Discs"),
    ("Abrasives", "cut", "Cut-Off Wheels"),
    ("Abrasives", "grind", "Grinding Wheels"),
    ("Cutting Tools", "end mill", "End Mills"),
    ("Cutting Tools", "drill", "Drill Bits"),
    ("Cutting Tools", "insert", "Carbide Inserts"),
    ("Cutting Tools", "blade", "Saw Blades"),
    ("Fasteners", "bolt", "Bolts"),
    ("Fasteners", "screw", "Screws"),
    ("Fasteners", "nut", "Nuts"),
    ("Fasteners", "washer", "Washers"),
    ("Fasteners", "anchor", "Anchors"),
    ("Electrical", "terminal", "Terminals"),
    ("Electrical", "connector", "Connectors"),
    ("Electrical", "wire", "Wire"),
    ("Safety Supplies", "glove", "Hand Protection"),
    ("Safety Supplies", "glasses", "Eye Protection"),
    ("Safety Supplies", "respirator", "Respiratory Protection"),
    ("Safety Supplies", "hat", "Head Protection"),
    ("Lubricants", "grease", "Grease"),
    ("Lubricants", "oil", "Oil"),
    ("Lubricants", "spray", "Sprays"),
    ("MRO Supplies", "cleaner", "Cleaners"),
    ("MRO Supplies", "wipe", "Wipers"),
    ("Material Handling", "cart", "Carts"),
    ("Material Handling", "bin", "Bins"),
    ("Electrical Insulation", "tape", "Insulation Tape"),
    ("Electrical Insulation", "sleeving", "Sleeving"),
    ("Specialty Tapes & Films", "tape", "Specialty Tape"),
    ("Specialty Tapes & Films", "film", "Films"),
]

DEFAULT_SUBCATEGORY = {
    "Bearings": "Industrial Bearings",
    "Power Transmission": "Drive Components",
    "Abrasives": "Abrasive Products",
    "Cutting Tools": "Cutting Tools",
    "Fasteners": "Fasteners",
    "Electrical": "Electrical Components",
    "Safety Supplies": "Safety Supplies",
    "Lubricants": "Lubricants",
    "MRO Supplies": "MRO Supplies",
    "Material Handling": "Material Handling",
    "Electrical Insulation": "Electrical Insulation",
    "Specialty Tapes & Films": "Specialty Tapes & Films",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clean_text(value: str | None) -> str:
    return " ".join(str(value or "").split())


def money(value: str | None) -> str:
    try:
        return f"{float(value or 0):.2f}"
    except ValueError:
        return "0.00"


def safe_int(value: str | None, default: int = 0) -> int:
    try:
        return int(float(value or default))
    except ValueError:
        return default


def product_id(replit_id: str) -> str:
    return f"RPL-{int(replit_id):04d}"


def derive_subcategory(category: str, name: str, description: str) -> str:
    haystack = f"{name} {description}".lower()
    for rule_category, needle, subcategory in SUBCATEGORY_RULES:
        if rule_category == category and needle in haystack:
            return subcategory
    return DEFAULT_SUBCATEGORY.get(category, category)


def stock_status(quantity: int, reorder_point: int) -> str:
    if quantity <= 0:
        return "Special Order"
    if quantity <= reorder_point:
        return "Low"
    if quantity <= reorder_point * 2:
        return "Reorder Soon"
    return "OK"


def lead_time(category: str, show_price: bool) -> str:
    if not show_price:
        return "Quote required"
    if category in {"Bearings", "Power Transmission", "Electrical Insulation", "Specialty Tapes & Films"}:
        return "3-5 business days"
    return "1-3 business days"


def source_domain(url: str) -> str:
    if not url:
        return ""
    return urlparse(url).netloc.lower()


def build_rows() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    categories = {row["id"]: row for row in read_csv(CATEGORIES_IN)}
    products = [row for row in read_csv(PRODUCTS_IN) if row.get("isActive") == "True"]
    product_rows: list[dict[str, str]] = []
    source_rows: list[dict[str, str]] = []

    for index, row in enumerate(products, start=1):
        category = clean_text(row.get("categoryName")) or clean_text(categories.get(row.get("categoryId"), {}).get("name"))
        name = clean_text(row.get("name"))
        description = clean_text(row.get("description"))
        show_price = row.get("showPrice") == "True"
        quantity = safe_int(row.get("availableQty"))
        reorder = max(1, round(quantity * 0.25))
        price = money(row.get("price"))
        image_url = clean_text(row.get("imageUrl"))
        pid = product_id(row["id"])
        tags = [
            "replit-import",
            f"replit-id-{row['id']}",
            f"show-price-{str(show_price).lower()}",
            "remote-image-source" if image_url.startswith(("http://", "https://")) else "local-image-source",
            category.lower().replace(" ", "-").replace("&", "and"),
        ]

        product_rows.append(
            {
                "product_id": pid,
                "SKU / Pioneer part number": clean_text(row.get("sku")),
                "manufacturer": clean_text(row.get("manufacturerName")) or "Pioneer Industrial",
                "manufacturer_part_number": clean_text(row.get("sku")),
                "product_name": name,
                "category": category,
                "subcategory": derive_subcategory(category, name, description),
                "description": description,
                "specs": clean_text(row.get("specs")) or "Spec details available on request.",
                "unit_of_measure": clean_text(row.get("unitOfMeasure")) or "Each",
                "quantity_in_stock": str(quantity),
                "reorder_point": str(reorder),
                "price": price,
                "customer_specific_price": price,
                "image_ref": image_url,
                "lead_time": lead_time(category, show_price),
                "warehouse_location": f"R{((index - 1) // 10) + 1}-{((index - 1) % 10) + 1:02d}",
                "is_icc_supply": "TRUE" if row.get("featured") == "True" else "FALSE",
                "tags": ";".join(tags),
                "safety_stock_status": stock_status(quantity, reorder),
            }
        )

        source_rows.append(
            {
                "product_id": pid,
                "product_name": name,
                "image_ref": image_url,
                "source_url": image_url,
                "source_page": "",
                "search_query": "Imported from Replit reference product imageUrl",
                "license": "Replit reference remote image URL; commercial-use rights not verified. Replace with local licensed asset before external customer demo.",
                "license_url": "",
                "creator": "",
                "source": source_domain(image_url),
                "title": name,
                "retrieved_date": date.today().isoformat(),
            }
        )

    return product_rows, source_rows


def validate(rows: list[dict[str, str]], source_rows: list[dict[str, str]]) -> None:
    if len(rows) != 65:
        raise SystemExit(f"Expected 65 active Replit products, got {len(rows)}")
    missing = [
        (row["product_id"], field)
        for row in rows
        for field in PRODUCT_FIELDS
        if field != "image_ref" and not str(row.get(field, "")).strip()
    ]
    if missing:
        raise SystemExit(f"Missing required values: {missing[:10]}")
    if len({row["product_id"] for row in rows}) != len(rows):
        raise SystemExit("Duplicate product_id values generated")
    if len({row["SKU / Pioneer part number"] for row in rows}) != len(rows):
        raise SystemExit("Duplicate SKU values found")
    if len(source_rows) != len(rows):
        raise SystemExit("Source tracker row count does not match product count")


def main() -> None:
    product_rows, source_rows = build_rows()
    validate(product_rows, source_rows)
    write_csv(PRODUCTS_OUT, product_rows, PRODUCT_FIELDS)
    write_csv(SOURCES_OUT, source_rows, SOURCE_FIELDS)
    remote_images = sum(row["image_ref"].startswith(("http://", "https://")) for row in product_rows)
    categories = len({row["category"] for row in product_rows})
    print(f"converted_products={len(product_rows)}")
    print(f"categories={categories}")
    print(f"remote_image_refs={remote_images}")
    print(f"source_rows={len(source_rows)}")


if __name__ == "__main__":
    main()
