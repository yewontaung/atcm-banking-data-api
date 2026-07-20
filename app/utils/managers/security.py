from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from functools import wraps
import inspect
from typing import Callable, ClassVar, Generator, ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

@dataclass(frozen=True)
class SecurityUser:
    user_id:str
    username:str
    roles:frozenset[str] = field(default_factory=frozenset)
    disabled:bool = field(default=False)

class SecurityException(Exception):
    def __init__(self, message:str):
        super().__init__(message)
        self.message = message

class SecurityContext:

    __user__:ClassVar[ContextVar[SecurityUser | None]] = ContextVar("security_user", default=None)

    @classmethod
    def set_user(cls, user:SecurityUser) -> Token[SecurityUser | None]:
        return cls.__user__.set(user)

    @classmethod        
    def reset_user(cls, token:Token[SecurityUser | None]):
        cls.__user__.reset(token)
    
    @classmethod
    def get_user(cls) -> SecurityUser | None:
        return cls.__user__.get()
    
class SecurityManager(Protocol):

    def has_roles(self, *roles:str) -> Callable[[Callable[P, R]], Callable[P, R]]:...

    def authenticated(self, func:Callable[P, R]) -> Callable[P, R]:...

class DefaultSecurityManager(SecurityManager):

    def has_roles(self, *roles:str):
        allowed = frozenset(roles)
        def decorate(func:Callable[P, R]):
            @wraps(func)
            async def wrapper(*args:P.args, **kwargs:P.kwargs) -> R:
                user = SecurityContext.get_user()
                if user is None:raise SecurityException("Not Authenticated.")
                if user.disabled:raise SecurityException("Not Authorized.")
                if not allowed.intersection(user.roles):raise SecurityException("Role is not Authorized.")
                result = func(*args, **kwargs)
                if inspect.isawaitable(result):
                    return await result
                return result

            return wrapper        
        return decorate
    
    def authenticated(self, func:Callable[P, R]):
        @wraps(func)
        async def wrapper(*args:P.args, **kwargs:P.kwargs) -> R:
            user = SecurityContext.get_user()
            if not user:raise SecurityException("Not Authenticated.")
            if user.disabled:raise SecurityException("Not Authorized.")
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                return await result
            return result
        return wrapper