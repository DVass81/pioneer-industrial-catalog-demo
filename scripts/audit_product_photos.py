from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = ROOT / "data" / "demo_products.csv"
SOURCES_CSV = ROOT / "data" / "product_image_sources.csv"
REVIEW_CSV = ROOT / "data" / "product_photo_review_queue.csv"

REVIEW_FIELDS = [
    "priority",
    "product_id",
    "product_name",
    "category",
    "subcategory",
    "image_ref",
    "issue_type",
    "recommended_action",
    "source_url",
    "source_page",
    "license",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def photo_issues(product: dict[str, str], source: dict[str, str]) -> list[str]:
    issues: list[str] = []
    image_ref = product.get("image_ref", "")
    normalized_ref = image_ref.replace("\\", "/")
    if not image_ref:
        issues.append("missing_image_ref")
    elif image_ref.startswith(("http://", "https://")):
        issues.append("remote_image_ref")
    elif not (ROOT / image_ref).exists():
        issues.append("missing_local_file")
    elif not normalized_ref.startswith("assets/product_images/real/"):
        issues.append("not_real_image_folder")
    elif not image_ref.lower().endswith(".jpg"):
        issues.append("not_local_jpg")

    if "-curated-" in Path(image_ref).name:
        issues.append("similar_photo_match")
    if not source.get("source_url"):
        issues.append("missing_direct_source_url")
    return issues


def action_for(issues: list[str]) -> str:
    if any(issue in issues for issue in ["missing_image_ref", "remote_image_ref", "missing_local_file", "not_real_image_folder", "not_local_jpg"]):
        return "Replace with a valid local 640x420 JPG and update attribution."
    if "similar_photo_match" in issues:
        return "Replace with an exact or closer product-type photo before external demo."
    if "missing_direct_source_url" in issues:
        return "Backfill source URL/license metadata or replace with a fully attributed image."
    return "No action needed."


def priority_for(issues: list[str]) -> str:
    if any(issue in issues for issue in ["missing_image_ref", "remote_image_ref", "missing_local_file", "not_real_image_folder", "not_local_jpg"]):
        return "P0"
    if "similar_photo_match" in issues:
        return "P1"
    return "P2"


def build_review_rows() -> list[dict[str, str]]:
    products = read_csv(PRODUCTS_CSV)
    sources = {row["product_id"]: row for row in read_csv(SOURCES_CSV)}
    rows: list[dict[str, str]] = []
    for product in products:
        source = sources.get(product["product_id"], {})
        issues = photo_issues(product, source)
        if not issues:
            continue
        rows.append(
            {
                "priority": priority_for(issues),
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "category": product["category"],
                "subcategory": product["subcategory"],
                "image_ref": product["image_ref"],
                "issue_type": ";".join(issues),
                "recommended_action": action_for(issues),
                "source_url": source.get("source_url", ""),
                "source_page": source.get("source_page", ""),
                "license": source.get("license", ""),
            }
        )
    return rows


def main() -> None:
    rows = build_review_rows()
    with REVIEW_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    issue_counts: dict[str, int] = {}
    for row in rows:
        for issue in row["issue_type"].split(";"):
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

    print(f"review_rows {len(rows)}")
    for issue, count in sorted(issue_counts.items()):
        print(f"{issue} {count}")


if __name__ == "__main__":
    main()
