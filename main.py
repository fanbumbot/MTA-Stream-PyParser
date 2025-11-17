from typing import Iterable, Union
from dataclasses import dataclass

from itertools import chain, groupby
import pathlib
import shutil
import multiprocessing

import numpy as np

class Intention:
    pass

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

@dataclass(frozen=True)
class CreateObjectType(Intention):
    object_id: int
    object_model: str
    texture: str
    draw_distance: float
    flag: int
    time_on: Union[int, None] = None
    tine_off: Union[int, None] = None



def quaternion_to_euler(w, x, y, z):
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    if np.abs(sinp) >= 1:
        pitch = np.copysign(np.pi / 2, sinp)
    else:
        pitch = np.arcsin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def remove_comment(text: str):
    mark = text.find("#")
    if mark != -1:
        return text[:mark]
    return text

def get_ipl_intentions(text: str):
    lines = filter(lambda x: len(x) != 0, map(lambda x: str.strip(remove_comment(x)), text.split("\n")))

    state = 0
    for line in lines:
        if line == "end" and state == 1:
            state = 0
            break

        if state == 1:
            yield parse_ipl_object(line)

        if line == "inst":
            state = 1

def parse_ipl_object(text: str):
    strings = tuple(map(str.strip, text.split(",")))
    rx, ry, rz = quaternion_to_euler(
        float(strings[6]),
        float(strings[7]),
        float(strings[8]),
        float(strings[9]),
    )
    LOD_id = int(strings[10])
    return CreateObject(
        int(strings[0]),
        strings[1],
        int(strings[2]),
        float(strings[3]),
        float(strings[4]),
        float(strings[5]),
        rx,
        ry,
        rz,
        LOD_id if LOD_id != -1 else None
    )

def get_ide_intentions(text: str):
    lines = filter(lambda x: len(x) != 0, map(lambda x: str.strip(remove_comment(x)), text.split("\n")))

    state = 0
    for line in lines:
        if line == "end" and state == 1:
            state = 0
            break

        if state == 1:
            yield parse_ide_object(line)

        if line == "objs":
            state = 1

def parse_ide_object(text: str):
    strings = tuple(map(str.strip, text.split(",")))
    return CreateObjectType(
        int(strings[0]),
        strings[1],
        strings[2],
        float(strings[3]),
        int(strings[4]),
        strings[5] if len(strings) >= 6 else None,
        strings[6] if len(strings) >= 7 else None
    )

def get_intentions_from_row(row: tuple[str, str]):
    file_type = row[0]
    path = "input/" + row[1].replace("\\", "/")
    
    if file_type == "IMG":
        return
    
    if file_type != "IPL" and file_type != "IDE":
        raise Exception("Unknown format")
    
    try:
        with open(path, "r") as file:
            text = file.read()
    except FileNotFoundError as e:
        print(f"File {e.filename} does not exist")
        return

    if file_type == "IPL":
        for intention in get_ipl_intentions(text):
            yield intention
    elif file_type == "IDE":
        for intention in get_ide_intentions(text):
            yield intention
    else:
        raise Exception(f"Unknown format ({file_type})")

def get_all_intentions(gta_rows: Iterable[tuple[str, str]]):
    return groupby(
        chain(*map(get_intentions_from_row, gta_rows)), 
        lambda x: type(x)
    )

def get_flag(flag: int):
    return flag == 4 or flag == 8

def is_culled(culled: int):
    return culled == 2097152

def write_jsd_file(path: str, intentions: Iterable[CreateObjectType], lods: dict[int, int]):
    with open(path, "w") as file:
        for intention in intentions:
            model = intention.object_model
            texture = intention.texture
            draw_distance = intention.draw_distance
            flag = "true" if get_flag(intention.flag) else "nil"
            culled = "true" if is_culled(intention.flag) else "nil"
            lod = "true" if intention.object_id in lods else "nil"
            time_on = intention.time_on
            time_off = intention.tine_off

            if time_on and time_off:
                output = f"{model},{model},{texture},{model},{draw_distance},{flag},{culled},{lod},{time_on},{time_off}"
            else:
                output = f"{model},{model},{texture},{model},{draw_distance},{flag},{culled},{lod}"
            file.write(output + "\n")

def write_jsp_file(path: str, intentions: Iterable[CreateObject]):
    with open(path, "w") as file:
        file.write("0,0,0\n")
        for intention in intentions:
            model = intention.object_model
            interior = intention.interior
            x = intention.x
            y = intention.y
            z = intention.z
            rx = intention.rx
            ry = intention.ry
            rz = intention.rz
            output = f"{model},{interior},-1,{x},{y},{z},{rx},{ry},{rz}"

            file.write(output + "\n")

def get_all_models_paths(base_path):
    for path in pathlib.Path(base_path).rglob("*"):
        if not path.is_file():
            continue
        yield path


class CopyFileData:
    def __init__(self, output_path: str, all_objects: dict, path: pathlib.Path):
        self.output_path = output_path
        self.all_objects = all_objects
        self.path = path

def copy_file(data: CopyFileData):
    path = data.path
    if path.stem not in data.all_objects:
        return
    shutil.copyfile(path, f"{data.output_path}/{path.name}")

def main():
    gta_path = "input/data/gta.dat"
    with open(gta_path, "r") as file:
        input = file.read()

    lines = input.split("\n")
    clean_lines_str = filter(
        lambda x: len(x) != 0,
        map(
            lambda x: remove_comment(x).strip(),
            lines
        )
    )
    gta_rows = map(
        lambda x: tuple(map(
            str.strip,
            x.split(maxsplit = 1)
        )),
        clean_lines_str
    )

    intentions_dict = {a: tuple(b) for a, b in get_all_intentions(gta_rows)}

    model_paths = get_all_models_paths("input/models")
    grouped_model_paths = {
        a: tuple(b) for a, b in filter(
            lambda x: x[0] == '.dff' or x[0] == '.col' or x[0] == '.txd',
            groupby(model_paths, lambda x: x.suffix)
        )
    }

    object_model_to_object_type = {a.object_model: a for a in intentions_dict[CreateObjectType]}
    object_texture_to_object_type = {a.texture: a for a in intentions_dict[CreateObjectType]}

    dff_iter = map(
        lambda x: CopyFileData(
            f"output/Content/models",
            object_model_to_object_type,
            x
        ),
        grouped_model_paths[".dff"]
    )
    col_iter = map(
        lambda x: CopyFileData(
            f"output/Content/coll",
            object_model_to_object_type,
            x
        ),
        grouped_model_paths[".col"]
    )
    txd_iter = map(
        lambda x: CopyFileData(
            f"output/Content/textures",
            object_texture_to_object_type,
            x
        ),
        grouped_model_paths[".txd"]
    )

    all_copy_iter = chain(dff_iter, col_iter, txd_iter)

    with multiprocessing.Pool() as p:
        p.map(copy_file, all_copy_iter)

    lods = {
        x[0]: x[1] for x in filter(
            lambda x: x[1] is not None,
            map(
                lambda x: (x.object_id, x.LOD_id),
                intentions_dict[CreateObject]
            )
        )
    }

    write_jsd_file("output/gta3.JSD", intentions_dict[CreateObjectType], lods)
    write_jsp_file("output/gta3.JSP", intentions_dict[CreateObject])

if __name__ == '__main__':
    main()




