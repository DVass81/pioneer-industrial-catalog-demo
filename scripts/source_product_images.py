from __future__ import annotations

import csv
import io
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = ROOT / "data" / "demo_products.csv"
SOURCES_CSV = ROOT / "data" / "product_image_sources.csv"
IMAGE_DIR = ROOT / "assets" / "product_images" / "real"
OPENVERSE_API = "https://api.openverse.engineering/v1/images/"
USER_AGENT = "PioneerIndustrialCatalogDemo/1.0"

QUERY_BY_SUBCATEGORY = {
    "Hand Protection": ["work gloves", "safety gloves", "industrial gloves"],
    "Eye Protection": ["safety glasses", "protective eyewear"],
    "Head Protection": ["hard hat", "safety helmet"],
    "Hearing Protection": ["ear plugs", "hearing protection"],
    "Respiratory Protection": ["respirator mask", "dust mask"],
    "Fall Protection": ["safety harness", "fall protection"],
    "Protective Clothing": ["welding jacket", "protective clothing"],
    "First Aid": ["first aid kit", "first aid supplies"],
    "Spill Control": ["absorbent pads", "spill kit"],
    "Lockout Tagout": ["lockout tagout", "safety lockout"],
    "Cut-Off Wheels": ["cut off wheel", "abrasive cutting disc"],
    "Grinding Wheels": ["grinding wheel", "abrasive wheel"],
    "Flap Discs": ["flap disc", "abrasive disc"],
    "Sanding Belts": ["sanding belt", "abrasive belt"],
    "Wire Brushes": ["wire brush", "cup brush"],
    "Surface Conditioning": ["sanding disc", "abrasive pad"],
    "Deburring": ["deburring tool", "metal burr tool"],
    "Polishing": ["polishing wheel", "buffing wheel"],
    "Abrasive Sheets": ["sandpaper sheets", "abrasive paper"],
    "Grinding Accessories": ["grinding wheel", "angle grinder disc"],
    "Hex Bolts": ["hex bolts", "steel bolts"],
    "Nuts": ["hex nuts", "nuts bolts"],
    "Washers": ["flat washers", "metal washers"],
    "Anchors": ["anchor bolts", "concrete anchors"],
    "Screws": ["metal screws", "self drilling screws"],
    "Threaded Rod": ["threaded rod", "steel threaded bar"],
    "Pins & Clips": ["cotter pins", "retaining clips"],
    "Rivets": ["blind rivets", "pop rivets"],
    "Stud Anchors": ["wedge anchor", "stud anchor"],
    "Retaining Rings": ["retaining rings", "circlips"],
    "Cable Ties": ["cable ties", "zip ties"],
    "Conduit Fittings": ["conduit fittings", "electrical conduit"],
    "Wire": ["copper wire spool", "electrical wire"],
    "Terminals": ["electrical terminals", "wire terminals"],
    "Heat Shrink": ["heat shrink tubing", "heat shrink"],
    "Labels": ["wire labels", "industrial labels"],
    "Enclosures": ["electrical enclosure", "junction box"],
    "Disconnects": ["electrical disconnect switch", "safety switch"],
    "Grounding": ["grounding clamp", "ground wire"],
    "Wire Duct": ["wire duct", "cable duct"],
    "MIG Wire": ["welding wire spool", "mig welding wire"],
    "Stick Electrodes": ["welding electrodes", "stick welding rods"],
    "TIG Rod": ["tig welding rod", "welding rods"],
    "Welding Tips": ["welding contact tips", "mig tips"],
    "Nozzles": ["welding nozzle", "mig nozzle"],
    "Anti-Spatter": ["anti spatter spray", "welding spray"],
    "Gas Accessories": ["welding hose", "gas hose"],
    "Welding Blankets": ["welding blanket", "fire blanket"],
    "Helmet Lenses": ["welding helmet lens", "welding helmet"],
    "Torch Consumables": ["plasma cutter consumables", "welding torch"],
    "Lubricants": ["grease cartridge", "industrial lubricant"],
    "Penetrants": ["penetrating oil", "lubricant spray"],
    "Cleaners": ["industrial cleaner", "contact cleaner"],
    "Threadlockers": ["threadlocker", "thread locker"],
    "Sealants": ["silicone sealant", "gasket maker"],
    "Coolants": ["machining coolant", "coolant container"],
    "Degreasers": ["industrial degreaser", "degreaser bottle"],
    "Rust Prevention": ["rust prevention spray", "corrosion inhibitor"],
    "Adhesives": ["epoxy putty", "industrial adhesive"],
    "Absorbents": ["oil absorbent", "absorbent granules"],
    "Drill Bits": ["drill bits", "twist drill bits"],
    "Annular Cutters": ["annular cutter", "hole cutter"],
    "Taps": ["thread tap", "tap set"],
    "Dies": ["threading die", "die set"],
    "Saw Blades": ["saw blade", "band saw blade"],
    "Hole Saws": ["hole saw", "hole saw set"],
    "End Mills": ["end mill cutter", "milling cutter"],
    "Countersinks": ["countersink bit", "countersink set"],
    "Reamers": ["reamer tool", "chuck reamer"],
    "Utility Blades": ["utility blades", "knife blades"],
    "Lifting Slings": ["lifting sling", "webbing sling"],
    "Chain": ["steel chain", "lifting chain"],
    "Hooks": ["clevis hook", "chain hook"],
    "Casters": ["caster wheel", "swivel caster"],
    "Pallet Equipment": ["pallet jack", "pallet truck"],
    "Carts": ["industrial cart", "service cart"],
    "Hoist Accessories": ["chain hoist", "hoist chain"],
    "Dock Supplies": ["dock bumper", "loading dock"],
    "Straps": ["ratchet strap", "tie down strap"],
    "Storage": ["parts bin", "storage bin"],
    "Pipe Fittings": ["pipe fitting", "steel pipe fitting"],
    "Ball Valves": ["ball valve", "brass ball valve"],
    "Hose Fittings": ["hose fitting", "quick coupler"],
    "Pipe Nipples": ["pipe nipple", "threaded pipe"],
    "Unions": ["pipe union", "pipe fitting"],
    "Strainers": ["y strainer", "pipe strainer"],
    "Pressure Gauges": ["pressure gauge", "industrial gauge"],
    "Gaskets": ["gasket", "flange gasket"],
    "Clamps": ["hose clamp", "metal clamp"],
    "Thread Sealants": ["thread seal tape", "ptfe tape"],
    "Hydraulic Hose": ["hydraulic hose", "hydraulic line"],
    "Hydraulic Fittings": ["hydraulic fittings", "hydraulic adapter"],
    "Pneumatic Tubing": ["pneumatic tubing", "air tubing"],
    "Push-to-Connect": ["push to connect fitting", "pneumatic fitting"],
    "Regulators": ["air regulator", "pressure regulator"],
    "Cylinders": ["pneumatic cylinder", "air cylinder"],
    "Valves": ["solenoid valve", "pneumatic valve"],
    "Couplers": ["air coupler", "quick coupler"],
    "Hydraulic Oil": ["hydraulic oil", "oil pail"],
    "Seals": ["o ring kit", "rubber o rings"],
    "Wipers": ["shop towels", "industrial wipes"],
    "Trash Bags": ["trash bags", "contractor bags"],
    "Brooms": ["push broom", "industrial broom"],
    "Mops": ["mop bucket", "industrial mop"],
    "Hand Cleaner": ["hand cleaner", "pumice soap"],
    "Paper Products": ["paper towel roll", "toilet paper roll"],
    "Floor Care": ["floor cleaner", "floor scrubber"],
    "Scrapers": ["razor scraper", "paint scraper"],
    "Buckets": ["utility bucket", "plastic bucket"],
    "Dispensers": ["paper towel dispenser", "wall dispenser"],
    "Tape Measures": ["tape measure", "measuring tape"],
    "Calipers": ["digital caliper", "caliper"],
    "Squares": ["combination square", "try square"],
    "Levels": ["spirit level", "torpedo level"],
    "Marking": ["paint marker", "marker pen"],
    "Chalk Lines": ["chalk line", "chalk reel"],
    "Gauges": ["feeler gauge", "gauge set"],
    "Laser Tools": ["laser level", "cross line laser"],
    "Rules": ["steel ruler", "metal rule"],
    "Plumb Tools": ["plumb bob", "plumb line"],
    "Adapters": ["socket adapter", "tool adapter"],
    "Driver Bits": ["driver bits", "screwdriver bits"],
    "Batteries": ["power tool battery", "lithium battery pack"],
    "Chargers": ["battery charger", "tool charger"],
    "Saw Accessories": ["saw blade", "circular saw blade"],
    "Drill Accessories": ["drill accessory", "drill chuck"],
    "Sanding Accessories": ["sanding disc", "sander pads"],
    "Tool Storage": ["tool box", "tool storage"],
    "Dust Collection": ["dust shroud", "dust collection"],
    "Hinges": ["piano hinge", "stainless hinge"],
    "Latches": ["draw latch", "toggle latch"],
    "Handles": ["pull handle", "equipment handle"],
    "Knobs": ["star knob", "threaded knob"],
    "Leveling Feet": ["leveling foot", "machine foot"],
    "Springs": ["compression spring", "spring assortment"],
    "Magnets": ["cup magnet", "rare earth magnet"],
    "Cable Hardware": ["wire rope clip", "cable clamp"],
    "Boxes": ["cardboard boxes", "corrugated box"],
    "Stretch Film": ["stretch film roll", "plastic wrap roll"],
    "Strapping": ["polyester strapping", "steel strapping"],
    "Packing Lists": ["packing list envelope", "shipping envelope"],
    "Pallet Supplies": ["pallet top sheet", "pallet wrap"],
    "Cushioning": ["packing paper", "void fill"],
    "Edge Protection": ["cardboard edge protector", "edge protector"],
}
SUBCATEGORY_QUERY_LOOKUP = {key.lower(): value for key, value in QUERY_BY_SUBCATEGORY.items()}

