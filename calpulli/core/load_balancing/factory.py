
from calpulli.core.load_balancing.strategies import LoadBalancerStrategy, RoundRobinStrategy, RandomStrategy
from calpulli.core.load_balancing.base import IRoryClient, RoryRemoteClient

class LoadBalancerFactory:
    _strategies = {
        "round_robin": RoundRobinStrategy(),
        "random": RandomStrategy()
    }

    @classmethod
    def get_balancer(cls, strategy_name: str = "round_robin") -> LoadBalancerStrategy:
        return cls._strategies.get(strategy_name, cls._strategies["round_robin"])

class RoryClientPool:
    def __init__(self, strategy_name: str = "round_robin"):
        self._clients = []
        self._balancer = LoadBalancerFactory.get_balancer(strategy_name)

    def add_client(self, client: IRoryClient):
        self._clients.append(client)

    def get_next_client(self) -> IRoryClient:
        return self._balancer.select_client(self._clients)