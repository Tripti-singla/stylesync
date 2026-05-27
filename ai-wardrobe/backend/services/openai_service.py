"""OpenAI/Gemini recommendation service for StyleSync.
"""

import json
import logging
import random
from typing import Any, Dict, List, Optional

import requests
from config import OPENAI_API_KEY, GEMINI_API_KEY
from services.recommendation_service import get_complementary_categories
from services.supabase_service import get_products
from services.external_api_service import fetch_products_rapidapi

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    OPENAI_CLIENT = None


def _build_openai_prompt(
    wardrobe: List[Dict[str, Any]],
    query: str,
    occasion: Optional[str] = None,
    gender: Optional[str] = None,
    style: Optional[str] = None,
    weather: Optional[str] = None,
    product_metadata: Optional[Dict[str, Any]] = None,
    ai_candidates: Optional[List[Dict[str, Any]]] = None,
) -> str:
    wardrobe_lines = []
    for item in wardrobe:
        name = item.get("name") or item.get("title") or "unknown item"
        category = item.get("category") or item.get("subcategory") or "unknown category"
        color = item.get("primary_color") or item.get("color") or "unknown color"
        tags = item.get("tags") or item.get("detected_tags") or []
        tags_text = ", ".join(tags) if tags else ""
        wardrobe_lines.append(f"- {name} ({category}, {color}{f', tags: {tags_text}' if tags_text else ''})")

    metadata_lines = []
    if product_metadata:
        for key, value in product_metadata.items():
            metadata_lines.append(f"- {key}: {value}")

    prompt_parts = [
        "You are a professional fashion stylist assistant.",
        "Based on the user's wardrobe, suggest how they can pair their existing wardrobe items with the item or category they are searching for.",
        "To keep styling advice fresh and diverse, pick a distinct styling theme (e.g. streetwear, chic, minimalist, bold contrast, bohemian, or elegant) based on the occasion and season, and write a unique recommendation. Avoid generic or repetitive phrasing.",
        "",
        "You must return your output in JSON format only with the following keys:",
        "  - score: a compatibility score from 1 to 100",
        "  - recommendation: a detailed and user-friendly explanation of why this pairing works and styling advice.",
        "  - pairings: list of names of wardrobe items that you selected from the user's wardrobe list to pair with this query.",
        "  - products: list of JSON objects of products you selected from the 'Available products to shop' list. Each object must have fields 'id', 'title', 'score' (relevance score 1-100), and 'reason' (brief sentence on why this product fits). Only select up to 4 products that are the best match.",
        "",
        "Do not write markdown formatting in your response (no ```json code blocks), just return the raw JSON object.",
        "",
        "User wardrobe:",
    ]

    if wardrobe_lines:
        prompt_parts.extend(wardrobe_lines)
    else:
        prompt_parts.append("- No wardrobe items provided.")

    if ai_candidates:
        prompt_parts.append("")
        prompt_parts.append("Available products to shop:")
        for prod in ai_candidates:
            p_id = prod.get("id")
            p_title = prod.get("title") or prod.get("name") or "Product"
            p_cat = prod.get("category") or "clothing"
            p_gender = prod.get("gender") or "unisex"
            p_price = prod.get("price") or 0.0
            p_desc = prod.get("description") or ""
            p_desc_short = p_desc[:100] + "..." if len(p_desc) > 100 else p_desc
            prompt_parts.append(f"- ID: {p_id} | Title: {p_title} | Category: {p_cat} | Gender: {p_gender} | Price: ${p_price} | Info: {p_desc_short}")

    prompt_parts.append("")
    prompt_parts.append(f"User is searching for: {query}")
    if occasion:
        prompt_parts.append(f"Occasion: {occasion}")
    if gender:
        prompt_parts.append(f"Gender: {gender}")
    if style:
        prompt_parts.append(f"Style: {style}")
    if weather:
        prompt_parts.append(f"Weather: {weather}")
    if metadata_lines:
        prompt_parts.append("")
        prompt_parts.append("Product metadata:")
        prompt_parts.extend(metadata_lines)

    return "\n".join(prompt_parts)


