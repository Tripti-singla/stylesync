import json
from typing import Dict, List, Tuple

from services.supabase_service import get_wardrobe, get_products
from services.external_api_service import fetch_products_rapidapi


def _as_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        value = value.strip()

        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = json.loads(value)

                if isinstance(parsed, list):
                    return parsed

                return [parsed]

            except Exception:
                pass

        return [value]

    return [str(value)]


def get_complementary_categories(category: str) -> List[str]:
    cat = (category or "").lower()
    if cat == "topwear":
        return ["bottomwear", "footwear", "accessories"]
    elif cat == "bottomwear":
        return ["topwear", "footwear", "accessories"]
    elif cat == "ethnic":
        return ["footwear", "accessories"]
    elif cat in ("footwear", "accessories"):
        return ["topwear", "bottomwear", "ethnic"]
    return []


CATEGORY_BREADCRUMB_MAP = {
    "topwear": ["shirts", "tops", "t-shirts", "blouses", "sweaters", "jackets"],
    "bottomwear": ["trousers", "jeans", "pants", "shorts", "skirts", "leggings"],
    "footwear": ["shoes", "sandals", "sneakers", "boots", "footwear"],
    "ethnic": ["kurta", "saree", "salwar", "ethnic", "lehenga"],
    "accessories": ["belts", "bags", "scarves", "watches", "accessories"],
}


def normalize_to_internal_category(raw_category: str) -> str:
    raw = (raw_category or "").lower()

    for internal, keywords in CATEGORY_BREADCRUMB_MAP.items():
        if any(keyword in raw for keyword in keywords):
            return internal

    return raw


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    try:
        hex_str = hex_str.strip().lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        if len(hex_str) == 6:
            return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
    except Exception:
        pass
    return 128, 128, 128


def rgb_to_color_category(r: int, g: int, b: int) -> str:
    # 1. Check for neutrals
    if r > 220 and g > 220 and b > 220:
        return "white"
    if r < 45 and g < 45 and b < 45:
        return "black"
    
    mx = max(r, g, b)
    mn = min(r, g, b)
    diff = mx - mn
    
    if diff < 25:
        if mx > 150:
            return "grey"
        elif mx > 45:
            return "grey"
        else:
            return "black"
            
    # Beige/Khaki vs Brown
    if r > 180 and g > 160 and 100 < b < 180 and (r - b) > 30:
        return "beige"
    if r > g and g >= b and mx < 150:
        if diff > 15:
            return "brown"
            
    # Simple Hue Calculation
    h = 0.0
    if diff > 0:
        if mx == r:
            h = (g - b) / diff
        elif mx == g:
            h = 2.0 + (b - r) / diff
        else:
            h = 4.0 + (r - g) / diff
        h *= 60.0
        if h < 0:
            h += 360.0

    # Categorize hue
    if h < 15 or h >= 345:
        return "red"
    elif h < 45:
        if mx > 180 and mn < 100:
            return "orange"
        return "brown"
    elif h < 75:
        return "yellow"
    elif h < 165:
        return "green"
    elif h < 255:
        if h >= 200 and h < 240 and mx < 80:
            return "navy"
        return "blue"
    elif h < 295:
        return "purple"
    else:
        return "pink"


def get_color_category(color_str: str) -> str:
    if not color_str:
        return "unknown"
    color_str = color_str.strip().lower()
    
    if "white" in color_str or "cream" in color_str or "off-white" in color_str:
        return "white"
    if "black" in color_str or "charcoal" in color_str or "dark grey" in color_str or "dark gray" in color_str:
        return "black"
    if "navy" in color_str or "dark blue" in color_str:
        return "navy"
    if "blue" in color_str or "denim" in color_str or "indigo" in color_str:
        return "blue"
    if "grey" in color_str or "gray" in color_str or "silver" in color_str:
        return "grey"
    if "beige" in color_str or "khaki" in color_str or "tan" in color_str or "sand" in color_str:
        return "beige"
    if "brown" in color_str or "chocolate" in color_str:
        return "brown"
    if "red" in color_str or "burgundy" in color_str or "maroon" in color_str:
        return "red"
    if "orange" in color_str or "peach" in color_str:
        return "orange"
    if "yellow" in color_str or "gold" in color_str or "mustard" in color_str:
        return "yellow"
    if "green" in color_str or "olive" in color_str or "emerald" in color_str or "mint" in color_str:
        return "green"
    if "pink" in color_str or "rose" in color_str or "coral" in color_str:
        return "pink"
    if "purple" in color_str or "violet" in color_str or "lavender" in color_str or "plum" in color_str:
        return "purple"
        
    # Process hex code
    clean_hex = color_str.lstrip("#")
    if color_str.startswith("#") or (len(clean_hex) in (3, 6) and all(c in "0123456789abcdef" for c in clean_hex)):
        try:
            r, g, b = hex_to_rgb(color_str)
            return rgb_to_color_category(r, g, b)
        except Exception:
            pass
            
    return "unknown"


