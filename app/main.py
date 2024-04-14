
"""File main.py with FastAPI app"""
import os
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request, Query, Body

from surquest.utils.split_balancer import SplitBalancer
# import surquest modules and objects
from surquest.fastapi.utils.route import Route  # custom routes for documentation and FavIcon
from surquest.fastapi.utils.GCP.tracer import Tracer
from surquest.fastapi.utils.GCP.logging import Logger
from surquest.fastapi.schemas.responses import Response
from surquest.fastapi.utils.GCP.middleware import LoggingMiddleware
from surquest.fastapi.utils.GCP.catcher import (
    catch_validation_exceptions,
    catch_http_exceptions,
)

from .schemas import Split

PATH_PREFIX = os.getenv('PATH_PREFIX','')

app = FastAPI(
    title="Split Balancer",
    openapi_url=F"{PATH_PREFIX}/openapi.json"
)

# add middleware
app.add_middleware(LoggingMiddleware)

# exception handlers
app.add_exception_handler(HTTPException, catch_http_exceptions)
app.add_exception_handler(RequestValidationError, catch_validation_exceptions)

# custom routes to documentation and favicon
app.add_api_route(path=F"{PATH_PREFIX}/", endpoint=Route.get_documentation, include_in_schema=False)
app.add_api_route(path=PATH_PREFIX, endpoint=Route.get_favicon, include_in_schema=False)


@app.post(F"{PATH_PREFIX}/split_balancer")
def split(
    split: Split = Body(...),
):
    """
    Split Balancer API
    """
    model = SplitBalancer(
        pool=split.pool,
        characteristics=split.characteristics,
        target_group_size=split.target_group_size,
        control_group_size=split.control_group_size,
        in_target_group=split.in_target_group,
        in_control_group=split.in_control_group,
    )

    results = model.solve()

    return Response.set(
        data=results
    )