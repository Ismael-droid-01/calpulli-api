# app/core/load_balancing/strategies.py
from abc import ABC, abstractmethod
from typing import List
import random
from calpulli.core.load_balancing.base  import IRoryClient


class LoadBalancerStrategy(ABC):
    @abstractmethod
    def select_client(self, clients: List[IRoryClient]):
        pass

class RoundRobinStrategy(LoadBalancerStrategy):
    def __init__(self):
        self._index = 0

    def select_client(self, clients: List[IRoryClient]):
        if not clients: return None
        client       = clients[self._index % len(clients)]
        self._index += 1
        return client

class RandomStrategy(LoadBalancerStrategy):
    def select_client(self, clients: List[IRoryClient]):
        return random.choice(clients) if clients else None