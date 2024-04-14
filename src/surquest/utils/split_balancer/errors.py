class SplitBalancerError(Exception):
    """Base class for exceptions in the SplitBalancer package."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InsufficientUnitsError(SplitBalancerError):
    """Exception raised when the size of the units pool is lower than the sum of target + control group sizes."""

    def __init__(self, pool_size, target_size, control_size):
        self.pool_size = pool_size
        self.target_size = target_size
        self.control_size = control_size
        message = f"Insufficient units: pool size ({self.pool_size}) is lower than the sum of target ({self.target_size}) + control ({self.control_size}) group sizes."
        super().__init__(message)


class OverlappingUnitsError(SplitBalancerError):
    """Exception raised when the same units are in both the target and control groups."""

    def __init__(self, overlapping_units):
        self.overlapping_units = overlapping_units
        if len(self.overlapping_units) == 1:
            message = f"Overlapping unit: The following unit is in both the target and control groups: {self.overlapping_units}"
        elif len(self.overlapping_units) > 1 and len(self.overlapping_units) < 5:
            message = f"Overlapping units: The following units are in both the target and control groups: {self.overlapping_units}"
        else:
            message = f"Overlapping units: The following units are in both the target and control groups: {self.overlapping_units[0:5]} and {len(self.overlapping_units) - 5} more"
        super().__init__(message)


class DuplicateUnitsError(SplitBalancerError):
    """Exception raised when the same units are in and out of the target group."""

    def __init__(self, duplicate_units, group_type="target"):
        self.duplicate_units = duplicate_units
        self.group_type = group_type 

        if len(self.duplicate_units) == 1:
            message = f"Duplicate unit: The following unit should be in and out of the {self.group_type} group: {self.duplicate_units}"

        elif len(self.duplicate_units) > 1 and len(self.duplicate_units) < 5:
            message = f"Duplicate units: The following units should be in and out of the {self.group_type} group: {self.duplicate_units}"

        else:
            message = f"Duplicate units: The following units should be in and out of the {self.group_type} group: {self.duplicate_units[0:5]} and {len(self.duplicate_units) - 5} more"

        super().__init__(message)

class InvalidGroupSizeError(SplitBalancerError):
    """Exception raised when the group size is smaller than 1 or greater than the amount of units in the pool - 1."""

    def __init__(self, group_size, pool_size):
        self.group_size = group_size
        self.pool_size = pool_size
        message = f"Invalid group size: Group size ({self.group_size}) is smaller than 1 or greater than the amount of units in the pool ({self.pool_size}) - 1."
        super().__init__(message)   


class NoOptimalSolutionError(SplitBalancerError):
    """Exception raised when there is no optimal solution to the split balancing problem."""

    def __init__(self):

        super().__init__("No optimal solution: There is no optimal solution to the split balancing problem.")