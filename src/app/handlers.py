from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse

from utils.exceptions import AppBusinessException, ResourceNotFoundException


async def handle_resource_notfound_exception(_:Request, exec:ResourceNotFoundException):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={
            "detail": exec.message,
        }
    )

async def handle_app_business_exception(_:Request, exec:AppBusinessException):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content={
            "detail": exec.message
        }
    )