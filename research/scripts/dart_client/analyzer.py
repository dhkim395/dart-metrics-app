"""
종목 분석 통합 함수.
재무 + 발행주식수 + 주가 → 10개 지표.
나중에 백엔드 API에서 이 함수를 그대로 호출.
"""
from .financials import get_financial_data
from .shares import get_shares_outstanding
from .price import get_current_price
from .metrics import calculate_metrics


def analyze_company(
    name: str,
    corp_code: str,
    stock_code: str,
    year: int = 2025,
    reprt_code: str = "11011",
    verbose: bool = True,
) -> dict:
    """
    한 회사의 전 과정 분석.
    
    Args:
        name: 회사명 (출력용)
        corp_code: DART 고유번호
        stock_code: KRX 종목코드
        year: 사업연도 (기본 2025)
        reprt_code: 보고서 코드 (기본 사업보고서)
        verbose: True면 진행 상황 출력
    
    Returns:
        dict: 회사명 + 10개 지표 + 메타데이터
        실패 시 {"회사명": ..., "error": "..."}
    """
    if verbose:
        print(f"\n[{name}] 분석 중...", end=" ")
    
    # 1. 재무
    fin = get_financial_data(corp_code, year, reprt_code)
    if "error" in fin:
        if verbose:
            print(f"❌ 재무: {fin['error']}")
        return {"회사명": name, "error": fin["error"]}
    
    # 2. 발행주식수
    shares = get_shares_outstanding(corp_code, year, reprt_code)
    if "error" in shares or not shares.get("보통주_유통"):
        if verbose:
            print(f"❌ 발행주식수")
        return {"회사명": name, "error": "발행주식수 없음"}
    
    # 3. 주가
    price_data = get_current_price(stock_code)
    if "error" in price_data:
        if verbose:
            print(f"❌ 주가: {price_data['error']}")
        return {"회사명": name, "error": price_data["error"]}
    
    # 4. 지표 계산
    metrics = calculate_metrics(fin, shares, price_data["close"])
    if "error" in metrics:
        if verbose:
            print(f"❌ 지표: {metrics['error']}")
        return {"회사명": name, "error": metrics["error"]}
    
    if verbose:
        print(f"✅ (주가 {price_data['close']:,}원)")
    
    return {
        "회사명": name,
        "종목코드": stock_code,
        "기준연도": year,
        "주가": price_data["close"],
        "주가날짜": price_data["date"],
        "EPS": metrics["EPS"],
        "SPS": metrics["SPS"],
        "BPS": metrics["BPS"],
        "DPS": metrics["DPS"],
        "PER": metrics["PER"],
        "PSR": metrics["PSR"],
        "PBR": metrics["PBR"],
        "ROE(%)": metrics["ROE(%)"],
        "배당성향(%)": metrics["배당성향(%)"],
        "EV/EBITDA": metrics["EV/EBITDA"],
        "시가총액(조)": round(metrics["_시가총액"] / 1e12, 1),
        "적자여부": metrics["_적자여부"],
        "EBITDA방식": metrics["_EBITDA_방식"],
    }