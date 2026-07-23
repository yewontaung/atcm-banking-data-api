from collections import defaultdict
from typing import Callable, Protocol, Type, TypeVar


E = TypeVar("E")
R = TypeVar("R")

class EventManager(Protocol):
    def listen(self, event:Type[E]) -> Callable[[Callable[[E], R]], Callable[[E], R]]:...
    def publish(self, event:E):...
    def handlers(self, event:Type[E]) -> list[Callable[[E], R]]:...

class SimpleEventManager(EventManager):

    def __init__(self):
        self.registry:dict[Type[E], list[Callable[[E], R]]] = defaultdict(list)

    def listen(self, event:Type[E]) -> Callable[[Callable[[E], R]], Callable[[E], R]]:
        def decorate(func:Callable[[E], R]) -> Callable[[E], R]:
            self.registry[event].append(func)
            return func
        return decorate
    
    def publish(self, event:E):
        for handler in self.registry.get(type(event), []):
            handler(event)

    def handlers(self, event:Type[E]) -> list[Callable[[E], R]]:
        return self.registry.get(event, [])