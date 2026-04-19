
# they must be models, not dtos, because they are used in the services and workers, which should not depend on the dtos(#41 https://github.com/Ismael-droid-01/calpulli-api/issues/41)
from calpulli.dtos import NumericValueDTO, StringValueDTO 
from typing import List

class TaskAggregate:
    def __init__(self, task_id: int, algorithm_name: str, status: str,algorithm_id: int = None):
        self.task_id            = task_id
        self.algorithm_name     = algorithm_name
        self.algorithm_id       =  algorithm_id
        self.status             = status
        self.numeric_parameters:List[NumericValueDTO] = []
        self.string_parameters:List[StringValueDTO]  = []
    def add_numeric_parameter(self, param: NumericValueDTO):
        self.numeric_parameters.append(param)
    def add_string_parameter(self, param: StringValueDTO):
        self.string_parameters.append(param)
    

