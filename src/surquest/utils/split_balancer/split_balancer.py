"""

"""
from typing import Optional
from ortools.math_opt.python import mathopt
from ortools.math_opt.python.ipc import remote_http_solve
from datetime import datetime, timedelta
from surquest.utils.split_balancer.errors import *
import numpy as np
import logging


class SplitBalancer:
    """Class to balance the split of units into two groups based on their characteristics. 
    """

    def __init__(
        self,
        pool: list,
        characteristics: list,
        target_group_size: int,
        control_group_size: int,
        in_target_group: Optional[list] = None,
        in_control_group: Optional[list] = None,
        out_target_group: Optional[list] = None,
        out_control_group: Optional[list] = None
    ):
        """Initializes the SplitBalancer class.

        Args:
            pool (list): A list of the pool of units.
            characteristics (list of list): An array of the characteristics of the units.
            target_group_size (int): The size of the target group.
            control_group_size (int): The size of the control group.
            in_target_group (list): A list of the units that must be in the target group.
            in_control_group (list): A list of the units that must be in the control group.
            out_target_group (list): A list of the units that must be out ofthe target group.
            out_control_group (list): A list of the units that must be out the control group.
        """

        # Validate the input

        # Check if the pool has enough units
        if len(pool) < target_group_size + control_group_size:

            raise InsufficientUnitsError(
                len(pool), target_group_size, control_group_size
            )

        # Check if the same units are in both the target and control groups
        if in_target_group is not None and in_control_group is not None:

            overlapping_units = list(set(in_target_group) & set(in_control_group))

            if len(overlapping_units) > 0:

                raise OverlappingUnitsError(overlapping_units)

        # Check if the same units are required to be in as well as out of the target
        if out_target_group is not None and in_target_group is not None:

            overlapping_units = list(set(in_target_group) & set(out_target_group))

            if len(overlapping_units) > 0:

                raise DuplicateUnitsError(overlapping_units, "target")

        # Check if the same units are required to be in as well as out of the control
        if out_control_group is not None and in_control_group is not None:

            overlapping_units = list(set(in_control_group) & set(out_control_group))

            if len(overlapping_units) > 0:

                raise DuplicateUnitsError(overlapping_units, "control")

        # Check if the group size is smaller than 1 or greater than the amount of units in the pool - 1
        if target_group_size < 1 or target_group_size > len(pool) - 1:

            raise InvalidGroupSizeError(target_group_size, len(pool))

        if control_group_size < 1 or control_group_size > len(pool) - 1:

            raise InvalidGroupSizeError(control_group_size, len(pool))

        self.pool = pool
        self.characteristics = characteristics
        self.target_group_size = target_group_size
        self.control_group_size = control_group_size
        self.in_target_group = in_target_group
        self.in_control_group = in_control_group
        self.out_target_group = out_target_group
        self.out_control_group = out_control_group

        # Log inputs
        logging.info(f"Pool: {self.pool}")
        logging.info(f"Characteristics: {self.characteristics}")
        logging.info(f"Target group size: {self.target_group_size}")
        logging.info(f"Control group size: {self.control_group_size}")
        logging.info(f"In target group: {self.in_target_group}")
        logging.info(f"In control group: {self.in_control_group}")
        logging.info(f"Out target group: {self.out_target_group}")
        logging.info(f"Out control group: {self.out_control_group}")

        self.groups = ["target", "control", "unassigned"]


    def _get_model(self, integer_only=False):
        """Method to create the optimization model.

        Returns:
            pywraplp.Solver: The optimization model.
        """

        pool = self.pool
        groups = self.groups
        target_group_size = self.target_group_size
        control_group_size = self.control_group_size

        # Create the optimization model
        model = mathopt.Model(name="split_balancer")

        # Define variables
        if integer_only is True:
            b = model.add_variable(is_integer=True, name="b")
        else:
            b = model.add_variable(name="b")

        x = {}
        for i in pool:
            for j in groups:
                x[(i, j)] = model.add_variable(lb=0, ub=1, is_integer=True, name=f"x_{i}_{j}")


        # Define constraints

        # Each unit from the pool needs to be assigned into one group
        for i in pool:
            model.add_linear_constraint(
                sum(x[(i, j)] for j in groups) == 1
            )

        # Define the target group size constraint
        model.add_linear_constraint(
            sum(x[(i, groups[0])] for i in pool) == target_group_size
        )

        # Define the control group size constraint
        model.add_linear_constraint(
            sum(x[(i, groups[1])] for i in pool) == control_group_size
        )

        simple_char = self.simplify_characteristics(self.characteristics)

        if integer_only is True:
          const = 10000
          coef = int(target_group_size/control_group_size)*const

          avg_target_char = sum(
              x[(i, "target")]*simple_char[idx] for idx, i in enumerate(pool)
          )*const

          avg_control_char = sum(
              x[(i, "control")]*simple_char[idx] for idx, i in enumerate(pool)
          )*coef

        else:
        
          avg_target_char = sum(
              x[(i, "target")]*simple_char[idx] for idx, i in enumerate(pool)
          )/target_group_size

          avg_control_char = sum(
              x[(i, "control")]*simple_char[idx] for idx, i in enumerate(pool)
          )/control_group_size

        # Define the distance constraint
        model.add_linear_constraint(
            avg_target_char - avg_control_char <= b
        )

        model.add_linear_constraint(
            avg_control_char - avg_target_char <= b
        )

        # Define the in target group constraint
        if self.in_target_group is not None:
            for i in self.in_target_group:
                model.add_linear_constraint(x[(i, self.groups[0])] == 1)

        # Define the in control group constraint
        if self.in_control_group is not None:
            for i in self.in_control_group:
                model.add_linear_constraint(x[(i, self.groups[1])] == 1)

        # Define the out target group constraint
        if self.out_target_group is not None:
            for i in self.out_target_group:
                model.add_linear_constraint(x[(i, self.groups[0])] == 0)

        # Define the out control group constraint
        if self.out_control_group is not None:
            for i in self.out_control_group:
                model.add_linear_constraint(x[(i, self.groups[1])] == 0)

        model.minimize(b)

        return model, x, b

    def solve(self, integer_only=False, limit=180, remote=False, api_key=None):
        """Method to solve the optimization model.

        Args:
            limit (int): The time limit for the optimization model. (default is 60 seconds)
            remote (bool): Whether to solve the optimization model remotely. (default is False)
            api_key (str): The API key for the remote solver. (default is None)
        Returns:
            dict: A dictionary with the units in each group.
        """

        groups = {"target": [], "control": [], "unassigned": []}

        model, x, b = self._get_model(integer_only=integer_only)
        params = mathopt.SolveParameters(time_limit=timedelta(seconds=limit))

        # Solve the optimization model
        if remote is True:
            api_key = api_key
            result, logs = remote_http_solve.remote_http_solve(
                model, 
                mathopt.SolverType.CP_SAT, 
                api_key=api_key
                # ToDO: add SolveParameters
            )

        else:
            result = mathopt.solve(
                model,
                mathopt.SolverType.CP_SAT,
                params=params
            )

        if result.termination.reason == mathopt.TerminationReason.OPTIMAL \
           or result.termination.reason == mathopt.TerminationReason.FEASIBLE:

            vec = {
                "target": np.array([result.variable_values()[x[(i, self.groups[0])]] for i in self.pool]),
                "control": np.array([result.variable_values()[x[(i, self.groups[1])]] for i in self.pool]),
                "unassigned": np.array([result.variable_values()[x[(i, self.groups[2])]] for i in self.pool])
            }

            # Get units in target and control groups
            for i in self.pool:
                for j in self.groups:
                    if result.variable_values()[x[(i, j)]] == 1:
                        groups[j].append(i)

            # Get avg characteristics for each group
            avg = {"characteristics": [], "total": None}

            n_characteristics = len(self.characteristics)

            for ch in range(n_characteristics):

                vec_characteristics = np.array(self.characteristics[ch])

                char_avg = {
                    "target": np.dot(vec.get("target"), vec_characteristics)
                    / self.target_group_size,
                    "control": np.dot(vec.get("control"), vec_characteristics)
                    / self.control_group_size,
                }

                avg["characteristics"].append(char_avg)

            # Get total avg characteristics
            avg["total"] = {
                "objectiveFunction": result.variable_values()[b],
                "target": np.sum(
                    [
                        avg["characteristics"][ch]["target"]
                        for ch in range(n_characteristics)
                    ]
                ),
                "control": np.sum(
                    [
                        avg["characteristics"][ch]["control"]
                        for ch in range(n_characteristics)
                    ]
                ),
            }

        else:

            logging.error("The problem does not have an optimal solution.")
            raise NoOptimalSolutionError()

        return {"stats": avg, "assignments": groups}

    @staticmethod
    def simplify_characteristics(characteristics, do_rescale=True, scale=1):
        """Method to simplify the characteristics of the units.
        to a single vector with values between 0 and 1.

        Args:
            characteristics (list of list): The characteristics of the units.
            do_rescale (bool): Whether to rescale (integers in rage 0 and 1000) the characteristics. 

        Returns:
            list: The simplified characteristics of the units.
        """


        matrix = np.array(characteristics)
        
        # Standardize the characteristics between 0 and 1
        std_matrix = (matrix - matrix.min()) / (matrix.max() - matrix.min())

        # Calculate the mean for each characteristic (column)
        average_unit = np.mean(std_matrix, axis=0)

        return average_unit