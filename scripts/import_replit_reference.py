from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

BASE_URL = "https://industrial-supply-hub.replit.app"
OUT_DIR = Path("data/replit_reference")
USER_AGENT = "PioneerIndustrialCatalogDemo-ReplitReference/1.0"

CATEGORY_FIELDS = ["id", "name", "slug", "description", "iconName", "productCount"]
PRODUCT_FIELDS = [
    "id",
    "sku",
    "name",
    "categoryId",
    "categoryName",
    "manufacturerId",
    "manufacturerName",
    "description",
    "unitOfMeasure",
    "availableQty",
    "price",
    "showPrice",
    "imageUrl",
    "specSheetUrl",
    "featured",
    "specs",
    "pricingTiers",
    "isActive",
    "createdAt",
]


def fetch_json(path: str, params: dict[str, int | str] | None = None):
    url = f"{BASE_URL}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fetch_all_products() -> list[dict]:
    first = fetch_json("/api/products", {"limit": 100, "page": 1})
    products = list(first.get("items", []))
    total = int(first.get("total", len(products)))
    page = 2
    while len(products) < total:
        payload = fetch_json("/api/products", {"limit": 100, "page": page})
        items = payload.get("items", [])
        if not items:
            break
        products.extend(items)
        page += 1
    return products


def image_domain(url: str) -> str:
    if not url:
        return ""
    return urllib.parse.urlparse(url).netloc.lower()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    categories = fetch_json("/api/categories")
    products = fetch_all_products()
    domains: dict[str, int] = {}
    for product in products:
        domain = image_domain(str(product.get("imageUrl") or ""))
        domains[domain] = domains.get(domain, 0) + 1

    summary = {
        "retrieved_date": date.today().isoformat(),
        "base_url": BASE_URL,
        "category_count": len(categories),
        "product_count": len(products),
        "image_domains": dict(sorted(domains.items(), key=lambda item: (-item[1], item[0]))),
        "category_counts": {category["name"]: category.get("productCount", 0) for category in categories},
        "notes": [
            "Reference data was pulled from the public Replit app API.",
            "Do not hotlink or blindly copy commercial image URLs into the production demo.",
            "Use categories/product browsing patterns as a migration reference first.",
        ],
    }
    write_json(OUT_DIR / "categories.json", categories)
    write_json(OUT_DIR / "products.json", products)
    write_json(OUT_DIR / "summary.json", summary)
    write_csv(OUT_DIR / "categories.csv", categories, CATEGORY_FIELDS)
    write_csv(OUT_DIR / "products.csv", products, PRODUCT_FIELDS)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
