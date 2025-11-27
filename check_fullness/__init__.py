from typing import Iterable
import pathlib
from itertools import groupby

from parsing.intention.create_object import CreateObject
from parsing.intention.create_object_type import CreateObjectType

from .message import Message

from get_required_files_and_intentions import get_required_files_and_intentions

def check_fullness(
    dat_paths: Iterable[pathlib.Path],
    gta_paths: Iterable[pathlib.Path],
    ipl_intentions: Iterable[CreateObject],
    ide_intentions: Iterable[CreateObjectType],
    import_paths: Iterable[pathlib.Path]
) -> Iterable[Message]:
    dat_paths = set(dat_paths)
    gta_paths = set(gta_paths)
    ipl_intentions = set(ipl_intentions)
    ide_intentions = set(ide_intentions)
    import_paths = set(import_paths)


    # Data import check
    dat_paths_set = set(dat_paths)

    for path in gta_paths:
        if path in dat_paths_set:
            dat_paths_set.remove(path)
        else:
            yield Message(f"Data import warning: file '{str(path)}' does not exists")

    for path in dat_paths_set:
        yield Message(f"Data import warning: file '{str(path)}' is unnecessary")


    # Intentions check
    all_lods_from_ipl = {intention.LOD_id for intention in ipl_intentions}
    if -1 in all_lods_from_ipl:
        all_lods_from_ipl.remove(-1)

    all_models_from_ipl = {intention.object_model for intention in ipl_intentions}

    for object_id, model in ((intention.object_id, intention.object_model) for intention in ide_intentions):
        if model in all_models_from_ipl:
            all_models_from_ipl.remove(model)
        elif object_id in all_lods_from_ipl:
            all_lods_from_ipl.remove(object_id)
        else:
            yield Message(f"Intentions warning: exists in IDE, but don't use in IPL (model '{model}')")
    
    for model in all_models_from_ipl:
        yield Message(f"Intentions warning: exists in IPL, but don't use in IDE (model '{model}')")

    for object_id in all_lods_from_ipl:
        yield Message(f"Intentions warning: unknown LOD '{object_id}' in IPL")


    # Model import check
    # Extension check
    models_files_sets = {suffix: set(paths) for suffix, paths in groupby(import_paths, lambda x: x.suffix[1:].lower())}

    for key, paths in models_files_sets.items():
        if key != "dff" and key != "col" and key != "txd":
            for path in paths:
                yield Message(f"Model import warning: file '{str(path)}' has unknown extension '{key}'")

    # Required files check
    required_ipl_intentions, required_ide_intentions, required_files = (
        get_required_files_and_intentions(
            ipl_intentions,
            ide_intentions,
            import_paths
        )
    )

    for file in required_files:
        suffix = file.suffix[1:].lower()

        if suffix not in models_files_sets:
            raise KeyError(f"Model import error: unknown file suffix '{suffix}'")
        
        current_models_files = models_files_sets[suffix]

        if file in current_models_files:
            current_models_files.remove(file)
        else:
            yield Message(f"Model import warning: file '{str(file)}' does not exist")

    for suffix in models_files_sets:
        for file in models_files_sets[suffix]:
            yield Message(f"Model import warning: file '{str(file)}' is unnecessary")


