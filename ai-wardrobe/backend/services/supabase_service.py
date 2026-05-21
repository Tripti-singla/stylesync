from supabase import create_client
import json
from pathlib import Path

from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
BASE_DIR = Path(__file__).resolve().parent.parent


def is_valid_uuid(val):
    import uuid
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def _normalize_db_product(row: dict) -> dict:
    if not row:
        return {}
    
    # Map raw Amazon scraper fields to standard schema fields
    normalized = {}
    
    # 1. ID - ensure it's a string
    normalized["id"] = str(row.get("id") or "")
    
    # 2. Title
    normalized["title"] = row.get("title") or "Unnamed Product"
    
    # 3. Description -> map about_item
    normalized["description"] = row.get("about_item") or row.get("description") or ""
    
    # 4. Image URL -> check all_images or fallback
    image_url = ""
    all_images_val = row.get("all_images")
    if all_images_val:
        if isinstance(all_images_val, list) and len(all_images_val) > 0:
            image_url = all_images_val[0]
        elif isinstance(all_images_val, str):
            try:
                parsed_imgs = json.loads(all_images_val)
                if isinstance(parsed_imgs, list) and len(parsed_imgs) > 0:
                    image_url = parsed_imgs[0]
                else:
                    image_url = parsed_imgs
            except Exception:
                image_url = all_images_val
    
    if not image_url:
        image_url = row.get("image_url") or ""
        
    normalized["image_url"] = image_url
    
    # 5. Price
    try:
        normalized["price"] = float(row.get("price_value") or row.get("price") or 0.0)
    except Exception:
        normalized["price"] = 0.0
    
    # 6. Original Price (List Price)
    orig_price = None
    list_price_val = row.get("list_price") or row.get("original_price")
    if list_price_val:
        if isinstance(list_price_val, (int, float)):
            orig_price = float(list_price_val)
        elif isinstance(list_price_val, str):
            import re
            match = re.search(r"\d+(\.\d+)?", list_price_val)
            if match:
                try:
                    orig_price = float(match.group())
                except ValueError:
                    pass
    normalized["original_price"] = orig_price
    
    # 7. Platform / Brand
    normalized["platform"] = row.get("brand_name") or row.get("platform") or "Amazon"
    
    # 8. Affiliate / Product Link
    normalized["affiliate_link"] = row.get("product_url") or row.get("affiliate_link") or ""
    
    # 9. Breadcrumbs parsing for category/gender/subcategory
    breadcrumbs = row.get("breadcrumbs") or ""
    
    # Determine gender from breadcrumbs
    gender = "unisex"
    breadcrumbs_lower = breadcrumbs.lower()
    if "women" in breadcrumbs_lower:
        gender = "women"
    elif "men" in breadcrumbs_lower:
        gender = "men"
    elif "girls" in breadcrumbs_lower:
        gender = "women"
    elif "boys" in breadcrumbs_lower:
        gender = "men"
        
    normalized["gender"] = gender
    
    # Determine category/subcategory
    subcat = ""
    if breadcrumbs:
        import re
        nodes = [n.strip() for n in re.split(r"\s*[›>»\x9b\uFFFD]\s*", breadcrumbs) if n.strip()]
        if nodes:
            subcat = nodes[-1].lower()
            
    normalized["category"] = subcat or "clothing"
    normalized["subcategory"] = subcat or "clothing"
    
    # 10. Tags, Occasion, Season
    normalized["tags"] = row.get("tags") or ([subcat] if subcat else [])
    normalized["occasion"] = row.get("occasion") or ["casual"]
    normalized["season"] = row.get("season") or ["all-season"]
    normalized["size_chart"] = row.get("size_chart") or {"S": {}, "M": {}, "L": {}, "XL": {}}
    normalized["created_at"] = row.get("created_at")
    
    return normalized


