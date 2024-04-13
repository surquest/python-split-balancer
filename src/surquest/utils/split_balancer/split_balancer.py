"""

"""

from ortools.linear_solver import pywraplp
import numpy as np
import logging

from .errors import *

class SplitBalancer:
    """
    """

    def __init__(
            self, 
            pool: list, 
            characteristics: list,
            target_group_size: int,
            control_group_size: int,
            in_target_group: list | None = None,
            in_control_group: list | None = None,
            out_target_group: list | None = None,
            out_control_group: list | None = None,
            model_type: str = "CP-SAT",
            groups: list = ["target", "control", "unassigned"]
    ):
        
        """Initializes the SplitBalancer class.

        Args:
            pool (list): A list of the pool of units.
            characteristics (list of list): An array of the characteristics of the units.
            target_group_size (int): The size of the target group.
            control_group_size (int): The size of the control group.
            in_target_group (list): A list of the units in the target group.
            in_control_group (list): A list of the units in the control group.
            out_target_group (list): A list of the units not in the target group.
            out_control_group (list): A list of the units not in the control group.

        """

        # Validate the input

        # Check if the pool has enough units
        if len(pool) < target_group_size + control_group_size:
            
            raise InsufficientUnitsError(len(pool), target_group_size, control_group_size)
        
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

        self.model_type = model_type
        self.groups = groups

        # Log inputs
        logging.info(f"Pool: {self.pool}")
        logging.info(f"Characteristics: {self.characteristics}")
        logging.info(f"Target group size: {self.target_group_size}")
        logging.info(f"Control group size: {self.control_group_size}")
        logging.info(f"In target group: {self.in_target_group}")
        logging.info(f"In control group: {self.in_control_group}")
        logging.info(f"Out target group: {self.out_target_group}")
        logging.info(f"Out control group: {self.out_control_group}")
        logging.info(f"Model type: {self.model_type}")
        logging.info(f"Groups: {self.groups}")



    def _get_model(self):
        """Method to create the optimization model.

        Returns:
            pywraplp.Solver: The optimization model.
        """

        solver = pywraplp.Solver.CreateSolver(self.model_type)

        # Define the variables
        dx = solver.NumVar(0, 1, "dx")
        x = {}
        for i in self.pool:
            for j in self.groups:
                x[(i,j)] = solver.IntVar(0, 1, f"x_{i}_{j}")

        # Define the constraints
        for i in self.pool:
            solver.Add(sum(x[(i,j)] for j in self.groups) == 1)

        # Define the target group size constraint
        solver.Add(sum(x[(i,self.groups[0])] for i in self.pool) == self.target_group_size)

        # Define the control group size constraint
        solver.Add(sum(x[(i,self.groups[1])] for i in self.pool) == self.control_group_size)

        # Define the in target group constraint
        if self.in_target_group is not None:
            for i in self.in_target_group:
                solver.Add(x[(i,self.groups[0])] == 1)

        # Define the in control group constraint
        if self.in_control_group is not None:
            for i in self.in_control_group:
                solver.Add(x[(i,self.groups[1])] == 1)

        # Define the out target group constraint
        if self.out_target_group is not None:
            for i in self.out_target_group:
                solver.Add(x[(i,self.groups[0])] == 0)

        # Define the out control group constraint
        if self.out_control_group is not None:
            for i in self.out_control_group:
                solver.Add(x[(i,self.groups[1])] == 0)

        
        # Define avg characteristics for each group
        avg = {
            "target": [],
            "control": []
        }

        n_characteristics = len(self.characteristics)
        logging.info(f"Number of characteristics: {n_characteristics}")

        for ch in range(n_characteristics):

            avg["target"].append(
                solver.Sum(x[val,self.groups[0]]*self.characteristics[ch][idx] for idx, val in enumerate(self.pool))/self.target_group_size
                )
            avg["control"].append(
                solver.Sum(x[val,self.groups[1]]*self.characteristics[ch][idx] for idx, val in enumerate(self.pool))/self.control_group_size
                )
            
            print(":> ch", ch)

        # Define sum of avg characteristics for each group
        total_avg_target = solver.Sum(avg["target"][ch] for ch in range(n_characteristics))
        total_avg_control = solver.Sum(avg["control"][ch] for ch in range(n_characteristics))

        solver.Add(total_avg_target - total_avg_control <= dx)
        solver.Add(total_avg_control - total_avg_target <= dx)

        solver.Minimize(dx)

        return solver, x, dx


    def solve(self):
        """Method to solve the optimization model.

        Returns:
            dict: A dictionary with the units in each group.
        """

        groups = {
            "target": [],
            "control": [],
            "unassigned": []
        }

        solver, x, dx = self._get_model()

        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:

            # Get units in target and control groups
            for i in self.pool:
                for j in self.groups:
                    if x[(i,j)].solution_value() == 1:
                        groups[j].append(i)
            

            # Get vector of target and control variables
            vec_target = np.array([x[(i,self.groups[0])].solution_value() for i in self.pool])
            vec_control = np.array([x[(i,self.groups[1])].solution_value() for i in self.pool])

            # Get avg characteristics for each group
            avg = {
                "target": [],
                "control": []
            }

            n_characteristics = len(self.characteristics)

            for ch in range(n_characteristics):

                vec_characteristics = np.array(self.characteristics[ch])
                        
                avg["target"].append(
                    np.dot(vec_target, vec_characteristics)/self.target_group_size
                    )
                avg["control"].append(
                     np.dot(vec_control, vec_characteristics)/self.control_group_size
                    )

        else:
            logging.error("The problem does not have an optimal solution.")
            return None
        
        logging.info(f"Groups: {groups}")
        return {
            "assignments": groups,
            "stats": avg
        }