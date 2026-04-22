
from tortoise.transactions import atomic

from calpulli.aggregates import TaskAggregate
from calpulli.dtos import TaskCreateAggregateDTO
from calpulli.models import Dataset, UserProfile, Algorithm, NumericParameter, StringParameter, Task, Result as ResultModel
from option import Err,Ok,Result
from calpulli.log import Log
import calpulli.config as Cfg
from typing import Union
from roryclient.models import KmeansResponse, KnnResponse, NncResponse
L= Log(
    name = __name__,
    path = Cfg.CALPULLI_LOG_PATH,
)   

class UsersProfilesRepository:

    async def create(self, user_id:str, username:str, email:str, first_name:str, last_name:str)->Result[UserProfile,Exception]:
        try:
            existing_user = await UserProfile.get_or_none(user_id=user_id)
            if existing_user:
                raise Exception(f"User with id {user_id} already exists.")
            
            profile = await UserProfile.create(
                user_id    = user_id,
                username   = username,
                email      = email,
                first_name = first_name,
                last_name  = last_name,
                is_disabled = False
            )
            return Ok(profile)
        except Exception as e:
            print(f"Error creating user: {e}")
            return Err(e)
    
    async def get_by_id(self, user_id:str)->Result[UserProfile,Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
            if user:
                return Ok(user)
            else:
                return Err(Exception(f"User with id {user_id} not found."))
        except Exception as e:
            return Err(e)
    
    async def get_by_username(self, username:str)->Result[UserProfile,Exception]:
        try:
            user = await UserProfile.get_or_none(username=username)
            if user:
                return Ok(user)
            else:
                return Err(Exception(f"User with username {username} not found."))
        except Exception as e:
            return Err(e)
    
    async def delete_by_id(self, user_id:str)->Result[bool,Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
            if user:
                await user.delete()
                return Ok(True)
            else:
                return Err(Exception(f"User with id {user_id} not found."))
        except Exception as e:
            return Err(e)

class AlgorithmsRepository:

    async def create(self, name:str, type:str)->Result[Algorithm,Exception]:
        try:
            existing_algorithm = await Algorithm.get_or_none(name=name)
            if existing_algorithm:
                raise Exception(f"Algorithm with name {name} already exists.")
            
            algorithm = await Algorithm.create(
                name    = name,
                type    = type
            )
            return Ok(algorithm)
        except Exception as e:
            print(f"Error creating algorithm: {e}")
            return Err(e)

    async def get_all(self)->Result[list[Algorithm],Exception]:
        try:
            algorithms = await Algorithm.all()
            return Ok(algorithms)
        except Exception as e:
            return Err(e)

    async def get_by_id(self, algorithm_id:int)->Result[Algorithm,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if algorithm:
                return Ok(algorithm)
            else:
                return Err(Exception(f"Algorithm with id {algorithm_id} not found."))
        except Exception as e:
            return Err(e)
    
    async def get_by_type(self, type:str)->Result[list[Algorithm],Exception]:
        try:
            algorithms = await Algorithm.filter(type=type).all()
            if algorithms:
                return Ok(algorithms)
            else:
                return Err(Exception(f"Algorithms with type {type} not found."))
        except Exception as e:
            return Err(e)
    
    async def update(self, algorithm_id:int, name:str, type:str)->Result[Algorithm,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if algorithm:
                algorithm.name = name
                algorithm.type = type
                await algorithm.save()
                return Ok(algorithm)
            else:
                return Err(Exception(f"Algorithm with id {algorithm_id} not found."))
        except Exception as e:
            return Err(e)

    async def delete_by_id(self, algorithm_id:int)->Result[bool,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if algorithm:
                await algorithm.delete()
                return Ok(True)
            else:
                return Err(Exception(f"Algorithm with id {algorithm_id} not found."))
        except Exception as e:
            return Err(e)
    
    async def get_parameters_by_algorithm_id(self, algorithm_id: int) -> Result[dict, Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if not algorithm:
                return Err(Exception(f"Algorithm with id {algorithm_id} not found."))
            
            numeric_parameters = await NumericParameter.filter(algorithm_id=algorithm_id).all()
            string_parameters  = await StringParameter.filter(algorithm_id=algorithm_id).all()
            
            return Ok({
                "algorithm_id"      : algorithm_id,
                "numeric_parameters": numeric_parameters,
                "string_parameters" : string_parameters
            })
        except ValueError:
            raise
        except Exception as e:
            return Err(e)

class NumericParametersRepository:

    async def create(self, algorithm_id:int, name:str, type:str, default_value:float, max_value:float)->Result[NumericParameter,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if not algorithm:
                raise Exception(f"Algorithm with id {algorithm_id} not found.")

            parameter = await NumericParameter.create(
                algorithm_id    = algorithm_id,
                name            = name,
                type            = type,
                default_value   = default_value,
                max_value       = max_value
            )
            return Ok(parameter)
        except Exception as e:
            print(f"Error creating numeric parameter: {e}")
            return Err(e)
    
    async def get_by_id(self, parameter_id:int)->Result[NumericParameter,Exception]:
        try:
            parameter = await NumericParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                return Ok(parameter)
            else:
                return Err(Exception(f"Numeric parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)
        
    async def get_by_algorithm_id(self, algorithm_id:int)->Result[list[NumericParameter],Exception]:
        try:
            parameters = await NumericParameter.filter(algorithm_id=algorithm_id).all()
            if parameters:
                return Ok(parameters)
            else:
                return Err(Exception(f"No numeric parameters found for algorithm with id {algorithm_id}."))
        except Exception as e:
            return Err(e)

    async def update(self, parameter_id:int, name:str, type:str, default_value:float, max_value:float)->Result[NumericParameter,Exception]:
        try:
            parameter = await NumericParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                parameter.name = name
                parameter.type = type
                parameter.default_value = default_value
                parameter.max_value = max_value
                await parameter.save()
                return Ok(parameter)
            else:
                return Err(Exception(f"Numeric parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)

    async def delete_by_id(self, parameter_id:int)->Result[bool,Exception]:
        try:
            parameter = await NumericParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                await parameter.delete()
                return Ok(True)
            else:
                return Err(Exception(f"Numeric parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)
    
class StringParametersRepository:

    async def create(self, algorithm_id:int, name:str, default_value:str)->Result[StringParameter,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if not algorithm:
                raise Exception(f"Algorithm with id {algorithm_id} not found.")

            parameter = await StringParameter.create(
                algorithm_id    = algorithm_id,
                name            = name,
                default_value   = default_value
            )
            return Ok(parameter)
        except Exception as e:
            print(f"Error creating string parameter: {e}")
            return Err(e)
    
    async def get_by_id(self, parameter_id:int)->Result[StringParameter,Exception]: 
        try:
            parameter = await StringParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                return Ok(parameter)
            else:
                return Err(Exception(f"String parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)

    async def get_by_algorithm_id(self, algorithm_id:int)->Result[list[StringParameter],Exception]:
        try:
            parameters = await StringParameter.filter(algorithm_id=algorithm_id).all()
            if parameters:
                return Ok(parameters)
            else:
                return Err(Exception(f"No string parameters found for algorithm with id {algorithm_id}."))
        except Exception as e:
            return Err(e)
        
    async def update(self, parameter_id:int, name:str, default_value:str)->Result[StringParameter,Exception]:
        try:
            parameter = await StringParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                parameter.name = name
                parameter.default_value = default_value
                await parameter.save()
                return Ok(parameter)
            else:
                return Err(Exception(f"String parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)
    
    async def delete_by_id(self, parameter_id:int)->Result[bool,Exception]:
        try:
            parameter = await StringParameter.get_or_none(parameter_id=parameter_id)
            if parameter:
                await parameter.delete()
                return Ok(True)
            else:
                return Err(Exception(f"String parameter with id {parameter_id} not found."))
        except Exception as e:
            return Err(e)

class TasksRepository:

    async def create(self, user_id: int, algorithm_id: int, response_time: float) -> Result[Task, Exception]:
        try:
            user = await UserProfile.get_or_none(id=user_id)
            if not user:
                raise Exception(f"User with id {user_id} not found.")
            
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if not algorithm:
                raise Exception(f"Algorithm with id {algorithm_id} not found.")
            
            task = await Task.create(
                user       = user,
                algorithm  = algorithm,
                response_time = response_time
            )
            return Ok(task)
        except Exception as e:
            print(f"Error creating task: {e}")
            return Err(e)
    
    async def complete_task(self, task_id: int, result: Union[KmeansResponse, KnnResponse, NncResponse]) -> Result[bool, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if not task:
                return Err(Exception(f"Task with id {task_id} not found."))
            
            task.response_time = result.response_time_clustering
            # task.status = "COMPLETED" # this must be a enum, im just modeling as fast as possible we can change this later
            # 
            await task.save()
            return Ok(True)
        except Exception as e:
            print(f"Error completing task: {e}")
            return Err(e)
    @atomic()
    async def create_task_aggregate(self, dto: TaskCreateAggregateDTO) -> Task:
        """
        Crea la tarea y sus parámetros en una sola transacción segura.
        Si algo falla, ninguna tabla se modifica.
        """
        # 1. Crear la entidad Padre (Aggregate Root)
        task = await Task.create(
            algorithm_id  = dto.algorithm_id,
            user_id       = dto.user_id, 
            response_time = 0.0,
            # status="PENDING" # #44 https://github.com/Ismael-droid-01/calpulli-api/issues/44
        )

        # 2. Preparar e insertar valores numéricos (si existen)
        # Implementar logica cuando se resuelva #41 https://github.com/Ismael-droid-01/calpulli-api/issues/41
        
        # if dto.numeric_values:
        #     num_instances = [
        #         NumericParameterValue(
        #             task_id=task.task_id,
        #             parameter_id=val.parameter_id,
        #             value=val.value
        #         ) for val in dto.numeric_values
        #     ]
        #     # bulk_create es mucho más rápido que .save() en un loop
        #     await NumericParameterValue.bulk_create(num_instances)

        # # 3. Preparar e insertar valores de texto (si existen)
        # if dto.string_values:
        #     str_instances = [
        #         StringParameterValue(
        #             task_id=task.task_id,
        #             parameter_id=val.parameter_id,
        #             value=val.value
        #         ) for val in dto.string_values
        #     ]
        #     await StringParameterValue.bulk_create(str_instances)

        # Retornamos la tarea padre recién creada
        return task
    async def update_status(self, task_id: int, status: str, detail: str = None) -> Result[bool, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if not task:
                return Err(Exception(f"Task with id {task_id} not found."))
            
            # task.status = status # It must be a enum, im just modeling as fast as possible we can change this later
            if detail:
                task.detail = detail
            await task.save()
            return Ok(True)
        except Exception as e:
            print(f"Error updating task status: {e}")
            return Err(e)
    async def get_task_aggregate(self,task_id:int)->Result[TaskAggregate, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            # print(f"Fetched task for aggregate: {task}")
            if not task:
                L.error(f"Task with id {task_id} not found.")
                return Err(Exception(f"Task with id {task_id} not found."))

            L.debug({
                "msg": "Fetched task for aggregate",
                "task_id": task_id,
                "algorithm_id": task.algorithm_id,
                "user_id": task.user_id
            })

            algorithm = await Algorithm.get_or_none(algorithm_id=task.algorithm_id)
            if not algorithm:
                L.error(f"Algorithm with id {task.algorithm} not found.")
                return Err(Exception(f"Algorithm with id {task.algorithm} not found."))
            L.debug({
                "msg": "Fetched algorithm for aggregate",
                "algorithm_id": algorithm.algorithm_id,
                "algorithm_name": algorithm.name,
                "algorithm_type": algorithm.type
            })

            numeric_parameters = [
                # Default numeric parameters cause they dont exists yet (see more on #41 https://github.com/Ismael-droid-01/calpulli-api/issues/41 )
            ]
            string_parameters  = [
                # Default string parameters cause they dont exists yet (see more on #41 https://github.com/Ismael-droid-01/calpulli-api/issues/41 )
            ]
            L.warning("Using default parameters for aggregate since parameter tables are not implemented yet.")
            
            task_agg = TaskAggregate(
                task_id         = task.task_id,
                algorithm_name  = algorithm.name,
                algorithm_id    = algorithm.algorithm_id,
                status          = "PENDING" # this must be a enum, im just modeling as fast as possible we can change this later, also this is just a default value, the real status must be obtained from the DB, but for now we can set it as PENDING
            )


            return Ok(task_agg)
        except Exception as e:
            return Err(e)

    async def get_by_id(self, task_id: int) -> Result[Task, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if task:
                return Ok(task)
            else:
                return Err(Exception(f"Task with id {task_id} not found."))
        except Exception as e:
            return Err(e)

    async def get_by_user_id(self, user_id: int) -> Result[list[Task], Exception]:
        try:
            user = await UserProfile.get_or_none(id=user_id)
            if not user:
                return Err(Exception(f"User with id {user_id} not found."))
            
            tasks = await Task.filter(user_id=user_id).all()
            return Ok(tasks)
        except Exception as e:
            return Err(e)
    
class ResultsRepository:
    
    async def create(self, task_id: int, format: str, url: str) -> Result[ResultModel, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if not task:
                raise Exception(f"Task with id {task_id} not found.")
            
            result = await ResultModel.create(
                task        = task,
                format      = format,
                url         = url
            )
            return Ok(result)
        except Exception as e:
            print(f"Error creating result: {e}")
            return Err(e)

    async def get_by_task_id(self, task_id: int) -> Result[list[ResultModel], Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if not task:
                return Err(Exception(f"Task with id {task_id} not found."))
            
            results = await ResultModel.filter(task_id=task_id).all()
            return Ok(results)
        except Exception as e:
            return Err(e)

class DatasetsRepository:
    
    async def create(self, user_id: str, name: str, extension: str) -> Result[Dataset, Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
            if not user:
                raise Exception(f"User with id {user_id} not found.")
            
            dataset = await Dataset.create(
                user       = user,
                name       = name,
                extension  = extension
            )
            return Ok(dataset)
        except Exception as e:
            print(f"Error creating dataset: {e}")
            return Err(e)
    
    async def get_by_user_id(self, user_id: str) -> Result[list[Dataset], Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
            if not user:
                return Err(Exception(f"User with id {user_id} not found."))
            
            datasets = await Dataset.filter(user=user).all()
            return Ok(datasets)
        except Exception as e:
            return Err(e)

    async def delete(self, user_id: str, dataset_id: int) -> Result[bool, Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
            if not user:
                return Err(Exception(f"User with id {user_id} not found."))
            
            dataset = await Dataset.get_or_none(dataset_id=dataset_id, user=user)
            if dataset:
                await dataset.delete()
                return Ok(True)
            else:
                return Err(Exception(f"Dataset with id {dataset_id} not found for user {user_id}."))
        except Exception as e:
            return Err(e)