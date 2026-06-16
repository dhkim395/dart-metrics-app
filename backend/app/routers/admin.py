"""
관리자 도구 라우터 (캐시 통계 등).
"""
from fastapi import APIRouter

from app.cache import cache


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/cache/stats")
async def cache_stats():
    """현재 캐시 상태 + 통계."""
    return cache.stats()


@router.delete("/cache/clear")
async def clear_cache():
    """전체 캐시 삭제."""
    count = cache.clear()
    return {"cleared": count, "message": f"{count}개 캐시 삭제됨"}