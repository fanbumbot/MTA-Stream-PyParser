from typing import Iterable, Union
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
from parsing.ipl import get_ipl_intentions
from parsing.ide import get_ide_intentions

from parsing.jsd import get_jsd
from parsing.jsp import get_jsp

from parsing.meta import get_meta

def get_paths_from_gta_dat(input):
    for row in get_gta_cleaned_rows(input):
        if row[0] == "IMG":
            continue
        if row[0] != "IPL" and row[0] != "IDE":
            raise Exception("Unknown format of file")
        yield pathlib.Path("input/" + row[1].replace("\\", "/"))

def get_all_models_paths(base_path):
    for path in pathlib.Path(base_path).rglob("*"):
        if not path.is_file():
            continue
        yield path

def get_intentions_from_file(path: pathlib.Path):
    suffix = path.suffix[1:].lower()
    if suffix != "ide" and suffix != "ipl":
        raise Exception(f"Unknown format '{suffix}' of file '{path}'")
    
    with open(path, 'r') as file:
        text = file.read()

    if suffix == "ide":
        intentions = get_ide_intentions(text)
    elif suffix == "ipl":
        intentions = get_ipl_intentions(text)
    return set(intentions)

def copy_file(data: tuple[str, str]):
    shutil.copyfile(data[0], data[1])

def copy_files_to_output(
    paths: Iterable[pathlib.Path]
):
    def get_pairs(input_path: pathlib.Path):
        return (input_path, get_output_path(input_path))

    def get_output_path(input_path: pathlib.Path):
        input_path = input_path.relative_to("input/models")
        input_path = input_path.relative_to(input_path.parents[-2])
        suffix = input_path.suffix[1:].lower()
        if suffix == "dff":
            output_dir = "output/Content/models"
        elif suffix == "txd":
            output_dir = "output/Content/textures"
        elif suffix == "col":
            output_dir = "output/Content/coll"
        else:
            Exception(f"Unknown format '{suffix}' of file '{input_path}'")
        return f"{output_dir}/{str(input_path).replace("\\", "/")}"

    copy_iter = map(get_pairs, paths)
    
    with multiprocessing.Pool() as p:
        p.map(copy_file, copy_iter)

def get_intensions_dict(gta_rows: Iterable[tuple[str]]):
    intentions_dict = {a: tuple(b) for a, b in groupby(
        get_gta_intentions(gta_rows),
        lambda x: type(x)
    )}
    return intentions_dict

def get_required_files_and_intentions(
    ipl_intentions: set[CreateObject],
    ide_intentions: set[CreateObjectType],
    all_files: Iterable[pathlib.Path]
):
    all_dffs = {a for a in map(lambda x: x.object_model, ipl_intentions)}
    required_ide_intentions = set(filter(lambda x: x.object_model in all_dffs, ide_intentions))
    
    required_dffs = map(lambda x: x.object_model, required_ide_intentions)
    required_txds = {a for a in map(lambda x: x.texture, required_ide_intentions)}

    required_files = set(filter(
        lambda x: (
            x.stem in required_dffs or
            x.stem in required_txds
        ),
        all_files
    ))
    return ipl_intentions, required_ide_intentions, required_files

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

def load_IPLs(paths: Iterable[pathlib.Path]):
    with multiprocessing.Pool() as p:
        ipl_intentions = set(chain(*p.map(
            get_intentions_from_file,
            paths
        )))
    return ipl_intentions

def load_IDEs(paths: Iterable[pathlib.Path]):
    with multiprocessing.Pool() as p:
        ide_intentions = set(chain(*p.map(
            get_intentions_from_file,
            paths
        )))
    return ide_intentions

def main():
    gta_path = "input/data/gta.dat"
    water_path = "input/data/water.dat"

    try:
        # ------ water.dat
        print("Reading water.dat")
        with open(water_path, "r") as file:
            input = file.read()
        
        water_intentions = get_water_intentions(get_water_cleaned_rows(input))

        # ------ water.lua
        print("Creating water.lua")
        with open("output/Settings/CWaterData.lua", "w") as file:
            text = get_water_lua(water_intentions)
            file.write(text)

        # ------ gta.dat
        print("Reading gta.dat")
        with open(gta_path, "r") as file:
            input = file.read()

        paths = get_paths_from_gta_dat(input)
        grouped_input_paths = {ext: {path for path in paths} for ext, paths in groupby(paths, lambda x: x.suffix[1:].lower())}
        
        print("Loading IPLs")
        ipl_intentions = load_IPLs(grouped_input_paths["ipl"])

        print("Loading IDEs")
        ide_intentions = load_IDEs(grouped_input_paths["ide"])

        # ------ DFFs, TXDs, COLs
        all_files = get_all_models_paths("input/models")

        required_ipl_intentions, required_ide_intentions, required_files = (
            get_required_files_and_intentions(
                ipl_intentions,
                ide_intentions,
                all_files
            )
        )

        # ------ JSD
        print("Creating gta3.JSD")
        lods = get_lods(required_ipl_intentions)
        with open("output/gta3.JSD", "w") as file:
            text = get_jsd(required_ide_intentions, lods)
            file.write(text)

        # ------ JSP
        print("Creating gta3.JSP")
        with open("output/gta3.JSP", "w") as file:
            text = get_jsp(required_ipl_intentions)
            file.write(text)

        # ------ meta.xml
        print("Creating meta.xml")
        with open("output/meta.xml", "w") as file:
            text = get_meta(required_files)
            file.write(text)

        print("Copying models, textures, coll")
        copy_files_to_output(required_files)
    except Exception as e:
        print("Something is wrong")
        print(e)
    else:
        print("Successful end")

if __name__ == '__main__':
    main()




