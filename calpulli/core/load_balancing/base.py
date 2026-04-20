# app/core/load_balancing/base.py
from abc import ABC, abstractmethod
from typing import List,Union
from roryclient.client import RoryClient
from roryclient.models import KmeansResponse,KnnResponse,NncResponse
from option import Result,Ok,Err
from calpulli.log import Log
from abc import ABC, abstractmethod
import calpulli.config as Cfg

from uuid import uuid4


L = Log(
    name = __name__,
    path = Cfg.CALPULLI_LOG_PATH,
)


class IRoryClient(ABC):
    @abstractmethod
    async def execute(self, algorithm: str, params: dict)->Result[Union[KmeansResponse, KnnResponse, NncResponse], Exception]:
        pass


class TaskResultDTO:
    def __init__(self,task_id:str, status: str, result: dict = None, error: str = None):
        self.task_id = task_id
        self.status  = status
        self.result  = result
        self.error   = error

class RoryRemoteClient(IRoryClient):
    def __init__(self, hostname: str,port:int=3001, timeout:int=5):
        self.client = RoryClient(
            hostname = hostname,
            port     = port,
            timeout  = timeout
        )
    async def execute(self, algorithm: str, params: dict)->Result[Union[KmeansResponse, KnnResponse, NncResponse], Exception]:
        algorithm_map = {
            'KMEANS': self.client.kmeans,
            'SKMEANS': self.client.skmeans,
        }
        if algorithm not in algorithm_map:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        sanitized_algorithm = algorithm.strip().upper()
        func = algorithm_map[sanitized_algorithm]

        try: 
            # L.warning("Static params")
            params = {
                "plaintext_matrix_filename":"auditdatadata",
                "plaintext_matrix_id":uuid4().hex,
            }
            raw_result:Result[Union[KmeansResponse, KnnResponse, NncResponse], Exception] =  func(**params)
            if raw_result.is_ok:
                L.info(f"Successfully executed algorithm {algorithm} with params {params}")
                return Ok(raw_result.unwrap())
            else:                
                L.error(f"Error executing algorithm {algorithm} with params {params}: {raw_result.unwrap_err()}")
                return Err(raw_result.unwrap_err())
            # L.debug({
            #     "msg": f"Received raw result from Rory for algorithm {algorithm} with params {params}",
            #     "raw_result": str(raw_result)
            # })
        except Exception as e:
            e= RuntimeError(f"Error executing algorithm {algorithm} with params {params}: {str(e)}")
            L.error({
                "msg": f"Error executing algorithm {algorithm} with params {params}: {str(e)}",
                "algorithm": algorithm,
                "params": params
            })
            return Err(e)