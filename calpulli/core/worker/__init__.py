
from calpulli.core.load_balancing.factory import LoadBalancerFactory, RoryClientPool
from calpulli.core.load_balancing.base import RoryRemoteClient
# from calpulli.services import TaskService, ParameterService
from calpulli.services import TasksService,NumericParametersService,StringParametersService
import calpulli.middleware as MX
from calpulli.log import Log
import calpulli.config as Cfg
from option import  Result, Ok, Err
from typing import Any

rory_pool = RoryClientPool(strategy_name=Cfg.CALPULLI_LOAD_BALANCING_STRATEGY)
# default client, we can add more clients later if needed
rory_pool.add_client(
    RoryRemoteClient(
        hostname = Cfg.RORY_HOSTNAME,
        port     = Cfg.RORY_PORT,
        timeout  = Cfg.RORY_TIMEOUT
    )
)

L = Log(
    name = __name__,
    path = Cfg.CALPULLI_LOG_PATH,
)


async def process_mining_task(task_id:str)->Result[Any, Exception]:
    # 1. Validar existencia de la tarea vía TaskService
    task_service     = MX.get_tasks_service(MX.get_results_service())
    aggregate_result = await task_service.get_task_for_execution(task_id)
    if aggregate_result.is_err:
        e = aggregate_result.unwrap_err()
        # await task_service.update_status(task_id, "FAILED", f"Error fetching task aggregate: {str(e)}")
        #  For now we only finish the task and write in the logs, but we should update the task status in the database to "FAILED" and save the error message for future reference.
        # Also we can in the future consider returning a event. `TaskFailedEvent` that can be consumed by other parts of the system, like a notification service or a dashboard.
        L.error({
            "msg": f"Error fetching task aggregate for task_id {task_id}: {str(e)}"
        })
        return Err(e)
    task_aggregate = aggregate_result.unwrap()
    
    execution_params = {}
    for num_param in task_aggregate.numeric_parameters:
        execution_params[num_param.name] = num_param.value
        
    for str_param in task_aggregate.string_parameters:
        execution_params[str_param.name] = str_param.value

    # 4. Get client from Load Balancer
    client = rory_pool.get_next_client()
    
    if not client:
        await task_service.update_status(task_id, "FAILED", detail="No available Rory clients in pool.")
        L.error(f"No available Rory clients in pool for task {task_id}")
        return Err(Exception("No available Rory clients in pool"))

    # 5. Execution
    try:
        # Mark as running
        await task_service.update_status(task_id, "RUNNING")
        
        # Execute the heavy computation
        L.info(f"Executing {task_aggregate.algorithm_name} on task {task_id} with params {execution_params}")
        rory_result = await client.execute(task_aggregate.algorithm_name, execution_params)
        if rory_result.is_err:
            e = rory_result.unwrap_err()
            L.error(f"Execution failed for task {task_id} with error: {str(e)}")
            await task_service.update_status(task_id, "FAILED", detail=str(e))
            return Err(e)
        result  = rory_result.unwrap()
        # Save results and mark as completed
        await task_service.complete_task(task_id, result)
        L.info(f"Task {task_id} completed successfully.")
        return Ok(result)
    except Exception as e:
        L.error(f"Execution failed for task {task_id}: {e}")
        await task_service.update_status(task_id, "FAILED", detail=str(e))
        return Err(e)
    # parameter_service = ParameterService()

    # task = await task_service.get_by_id(task_id)
    # if not task:
    #     await task_service.update_status(task_id, "FAILED", "Task not found ID")
    #     return

    # # 2. Validar parámetros en DB antes de computo costoso
    # params = await parameter_service.get_validated_params(task_id)
    # if not params:
    #     await task_service.update_status(task_id, "FAILED", "Invalid or missing parameters")
    #     return

    # # 3. Obtener cliente del balanceador
    # client = rory_pool.get_next_client()
    
    # # 4. Ejecución
    # try:
    #     await task_service.update_status(task_id, "RUNNING")
    #     result = await client.execute(task.algorithm.name, params)
    #     await task_service.complete_task(task_id, result)
    # except Exception as e:
    #     await task_service.update_status(task_id, "FAILED", str(e))