"""
종목 검색 기능.
corp_map.csv를 메모리에 로드해서 빠르게 검색.
"""
from pathlib import Path
import pandas as pd


# 모듈 레벨 캐시 (한 번 로드하면 메모리에 유지)
_corp_map: pd.DataFrame = None


def _load_corp_map() -> pd.DataFrame:
    """
    corp_map.csv를 메모리에 로드 (lazy, 한 번만).
    
    경로: research/data/corp_map.csv
    파일 위치: scripts/dart_client/search.py → 상위 2단계 → data/
    """
    global _corp_map
    if _corp_map is not None:
        return _corp_map
    
    # 이 파일(search.py)의 위치 기준으로 csv 경로 계산
    csv_path = Path(__file__).parent.parent.parent / "data" / "corp_map.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(
            f"corp_map.csv를 찾을 수 없습니다: {csv_path}\n"
            f"먼저 build_corp_map.py를 실행하세요."
        )
    
    # dtype 지정 필수 (앞 0 사라짐 방지)
    _corp_map = pd.read_csv(
        csv_path,
        dtype={"corp_code": str, "stock_code": str}
    )
    return _corp_map


def search_company(query: str, limit: int = 10) -> list:
    """
    종목명 또는 종목코드로 부분 매칭 검색.
    
    정렬 우선순위:
    1. 정확히 일치
    2. 시작 위치 일치 ("삼성전자" 검색 시 "삼성전자"가 "에이프로젠 삼성"보다 먼저)
    3. 종목명 길이 (짧을수록 더 핵심 회사일 가능성)
    """
    df = _load_corp_map()
    
    query = str(query).strip()
    if not query:
        return []
    
    # 종목코드(숫자만)로 검색 시
    if query.isdigit():
        mask = df["stock_code"].str.contains(query, na=False)
        matches = df[mask].head(limit)
    else:
        # 종목명으로 검색
        query_lower = query.lower()
        mask = df["corp_name"].str.contains(query, case=False, na=False)
        matches = df[mask].copy()
        
        # 점수 계산
        def score_match(name):
            name_lower = name.lower()
            if name_lower == query_lower:
                return 0  # 정확히 일치 → 최우선
            if name_lower.startswith(query_lower):
                return 1  # 시작 일치
            return 2  # 부분 일치
        
        matches["_score"] = matches["corp_name"].apply(score_match)
        matches["_name_len"] = matches["corp_name"].str.len()
        
        # 점수 → 이름 길이 순으로 정렬
        matches = matches.sort_values(["_score", "_name_len"]).head(limit)
    
    return [
        {
            "name": row["corp_name"],
            "stock_code": row["stock_code"],
            "corp_code": row["corp_code"],
        }
        for _, row in matches.iterrows()
    ]

def get_company_by_stock_code(stock_code: str) -> dict:
    """
    종목코드로 정확히 일치하는 회사 조회.
    
    Args:
        stock_code: KRX 종목코드 (6자리)
    
    Returns:
        dict: {"name", "stock_code", "corp_code"} 또는 None
    """
    df = _load_corp_map()
    
    matches = df[df["stock_code"] == str(stock_code)]
    if matches.empty:
        return None
    
    row = matches.iloc[0]
    return {
        "name": row["corp_name"],
        "stock_code": row["stock_code"],
        "corp_code": row["corp_code"],
    }


def get_company_by_corp_code(corp_code: str) -> dict:
    """corp_code로 정확히 일치하는 회사 조회."""
    df = _load_corp_map()
    
    matches = df[df["corp_code"] == str(corp_code)]
    if matches.empty:
        return None
    
    row = matches.iloc[0]
    return {
        "name": row["corp_name"],
        "stock_code": row["stock_code"],
        "corp_code": row["corp_code"],
    }