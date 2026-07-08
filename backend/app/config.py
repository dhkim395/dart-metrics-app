"""
백엔드 설정.
환경 변수에서 DART API 키 로드.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 사용 (research와 공유)
# backend/app/config.py → backend/ → 프로젝트 루트
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_PATH = ROOT_DIR / "research" / ".env"

# .env 파일이 있으면 로드 (로컬 개발)
# 없으면 시스템 환경변수 사용 (Render 배포)
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

DART_API_KEY = os.getenv("DART_API_KEY")
if not DART_API_KEY:
    raise RuntimeError(
        "DART_API_KEY 환경변수가 설정되지 않았습니다. "
        f".env 파일 위치: {ENV_PATH}"
    )

# dart_client 패키지 경로 (research의 것을 그대로 사용)
DART_CLIENT_PATH = str(ROOT_DIR / "research" / "scripts")


# API 설정
API_TITLE = "DART Metrics API"
API_VERSION = "0.1.0"
API_DESCRIPTION = """
공시 기반 주식 지표 분석 API.

- 종목 검색
- 10개 재무 지표 (EPS, PER, PBR, ROE 등)
- 분기별 추이
"""