BAD_TITLE_WORDS = {"landscape", "mountain", "beach", "church", "castle", "bird", "flower", "portrait", "painting", "art by kids", "aircraft", "locomotive", "tribe", "award", "no safety", "birthday", "lebaron", "chrysler", "sedan", "tibet", "sand belt", "good catch", "travel to", "bracelet", "showwheels", "prosperity"}

def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")[:90]

def openverse_search(query: str, page: int = 1, page_size: int = 20) -> list[dict]:
    params = {"q": query, "license_type": "commercial", "source": "flickr", "page_size": page_size, "page": page}
    request = urllib.request.Request(f"{OPENVERSE_API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=35) as response:
        return json.loads(response.read().decode("utf-8")).get("results", [])

def queries_for(product: dict[str, str]) -> list[str]:
    queries = []
    queries.extend(SUBCATEGORY_QUERY_LOOKUP.get(product["subcategory"].lower(), []))
    queries.extend([f"{product['subcategory']} product", f"{product['category']} {product['subcategory']}", product["product_name"]])
    seen, deduped = set(), []
    for query in queries:
        normalized = query.lower()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(query)
    return deduped

def candidate_urls(item: dict) -> list[str]:
    urls = []
    for key in ("thumbnail", "url"):
        value = item.get(key)
        if value and value.startswith(("http://", "https://")) and value not in urls:
            urls.append(value)
    return urls


def candidate_url(item: dict) -> str | None:
    urls = candidate_urls(item)
    return urls[0] if urls else None

def title_is_usable(item: dict) -> bool:
    title = str(item.get("title", "")).lower()
    return not any(word in title for word in BAD_TITLE_WORDS)

def relevance_words(query: str) -> set[str]:
    stop = {"and", "the", "with", "for", "product", "industrial", "supplies", "tool", "tools"}
    words = {word for word in re.findall(r"[a-z0-9]+", query.lower()) if len(word) > 2 and word not in stop}
    return words


def item_text(item: dict) -> str:
    parts = [str(item.get("title", "")), str(item.get("description", "")), str(item.get("tags", ""))]
    return " ".join(parts).lower()


def item_matches_query(item: dict, query: str) -> bool:
    words = relevance_words(query)
    if not words:
        return True
    text = item_text(item)
    return any(word in text for word in words)


def find_candidate(product: dict[str, str], used_urls: set[str]) -> tuple[dict, str]:
    for query in queries_for(product):
        for page in range(1, 9):
            try:
                results = openverse_search(query, page=page)
            except Exception:
                time.sleep(1)
                continue
            for item in results:
                url = candidate_url(item)
                if not url or url in used_urls or not title_is_usable(item):
                    continue
                if not item_matches_query(item, query):
                    continue
                if not item.get("license"):
                    continue
                return item, query
            time.sleep(0.1)
    # Last-resort loose pass keeps the catalog fully photographed when exact industrial products are sparse.
    for query in [product["subcategory"], product["category"], "industrial tools"]:
        for page in range(1, 6):
            try:
                results = openverse_search(query, page=page)
            except Exception:
                time.sleep(1)
                continue
            for item in results:
                url = candidate_url(item)
                if not url or url in used_urls or not title_is_usable(item):
                    continue
                if not item.get("license"):
                    continue
                return item, query
    raise RuntimeError(f"No Openverse image found for {product['product_id']} {product['product_name']}")

def download_image(url: str) -> Image.Image:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=40) as response:
                image = Image.open(io.BytesIO(response.read()))
            image = ImageOps.exif_transpose(image)
            if image.mode in {"RGBA", "LA"}:
                background = Image.new("RGB", image.size, "white")
                background.paste(image, mask=image.getchannel("A"))
                image = background
            return image.convert("RGB")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 429:
                time.sleep(5 + attempt * 5)
                continue
            raise
    raise last_error if last_error else RuntimeError("image download failed")

