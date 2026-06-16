"""
API 응답 데이터 모델 (Pydantic).
자동으로 JSON 직렬화 + 문서화에 사용됨.
"""
from typing import Optional
from pydantic import BaseModel, Field


class CompanyBasic(BaseModel):
    """검색 결과의 기본 정보."""
    name: str = Field(..., description="회사명")
    stock_code: str = Field(..., description="KRX 종목코드 (6자리)")
    corp_code: str = Field(..., description="DART 고유번호 (8자리)")


class SearchResponse(BaseModel):
    """검색 응답."""
    query: str
    count: int
    results: list[CompanyBasic]


class CompanyMetrics(BaseModel):
    """종목 분석 결과 (10개 지표)."""
    회사명: str
    종목코드: str
    기준연도: int
    주가: int
    주가날짜: str
    
    # 주당 지표
    EPS: float
    SPS: float
    BPS: float
    DPS: Optional[float] = None
    
    # 비율
    PER: Optional[float] = None
    PSR: Optional[float] = None
    PBR: Optional[float] = None
    ROE: float = Field(..., alias="ROE(%)")
    EV_EBITDA: Optional[float] = Field(None, alias="EV/EBITDA")
    배당성향: Optional[float] = Field(None, alias="배당성향(%)")
    
    # 메타
    시가총액_조: float = Field(..., alias="시가총액(조)")
    적자여부: bool
    EBITDA방식: str
    
    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """에러 응답."""
    error: str
    detail: Optional[str] = None

# === 추이 데이터 모델 ===

class QuarterData(BaseModel):
    """한 분기의 데이터."""
    quarter: str = Field(..., description="분기 라벨 (예: 2025_1Q)")
    매출액: Optional[int] = None
    영업이익: Optional[int] = None
    당기순이익: Optional[int] = None
    자본총계: Optional[int] = None
    출처: Optional[str] = None
    
    class Config:
        populate_by_name = True


class TrendResponse(BaseModel):
    """분기별 추이 응답."""
    stock_code: str
    company_name: str
    quarters: list[QuarterData]
    count: int