def get_wardrobe(user_id):
    if not supabase:
        return []
    if not is_valid_uuid(user_id):
        print(f"Skipping get_wardrobe: user_id '{user_id}' is not a valid UUID")
        return []
    try:
        return supabase.table("wardrobe_items").select("*").eq("user_id", user_id).execute().data or []
    except Exception as e:
        print("Error in get_wardrobe:", e)
        return []


def add_wardrobe_item(item_data: dict):
    if not supabase:
        return item_data
    user_id = item_data.get("user_id")
    if user_id and not is_valid_uuid(user_id):
        print(f"Cannot add_wardrobe_item: user_id '{user_id}' is not a valid UUID")
        return item_data
    try:
        response = supabase.table("wardrobe_items").insert(item_data).execute()
        if response.data:
            return response.data[0]
        return item_data
    except Exception as e:
        print("Error in add_wardrobe_item:", e)
        return item_data


def get_tryon_samples(user_id: str = None, limit: int = 100):
    if not supabase:
        return []
    try:
        query = supabase.table("tryon_samples").select("*").order("created_at", desc=True)
        if user_id is not None:
            query = query.eq("user_id", str(user_id))
        return query.limit(limit).execute().data or []
    except Exception as e:
        print("Error in get_tryon_samples:", e)
        return []


def add_tryon_sample(sample_data: dict):
    if not supabase:
        return sample_data
    try:
        payload = {key: value for key, value in sample_data.items() if key != "id"}
        response = supabase.table("tryon_samples").insert(payload).execute()
        if response.data:
            return response.data[0]
        return sample_data
    except Exception as e:
        print("Error in add_tryon_sample:", e)
        return sample_data


def seed_tryon_samples(samples: list):
    if not samples:
        return {"status": "skipped", "count": 0, "message": "No try-on samples provided."}
    if not supabase:
        return {"status": "error", "message": "Supabase client not initialized."}
    try:
        response = supabase.table("tryon_samples").insert(samples).execute()
        return {"status": "seeded", "count": len(samples), "response": response.data}
    except Exception as e:
        print("Error in seed_tryon_samples:", e)
        return {"status": "error", "message": str(e)}


def insert_outfit_score(data):
    if not supabase:
        raise Exception("Supabase client not initialized.")
    user_id = data.get("user_id")
    if user_id and not is_valid_uuid(user_id):
        raise Exception(f"user_id '{user_id}' is not a valid UUID")
    return supabase.table("outfit_scores").insert(data).execute()


def seed_products():
    return {
        "status": "deprecated",
        "message": "Direct mock seeding is deprecated. Please use the CSV import utility instead."
    }


def get_product_by_id(product_id: str):
    if not supabase:
        return None
    try:
        try:
            db_id = int(product_id)
        except ValueError:
            return None
        response = supabase.table("products").select("*").eq("id", db_id).single().execute()
        return _normalize_db_product(response.data) if response.data else None
    except Exception as e:
        print("Error in get_product_by_id:", e)
        return None


def get_products(search: str = None, category: str = None, gender: str = None, subcategory: str = None, limit: int = 20):
    if not supabase:
        return []

    query = supabase.table("products").select("*")

    if search:
        search_term = f"%{search}%"
        query = query.or_(f"title.ilike.{search_term},about_item.ilike.{search_term}")

    if category:
        query = query.ilike("breadcrumbs", f"%{category}%")

    if gender:
        query = query.ilike("breadcrumbs", f"%{gender}%")

    if subcategory:
        query = query.ilike("breadcrumbs", f"%{subcategory}%")

    db_limit = limit * 3 if gender else limit

    try:
        data = query.limit(db_limit).execute().data or []
        normalized = [_normalize_db_product(row) for row in data]
        if gender:
            g_lower = gender.lower()
            normalized = [row for row in normalized if row.get("gender") == g_lower]
        return normalized[:limit]
    except Exception as e:
        print("Error in get_products:", e)
        return []
