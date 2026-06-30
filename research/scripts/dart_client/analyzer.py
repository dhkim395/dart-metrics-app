"""
종목 분석 통합 함수.
재무 + 발행주식수 + 주가 → 10개 지표.
나중에 백엔드 API에서 이 함수를 그대로 호출.
"""
from .financials import get_financial_data
from .shares import get_shares_outstanding_with_fallback
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
    shares = get_shares_outstanding_with_fallback(corp_code, year, reprt_code)
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

from .search import get_company_by_stock_code, search_company

# 보고서 코드 → 사람이 읽는 라벨
REPORT_LABELS = {
    "11011": "사업보고서",
    "11014": "3분기보고서",
    "11012": "반기보고서",
    "11013": "1분기보고서",
}


def find_latest_report(corp_code: str) -> tuple:
    """
    가장 최신 가용 보고서를 자동으로 찾는다.
    
    시도 순서 (최신 → 과거):
    - 올해 사업보고서 → 3Q → 반기 → 1Q
    - 작년 사업보고서 → 3Q → 반기 → 1Q
    - ... 최대 3년 전까지
    
    Returns:
        (year, reprt_code, label) 또는 None
    """
    from datetime import datetime
    current_year = datetime.now().year
    
    # 보고서 우선순위 (최신부터)
    report_priority = ["11011", "11014", "11012", "11013"]
    
    for year_offset in range(0, 4):  # 올해, 작년, 재작년, 3년 전
        year = current_year - year_offset
        
        for reprt_code in report_priority:
            # 빠른 체크: 재무 데이터만 시도
            from .financials import get_financial_data
            fin = get_financial_data(corp_code, year, reprt_code)
            
            if "error" not in fin and fin.get("매출액") is not None:
                label = f"{year}년 {REPORT_LABELS[reprt_code]}"
                return (year, reprt_code, label)
    
    return None


def analyze_latest(
    name: str,
    corp_code: str,
    stock_code: str,
    verbose: bool = True,
) -> dict:
    """
    가장 최신 가용 보고서로 자동 분석.
    """
    latest = find_latest_report(corp_code)
    if not latest:
        return {"회사명": name, "error": "최근 4년 내 가용 보고서 없음"}
    
    year, reprt_code, label = latest
    
    if verbose:
        print(f"📅 자동 선택: {label}")
    
    result = analyze_company(
        name=name,
        corp_code=corp_code,
        stock_code=stock_code,
        year=year,
        reprt_code=reprt_code,
        verbose=verbose,
    )
    
    if "error" not in result:
        result["_보고서_라벨"] = label
        result["_보고서_코드"] = reprt_code
    
    return result


def analyze_latest_by_stock_code(
    stock_code: str,
    verbose: bool = True,
) -> dict:
    """종목코드로 자동 최신 분석."""
    from .search import get_company_by_stock_code
    
    company = get_company_by_stock_code(stock_code)
    if not company:
        return {"error": f"종목코드를 찾을 수 없음: {stock_code}"}
    
    return analyze_latest(
        name=company["name"],
        corp_code=company["corp_code"],
        stock_code=company["stock_code"],
        verbose=verbose,
    )

def analyze_by_stock_code(
    stock_code: str,
    year: int = 2025,
    reprt_code: str = "11011",
    verbose: bool = True,
) -> dict:
    """
    종목코드 하나만으로 전체 분석 (가장 편한 사용법).
    
    Args:
        stock_code: KRX 종목코드 (예: "005930")
    
    Returns:
        dict: 분석 결과 또는 {"error": "..."}
    """
    company = get_company_by_stock_code(stock_code)
    if not company:
        return {"error": f"종목코드를 찾을 수 없음: {stock_code}"}
    
    return analyze_company(
        name=company["name"],
        corp_code=company["corp_code"],
        stock_code=company["stock_code"],
        year=year,
        reprt_code=reprt_code,
        verbose=verbose,
    )


def analyze_by_search(
    query: str,
    year: int = 2025,
    reprt_code: str = "11011",
) -> dict:
    """
    검색어로 첫 번째 매칭 회사 분석.
    여러 결과 있으면 첫 번째만.
    
    Args:
        query: 검색어 (예: "삼성전자", "005930", "삼성")
    
    Returns:
        dict: 분석 결과 또는 {"error": "..."}
    """
    matches = search_company(query, limit=1)
    if not matches:
        return {"error": f"검색 결과 없음: {query}"}
    
    company = matches[0]
    return analyze_company(
        name=company["name"],
        corp_code=company["corp_code"],
        stock_code=company["stock_code"],
        year=year,
        reprt_code=reprt_code,
    )