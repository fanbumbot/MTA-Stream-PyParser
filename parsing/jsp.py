from typing import Iterable
from itertools import chain

from .intention.create_object import CreateObject

def get_jsp_row(intention: CreateObject):
    model = intention.object_model
    interior = intention.interior
    x = intention.x
    y = intention.y
    z = intention.z
    rx = intention.rx
    ry = intention.ry
    rz = intention.rz
    output = f"{model},{interior},-1,{x},{y},{z},{rx},{ry},{rz}"
    return output

def get_jsp(intentions: Iterable[CreateObject]):
    rows = chain(
        ("0,0,0",),
        map(
            get_jsp_row,
            intentions
        )
    )
    output = '\n'.join(rows)
    return output