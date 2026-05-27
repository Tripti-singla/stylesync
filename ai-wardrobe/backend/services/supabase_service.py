from supabase import create_client
import json
import re
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


def clean_amazon_image_url(url: str) -> str:
    if not url or not isinstance(url, str):
        return url or ""
    url_lower = url.lower()
    if "amazon" in url_lower or "media-amazon" in url_lower:
        parts = url.split('/')
        if parts:
            filename = parts[-1]
            file_parts = filename.split('.')
            if len(file_parts) > 2:
                # Keep only first and last parts (removes dynamic resizing suffix segments)
                clean_filename = file_parts[0] + '.' + file_parts[-1]
                parts[-1] = clean_filename
                url = '/'.join(parts)
    return url


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
        
    normalized["image_url"] = clean_amazon_image_url(image_url)
    
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
        nodes = [n.strip() for n in re.split(r"\s*(?:[›>»\x9b\uFFFD]|\u00e2\u20ac\u00ba)\s*", breadcrumbs) if n.strip()]
        if nodes:
            subcat = nodes[-1].lower()
            
    normalized["category"] = subcat or "clothing"
    normalized["subcategory"] = subcat or "clothing"
    
    # 10. Tags, Occasion, Season
    tags_val = row.get("tags") or ([subcat] if subcat else [])
    normalized["tags"] = tags_val
    normalized["occasion"] = row.get("occasion") or ["casual"]
    normalized["season"] = row.get("season") or ["all-season"]
    normalized["size_chart"] = row.get("size_chart") or {"S": {}, "M": {}, "L": {}, "XL": {}}
    normalized["created_at"] = row.get("created_at")
    
    # 11. Extract and normalize primary_color
    color_tags = [t for t in tags_val if isinstance(t, str) and t.startswith("color:")]
    if color_tags:
        normalized["primary_color"] = color_tags[0].split(":")[1]
    else:
        # Title keywords color extraction
        title_lower = (row.get("title") or "").lower()
        COLOR_KEYWORDS = ["black", "white", "grey", "gray", "silver", "navy", "blue", "denim", "indigo", "beige", "khaki", "tan", "sand", "brown", "chocolate", "red", "burgundy", "maroon", "orange", "peach", "yellow", "gold", "mustard", "green", "olive", "emerald", "mint", "pink", "rose", "coral", "purple", "violet", "lavender", "plum"]
        found_color = None
        for color in COLOR_KEYWORDS:
            if re.search(r'\b' + re.escape(color) + r'\b', title_lower):
                found_color = color
                break
        if found_color:
            normalized["primary_color"] = found_color
        else:
            # Fallback based on demo titles
            if "coofandy" in title_lower:
                normalized["primary_color"] = "grey"
            elif "valanch" in title_lower:
                normalized["primary_color"] = "blue"
            elif "oygsieg" in title_lower:
                normalized["primary_color"] = "grey"
            elif "zity" in title_lower:
                normalized["primary_color"] = "grey"
            else:
                normalized["primary_color"] = "grey"
    
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


def _int_id_to_uuid(int_id) -> str:
    try:
        val = int(int_id)
        return f"00000000-0000-0000-0000-{val:012d}"
    except (ValueError, TypeError):
        return str(int_id)


def _uuid_to_int_id(uuid_str: str) -> str:
    if not uuid_str:
        return ""
    if uuid_str.startswith("00000000-0000-0000-0000-"):
        try:
            return str(int(uuid_str.split("-")[-1]))
        except ValueError:
            pass
    return uuid_str


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


def clean_search_query(q: str) -> str:
    if not q:
        return ""
    q_lower = q.lower().strip()
    
    # Strip common prefixes
    prefixes = [
        "what should i wear with ",
        "what should i wear for ",
        "what should i wear ",
        "what matches ",
        "give me a ",
        "give me ",
        "suggest a ",
        "suggest ",
        "best outfit for a ",
        "best outfit for ",
        "style tips for ",
        "style tips ",
        "outfit for a ",
        "outfit for "
    ]
    for prefix in prefixes:
        if q_lower.startswith(prefix):
            q = q[len(prefix):]
            q_lower = q.lower().strip()
            
    # Strip common suffixes/fillers
    suffixes = [
        " outfit",
        " outfits"
    ]
    for suffix in suffixes:
        if q_lower.endswith(suffix):
            q = q[:-len(suffix)]
            q_lower = q.lower().strip()
            
    # Strip trailing question mark
    q = q.rstrip('?').strip()
    return q