COLOR_HARMONY = {
    "white": {
        "white": 6, "black": 10, "navy": 10, "blue": 9, "grey": 8, "beige": 9, "brown": 8,
        "red": 10, "orange": 9, "yellow": 9, "green": 9, "pink": 10, "purple": 9, "unknown": 5
    },
    "black": {
        "white": 10, "black": 6, "navy": 8, "blue": 9, "grey": 9, "beige": 10, "brown": 8,
        "red": 10, "orange": 9, "yellow": 10, "green": 9, "pink": 10, "purple": 9, "unknown": 5
    },
    "grey": {
        "white": 8, "black": 9, "navy": 9, "blue": 8, "grey": 5, "beige": 7, "brown": 6,
        "red": 9, "orange": 8, "yellow": 8, "green": 8, "pink": 9, "purple": 8, "unknown": 5
    },
    "beige": {
        "white": 9, "black": 10, "navy": 10, "blue": 9, "grey": 7, "beige": 5, "brown": 9,
        "red": 8, "orange": 8, "yellow": 7, "green": 9, "pink": 8, "purple": 7, "unknown": 5
    },
    "navy": {
        "white": 10, "black": 8, "navy": 5, "blue": 8, "grey": 9, "beige": 10, "brown": 8,
        "red": 9, "orange": 8, "yellow": 8, "green": 8, "pink": 9, "purple": 7, "unknown": 5
    },
    "blue": {
        "white": 9, "black": 9, "navy": 8, "blue": 6, "grey": 8, "beige": 9, "brown": 9,
        "red": 8, "orange": 7, "yellow": 8, "green": 7, "pink": 8, "purple": 7, "unknown": 5
    },
    "brown": {
        "white": 8, "black": 8, "navy": 8, "blue": 9, "grey": 6, "beige": 9, "brown": 5,
        "red": 7, "orange": 8, "yellow": 8, "green": 8, "pink": 7, "purple": 6, "unknown": 5
    },
    "red": {
        "white": 10, "black": 10, "navy": 9, "blue": 8, "grey": 9, "beige": 8, "brown": 7,
        "red": 4, "orange": 6, "yellow": 7, "green": 5, "pink": 7, "purple": 6, "unknown": 5
    },
    "orange": {
        "white": 9, "black": 9, "navy": 8, "blue": 7, "grey": 8, "beige": 8, "brown": 8,
        "red": 6, "orange": 4, "yellow": 8, "green": 6, "pink": 6, "purple": 5, "unknown": 5
    },
    "yellow": {
        "white": 9, "black": 10, "navy": 8, "blue": 8, "grey": 8, "beige": 7, "brown": 8,
        "red": 7, "orange": 8, "yellow": 4, "green": 7, "pink": 7, "purple": 8, "unknown": 5
    },
    "green": {
        "white": 9, "black": 9, "navy": 8, "blue": 7, "grey": 8, "beige": 9, "brown": 8,
        "red": 5, "orange": 6, "yellow": 7, "green": 4, "pink": 7, "purple": 6, "unknown": 5
    },
    "pink": {
        "white": 10, "black": 10, "navy": 9, "blue": 8, "grey": 9, "beige": 8, "brown": 7,
        "red": 7, "orange": 6, "yellow": 7, "green": 7, "pink": 4, "purple": 7, "unknown": 5
    },
    "purple": {
        "white": 9, "black": 9, "navy": 7, "blue": 7, "grey": 8, "beige": 7, "brown": 6,
        "red": 6, "orange": 5, "yellow": 8, "green": 6, "pink": 7, "purple": 4, "unknown": 5
    },
    "unknown": {
        "white": 5, "black": 5, "navy": 5, "blue": 5, "grey": 5, "beige": 5, "brown": 5,
        "red": 5, "orange": 5, "yellow": 5, "green": 5, "pink": 5, "purple": 5, "unknown": 5
    }
}


