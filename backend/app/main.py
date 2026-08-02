from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: replace with the actual frontend origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_STR)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint returning the API name."""
    return {"message": settings.PROJECT_NAME}
