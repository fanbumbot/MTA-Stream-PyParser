from typing import Union
from dataclasses import dataclass
from collections import namedtuple

from .intention import Intention

Point = namedtuple("Point", ['x', 'y', 'z'])

@dataclass(frozen=True)
class CreateWater(Intention):
    points: tuple[Point]
    type: int