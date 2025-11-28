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

from differences.differences import get_diffs, get_required_by_diffs, Differences

def get_paths_from_gta_dat(input):
    for row in get_gta_cleaned_rows(input):
        if row[0] == "IMG":
            continue
        if row[0] != "IPL" and row[0] != "IDE":
            raise Exception("Unknown format of file")
        yield pathlib.Path("input/" + row[1].replace("\\", "/"))

def get_all_files(base_path):
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
    intentions = set(intentions)
    return intentions

def copy_file(data: tuple[str, str]):
    shutil.copyfile(data[0], data[1])

def copy_files_to_output(
    transform_files: Iterable[tuple[pathlib.Path, str]]
):
    def get_pairs(file_transformation: tuple[pathlib.Path, str]):
        return (file_transformation[0], get_output_path(file_transformation))

    def get_output_path(file_transformation: tuple[pathlib.Path, str]):
        main_dir_by_suffix = {
            "dff": "models",
            "txd": "textures",
            "col": "coll"
        }
        suffix = file_transformation[0].suffix[1:].lower()
        main_dir = pathlib.Path("output/Content").joinpath(pathlib.Path(main_dir_by_suffix[suffix]))
        relative_path = main_dir.joinpath(pathlib.Path(f"{file_transformation[1]}.{suffix}")).as_posix()

        return f"{str(relative_path).replace("\\", "/")}"

    copy_iter = map(get_pairs, transform_files)
    
    with multiprocessing.Pool() as p:
        p.map(copy_file, copy_iter)

def get_intensions_dict(gta_rows: Iterable[tuple[str]]):
    intentions_dict = {a: tuple(b) for a, b in groupby(
        get_gta_intentions(gta_rows),
        lambda x: type(x)
    )}
    return intentions_dict

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

use_log = True
log_path = "log.txt"

def send_message(text: str, to_print = True, to_log = True):
    global use_log, log_path

    if use_log and to_log:
        with open(log_path, "a") as file:
            file.write(text+"\n")
    if to_print:
        print(text)

def get_info_about_differences(diffs: Differences):
    for path in diffs.data_import_diffs.only_in_dat:
        yield f"diffs: Path {path} does not exist"

    for path in diffs.data_import_diffs.only_in_gta:
        yield f"diffs: Path {path} is not necessary"

    for intention in diffs.intentions_diffs.only_in_ipl:
        yield f"diffs: Model {intention.object_model} does not exist in IDEs"

    for intention in diffs.intentions_diffs.only_in_ide:
        yield f"diffs: Model {intention.object_model} is not necessary in IDEs"

    for model in diffs.models_import_diffs.only_in_dffs:
        yield f"diffs: DFF {model} does not exist in files"

    for texture in diffs.models_import_diffs.only_in_txds:
        yield f"diffs: TXD {texture} does not exist in files"

    for file in diffs.models_import_diffs.only_in_files:
        yield f"diffs: File {file} is not necessary"

def main():
    import os
    if os.path.exists(log_path):
        os.remove(log_path)

    import os
    if os.path.exists(log_path):
        os.remove(log_path)

    gta_path = "input/data/gta.dat"
    water_path = "input/data/water.dat"

    try:
        # ------ water.dat
        send_message("Reading water.dat")
        with open(water_path, "r") as file:
            input = file.read()
        
        water_intentions = get_water_intentions(get_water_cleaned_rows(input))

        # ------ water.lua
        send_message("Creating water.lua")
        with open("output/Settings/CWaterData.lua", "w") as file:
            text = get_water_lua(water_intentions)
            file.write(text)

        # ------ gta.dat
        send_message("Reading gta.dat")
        with open(gta_path, "r") as file:
            input = file.read()

        gta_paths = set(get_paths_from_gta_dat(input))
        grouped_gta_paths: dict[str, set[pathlib.Path]] = dict()
        for path in gta_paths:
            suffix = path.suffix[1:].lower()
            if suffix not in grouped_gta_paths:
                grouped_gta_paths[suffix] = set()
            grouped_gta_paths[suffix].add(path)
        gta_paths = set(get_paths_from_gta_dat(input))
        grouped_gta_paths: dict[str, set[pathlib.Path]] = dict()
        for path in gta_paths:
            suffix = path.suffix[1:].lower()
            if suffix not in grouped_gta_paths:
                grouped_gta_paths[suffix] = set()
            grouped_gta_paths[suffix].add(path)

        # ------ DFFs, TXDs, COLs        
        send_message("Loading IPLs")
        ipl_intentions = load_IPLs(grouped_gta_paths["ipl"])

        send_message("Loading IDEs")
        ide_intentions = load_IDEs(grouped_gta_paths["ide"])

        import_paths = set(get_all_files("input/models"))
        dat_paths = get_all_files("input/data")

        diffs = get_diffs(
            dat_paths,
            gta_paths,
            ipl_intentions,
            ide_intentions,
            import_paths
        )

        for message in get_info_about_differences(diffs):
            send_message(message, to_print = False)

        required_ipl_intentions, required_ide_intentions, transform_files = (
            get_required_by_diffs(diffs)
        )

        # ------ JSD
        send_message("Creating gta3.JSD")
        lods = get_lods(required_ipl_intentions)
        with open("output/gta3.JSD", "w") as file:
            text = get_jsd(required_ide_intentions, lods)
            file.write(text)

        # ------ JSP
        send_message("Creating gta3.JSP")
        with open("output/gta3.JSP", "w") as file:
            text = get_jsp(required_ipl_intentions)
            file.write(text)

        # ------ meta.xml
        send_message("Creating meta.xml")
        with open("output/meta.xml", "w") as file:
            text = get_meta(transform_files)
            file.write(text)

        send_message("Copying models, textures, cols")
        copy_files_to_output(transform_files)
    except Exception as e:
        send_message("Something is wrong")
        send_message(str(e))
        raise e
    else:
        send_message("Successful end")

if __name__ == '__main__':
    main()