def _score_item(item: Dict, occasion: str, category: str = None, primary_color: str = None, tags: List[str] = None) -> int:
    score = 65
    
    occasion_l = (occasion or "").lower()
    category_l = (category or "").lower()
    primary_color_l = (primary_color or "").lower()
    tags_l = {t.lower() for t in (tags or [])}

    item_occasion = {o.lower() for o in _as_list(item.get("occasion"))}
    item_tags = {t.lower() for t in _as_list(item.get("tags") or item.get("detected_tags"))}
    raw_item_category = (item.get("category") or "").lower()
    item_category = normalize_to_internal_category(raw_item_category)
    item_primary_color = (item.get("primary_color") or "").lower()

    # 1. Occasion Match (up to 15 points)
    if occasion_l:
        if occasion_l in item_occasion:
            score += 15
        elif any(occ in occasion_l or occasion_l in occ for occ in item_occasion):
            score += 10
            
    # 2. Complementary Category Match (up to 10 points)
    comp_cats = get_complementary_categories(category_l)
    if comp_cats and item_category in comp_cats:
        score += 10
    elif category_l == item_category:
        score -= 5
        
    # 3. Color Harmony Match (up to 10 points)
    if primary_color_l and item_primary_color:
        cat_query = get_color_category(primary_color_l)
        cat_item = get_color_category(item_primary_color)
        harmony_val = COLOR_HARMONY.get(cat_query, COLOR_HARMONY["unknown"]).get(cat_item, 5)
        score += int(harmony_val)
        
    # 4. Tags overlap (up to 5 points)
    if tags_l and item_tags:
        intersect = tags_l.intersection(item_tags)
        score += min(len(intersect) * 2, 5)

    return max(0, min(score, 100))


def _rank_items(items: List[Dict], occasion: str, category=None, primary_color=None, tags=None) -> List[Dict]:
    ranked = []

    for item in items:
        score = _score_item(item, occasion, category, primary_color, tags)
        ranked.append((score, item))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [{**item, "match_score": score} for score, item in ranked]


def build_outfit_matches(
    user_id: str,
    occasion: str,
    category: str = None,
    gender: str = None,
    primary_color: str = None,
    tags: List[str] = None,
    limit: int = 10,
    exclude_item_id: str = None,
) -> Dict:

    # 🔹 Wardrobe
    wardrobe_items = get_wardrobe(user_id) or []

    # Filter out query item by ID and other items of the same category (no top-on-top matching)
    filtered_wardrobe = []
    for item in wardrobe_items:
        if exclude_item_id and str(item.get("id")) == str(exclude_item_id):
            continue
        if category and item.get("category") == category:
            continue
        filtered_wardrobe.append(item)

    ranked_wardrobe = _rank_items(
        filtered_wardrobe,
        occasion,
        category,
        primary_color,
        tags,
    )

    strong_matches = [item for item in ranked_wardrobe if item.get("match_score", 0) >= 40][:limit]

    # 🔹 DB products of complementary categories
    comp_cats = get_complementary_categories(category)
    external_items = []
    if comp_cats:
        for comp_cat in comp_cats:
            items = get_products(
                search=occasion,
                category=comp_cat,
                gender=gender,
                limit=limit,
            ) or []
            external_items.extend(items)
    else:
        external_items = get_products(
            search=occasion,
            category=category,
            gender=gender,
            limit=max(limit * 2, limit),
        ) or []

    # 🔹 RapidAPI
    try:
        rapid_items = fetch_products_rapidapi(occasion or "fashion")
    except Exception:
        rapid_items = []

    # 🔹 Merge
    external_items = external_items + rapid_items

    if not external_items:
        if comp_cats:
            for comp_cat in comp_cats:
                items = get_products(category=comp_cat, gender=gender, limit=max(limit * 3, 24)) or []
                external_items.extend(items)
        else:
            external_items = get_products(category=category, gender=gender, limit=max(limit * 3, 24)) or []

    if not external_items:
        external_items = get_products(limit=max(limit * 3, 24)) or []

    ranked_external = _rank_items(
        external_items,
        occasion,
        category,
        primary_color,
        tags,
    )

    if strong_matches:
        return {
            "strategy": "wardrobe_first",
            "occasion": occasion,
            "wardrobe_matches": strong_matches,
            "external_matches": ranked_external[:limit],
            "message": "Found good matching items in your wardrobe.",
        }

    return {
        "strategy": "external_fallback",
        "occasion": occasion,
        "wardrobe_matches": ranked_wardrobe[:limit],
        "external_matches": ranked_external[:limit],
        "message": "Showing matching products from APIs.",
    }