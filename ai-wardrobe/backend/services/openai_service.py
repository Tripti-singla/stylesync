"""OpenAI recommendation service for StyleSync.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from config import OPENAI_API_KEY

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
        "You are a helpful fashion stylist assistant.",
        "Given the user's wardrobe, provide a concise recommendation for an outfit or item that pairs well with the existing pieces.",
        "Use the user's style, occasion, weather, and product metadata when available.",
        "Return your answer in a short, user-friendly format, and include a compatibility score from 1 to 100.",
        "Do not invent unavailable wardrobe items; base your answer on the wardrobe list and contextual data.",
        "",
        "User wardrobe:",
    ]

    if wardrobe_lines:
        prompt_parts.extend(wardrobe_lines)
    else:
        prompt_parts.append("- No wardrobe items provided.")

    prompt_parts.append("")
    prompt_parts.append(f"User request: {query}")
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

    prompt_parts.append("")
    prompt_parts.append(
        "Please provide the recommendation and a brief reason. "
        "If possible, suggest one or two matching pieces and a compatibility score."
    )

    return "\n".join(prompt_parts)


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
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for OpenAI recommendations.")

    if OPENAI_CLIENT is None:
        raise RuntimeError("OpenAI client could not be initialized. Check your openai package installation.")

    prompt = _build_openai_prompt(
        wardrobe=wardrobe,
        query=query,
        occasion=occasion,
        gender=gender,
        style=style,
        weather=weather,
        product_metadata=product_metadata,
    )

    messages = [
        {"role": "system", "content": "You are a helpful fashion stylist assistant."},
        {"role": "user", "content": prompt},
    ]

    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=320,
        )
        content = response.choices[0].message.content
    except Exception as err:
        logger.warning("OpenAI chat completion failed, trying fallback conversation API: %s", err)
        try:
            import openai as openai_fallback

            openai_fallback.api_key = OPENAI_API_KEY
            response = openai_fallback.ChatCompletion.create(
                model="gpt-4.1-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=320,
            )
            content = response.choices[0].message.content
        except Exception as err2:
            logger.error("OpenAI fallback also failed: %s", err2)
            raise RuntimeError(f"OpenAI recommendation failed: {err2}")

    parsed: Optional[Dict[str, Any]] = None
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = None

    return {
        "model": "gpt-4.1-mini",
        "recommendation": content,
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
