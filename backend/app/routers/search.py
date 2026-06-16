"""
종목 검색 라우터.
GET /search?q=삼성  →  검색 결과 반환
"""
import sys
from fastapi import APIRouter, Query, HTTPException

from app.config import DART_CLIENT_PATH

# research의 dart_client 패키지를 사용
if DART_CLIENT_PATH not in sys.path:
    sys.path.insert(0, DART_CLIENT_PATH)

from dart_client import search_company, get_company_by_stock_code

from app.models import SearchResponse, CompanyBasic


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="검색어 (종목명 또는 종목코드)"),
    limit: int = Query(10, ge=1, le=50, description="최대 결과 개수"),
):
    """
    종목명 또는 종목코드로 검색.
    
    - **q**: 검색어 (예: "삼성", "005930")
    - **limit**: 최대 결과 (기본 10, 최대 50)
    """
    results = search_company(q, limit=limit)
    return SearchResponse(
        query=q,
        count=len(results),
        results=[CompanyBasic(**r) for r in results],
    )


@router.get("/code/{stock_code}", response_model=CompanyBasic)
async def get_by_code(stock_code: str):
    """
    종목코드로 정확히 일치하는 회사 조회.
    
    - **stock_code**: KRX 종목코드 (6자리)
    """
    company = get_company_by_stock_code(stock_code)
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"종목코드를 찾을 수 없음: {stock_code}",
        )
    return CompanyBasic(**company)