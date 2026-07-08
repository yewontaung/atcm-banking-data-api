from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class PaginationResult(Generic[T]):

    items:list[T]
    page:int
    size:int
    total:int
