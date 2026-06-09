"""
원천 데이터로부터 10개 지표를 계산한다.
교과서 공식 기반 (당기순이익 / 보통주_유통).
"""


def calculate_metrics(financials: dict, shares_data: dict, price: int) -> dict:
    """
    7개 원천 데이터 + 발행주식수 + 주가 → 10개 지표.
    
    교과서 공식:
        EPS = 당기순이익 / 보통주_유통
        BPS = 자본총계 / 보통주_유통
        SPS = 매출액 / 보통주_유통
        ROE = 당기순이익 / 자본총계 × 100
    
    적자 회사 처리:
        - EPS, ROE는 음수도 그대로 (정상)
        - PER, 배당성향은 None (의미 없음)
    """
    REQUIRED = ["당기순이익", "매출액", "자본총계"]
    missing = [k for k in REQUIRED if financials.get(k) is None]
    if missing:
        return {"error": f"필수 데이터 누락: {missing}"}
    
    shares = shares_data.get("보통주_유통")
    if not shares or not price:
        return {"error": "주식수 또는 주가 없음"}
    
    net_income = financials["당기순이익"]
    total_dividend = financials.get("배당금")
    
    # 주당 지표
    eps = net_income / shares
    sps = financials["매출액"] / shares
    bps = financials["자본총계"] / shares
    dps = (total_dividend / shares) if total_dividend else None
    
    is_profitable = net_income > 0
    
    # 배당성향: 적자에선 의미 없음
    if is_profitable and total_dividend:
        dividend_payout_ratio = total_dividend / net_income * 100
    else:
        dividend_payout_ratio = None
    
    # PER: 적자에선 의미 없음
    per = price / eps if (is_profitable and eps > 0) else None
    
    # 나머지 비율
    psr = price / sps if sps > 0 else None
    pbr = price / bps if bps > 0 else None
    roe = net_income / financials["자본총계"] * 100
    
    # EV/EBITDA
    ev_ebitda = None
    market_cap = price * shares
    
    can_calc_ev = (
        financials.get("EBITDA") is not None and
        financials.get("부채총계") is not None and
        financials.get("현금성자산") is not None
    )
    
    if can_calc_ev:
        net_debt = financials["부채총계"] - financials["현금성자산"]
        ev = market_cap + net_debt
        ebitda = financials["EBITDA"]
        ev_ebitda = ev / ebitda if ebitda > 0 else None
    
    return {
        "EPS": round(eps, 2),
        "SPS": round(sps, 2),
        "BPS": round(bps, 2),
        "DPS": round(dps, 2) if dps else None,
        "배당성향(%)": round(dividend_payout_ratio, 2) if dividend_payout_ratio else None,
        "PER": round(per, 2) if per else None,
        "PSR": round(psr, 2) if psr else None,
        "PBR": round(pbr, 2) if pbr else None,
        "ROE(%)": round(roe, 2),
        "EV/EBITDA": round(ev_ebitda, 2) if ev_ebitda else None,
        "_적자여부": not is_profitable,
        "_계산방식": "교과서 공식",
        "_EBITDA_방식": financials.get("EBITDA_방식"),
        "_시가총액": int(market_cap),
        "_주가": price,
        "_보통주_유통": shares,
        "_총배당금": total_dividend,
    }