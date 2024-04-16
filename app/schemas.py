from pydantic import BaseModel, Field
from typing import List, Optional


class Split(BaseModel):
    """Inputs for running the SplitBalancer"""

    pool: List = Field(
        ...,
        example=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        description="A list of the pool of units.",
        min_items=2,
        max_items=100,
    )

    characteristics: List[List] = Field(
        ...,
        example=[[4, 5, 6, 4, 6, 9, 1, 4, 6, 5]],
        description="An array of the characteristics of the units.",
        min_items=1,
    )

    target_group_size: int = Field(
        ...,
        alias="targetGroupSize",
        example=5, description="The size of the target group.", gt=0
    )

    control_group_size: int = Field(
        ...,
        alias="controlGroupSize",
        example=3, description="The size of the control group.", gt=0
    )

    in_target_group: Optional[List] = Field(
        ...,
        alias="inTargetGroup",
        example=[0, 1, 2],
        description="A list of the units that must be in the target group.",
    )

    in_control_group: Optional[List] = Field(
        ...,
        alias="inControlGroup",
        example=[9],
        description="A list of the units that must be in the control group.",
    )
    out_target_group: Optional[List] = Field(
        ...,
        alias="outTargetGroup",
        example=[8, 9],
        description="A list of the units that must be out of the target group.",
    )

    out_control_group: Optional[List] = Field(
        ...,
        alias="outControlGroup",
        example=[4, 5],
        description="A list of the units that must be out of the control group.",
    )