def get_local_recommendation_fallback(
    wardrobe: List[Dict[str, Any]],
    query: str,
    occasion: Optional[str] = None,
    gender: Optional[str] = None,
    style: Optional[str] = None,
    weather: Optional[str] = None,
    product_metadata: Optional[Dict[str, Any]] = None,
    ai_candidates: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    # A simple but smart local rule-based stylist
    meta = product_metadata or {}
    category = meta.get("category") or ""
    if not category and wardrobe:
        # Try to infer category from query matching wardrobe item name
        for item in wardrobe:
            if item.get("name", "").lower() in query.lower():
                category = item.get("category")
                break
    
    # Defaults
    if not category:
        category = "topwear"
        
    occasion = occasion or "casual"
    gender = gender or "unisex"
    
    # Select complementary items from user wardrobe
    comp_cats = get_complementary_categories(category)
    pairings = []
    pairing_details = []
    for item in wardrobe:
        item_cat = item.get("category") or ""
        if item_cat in comp_cats and item.get("name") not in pairings:
            pairings.append(item.get("name"))
            pairing_details.append(f"{item.get('name')} ({item.get('primary_color', 'coordinating color')})")
            if len(pairings) >= 3:
                break

    item_title = meta.get("title") or query or "StyleSync Piece"
    occ = occasion.capitalize()
    style_theme = style or "smart casual"
    weather_info = f"perfect for {weather}" if weather else "versatile for all-season wear"
    pairings_text = ", ".join(pairing_details) if pairing_details else "complementary neutrals"
    
    # Generate dynamic advice based on occasion and category
    silhouette_advice = ""
    if category == "topwear":
        silhouette_advice = f"Since you're styling topwear, the goal is to balance the upper proportions. Pairing it with {pairings_text} from your wardrobe will define a clean waistline and form a flattering silhouette."
    elif category == "bottomwear":
        silhouette_advice = f"As this is a bottomwear piece, we want to anchor the look. Pairing it with {pairings_text} creates a balanced vertical line, keeping the focus clean and highly proportional."
    elif category == "footwear":
        silhouette_advice = f"Footwear is the foundation of any outfit. Styling this with {pairings_text} ensures the visual weight is distributed beautifully, presenting an integrated and stylish look."
    else:
        silhouette_advice = f"This gorgeous {category} works wonders for structural layering! When combined with {pairings_text}, it builds a sleek, high-fashion depth that feels both deliberate and effortless."

    color_theme = "a coordinating color scheme"
    primary_color = meta.get("primary_color") or ""
    if not primary_color and wardrobe:
        for item in wardrobe:
            if item.get("name", "").lower() in query.lower():
                primary_color = item.get("primary_color")
                break
    
    if primary_color:
        color_theme = f"a palette focused around {primary_color.capitalize()}"
    
    color_advice = f"We are building {color_theme}. Combining this garment with coordinating pieces from your wardrobe avoids clashing while creating a modern color-blocked harmony."
    
    occasion_advice = ""
    if occasion == "casual":
        occasion_advice = f"For a relaxed Casual setting, keep the look easygoing. Style it with clean minimalist sneakers or flats. Roll up the sleeves slightly if layering, and finish with simple accessories."
    elif occasion == "formal":
        occasion_advice = f"To adapt this for a Formal environment, structured layering is key. Pair with a crisp blazer, tailored trousers, and leather dress shoes or elegant heels to command the room."
    elif occasion == "party":
        occasion_advice = f"For a lively Party atmosphere, lean into bold styling! Add some statement jewelry, metallic highlights, and sleek footwear to bring a vibrant energy to the look."
    elif occasion == "business":
        occasion_advice = f"Perfecting this for Business wear requires sharp, neat lines. Combine with neutral trousers or a pencil skirt, and anchor with professional oxfords or pumps."
    else:
        occasion_advice = f"To bring this look together for {occ} settings, balance comfort with tailored pieces. Layer with an unbuttoned lightweight overshirt or blazer to adapt to {weather_info} seamlessly."

    # Pro tip based on gender
    pro_tip = "Roll up the sleeves slightly or try a 'French tuck' to define your waistline and convey a relaxed yet tailored vibe."
    if gender == "men":
        pro_tip = "Pro Tip: Keep the bottom hem clean, and anchor the outfit with structured leather boots or minimalist sneakers for a sharp masculine frame."
    elif gender == "women":
        pro_tip = "Pro Tip: Define your waistline with a high-rise fit or a delicate belt, and add understated silver or gold jewelry to complete the feminine contour."

    advice = (
        f"✨ **StyleSync AI Stylist [Local Mode]**: Here is a curated styling guide to elevate your **{item_title}**!\n\n"
        f"👗 **The Silhouette & Proportions**\n"
        f"{silhouette_advice}\n\n"
        f"🎨 **Color Story & Harmony**\n"
        f"{color_advice}\n\n"
        f"💼 **Occasion Guide: {occ} ({style_theme})**\n"
        f"{occasion_advice}\n\n"
        f"🌟 **AI Stylist Tip**\n"
        f"{pro_tip}"
    )

    candidates = ai_candidates or []
    enriched_products = []
    for i, prod in enumerate(candidates[:4]):
        merged = dict(prod)
        merged["match_score"] = 90 - i * 5
        merged["ai_reason"] = f"Highly recommended option to complete your {occasion} look."
        enriched_products.append(merged)

    parsed = {
        "score": 85,
        "recommendation": advice,
        "pairings": pairings,
        "products": enriched_products
    }

    return {
        "model": "local-rules-engine",
        "recommendation": advice,
        "parsed_recommendation": parsed,
        "request": {
            "wardrobe": wardrobe,
            "query": query,
            "occasion": occasion,
            "gender": gender,
            "style": style,
            "weather": weather,
            "product_metadata": product_metadata,
        },
    }


def get_gemini_recommendation(
    wardrobe: List[Dict[str, Any]],
    query: str,
    occasion: Optional[str] = None,
    gender: Optional[str] = None,
    style: Optional[str] = None,
    weather: Optional[str] = None,
    product_metadata: Optional[Dict[str, Any]] = None,
    limit: int = 6,
    ai_candidates: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")

    prompt = _build_openai_prompt(
        wardrobe=wardrobe,
        query=query,
        occasion=occasion,
        gender=gender,
        style=style,
        weather=weather,
        product_metadata=product_metadata,
        ai_candidates=ai_candidates,
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.85,
            "maxOutputTokens": 8192
        }
    }

    import time
    response = None
    resp_json = None
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            if response.status_code == 429:
                print(f"Gemini API rate limited (429), retrying in {2 * (attempt + 1)}s... (attempt {attempt+1}/3)")
                time.sleep(2 * (attempt + 1))
                continue
            response.raise_for_status()
            resp_json = response.json()
            break
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))
            
    if resp_json is None:
        raise ValueError("Failed to get response from Gemini API after retries")
    
    try:
        content = resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"Failed to parse Gemini response: {resp_json}") from e

    content_clean = content.strip()
    if content_clean.startswith("```"):
        lines = content_clean.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content_clean = "\n".join(lines).strip()

    parsed = json.loads(content_clean)
    
    # Enrich the returned products with full database metadata
    if parsed.get("products") and ai_candidates:
        candidates_by_id = {str(prod.get("id")): prod for prod in ai_candidates}
        enriched_products = []
        for p_item in parsed["products"]:
            p_id = str(p_item.get("id"))
            orig_prod = candidates_by_id.get(p_id)
            if orig_prod:
                merged = dict(orig_prod)
                merged["match_score"] = p_item.get("score", 85)
                merged["ai_reason"] = p_item.get("reason", "")
                enriched_products.append(merged)
        parsed["products"] = enriched_products

    return {
        "model": "gemini-flash-latest",
        "recommendation": parsed.get("recommendation", content),
        "parsed_recommendation": parsed,
        "request": {
            "wardrobe": wardrobe,
            "query": query,
            "occasion": occasion,
            "gender": gender,
            "style": style,
            "weather": weather,
            "product_metadata": product_metadata,
            "limit": limit,
        },
    }