def get_products(search: str = None, category: str = None, gender: str = None, subcategory: str = None, limit: int = 20):
    if not supabase:
        return []

    query = supabase.table("products").select("*")

    if search:
        cleaned_search = clean_search_query(search)
        if cleaned_search:
            search_term = f"%{cleaned_search}%"
            words = [w for w in cleaned_search.lower().split() if len(w) > 1]
            if len(words) > 1:
                or_parts = []
                for w in words:
                    or_parts.append(f"title.ilike.%{w}%")
                    or_parts.append(f"about_item.ilike.%{w}%")
                query = query.or_(",".join(or_parts))
            else:
                query = query.or_(f"title.ilike.{search_term},about_item.ilike.{search_term}")

    if category:
        cat_lower = category.lower()
        # Import CATEGORY_BREADCRUMB_MAP inside the function to avoid circular imports
        from services.recommendation_service import CATEGORY_BREADCRUMB_MAP
        if cat_lower in CATEGORY_BREADCRUMB_MAP:
            keywords = CATEGORY_BREADCRUMB_MAP[cat_lower]
            or_conditions = ",".join([f"breadcrumbs.ilike.%{kw}%" for kw in keywords])
            query = query.or_(or_conditions)
        else:
            query = query.ilike("breadcrumbs", f"%{category}%")

    if gender:
        g_lower = gender.lower()
        if g_lower == "men":
            query = query.ilike("breadcrumbs", "%men%").not_.ilike("breadcrumbs", "%women%")
        elif g_lower == "women":
            query = query.ilike("breadcrumbs", "%women%")
        else:
            query = query.ilike("breadcrumbs", f"%{gender}%")

    if subcategory:
        query = query.ilike("breadcrumbs", f"%{subcategory}%")

    # Increase query limit for ranking to have enough candidates for post-query filtering
    db_limit = max(limit * 5, 200) if gender else limit
    if search:
        db_limit = 1000

    try:
        data = query.limit(db_limit).execute().data or []
        normalized = [_normalize_db_product(row) for row in data]
        
        # Filter by gender in normalized objects if specified
        if gender:
            g_lower = gender.lower()
            normalized = [row for row in normalized if row.get("gender") == g_lower]

        # Prioritize matching logic
        if search:
            cleaned_search = clean_search_query(search)
            s_lower = cleaned_search.lower() if cleaned_search else search.lower()
            s_words = [w for w in s_lower.split() if len(w) > 1]
            
            def get_search_score(item):
                title = (item.get("title") or "").lower()
                desc = (item.get("description") or "").lower()
                
                # Full matches are highest priority
                if s_lower == title:
                    return 100
                elif s_lower in title:
                    return 80
                elif s_lower in desc:
                    return 60
                
                # Keyword matches
                if s_words:
                    matched_score = 0
                    for w in s_words:
                        if w in title:
                            matched_score += 5
                        elif w in desc:
                            matched_score += 2
                    return matched_score
                return 0

            normalized.sort(key=get_search_score, reverse=True)
            normalized = [item for item in normalized if get_search_score(item) > 0]

        return normalized[:limit]
    except Exception as e:
        print("Error in get_products:", e)
        return []


def delete_wardrobe_item(item_id: str, user_id: str) -> bool:
    if not supabase:
        return False
    if not is_valid_uuid(user_id):
        print(f"Cannot delete_wardrobe_item: user_id '{user_id}' is not a valid UUID")
        return False
    try:
        if is_valid_uuid(item_id):
            supabase.table("wardrobe_items").delete().eq("id", item_id).eq("user_id", user_id).execute()
            return True
        return False
    except Exception as e:
        print("Error in delete_wardrobe_item:", e)
        return False


def get_wishlist(user_id: str):
    if not supabase:
        return []
    if not is_valid_uuid(user_id):
        print(f"Skipping get_wishlist: user_id '{user_id}' is not a valid UUID")
        return []
    try:
        wishlist_data = supabase.table("wishlist").select("product_id").eq("user_id", user_id).execute().data or []
        db_ids = []
        for item in wishlist_data:
            uuid_id = item.get("product_id")
            if uuid_id:
                int_id = _uuid_to_int_id(uuid_id)
                try:
                    db_ids.append(int(int_id))
                except ValueError:
                    pass
        if not db_ids:
            return []
        
        products_data = supabase.table("products").select("*").in_("id", db_ids).execute().data or []
        id_to_product = {str(p.get("id")): _normalize_db_product(p) for p in products_data}
        ordered_products = []
        for item in wishlist_data:
            uuid_id = item.get("product_id")
            int_id = _uuid_to_int_id(uuid_id)
            if int_id in id_to_product:
                ordered_products.append(id_to_product[int_id])
        return ordered_products
    except Exception as e:
        print("Error in get_wishlist:", e)
        return []


def add_to_wishlist(user_id: str, product_id: str):
    if not supabase:
        return None
    if not is_valid_uuid(user_id):
        print(f"Cannot add_to_wishlist: user_id '{user_id}' is not a valid UUID")
        return None
    try:
        uuid_product_id = _int_id_to_uuid(product_id)
        res = supabase.table("wishlist").insert({
            "user_id": user_id,
            "product_id": uuid_product_id
        }).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print("Error in add_to_wishlist:", e)
        return None


def remove_from_wishlist(user_id: str, product_id: str) -> bool:
    if not supabase:
        return False
    if not is_valid_uuid(user_id):
        print(f"Cannot remove_from_wishlist: user_id '{user_id}' is not a valid UUID")
        return False
    try:
        uuid_product_id = _int_id_to_uuid(product_id)
        supabase.table("wishlist").delete().eq("user_id", user_id).eq("product_id", uuid_product_id).execute()
        return True
    except Exception as e:
        print("Error in remove_from_wishlist:", e)
        return False

