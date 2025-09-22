from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

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

@app.get("/health")
def health_check():
    # 서버 정상 배포 여부를 확인하기 위한 엔드포인트입니다.
    # 본 코드는 수정하지 말아주세요!
    hash = get_all_src_py_files_hash()
    return {
        "status": "ok",
        "hash": hash
    }