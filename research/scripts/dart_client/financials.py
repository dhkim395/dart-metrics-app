"""
DART에서 재무제표 데이터를 가져와 7개 원천 데이터를 추출한다.
"""
import requests
import pandas as pd
from .config import DART_API_KEY, DART_BASE_URL


def get_financial_data(
    corp_code: str,
    year: int,
    reprt_code: str,
    fs_div: str = "CFS",
) -> dict:
    """
    DART '단일회사 전체 재무제표' API로 7개 원천 데이터를 추출한다.
    
    Args:
        corp_code: DART 기업 고유번호 (8자리)
        year: 사업연도 (예: 2025)
        reprt_code: 보고서 코드 (11011=사업, 11014=3Q, 11012=반기, 11013=1Q)
        fs_div: CFS(연결) 또는 OFS(별도)
    
    Returns:
        dict: 매출액, 영업이익, 당기순이익, 자본총계, 부채총계,
              현금성자산, 감가상각비, 영업활동현금흐름, 배당금, EBITDA
        실패 시 {"error": "..."}
    
    Notes:
        - 감가상각비 누락 시 영업활동현금흐름을 EBITDA 대체값으로 사용
        - thstrm_amount는 분기 단독값 (분기보고서일 때)
        - 사업보고서일 때 연간 합계
    """
    url = f"{DART_BASE_URL}/fnlttSinglAcntAll.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": reprt_code,
        "fs_div": fs_div,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"네트워크 오류: {e}"}
    
    if data.get("status") != "000":
        return {
            "error": f"DART {data.get('status')}: {data.get('message')}",
            "corp_code": corp_code,
            "year": year,
        }
    
    df = pd.DataFrame(data["list"])
    
    # 7개 원천 데이터 + α
    target_ids = {
        "매출액": ["ifrs-full_Revenue", "ifrs_Revenue"],
        "영업이익": ["dart_OperatingIncomeLoss"],
        "당기순이익": ["ifrs-full_ProfitLoss"],
        "자본총계": ["ifrs-full_Equity"],
        "부채총계": ["ifrs-full_Liabilities"],
        "현금성자산": ["ifrs-full_CashAndCashEquivalents"],
        "감가상각비": [
            "dart_DepreciationAndAmortisationExpense",
            "dart_DepreciationExpense",
            "ifrs-full_DepreciationExpense",
        ],
        "영업활동현금흐름": [
            "ifrs-full_CashFlowsFromUsedInOperatingActivities",
            "dart_CashFlowsFromOperatingActivities",
        ],
        "배당금": [
            "ifrs-full_DividendsPaidClassifiedAsFinancingActivities",
            "ifrs-full_DividendsPaid",
            "dart_DividendsPaid",
        ],
        "자기주식취득": ["ifrs-full_PurchaseOfTreasuryShares"],
    }
    
    result = {
        "corp_code": corp_code,
        "year": year,
        "reprt_code": reprt_code,
        "fs_div": fs_div,
    }
    
    for name, ids in target_ids.items():
        found = df[df["account_id"].isin(ids)]
        if not found.empty:
            amount_str = found.iloc[0]["thstrm_amount"]
            try:
                amount = int(amount_str.replace(",", "")) if amount_str and amount_str.strip() else None
                if amount is not None and name in ["배당금", "자기주식취득"]:
                    amount = abs(amount)
            except (ValueError, AttributeError):
                amount = None
            result[name] = amount
        else:
            result[name] = None
    
    # EBITDA 계산 (정공법 우선, 안 되면 근사치)
    if result["감가상각비"] is not None and result["영업이익"] is not None:
        result["EBITDA"] = result["영업이익"] + result["감가상각비"]
        result["EBITDA_방식"] = "정공법"
    elif result["영업활동현금흐름"] is not None:
        result["EBITDA"] = result["영업활동현금흐름"]
        result["EBITDA_방식"] = "근사치 (영업활동현금흐름)"
    else:
        result["EBITDA"] = None
        result["EBITDA_방식"] = "계산 불가"
    
    return result