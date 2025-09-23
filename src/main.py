from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

from tests.util import get_all_src_py_files_hash
from src.api import api_router
from src.common.custom_exception import CustomException
from fastapi.responses import JSONResponse
from fastapi import Request
app = FastAPI()

app.include_router(api_router)

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "error_msg": exc.error_message},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "HTTP ERROR"
    mapping = {
        "BAD AUTHORIZATION HEADER": "ERR_007",
        "INVALID TOKEN": "ERR_008",
        "INVALID SESSION": "ERR_006",
        "UNAUTHENTICATED": "ERR_009",
        "INVALID ACCOUNT": "ERR_010",
    }
    error_code = mapping.get(detail, f"ERR_{exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": error_code,
            "error_msg": detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        errors = exc.errors()
        for err in errors:
            loc = err.get("loc") or []
            field = loc[-1] if loc else None
            if field == "phone_number":
                return JSONResponse(
                    status_code=422,
                    content={
                        "error_code": "ERR_003",
                        "error_msg": "INVALID PHONE NUMBER",
                    },
                )
            if field == "bio":
                return JSONResponse(
                    status_code=422,
                    content={
                        "error_code": "ERR_004",
                        "error_msg": "BIO TOO LONG",
                    },
                )
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "ERR_001",
                "error_msg": "MISSING VALUE",
            },
        )
    except Exception:
        return JSONResponse(
            status_code=422,
            content={
                "error_code": "ERR_001",
                "error_msg": "MISSING VALUE",
            },
        )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "ERR_500",
            "error_msg": "INTERNAL SERVER ERROR",
        },
    )

@app.get("/health")
def health_check():
    hash = get_all_src_py_files_hash()
    return {
        "status": "ok",
        "hash": hash
    }