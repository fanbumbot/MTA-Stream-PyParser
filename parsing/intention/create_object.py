from typing import Union
from dataclasses import dataclass

from .intention import Intention

@dataclass(frozen=True)
class CreateObject(Intention):
    object_id: int
    object_model: str
    interior: int
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float
    LOD_id: Union[int, None] = None