def get_outfit_recommendation(
    wardrobe: List[Dict[str, Any]],
    query: str,
    occasion: Optional[str] = None,
    gender: Optional[str] = None,
    style: Optional[str] = None,
    weather: Optional[str] = None,
    product_metadata: Optional[Dict[str, Any]] = None,
    limit: int = 6,
) -> Dict[str, Any]:
    # 1. Identify selected wardrobe item and category
    selected_item = None
    if wardrobe:
        for item in wardrobe:
            if item.get("name", "").lower() in query.lower():
                selected_item = item
                break
        if not selected_item:
            selected_item = wardrobe[0]
            
    selected_category = selected_item.get("category") if selected_item else "topwear"
    selected_gender = gender or "unisex"
    if selected_item and selected_item.get("gender"):
        selected_gender = selected_item.get("gender")
        
    # Use None (all genders) for unisex items to prevent empty lists due to strict filtering
    query_gender = selected_gender if selected_gender != "unisex" else None
    
    # 2. Fetch candidate products of complementary categories strictly
    candidate_products = []
    target_cats = []
    if selected_category == "topwear":
        target_cats = ["bottomwear"]
    elif selected_category == "bottomwear":
        target_cats = ["topwear"]
    else:
        target_cats = get_complementary_categories(selected_category)
        
    for comp_cat in target_cats:
        prods = get_products(category=comp_cat, gender=query_gender, limit=15)
        if not prods and query_gender:
            # Fallback to general gender/unisex for this category
            prods = get_products(category=comp_cat, gender=None, limit=15) or []
        candidate_products.extend(prods)
        
    # Fallback to general products of complementary category if catalog is small
    if len(candidate_products) < 6:
        for comp_cat in target_cats:
            prods = get_products(category=comp_cat, limit=20) or []
            candidate_products.extend(prods)
        
    # RapidAPI fetch if configured
    try:
        rapid_items = fetch_products_rapidapi(occasion or "fashion")
        if rapid_items:
            candidate_products.extend(rapid_items)
    except Exception:
        pass

    # 3. Shuffle pool and deduplicate to ensure variety and keep answers fresh
    random.shuffle(candidate_products)
    seen_ids = set()
    deduped_candidates = []
    for prod in candidate_products:
        p_id = str(prod.get("id"))
        if p_id and p_id not in seen_ids:
            seen_ids.add(p_id)
            deduped_candidates.append(prod)
            
    ai_candidates = deduped_candidates[:12]

    # 4. Attempt Gemini
    if GEMINI_API_KEY:
        try:
            logger.info("Attempting Gemini API for outfit recommendation...")
            return get_gemini_recommendation(
                wardrobe=wardrobe,
                query=query,
                occasion=occasion,
                gender=gender,
                style=style,
                weather=weather,
                product_metadata=product_metadata,
                limit=limit,
                ai_candidates=ai_candidates,
            )
        except Exception as e:
            logger.error("Gemini recommendation failed. Falling back to OpenAI...", exc_info=True)

    # 5. Fallback/Primary to OpenAI
    if not OPENAI_API_KEY or OPENAI_CLIENT is None:
        logger.warning("OpenAI API key missing or client uninitialized. Using local stylist fallback.")
        return get_local_recommendation_fallback(
            wardrobe=wardrobe,
            query=query,
            occasion=occasion,
            gender=gender,
            style=style,
            weather=weather,
            product_metadata=product_metadata,
            ai_candidates=ai_candidates,
        )

    prompt = _build_openai_prompt(
        wardrobe=wardrobe,
        query=query,
        occasion=occasion,
        gender=gender,
        style=style,
        weather=weather,
        product_metadata=product_metadata,
        ai_candidates=ai_candidates,
    )

    messages = [
        {"role": "system", "content": "You are a helpful fashion stylist assistant."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.85,
            max_tokens=1000,
        )
        content = response.choices[0].message.content
    except Exception as err:
        logger.warning("OpenAI chat completion failed, trying fallback conversation API: %s", err)
        try:
            import openai as openai_fallback

            openai_fallback.api_key = OPENAI_API_KEY
            response = openai_fallback.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.85,
                max_tokens=1000,
            )
            content = response.choices[0].message.content
        except Exception as err2:
            logger.error("OpenAI service completely unavailable, using local stylist fallback. Error: %s", err2)
            return get_local_recommendation_fallback(
                wardrobe=wardrobe,
                query=query,
                occasion=occasion,
                gender=gender,
                style=style,
                weather=weather,
                product_metadata=product_metadata,
                ai_candidates=ai_candidates,
            )

    # Strip markdown block ticks if present
    content_clean = content.strip()
    if content_clean.startswith("```"):
        lines = content_clean.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        content_clean = "\n".join(lines).strip()

    parsed: Optional[Dict[str, Any]] = None
    try:
        parsed = json.loads(content_clean)
        
        # Enrich LLM-selected products
        if parsed.get("products") and ai_candidates:
            candidates_by_id = {str(prod.get("id")): prod for prod in ai_candidates}
            enriched_products = []
            for p_item in parsed["products"]:
                p_id = str(p_item.get("id"))
                orig_prod = candidates_by_id.get(p_id)
                if orig_prod:
                    merged = dict(orig_prod)
                    merged["match_score"] = p_item.get("score", 85)
                    merged["ai_reason"] = p_item.get("reason", "")
                    enriched_products.append(merged)
            parsed["products"] = enriched_products
            
    except Exception as parse_err:
        logger.error("Failed to parse LLM JSON response: %s", parse_err)
        # Fallback dictionary if not parsable
        parsed = {
            "score": 85,
            "recommendation": content,
            "pairings": [],
            "products": []
        }

    return {
        "model": "gpt-4o-mini",
        "recommendation": parsed.get("recommendation", content),
        "parsed_recommendation": parsed,
        "request": {
            "wardrobe": wardrobe,
            "query": query,
            "occasion": occasion,
            "gender": gender,
            "style": style,
            "weather": weather,
            "product_metadata": product_metadata,
            "limit": limit,
        },
    }
