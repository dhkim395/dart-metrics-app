"""
DART API 클라이언트 설정.
환경 변수에서 API 키를 로드한다.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 경로 (scripts/dart_client/ → research/ 의 .env)
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

DART_API_KEY = os.getenv("DART_API_KEY")

if not DART_API_KEY:
    raise RuntimeError(
        f".env 파일에서 DART_API_KEY를 찾을 수 없습니다.\n"
        f"확인 경로: {ENV_PATH}"
    )

# DART API base URL
DART_BASE_URL = "https://opendart.fss.or.kr/api"

# 보고서 코드
REPORT_CODES = {
    "1Q": "11013",  # 1분기보고서
    "2Q": "11012",  # 반기보고서
    "3Q": "11014",  # 3분기보고서
    "FY": "11011",  # 사업보고서 (연간)
}

# 재무제표 종류
FS_DIV = {
    "CFS": "CFS",  # 연결재무제표
    "OFS": "OFS",  # 별도재무제표
}