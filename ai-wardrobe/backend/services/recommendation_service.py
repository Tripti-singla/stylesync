# from typing import Dict, List, Tuple

# from services.external_api_service import fetch_products_rapidapi


# def _as_list(value):
#     if value is None:
#         return []
#     if isinstance(value, list):
#         return value
#     return [value]


# def _score_item(
#     item: Dict,
#     occasion: str,
#     category: str = None,
#     primary_color: str = None,
#     tags: List[str] = None,
# ) -> int:
#     score = 0
#     occasion_l = (occasion or "").lower()
#     category_l = (category or "").lower()
#     primary_color_l = (primary_color or "").lower()
#     tags_l = {t.lower() for t in (tags or [])}

#     item_occasion = {o.lower() for o in _as_list(item.get("occasion"))}
#     item_tags = {t.lower() for t in _as_list(item.get("tags") or item.get("detected_tags"))}
#     item_category = (item.get("category") or "").lower()
#     item_primary_color = (item.get("primary_color") or "").lower()

#     if occasion_l and occasion_l in item_occasion:
#         score += 40
#     if category_l and category_l == item_category:
#         score += 20
#     if primary_color_l and item_primary_color and primary_color_l == item_primary_color:
#         score += 10
#     score += min(len(tags_l.intersection(item_tags)) * 8, 24)

#     return score


# def _rank_items(
#     items: List[Dict],
#     occasion: str,
#     category: str = None,
#     primary_color: str = None,
#     tags: List[str] = None,
# ) -> List[Dict]:
#     ranked: List[Tuple[int, Dict]] = []
#     for item in items:
#         score = _score_item(
#             item=item,
#             occasion=occasion,
#             category=category,
#             primary_color=primary_color,
#             tags=tags,
#         )
#         ranked.append((score, item))

#     ranked.sort(key=lambda row: row[0], reverse=True)
#     return [{**item, "match_score": score} for score, item in ranked]


# def build_outfit_matches(
#     user_id: str,
#     occasion: str,
#     category: str = None,
#     gender: str = None,
#     primary_color: str = None,
#     tags: List[str] = None,
#     limit: int = 10,
# ) -> Dict:
#     wardrobe_items = get_wardrobe(user_id) or []
#     ranked_wardrobe = _rank_items(
#         wardrobe_items,
#         occasion=occasion,
#         category=category,
#         primary_color=primary_color,
#         tags=tags,
#     )

#     strong_wardrobe_matches = [item for item in ranked_wardrobe if item.get("match_score", 0) >= 40][:limit]

#     if strong_wardrobe_matches:
#         return {
#             "strategy": "wardrobe_first",
#             "occasion": occasion,
#             "wardrobe_matches": strong_wardrobe_matches,
#             "external_matches": [],
#             "message": "Found good matching items in your wardrobe.",
#         }

#     # Get DB products
# external_items = get_products(
#     search=occasion,
#     category=category,
#     gender=gender,
#     limit=max(limit * 2, limit),
# ) or []

# # Add RapidAPI products
# try:
#     rapid_items = fetch_products_rapidapi(occasion or "fashion")
# except Exception:
#     rapid_items = []

# # Merge both
# external_items = external_items + rapid_items

#     ranked_external = _rank_items(
#         external_items,
#         occasion=occasion,
#         category=category,
#         primary_color=primary_color,
#         tags=tags,
#     )

#     return {
#         "strategy": "external_fallback",
#         "occasion": occasion,
#         "wardrobe_matches": ranked_wardrobe[:limit],
#         "external_matches": ranked_external[:limit],
#         "message": "No strong wardrobe match found. Showing matching products from ecommerce APIs.",
#     }


from typing import Dict, List, Tuple

from services.supabase_service import get_wardrobe, get_products
from services.external_api_service import fetch_products_rapidapi


def _as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _score_item(item: Dict, occasion: str, category: str = None, primary_color: str = None, tags: List[str] = None) -> int:
    score = 0
    occasion_l = (occasion or "").lower()
    category_l = (category or "").lower()
    primary_color_l = (primary_color or "").lower()
    tags_l = {t.lower() for t in (tags or [])}

    item_occasion = {o.lower() for o in _as_list(item.get("occasion"))}
    item_tags = {t.lower() for t in _as_list(item.get("tags") or item.get("detected_tags"))}
    item_category = (item.get("category") or "").lower()
    item_primary_color = (item.get("primary_color") or "").lower()

    if occasion_l and occasion_l in item_occasion:
        score += 40
    if category_l and category_l == item_category:
        score += 20
    if primary_color_l and item_primary_color and primary_color_l == item_primary_color:
        score += 10

    score += min(len(tags_l.intersection(item_tags)) * 8, 24)
    return score


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
) -> Dict:

    # 🔹 Wardrobe
    wardrobe_items = get_wardrobe(user_id) or []

    ranked_wardrobe = _rank_items(
        wardrobe_items,
        occasion,
        category,
        primary_color,
        tags,
    )

    strong_matches = [item for item in ranked_wardrobe if item.get("match_score", 0) >= 40][:limit]

    if strong_matches:
        return {
            "strategy": "wardrobe_first",
            "occasion": occasion,
            "wardrobe_matches": strong_matches,
            "external_matches": [],
            "message": "Found good matching items in your wardrobe.",
        }

    # 🔹 DB products
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

    return {
        "strategy": "external_fallback",
        "occasion": occasion,
        "wardrobe_matches": ranked_wardrobe[:limit],
        "external_matches": ranked_external[:limit],
        "message": "Showing matching products from APIs.",
    }