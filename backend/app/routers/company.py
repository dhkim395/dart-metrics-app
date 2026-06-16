"""
종목 분석 라우터.
GET /company/{stock_code}/metrics  →  10개 지표
GET /company/{stock_code}/trend    →  분기별 추이

캐싱:
- metrics: TTL 1시간 (주가가 매일 변하지만, 시간 단위 변동은 작음)
- trend: TTL 24시간 (분기 데이터는 거의 안 변함)
"""
import sys
from fastapi import APIRouter, HTTPException, Query

from app.config import DART_CLIENT_PATH
from app.cache import cache  # ⭐ 추가

if DART_CLIENT_PATH not in sys.path:
    sys.path.insert(0, DART_CLIENT_PATH)

from dart_client import (
    analyze_by_stock_code,
    get_quarterly_trend,
    get_company_by_stock_code,
)

from app.models import TrendResponse, QuarterData


router = APIRouter(prefix="/company", tags=["company"])


# 캐시 TTL 설정 (초 단위)
METRICS_TTL = 60 * 60        # 1시간
TREND_TTL = 60 * 60 * 24      # 24시간


@router.get("/{stock_code}/metrics")
async def get_metrics(
    stock_code: str,
    year: int = Query(2025, ge=2020, le=2030),
    reprt_code: str = Query("11011"),
):
    """
    종목코드로 10개 재무 지표 분석.
    캐시 TTL: 1시간
    """
    # ⭐ 캐시 키 생성
    cache_key = f"metrics:{stock_code}:{year}:{reprt_code}"
    
    # ⭐ 캐시 조회
    cached = cache.get(cache_key)
    if cached:
        # 캐시 적중! 응답에 표시
        cached["_cache"] = "HIT"
        return cached
    
    # 캐시 미스 → 실제 계산
    result = analyze_by_stock_code(
        stock_code=stock_code,
        year=year,
        reprt_code=reprt_code,
        verbose=False,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # ⭐ 캐시 저장
    cache.set(cache_key, result, ttl_seconds=METRICS_TTL)
    result["_cache"] = "MISS"  # 첫 호출 표시
    return result


@router.get("/{stock_code}/trend", response_model=TrendResponse)
async def get_trend(
    stock_code: str,
    year: int = Query(2025, ge=2020, le=2030),
    fs_div: str = Query("CFS"),
):
    """
    분기별 추이 (4개 분기 시계열).
    캐시 TTL: 24시간 (분기 데이터는 거의 변하지 않음)
    """
    # ⭐ 캐시 키
    cache_key = f"trend:{stock_code}:{year}:{fs_div}"
    
    # ⭐ 캐시 조회
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # 캐시 미스 → 실제 수집
    company = get_company_by_stock_code(stock_code)
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"종목코드를 찾을 수 없음: {stock_code}",
        )
    
    trend = get_quarterly_trend(company["corp_code"], year, fs_div)
    if not trend:
        raise HTTPException(status_code=500, detail="추이 데이터 수집 실패")
    
    quarters = []
    for q in trend:
        if "error" in q:
            quarters.append(QuarterData(quarter=q["quarter"]))
        else:
            quarters.append(QuarterData(
                quarter=q["quarter"],
                매출액=q.get("매출액"),
                영업이익=q.get("영업이익"),
                당기순이익=q.get("당기순이익"),
                자본총계=q.get("자본총계"),
                출처=q.get("출처"),
            ))
    
    response = TrendResponse(
        stock_code=stock_code,
        company_name=company["name"],
        quarters=quarters,
        count=len(quarters),
    )
    
    # ⭐ 캐시 저장
    cache.set(cache_key, response.model_dump(), ttl_seconds=TREND_TTL)
    return response