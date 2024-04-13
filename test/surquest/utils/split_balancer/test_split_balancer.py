import pytest
import random
from surquest.utils.split_balancer import SplitBalancer
from surquest.utils.split_balancer.errors import *


target_group_size = 5
control_group_size = 3
in_target_group = [1, 2, 3]
in_control_group = [10]
out_target_group = [9, 10]
out_control_group = [4, 5]
pool = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
characteristics = {
    1: [
        [0.4, 0.5, 0.6, 0.4, 0.6, 0.9, 0.1, 0.4, 0.6, 0.5]
    ],
    2: [
        [0.4, 0.5, 0.6, 0.4, 0.6, 0.9, 0.1, 0.4, 0.6, 0.5],
        [0.2, 0.3, 0.4, 0.2, 0.4, 0.7, 0.1, 0.2, 0.4, 0.3]
    ]
}

big_N = 5000
big_pool = range(big_N)
characteristics["big"] = [
    [random.random() for _ in range(big_N)],
    [random.random() for _ in range(big_N)],
    [random.random() for _ in range(big_N)]
]
big_target_group_size = 0.8*big_N
big_control_group_size = 0.1*big_N

class TestSplitBalancer:


    @pytest.mark.parametrize(
        "target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics, expected",
        [
            (8, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(1), InsufficientUnitsError),
            (0, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(1), InvalidGroupSizeError),
            (target_group_size, 0, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(1), InvalidGroupSizeError),
            (target_group_size, control_group_size, [1], [1], out_target_group, out_control_group, pool, characteristics.get(1), OverlappingUnitsError),
            (target_group_size, control_group_size, [1,2,3,4], [1,2,3,4], out_target_group, out_control_group, pool, characteristics.get(1), OverlappingUnitsError),
            (target_group_size, control_group_size, [1,2,3,4,5,6], [1,2,3,4,5,6], out_target_group, out_control_group, pool, characteristics.get(1), OverlappingUnitsError),
            (target_group_size, control_group_size, [1], in_control_group, [1], out_control_group, pool, characteristics.get(1), DuplicateUnitsError),
            (target_group_size, control_group_size, [1,2,3,4], in_control_group, [1,2,3,4], out_control_group, pool, characteristics.get(1), DuplicateUnitsError),
            (target_group_size, control_group_size, [1,2,3,4,5,6], in_control_group, [1,2,3,4,5,6], out_control_group, pool, characteristics.get(1), DuplicateUnitsError),
            (target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, in_control_group, pool, characteristics.get(1), DuplicateUnitsError),
        ],
    )
    def test_failure(self, target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics, expected):

        try:
            split_balancer = SplitBalancer(
                pool=pool,
                characteristics=characteristics,
                target_group_size=target_group_size,
                control_group_size=control_group_size,
                in_target_group=in_target_group,
                in_control_group=in_control_group,
                out_target_group=out_target_group,
                out_control_group=out_control_group
            )
        except Exception as e:
            assert isinstance(e, expected)
            # assert str(e) == f"Insufficient units: pool size ({len(pool)}) is lower than the sum of target ({target_group_size}) + control ({control_group_size}) group sizes."

    @pytest.mark.parametrize(
        "target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics, expected",
        [
            (target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(1), dict),
            (target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(2), dict),
            (8, 2, in_target_group, [7, 8, 9, 10], out_target_group, out_control_group, pool, characteristics.get(1), type(None)),
            (big_target_group_size, big_control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, big_pool, characteristics.get("big"), dict),


        ],
    )
    def test_success(self, target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics, expected):
        
        split_balancer = SplitBalancer(
            pool=pool,
            characteristics=characteristics,
            target_group_size=target_group_size,
            control_group_size=control_group_size,
            in_target_group=in_target_group,
            in_control_group=in_control_group,
            out_target_group=out_target_group,
            out_control_group=out_control_group
        )

        results = split_balancer.solve()

        assert isinstance(results, expected)

        if expected is dict:

            groups = results.get("assignments")

            # Check if the groups are of the correct size
            assert target_group_size == len(groups["target"])
            assert control_group_size == len(groups["control"])

            # Check if the units are in the correct groups
            for unit in in_target_group:
                assert unit in groups["target"], f"Unit {unit} is not in the target group: {groups['target']}"

            for unit in in_control_group:
                assert unit in groups["control"], f"Unit {unit} is not in the control group: {groups['control']}"

            for unit in out_target_group:
                assert unit not in groups["target"], f"Unit {unit} is in the target group: {groups['target']}"

            for unit in out_control_group:
                assert unit not in groups["control"], f"Unit {unit} is in the control group: {groups['control']}"

        