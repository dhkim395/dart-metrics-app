"""
DART API 클라이언트 패키지.

사용 예:
    from dart_client import analyze_company
    
    result = analyze_company("삼성전자", "00126380", "005930")
"""
from .analyzer import analyze_company
from .financials import get_financial_data
from .shares import get_shares_outstanding
from .price import get_current_price
from .metrics import calculate_metrics

__all__ = [
    "analyze_company",
    "get_financial_data",
    "get_shares_outstanding",
    "get_current_price",
    "calculate_metrics",
]

__version__ = "0.1.0"