
from ppml.models import UserProfile, Algorithm, NumericParameter, StringParameter
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

    async def get_by_id(self, algorithm_id:int)->Result[Algorithm,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if algorithm:
                return Ok(algorithm)
            else:
                return Err(Exception(f"Algorithm with id {algorithm_id} not found."))
        except Exception as e:
            return Err(e)
    
    async def get_by_name(self, name:str)->Result[Algorithm,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(name=name)
            if algorithm:
                return Ok(algorithm)
            else:
                return Err(Exception(f"Algorithm with name {name} not found."))
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

class NumericParametersRepository:

    async def create(self, algorithm_id:int, type:str, default_value:float, max_value:float)->Result[NumericParameter,Exception]:
        try:
            algorithm = await Algorithm.get_or_none(algorithm_id=algorithm_id)
            if not algorithm:
                raise Exception(f"Algorithm with id {algorithm_id} not found.")

            parameter = await NumericParameter.create(
                algorithm_id    = algorithm_id,
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