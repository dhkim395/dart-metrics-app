"""
분기별 추이 데이터 수집.
1Q, 2Q, 3Q, 4Q 각 분기의 단독값을 시계열로 정리한다.
"""
from .financials import get_financial_data


def get_quarterly_trend(corp_code: str, year: int, fs_div: str = "CFS") -> list:
    """
    한 회사의 1년치 4분기 데이터를 수집.
    
    각 분기의 단독값(누적 아님) 반환.
    4Q는 연간 - (1Q+2Q+3Q)로 계산.
    
    Args:
        corp_code: DART 기업 고유번호
        year: 사업연도
        fs_div: 연결(CFS) 또는 별도(OFS)
    
    Returns:
        list of dict: 4개 분기 데이터
        각 분기마다: {"quarter", "매출액", "영업이익", "당기순이익", ...}
    """
    # 4개 보고서 정의
    reports = [
        ("11013", f"{year}_1Q"),  # 1분기
        ("11012", f"{year}_2Q"),  # 반기 → 2Q 단독
        ("11014", f"{year}_3Q"),  # 3분기 → 3Q 단독
        ("11011", f"{year}_FY"),  # 연간
    ]
    
    # 각 보고서 데이터 수집
    raw_data = []
    for reprt_code, label in reports:
        fin = get_financial_data(corp_code, year, reprt_code, fs_div)
        raw_data.append({
            "reprt_code": reprt_code,
            "label": label,
            "data": fin if "error" not in fin else None,
            "error": fin.get("error") if "error" in fin else None,
        })
    
    # 결과 정리
    result = []
    
    # 1Q, 2Q, 3Q는 그대로 단독값 사용
    for item in raw_data[:3]:
        if item["data"]:
            result.append({
                "quarter": item["label"],
                "reprt_code": item["reprt_code"],
                "매출액": item["data"].get("매출액"),
                "영업이익": item["data"].get("영업이익"),
                "당기순이익": item["data"].get("당기순이익"),
                "자본총계": item["data"].get("자본총계"),
                "출처": "분기보고서",
            })
        else:
            result.append({
                "quarter": item["label"],
                "error": item["error"],
            })
    
    # 4Q = 연간 - (1Q + 2Q + 3Q) — flow 항목만
    fy_data = raw_data[3]["data"]
    if fy_data and all(r.get("매출액") for r in result):
        sum_1to3 = {
            "매출액": sum(r["매출액"] for r in result),
            "영업이익": sum(r["영업이익"] for r in result if r.get("영업이익")),
            "당기순이익": sum(r["당기순이익"] for r in result if r.get("당기순이익")),
        }
        result.append({
            "quarter": f"{year}_4Q",
            "reprt_code": "11011_minus",  # 4Q는 빼기로 계산
            "매출액": fy_data["매출액"] - sum_1to3["매출액"] if fy_data.get("매출액") else None,
            "영업이익": fy_data["영업이익"] - sum_1to3["영업이익"] if fy_data.get("영업이익") else None,
            "당기순이익": fy_data["당기순이익"] - sum_1to3["당기순이익"] if fy_data.get("당기순이익") else None,
            "자본총계": fy_data.get("자본총계"),  # 자본은 시점 데이터 → 그대로
            "출처": "사업보고서 - 1~3분기합",
        })
    elif fy_data:
        # 1~3분기 데이터 일부 누락 시 연간만 표시
        result.append({
            "quarter": f"{year}_FY",
            "reprt_code": "11011",
            "매출액": fy_data.get("매출액"),
            "영업이익": fy_data.get("영업이익"),
            "당기순이익": fy_data.get("당기순이익"),
            "자본총계": fy_data.get("자본총계"),
            "출처": "사업보고서 (연간)",
            "주의": "1~3분기 데이터 부족으로 4Q 단독 계산 불가",
        })
    
    return result


def get_quarterly_trend_multi_year(
    corp_code: str,
    start_year: int,
    end_year: int,
    fs_div: str = "CFS",
) -> list:
    """
    여러 년도의 분기 추이 수집.
    예: 2024~2025 → 8개 분기 데이터
    
    Returns:
        list of dict (시간 순으로 정렬)
    """
    all_quarters = []
    for year in range(start_year, end_year + 1):
        year_data = get_quarterly_trend(corp_code, year, fs_div)
        all_quarters.extend(year_data)
    return all_quarters