"""
DART API 클라이언트 패키지.

사용 예:
    from dart_client import search_company, analyze_company
    
    # 검색
    matches = search_company("삼성")
    
    # 분석
    result = analyze_company("삼성전자", "00126380", "005930")
"""
from .analyzer import (
    analyze_company,
    analyze_by_stock_code,
    analyze_by_search,
)
from .financials import get_financial_data
from .shares import (
    get_shares_outstanding,
    get_shares_outstanding_with_fallback,
)
from .price import get_current_price
from .metrics import calculate_metrics
from .search import (
    search_company,
    get_company_by_stock_code,
    get_company_by_corp_code,
)
from .trend import get_quarterly_trend, get_quarterly_trend_multi_year

__all__ = [
    # 검색
    "search_company",
    "get_company_by_stock_code",
    "get_company_by_corp_code",
    # 분석
    "analyze_company",
    # 개별 함수
    "get_financial_data",
    "get_shares_outstanding",
    "get_shares_outstanding_with_fallback",
    "get_current_price",
    "calculate_metrics",
    "get_quarterly_trend",
    "get_quarterly_trend_multi_year",
]

__version__ = "0.2.0"