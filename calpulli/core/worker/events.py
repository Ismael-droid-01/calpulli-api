class TaskCreatedEvent:
    def __init__(self, task_id: int, max_tries: int = 3):
        self.task_id = task_id
        self.max_tries = max_tries
        self.current_tries = 0