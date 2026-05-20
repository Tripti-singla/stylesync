from supabase import create_client
import json
from pathlib import Path

from config import SUPABASE_URL, SUPABASE_KEY
from services.supabase_data import sample_products
from services.external_api_service import fetch_product_by_id as fetch_external_product_by_id

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
_wardrobe_store = []
_tryon_samples_store = []
BASE_DIR = Path(__file__).resolve().parent.parent
TRYON_SAMPLES_FILE = BASE_DIR / "tryon_dataset" / "samples.json"


def _load_local_tryon_samples():
    if not TRYON_SAMPLES_FILE.exists():
        return []
    try:
        data = json.loads(TRYON_SAMPLES_FILE.read_text(encoding="utf-8") or "[]")
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_local_tryon_samples(samples):
    TRYON_SAMPLES_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRYON_SAMPLES_FILE.write_text(json.dumps(samples, indent=2), encoding="utf-8")


def _with_fallback_ids(items):
    return [
        {**item, "id": item.get("id") or f"sample-{idx + 1}"}
        for idx, item in enumerate(items)
    ]


def _product_lookup_key(item):
    return (item.get("title") or item.get("name") or "").strip().lower()


_sample_product_by_title = {
    _product_lookup_key(item): item
    for item in _with_fallback_ids(sample_products)
    if _product_lookup_key(item)
}


def _merge_sample_product_details(item):
    merged_item = dict(item)
    sample_item = _sample_product_by_title.get(_product_lookup_key(merged_item))

    if sample_item:
        for field in ("image", "image_url", "badge", "originalPrice", "description", "platform", "category", "gender", "occasion", "season", "tags", "size_chart"):
            if merged_item.get(field) in (None, "", []):
                if sample_item.get(field) not in (None, "", []):
                    merged_item[field] = sample_item.get(field)

        if not merged_item.get("image") and merged_item.get("image_url"):
            merged_item["image"] = merged_item["image_url"]

    return merged_item


def _filter_sample_products(search: str = None, category: str = None, gender: str = None, subcategory: str = None, limit: int = 20):
    filtered = _with_fallback_ids(sample_products)

    if search:
        search_lower = search.lower()
        filtered = [
            item
            for item in filtered
            if search_lower in (item.get("title") or "").lower()
            or search_lower in (item.get("description") or "").lower()
        ]

    if gender:
        gender_lower = gender.lower().strip()
        filtered = [
            item
            for item in filtered
            if (item.get("gender") or "").lower().strip() == gender_lower
        ]

    # Subcategory filters by the "category" field in raw data (clothing type)
    if subcategory:
        subcategory_lower = subcategory.lower().strip()
        filtered = [
            item
            for item in filtered
            if (item.get("category") or "").lower().strip() == subcategory_lower or
               (item.get("subcategory") or "").lower().strip() == subcategory_lower
        ]

    # Category is a separate filter (kept for compatibility)
    if category:
        category_lower = category.lower().strip()
        filtered = [
            item
            for item in filtered
            if (item.get("category") or "").lower().strip() == category_lower
        ]

    return filtered[:limit]


def get_wardrobe(user_id):
    if not supabase:
        return [item for item in _wardrobe_store if str(item.get("user_id")) == str(user_id)]
    try:
        return supabase.table("wardrobe_items").select("*").eq("user_id", user_id).execute().data
    except Exception:
        return [item for item in _wardrobe_store if str(item.get("user_id")) == str(user_id)]


def add_wardrobe_item(item_data: dict):
    stored = {
        **item_data,
        "id": item_data.get("id") or f"wardrobe-{len(_wardrobe_store) + 1}",
    }

    if not supabase:
        _wardrobe_store.append(stored)
        return stored

    try:
        response = supabase.table("wardrobe_items").insert(item_data).execute()
        if response.data:
            return response.data[0]
        return item_data
    except Exception:
        _wardrobe_store.append(stored)
        return stored


def get_tryon_samples(user_id: str = None, limit: int = 100):
    if not supabase:
        samples = _load_local_tryon_samples() or _tryon_samples_store
        if user_id is not None:
            samples = [item for item in samples if str(item.get("user_id")) == str(user_id)]
        return samples[:limit]

    try:
        query = supabase.table("tryon_samples").select("*").order("created_at", desc=True)
        if user_id is not None:
            query = query.eq("user_id", str(user_id))
        return query.limit(limit).execute().data or []
    except Exception:
        samples = _load_local_tryon_samples() or _tryon_samples_store
        if user_id is not None:
            samples = [item for item in samples if str(item.get("user_id")) == str(user_id)]
        return samples[:limit]


