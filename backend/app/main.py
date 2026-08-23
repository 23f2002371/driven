from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw_errors = []
    for err in exc.errors():
        err_dict = dict(err)
        if isinstance(err_dict.get("input"), (bytes, bytearray)):
            err_dict["input"] = "<binary data>"
        raw_errors.append(err_dict)
    errors = jsonable_encoder(raw_errors)
    for err in errors:
        loc = err.get("loc", ())
        field_raw = str(loc[-1]) if loc else ""
        msg = str(err.get("msg", ""))

        if msg.startswith("Value error, "):
            msg = msg[13:]

        if field_raw and field_raw != "body":
            field_name = field_raw.replace("_", " ").capitalize()
            if msg.startswith("String "):
                msg = f"{field_name} " + msg[7:]
            elif msg == "Field required":
                msg = f"{field_name} is required"
        elif msg.startswith("String should have"):
            msg = "Password " + msg[7:]

        err["msg"] = msg

    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )

# SessionMiddleware is required by Authlib to persist the OAuth state/verifier
# between the login redirect and the callback request.
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS: replace with the actual frontend origins in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "https://localhost:5173",
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
