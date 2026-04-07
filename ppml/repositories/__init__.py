
from ppml.models import UserProfile, Algorithm, NumericParameter, StringParameter, Task, Result as ResultModel
from option import Err,Ok,Result

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

    async def create(self, user_id: str, algorithm_id: int, response_time: float) -> Result[Task, Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
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

    async def get_by_id(self, task_id: int) -> Result[Task, Exception]:
        try:
            task = await Task.get_or_none(task_id=task_id)
            if task:
                return Ok(task)
            else:
                return Err(Exception(f"Task with id {task_id} not found."))
        except Exception as e:
            return Err(e)

    async def get_by_user_id(self, user_id: str) -> Result[list[Task], Exception]:
        try:
            user = await UserProfile.get_or_none(user_id=user_id)
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