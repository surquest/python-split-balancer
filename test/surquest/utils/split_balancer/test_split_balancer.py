import pytest
import random
import time
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
        [4, 5, 6, 4, 6, 9, 1, 4, 6, 5]
    ],
    2: [
        [4, 5, 6, 4, 6, 9, 1, 4, 6, 5],
        [2, 3, 4, 2, 4, 7, 1, 2, 4, 3]
    ]
}

big_N = 1000
big_pool = range(big_N)
characteristics["big"] = [
    [random.randrange(1, 100) for _ in range(big_N)],
    [random.randrange(1, 100) for _ in range(big_N)],
    [random.randrange(1, 100) for _ in range(big_N)]
]
big_target_group_size = int(0.8*big_N)
big_control_group_size = int(0.1*big_N)

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
            (8, 2, in_target_group, [7, 8, 9, 10], out_target_group, out_control_group, pool, characteristics.get(1), NoOptimalSolutionError),
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
            assert isinstance(e, expected), f"Expected {expected}, but got {type(e)}"

    @pytest.mark.parametrize(
        "target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics, expected",
        [
            (target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(1), dict),
            (target_group_size, control_group_size, in_target_group, in_control_group, out_target_group, out_control_group, pool, characteristics.get(2), dict),
            (target_group_size, control_group_size, in_target_group, [7, 8, 9, 10], out_target_group, out_control_group, pool, characteristics.get(1), type(None)),
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

        results = None

        try:
            results = split_balancer.solve()
        except NoOptimalSolutionError as e:
            pass

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

    def test_benchmark(self):

        for i in [10, 100]: # 500, 1000, 1500, 2500, 5000
            for j in [1, 2, 5, 10, 100]: # [1, 5, 10, 50]:

                n = i
                pool = range(n)
                characteristics = []
                for x in range(j):
                    characteristics.append(
                        [random.randrange(0, 100) for _ in range(n)]
                        )
                        
                target_group_size = int(0.6*n)
                control_group_size = int(0.2*n)
                in_target_group = None
                in_control_group = None
                out_target_group = None
                out_control_group = None

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

                start = time.time()
                out = split_balancer.solve()
                end = time.time()

                print(f":> {i} - {j} - time {end-start}")
                print("-"*150)