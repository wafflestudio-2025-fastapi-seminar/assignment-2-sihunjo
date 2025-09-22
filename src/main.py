from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from tests.util import get_all_src_py_files_hash
from src.api import api_router
from common import custom_exception
import JSONResponse

app = FastAPI()

app.include_router(api_router)

@app.exception_handler(custom_exception.CustomException)
async def custom_exception_handler(request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "error_msg": exc.error_message},
    )

@app.get("/health")
def health_check():
    # 서버 정상 배포 여부를 확인하기 위한 엔드포인트입니다.
    # 본 코드는 수정하지 말아주세요!
    hash = get_all_src_py_files_hash()
    return {
        "status": "ok",
        "hash": hash
    }