from typing import Iterable
from functools import partial

from .intention.create_object_type import CreateObjectType

def get_flag(flag: int):
    return flag == 4 or flag == 8

def is_culled(culled: int):
    return culled == 2097152

def get_jsd_row(intention: CreateObjectType, lods: dict[int, int]):
    model = intention.object_model
    collision = "nil" if intention.object_col is None else intention.object_col
    texture = intention.texture
    draw_distance = intention.draw_distance
    flag = "true" if get_flag(intention.flag) else "nil"
    culled = "true" if is_culled(intention.flag) else "nil"
    lod = "true" if intention.object_id in lods else "nil"
    time_on = intention.time_on
    time_off = intention.tine_off

    if time_on and time_off:
        output = f"{model},{model},{texture},{collision},{draw_distance},{flag},{culled},{lod},{time_on},{time_off}"
    else:
        output = f"{model},{model},{texture},{collision},{draw_distance},{flag},{culled},{lod}"
    return output

def get_jsd(intentions: Iterable[CreateObjectType], lods: dict[int, int]):
    handler = partial(get_jsd_row, lods=lods)
    rows = map(
        handler,
        intentions
    )
    
    output = '\n'.join(rows)
    return output
