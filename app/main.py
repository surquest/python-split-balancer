
"""File main.py with FastAPI app"""
import os
import random
import time
import numpy as np
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi import FastAPI, Request, Query, Body, Response


from surquest.utils.split_balancer import SplitBalancer
# import surquest modules and objects
from surquest.fastapi.utils.route import Route  # custom routes for documentation and FavIcon
from surquest.fastapi.utils.GCP.tracer import Tracer
from surquest.fastapi.utils.GCP.logging import Logger
from surquest.fastapi.schemas.responses import Response, Message
from surquest.fastapi.utils.GCP.middleware import LoggingMiddleware
from surquest.fastapi.utils.GCP.catcher import (
    catch_validation_exceptions,
    catch_http_exceptions,
)

from .schemas import Split

PATH_PREFIX = os.getenv('PATH_PREFIX','')

app = FastAPI(
    title="Split Balancer",
    openapi_url=F"{PATH_PREFIX}/openapi.json",
    description="""
# Introduction

This project provides sample access to REST API applications for dividing a set of units into two most comparable groups based on their characteristics.

## Problem Statement

Balancing Numeric Characteristics Across Two Groups from the same source/pool.

### Input:

* A set of units, where each unit possesses one or more numeric characteristics.
* Desired size for each of the two groups.
* (Optional) Pre-assignment constraints:
    
   - Specify units that must belong to a particular group (Group A or Group B).
   - Specify units that cannot belong to a particular group (Group A or Group B).

### Objective:

Partition the units into two groups (Group A and Group B) of the specified size, ensuring maximum similarity between the groups. Similarity is measured by minimizing the sum of absolute differences in mean values for each characteristic across the two groups.

### Constraints:

* Each unit is assigned to either Group A, Group B, or remains unassigned.
* The final size of Group A and Group B must match the specified desired size.

### Output:

* A list of units assigned to Group A and Group B.
* The mean values for each characteristic in Group A and Group B.
* The sum of absolute differences in mean values for each characteristic across the two groups.
"""
)

# add middleware
app.add_middleware(LoggingMiddleware)

# exception handlers
app.add_exception_handler(HTTPException, catch_http_exceptions)
app.add_exception_handler(RequestValidationError, catch_validation_exceptions)

# custom routes to documentation and favicon
app.add_api_route(path=F"{PATH_PREFIX}/", endpoint=Route.get_documentation, include_in_schema=False)
app.add_api_route(path=PATH_PREFIX, endpoint=Route.get_favicon, include_in_schema=False)


@app.post(
        F"{PATH_PREFIX}/balancer/split", 
        tags=["Split Balancer"]
    )
def split(
    split: Split = Body(...),
):
    """
    Split Balancer API
    """

    # Raise out of free usage if the pool size is higher than 500
    max_size = 500
    if len(split.pool) > max_size:
       
       return Response.set(
            status_code=422,
            errors=[
               Message(
                   msg="The pool size is too large for free usage. Please contact us for a custom solution.",
                   type="OUT OF FREE TIER",
                   loc=["body","pool"],
                   ctx={
                      "maxSize": {
                         "pool": max_size
                      }
                   }
                   )
               ],
       )

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

@app.get(
        F"{PATH_PREFIX}/benchmark/balancer/split", 
        tags=["Benchmark Split Balancer"]
    )
def banchmark_split(
    pool_size: int = Query(
        ...,
        alias="poolSize",
        example=100,
        description="The size of the pool.",
        gt=1,
        le=5000
    )
):
    """
    Test Split Balancer performance for a given pool size
    """

    pool = range(pool_size)
    characteristics = []
    for _ in range(5):
      characteristics.append(
          [random.randrange(1, 10) for _ in range(pool_size)]
          )

    target_group_size = int(0.6*pool_size)
    control_group_size = int(0.2*pool_size)
    in_target_group = None
    in_control_group = None
    out_target_group = None
    out_control_group = None

    model = SplitBalancer(
        pool=pool,
        characteristics=characteristics,
        target_group_size=target_group_size,
        control_group_size=control_group_size,
        in_target_group=in_target_group,
        in_control_group=in_control_group,
        out_target_group=out_target_group,
        out_control_group=out_control_group
    )

    results = model.solve()

    return Response.set(
        data=results
    )