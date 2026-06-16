"""
FastAPI 백엔드 진입점.

실행:
    cd backend
    uvicorn app.main:app --reload
    
브라우저에서:
    http://localhost:8000        - 홈
    http://localhost:8000/docs   - Swagger UI (대화형 API 문서)
    http://localhost:8000/redoc  - ReDoc (API 문서)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_TITLE, API_VERSION, API_DESCRIPTION
from app.routers import search, company, admin


app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
)

# CORS 설정 (모바일 앱에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용 (배포 시 특정 도메인만)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(search.router)
app.include_router(company.router)
app.include_router(admin.router)



@app.get("/")
async def root():
    """헬스 체크 + 안내."""
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "endpoints": {
            "search": "/search?q=삼성",
            "company_metrics": "/company/005930/metrics",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health():
    """헬스 체크 (모니터링용)."""
    return {"status": "ok"}