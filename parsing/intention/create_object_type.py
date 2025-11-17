from typing import Union
from dataclasses import dataclass

from .intention import Intention

@dataclass(frozen=True)
class CreateObjectType(Intention):
    object_id: int
    object_model: str
    texture: str
    draw_distance: float
    flag: int
    time_on: Union[int, None] = None
    tine_off: Union[int, None] = None