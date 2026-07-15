from typing import Generic, TypeVar

from utils.basedto import BaseDto

T = TypeVar("T")

class PaginationResult(BaseDto, Generic[T]):

    items:list[T]
    page:int
    size:int
    total:int
