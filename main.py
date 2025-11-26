from typing import Iterable
from itertools import chain, groupby
import pathlib
import shutil
import multiprocessing

from parsing.ide import CreateObjectType
from parsing.ipl import CreateObject

from parsing.gta import get_gta_cleaned_rows
from parsing.gta import get_gta_intentions
from parsing.water_dat import get_water_intentions, get_water_cleaned_rows
from parsing.water_lua import get_water_lua

from parsing.jsd import get_jsd
from parsing.jsp import get_jsp

from parsing.meta import get_meta

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

def get_intensions_dict(gta_rows: Iterable[tuple[str]]):
    intentions_dict = {a: tuple(b) for a, b in groupby(
        get_gta_intentions(gta_rows),
        lambda x: type(x)
    )}
    return intentions_dict

def get_all_copy_iter(
    grouped_model_paths: dict[str, Iterable[str]],
    object_model_to_object_type,
    object_texture_to_object_type
):
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
    return all_copy_iter

def get_lods(create_object_intentions: Iterable[CreateObject]):
    lods = {
        x[0]: x[1] for x in filter(
            lambda x: x[1] is not None,
            map(
                lambda x: (x.object_id, x.LOD_id),
                create_object_intentions
            )
        )
    }
    return lods

def main():
    gta_path = "input/data/gta.dat"
    water_path = "input/data/water.dat"

    with open(water_path, "r") as file:
        input = file.read()
    
    water_intentions = get_water_intentions(get_water_cleaned_rows(input))

    with open("output/Settings/CWaterData.lua", "w") as file:
        text = get_water_lua(water_intentions)
        file.write(text)



    with open(gta_path, "r") as file:
        input = file.read()

    intentions_dict = get_intensions_dict(get_gta_cleaned_rows(input))

    model_paths = get_all_models_paths("input/models")
    grouped_model_paths = {
        a: tuple(b) for a, b in filter(
            lambda x: x[0] == '.dff' or x[0] == '.col' or x[0] == '.txd',
            groupby(model_paths, lambda x: x.suffix)
        )
    }

    object_model_to_object_type = {a.object_model: a for a in intentions_dict[CreateObjectType]}
    object_texture_to_object_type = {a.texture: a for a in intentions_dict[CreateObjectType]}

    all_copy_iter = get_all_copy_iter(
        grouped_model_paths,
        object_model_to_object_type,
        object_texture_to_object_type
    )

    with multiprocessing.Pool() as p:
        p.map(copy_file, all_copy_iter)

    lods = get_lods(intentions_dict[CreateObject])

    with open("output/gta3.JSD", "w") as file:
        text = get_jsd(intentions_dict[CreateObjectType], lods)
        file.write(text)

    with open("output/gta3.JSP", "w") as file:
        text = get_jsp(intentions_dict[CreateObject])
        file.write(text)

    with open("output/meta.xml", "w") as file:
        all_paths = chain(*grouped_model_paths.values())
        text = get_meta(all_paths)
        file.write(text)

if __name__ == '__main__':
    main()




