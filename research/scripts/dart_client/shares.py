"""
DART에서 발행주식수 정보를 가져온다.
"""
import requests
import pandas as pd
from .config import DART_API_KEY, DART_BASE_URL


def _safe_int(val) -> int:
    """문자열을 안전하게 정수로 변환. 빈값/하이픈은 0."""
    if val is None:
        return 0
    s = str(val).strip()
    if not s or s == "-" or s == "":
        return 0
    try:
        return int(s.replace(",", ""))
    except (ValueError, AttributeError):
        return 0


def get_shares_outstanding(corp_code: str, year: int, reprt_code: str) -> dict:
    """
    DART '주식의 총수 현황' API로 발행주식수를 가져온다.
    
    두 가지 증권 표기 방식 모두 지원:
    - "보통주" / "우선주" (삼성전자 등)
    - "의결권 있는 주식" / "의결권 없는 주식" (셀트리온 등)
    
    Args:
        corp_code: DART 기업 고유번호
        year: 사업연도
        reprt_code: 보고서 코드
    
    Returns:
        dict: 보통주_발행, 보통주_자기주식, 보통주_유통,
              우선주_발행, 우선주_유통, 증권표기방식
    """
    url = f"{DART_BASE_URL}/stockTotqySttus.json"
    params = {
        "crtfc_key": DART_API_KEY,
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": reprt_code,
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        return {"error": f"네트워크 오류: {e}"}
    
    if data.get("status") != "000":
        return {"error": f"DART {data.get('status')}: {data.get('message')}"}
    
    df = pd.DataFrame(data["list"])

    result = {
        "corp_code": corp_code,
        "year": year,
        "보통주_발행": 0,
        "보통주_자기주식": 0,
        "보통주_유통": 0,
        "우선주_발행": 0,
        "우선주_유통": 0,
        "증권표기방식": "",
    }
    
    for _, row in df.iterrows():
        se = str(row.get("se", "")).strip()
        
        # 보통주 (또는 의결권 있는 주식)
        if se in ("합계", "비고"):
            continue

        if "보통주" in se:
            result["보통주_발행"] = _safe_int(row.get("istc_totqy"))
            result["보통주_자기주식"] = _safe_int(row.get("tesstk_co"))
            result["보통주_유통"] = _safe_int(row.get("distb_stock_co"))
            result["증권표기방식"] = se
        
        # 우선주 (또는 의결권 없는 주식)
        elif "우선주" in se:
            result["우선주_발행"] = _safe_int(row.get("istc_totqy"))
            result["우선주_유통"] = _safe_int(row.get("distb_stock_co"))
    
    return result

def get_shares_outstanding_with_fallback(
    corp_code: str,
    year: int,
    reprt_code: str,
) -> dict:
    """
    발행주식수 조회 with fallback.
    
    1. 요청한 보고서에서 시도
    2. 없으면 같은 해 반기보고서 시도
    3. 없으면 같은 해 사업보고서 시도
    4. 없으면 전년도 사업보고서 시도
    """
    # 1차: 요청한 보고서
    result = get_shares_outstanding(corp_code, year, reprt_code)
    if "error" not in result and result.get("보통주_유통"):
        return result
    
    # 2차: 같은 해 반기보고서 (1Q일 때만 의미 있음)
    if reprt_code == "11013":
        result = get_shares_outstanding(corp_code, year, "11012")
        if "error" not in result and result.get("보통주_유통"):
            result["_fallback"] = f"{year}년 반기보고서"
            return result
    
    # 3차: 같은 해 사업보고서
    if reprt_code != "11011":
        result = get_shares_outstanding(corp_code, year, "11011")
        if "error" not in result and result.get("보통주_유통"):
            result["_fallback"] = f"{year}년 사업보고서"
            return result
    
    # 4차: 전년도 사업보고서
    result = get_shares_outstanding(corp_code, year - 1, "11011")
    if "error" not in result and result.get("보통주_유통"):
        result["_fallback"] = f"{year - 1}년 사업보고서"
        return result
    
    # 5차: 2년 전 사업보고서
    result = get_shares_outstanding(corp_code, year - 2, "11011")
    if "error" not in result and result.get("보통주_유통"):
        result["_fallback"] = f"{year - 2}년 사업보고서"
        return result
    
    return {"error": "발행주식수를 어느 보고서에서도 찾을 수 없음"}