def add_tryon_sample(sample_data: dict):
    payload = {key: value for key, value in sample_data.items() if key != "id"}
    stored = {
        **sample_data,
        "id": sample_data.get("id") or f"tryon-{len(_tryon_samples_store) + 1}",
    }

    if not supabase:
        _tryon_samples_store.append(stored)
        local_samples = _load_local_tryon_samples()
        local_samples.append(stored)
        _save_local_tryon_samples(local_samples)
        return stored

    try:
        response = supabase.table("tryon_samples").insert(payload).execute()
        if response.data:
            return response.data[0]
        return stored
    except Exception:
        _tryon_samples_store.append(stored)
        local_samples = _load_local_tryon_samples()
        local_samples.append(stored)
        _save_local_tryon_samples(local_samples)
        return stored


def seed_tryon_samples(samples: list):
    if not samples:
        return {"status": "skipped", "count": 0, "message": "No try-on samples provided."}

    if not supabase:
        inserted = []
        for sample in samples:
            inserted.append(add_tryon_sample(sample))
        return {"status": "fallback", "count": len(inserted), "response": inserted}

    try:
        response = supabase.table("tryon_samples").insert(samples).execute()
        return {"status": "seeded", "count": len(samples), "response": response.data}
    except Exception:
        inserted = []
        for sample in samples:
            inserted.append(add_tryon_sample(sample))
        return {"status": "fallback", "count": len(inserted), "response": inserted}

def insert_outfit_score(data):
    return supabase.table("outfit_scores").insert(data).execute()


def seed_products():
    if not supabase:
        return {
            "status": "fallback",
            "count": len(sample_products),
            "response": _with_fallback_ids(sample_products),
        }
    try:
        try:
            # Clear existing products to prevent duplicates and clean up old database state
            supabase.table("products").delete().neq("title", "").execute()
        except Exception as del_err:
            print("Failed to delete existing products:", del_err)
            
        response = supabase.table("products").insert(sample_products).execute()
        return {
            "status": "seeded",
            "count": len(sample_products),
            "response": response.data,
        }
    except Exception:
        # Fallback to local sample data when remote insert fails (schema mismatch or missing table)
        return {
            "status": "fallback",
            "count": len(sample_products),
            "response": _with_fallback_ids(sample_products),
        }


def get_product_by_id(product_id: str):
    # if has_external_sources():
    #     return fetch_external_product_by_id(product_id)

    if not supabase:
        return next((item for item in _with_fallback_ids(sample_products) if str(item.get("id")) == str(product_id)), None)

    try:
        response = supabase.table("products").select("*").eq("id", product_id).single().execute()
        return _merge_sample_product_details(response.data)
    except Exception:
        return next((item for item in _with_fallback_ids(sample_products) if str(item.get("id")) == str(product_id)), None)


def get_products(search: str = None, category: str = None, gender: str = None, subcategory: str = None, limit: int = 20):
    
    if not supabase:
        return _filter_sample_products(search=search, category=category, gender=gender, subcategory=subcategory, limit=limit)

    query = supabase.table("products").select("*")

    if search:
        search_term = f"%{search}%"
        query = query.ilike("title", search_term)
        # If search should extend to description or tags, add additional filters here.

    if category:
        query = query.eq("category", category)

    if gender:
        query = query.eq("gender", gender)

    if subcategory:
        query = query.eq("category", subcategory)

    try:
        return [_merge_sample_product_details(item) for item in query.limit(limit).execute().data]
    except Exception:
        return _filter_sample_products(search=search, category=category, gender=gender, subcategory=subcategory, limit=limit)


# def get_products_from_all_sources(search: str = None, category: str = None, gender: str = None, limit: int = 20):
#     external_items = fetch_products_from_all_sources(
#         search=search,
#         category=category,
#         gender=gender,
#         limit=limit,
#     )
#     if external_items:
#         return external_items
#     return _filter_sample_products(search=search, category=category, gender=gender, limit=limit)
