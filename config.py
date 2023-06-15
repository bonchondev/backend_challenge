from typing import Callable, Annotated, Literal
from fastapi import FastAPI, Request, Response, Query
from fastapi.routing import APIRoute
from fastapi import HTTPException
from pydantic import BaseSettings, ValidationError
from pydantic.fields import Field


class ValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except ValidationError as exc:
                body = await request.body()
                detail = {"errors": exc.errors(), "body": body.decode()}
                raise HTTPException(status_code=422, detail=detail)

        return custom_route_handler


def alphanumeric_query_validation(vin:Annotated[str, Query(min_length=17,max_length=17)] ):
    if not vin.isalnum():
        raise HTTPException(status_code=422, detail={"errors" : "VIN must be alphanumeric"})
    return vin

class Settings(BaseSettings):
    environment: Literal['dev', 'prod', 'staging'] = 'dev'
    version: str = "1.0.0"

settings = Settings()

def init_app():
    app = FastAPI()

    app.router.route_class = ValidationErrorLoggingRoute

    return app
