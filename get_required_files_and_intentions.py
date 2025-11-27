from typing import Iterable
import pathlib

from parsing.intention.create_object import CreateObject
from parsing.intention.create_object_type import CreateObjectType

def get_required_files_and_intentions(
    ipl_intentions: set[CreateObject],
    ide_intentions: set[CreateObjectType],
    import_paths: Iterable[pathlib.Path]
):
    all_dffs = {a for a in map(lambda x: x.object_model, ipl_intentions)}
    required_ide_intentions = set(filter(lambda x: x.object_model in all_dffs, ide_intentions))
    
    required_dffs = {a.object_model for a in required_ide_intentions}
    required_txds = {a for a in map(lambda x: x.texture, required_ide_intentions)}

    required_files = set(filter(
        lambda x: (
            x.stem in required_dffs or
            x.stem in required_txds
        ),
        import_paths
    ))
    return ipl_intentions, required_ide_intentions, required_files