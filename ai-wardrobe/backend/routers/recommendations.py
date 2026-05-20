from fastapi import APIRouter, HTTPException

from models.schemas import OpenAIRecommendationRequest, OutfitMatchRequest, WardrobeUploadRequest
from services.openai_service import get_outfit_recommendation
from services.recommendation_service import build_outfit_matches
from services.supabase_service import add_wardrobe_item

router = APIRouter()


@router.post("/wardrobe/items")
async def create_wardrobe_item(req: WardrobeUploadRequest):
    try:
        item = add_wardrobe_item(req.model_dump())
        return {"status": "saved", "item": item}
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/recommendations/outfit")
async def recommend_outfit(req: OutfitMatchRequest):
    try:
        result = build_outfit_matches(
            user_id=req.user_id,
            occasion=req.occasion,
            category=req.category,
            gender=req.gender,
            primary_color=req.primary_color,
            tags=req.tags,
            limit=req.limit,
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/recommendations/openai")
async def recommend_outfit_openai(req: OpenAIRecommendationRequest):
    try:
        result = get_outfit_recommendation(
            wardrobe=req.wardrobe,
            query=req.query,
            occasion=req.occasion,
            gender=req.gender,
            style=req.style,
            weather=req.weather,
            product_metadata=req.product_metadata,
            limit=req.limit,
        )
        return result
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))
