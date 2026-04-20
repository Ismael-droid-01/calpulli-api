import asyncio
from calpulli.core.worker.events import TaskCreatedEvent
from calpulli.log import Log
from calpulli.core.worker import process_mining_task
import calpulli.config as Cfg

L = Log(
    name = __name__,
    path = Cfg.CALPULLI_LOG_PATH,
)

class TaskConsumer:
    def __init__(self, n_workers: int = 1, max_queue_size: int = 100):
        # maxsize define tu threshold. Si la cola se llena, el POST /tasks tendrá que esperar o fallar.
        self.queue = asyncio.Queue(maxsize=max_queue_size)
        self.n_workers = n_workers
        self.workers = []

    async def start(self):
        """Inicia los workers en background."""
        L.info(f"Starting {self.n_workers} background workers...")
        for i in range(self.n_workers):
            task = asyncio.create_task(self._worker_loop(f"Worker-{i+1}"))
            self.workers.append(task)

    async def stop(self):
        """Detiene los workers de forma segura al apagar el servidor."""
        L.info("Stopping background workers...")
        for w in self.workers:
            w.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)

    async def push_event(self, task_id: str):
        """Agrega un evento a la cola."""
        await self.queue.put(task_id)
        L.info(f"Task {task_id} pushed to queue. Queue size: {self.queue.qsize()}")

    async def _worker_loop(self, worker_name: str):
        """El loop infinito que escucha la cola."""
        while True:
            try:
                event = await self.queue.get()
                L.info(f"[{worker_name}] Picked up task {event}")
                if isinstance(event, TaskCreatedEvent):
                    task_id = event.task_id
                else:
                    L.error(f"[{worker_name}] Received unknown event type: {type(event)}. Skipping.")
                    self.queue.task_done()
                    continue
            except asyncio.CancelledError:
                break

            try:
                result = await process_mining_task(task_id)
                if result.is_ok:
                    L.info(f"[{worker_name}] Task {task_id} completed successfully.")
                else:
                    L.error(f"[{worker_name}] Task {task_id} failed with error: {result.unwrap_err()}")
                    if event.current_tries < event.max_tries:
                        event.current_tries += 1
                        L.info(f"[{worker_name}] Re-enqueuing task {task_id} for retry. Remaining tries: {event.max_tries - event.current_tries}")
                        await asyncio.sleep(5)  # Optional: add a delay before retrying
                        await self.push_event(event)
                # print(f"[{worker_name}] Finished processing task {task_id} with result: {result}")
            except asyncio.CancelledError:
                L.warning(f"[{worker_name}] Cancelled while processing {task_id}")
                self.queue.task_done()  # Aseguramos marcar la tarea como hecha para liberar espacio en la cola
            except Exception as e:
                L.error(f"[{worker_name}] Critical error processing {task_id}: {e}")
                if event.current_tries < event.max_tries:
                    event.current_tries += 1
                    L.info(f"[{worker_name}] Re-enqueuing task {task_id} for retry after critical error. Remaining tries: {event.max_tries - event.current_tries}")
                    await self.push_event(event)
            finally:
                L.warning(f"[{worker_name}] Finished processing {task_id}. Marking task as done.")
                self.queue.task_done()