def crop_catalog_image(image: Image.Image) -> Image.Image:
    return ImageOps.fit(image, (640, 420), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))

def read_existing_sources() -> dict[str, dict[str, str]]:
    if not SOURCES_CSV.exists():
        return {}
    return {row["product_id"]: row for row in csv.DictReader(SOURCES_CSV.open(encoding="utf-8-sig"))}


def write_products(products: list[dict[str, str]]) -> None:
    with PRODUCTS_CSV.open("w", newline="", encoding="utf-8") as product_file:
        writer = csv.DictWriter(product_file, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)


def write_sources(source_rows: list[dict[str, str]]) -> None:
    fieldnames = ["product_id", "product_name", "image_ref", "source_url", "source_page", "search_query", "license", "license_url", "creator", "source", "title", "retrieved_date"]
    with SOURCES_CSV.open("w", newline="", encoding="utf-8") as source_file:
        writer = csv.DictWriter(source_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(source_rows)


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    products = list(csv.DictReader(PRODUCTS_CSV.open(encoding="utf-8-sig")))
    existing_sources = read_existing_sources()
    source_rows = list(existing_sources.values())
    used_urls: set[str] = {row.get("source_url", "") for row in source_rows if row.get("source_url")}
    source_ids = {row["product_id"] for row in source_rows}

    for index, product in enumerate(products, start=1):
        current_ref = product.get("image_ref", "")
        current_path = ROOT / current_ref if current_ref else None
        if product["product_id"] in source_ids and current_path and current_path.exists() and "assets/product_images/real/" in current_ref:
            print(f"{index:03d}/{len(products)} {product['product_id']} <- cached")
            continue

        last_error = None
        for _attempt in range(50):
            item, query = find_candidate(product, used_urls)
            urls = candidate_urls(item)
            assert urls
            filename = f"{product['product_id'].lower()}-{slug(product['product_name'])}.jpg"
            output_path = IMAGE_DIR / filename
            for url in urls:
                used_urls.add(url)
                try:
                    crop_catalog_image(download_image(url)).save(output_path, quality=88, optimize=True)
                    break
                except Exception as exc:
                    last_error = exc
                    time.sleep(0.2)
            else:
                continue
            break
        else:
            raise RuntimeError(f"Could not download usable image for {product['product_id']}: {last_error}")

        image_ref = output_path.relative_to(ROOT).as_posix()
        product["image_ref"] = image_ref
        row = {
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "image_ref": image_ref,
            "source_url": url,
            "source_page": item.get("foreign_landing_url", ""),
            "search_query": query,
            "license": item.get("license", ""),
            "license_url": item.get("license_url", ""),
            "creator": item.get("creator", ""),
            "source": item.get("source", ""),
            "title": item.get("title", ""),
            "retrieved_date": date.today().isoformat(),
        }
        source_rows = [existing for existing in source_rows if existing["product_id"] != product["product_id"]]
        source_rows.append(row)
        source_ids.add(product["product_id"])
        write_products(products)
        write_sources(source_rows)
        safe_title = str(item.get("title", "")).encode("ascii", "ignore").decode("ascii")[:90]
        print(f"{index:03d}/{len(products)} {product['product_id']} <- {safe_title}")
        time.sleep(0.2)

if __name__ == "__main__":
    main()
