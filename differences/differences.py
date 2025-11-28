from typing import Iterable
import pathlib
from itertools import chain

from parsing.intention.create_object import CreateObject
from parsing.intention.create_object_type import CreateObjectType

from .dto import DataImportDifferences, Differences, IntentionsDifferences, ModelsImportDifferences, RequiredIntentionsAndFiles

def get_data_import_diffs(
    dat_paths: Iterable[pathlib.Path],
    gta_paths: Iterable[pathlib.Path],
):
    dat_paths = set(dat_paths)
    gta_paths = set(gta_paths)

    diffs = DataImportDifferences(
        dat_paths - gta_paths,
        gta_paths - dat_paths,
        dat_paths & gta_paths
    )
    return diffs

def get_intentions_diffs(
    ipl_intentions: Iterable[CreateObject],
    ide_intentions: Iterable[CreateObjectType],
):
    ipl_intentions = set(ipl_intentions)
    ide_intentions = set(ide_intentions)

    lods = {x.LOD_id: x for x in ipl_intentions}

    only_in_ipl: dict[str, set[CreateObject]] = dict()
    for x in ipl_intentions:
        model = x.object_model
        if model not in only_in_ipl:
            only_in_ipl[model] = set()
        only_in_ipl[model].add(x)
        
    only_in_ide = {x.object_model: x for x in ide_intentions}
    ipl_in_both = set()
    ide_in_both = set()

    for intention in (x for x in ide_intentions):
        model = intention.object_model
        object_id = intention.object_id
        if model in only_in_ipl:
            ipl_in_both = ipl_in_both | only_in_ipl[model]
            ide_in_both.add(intention)
            del only_in_ipl[model]
        elif object_id in lods:
            ipl_in_both.add(lods[object_id])
            ide_in_both.add(intention)
        else:
            only_in_ide[model] = intention

    diffs = IntentionsDifferences(
        set(chain(*only_in_ipl.values())),
        set(only_in_ide.values()),
        ipl_in_both,
        ide_in_both
    )
    return diffs

def get_models_import_diffs(
    required_ide_intentions: Iterable[CreateObjectType],
    import_paths: Iterable[pathlib.Path]
):
    required_ide_intentions = set(required_ide_intentions)
    import_paths = set(import_paths)

    # Object requires txd, dff and col files

    only_in_dffs = {x.object_model.lower() for x in required_ide_intentions}
    only_in_txds = {x.texture.lower() for x in required_ide_intentions}
    only_in_cols = {x.object_model.lower() for x in required_ide_intentions}
    only_in_files = set()
    in_all: set[tuple[str, pathlib.Path]] = set()

    for file in import_paths:
        name = file.stem.lower()
        suffix = file.suffix[1:].lower()

        if suffix == "dff" and name in only_in_dffs:
            in_all.add((name, file))
            only_in_dffs.remove(name)
        elif suffix == "col" and name in only_in_cols:
            in_all.add((name, file))
            only_in_cols.remove(name)
        elif suffix == "txd" and name in only_in_txds:
            in_all.add((name, file))
            only_in_txds.remove(name)
        else:
            only_in_files.add(file)

    diffs = ModelsImportDifferences(
        only_in_dffs,
        only_in_txds,
        only_in_cols,
        only_in_files,
        in_all
    )
    return diffs

def get_diffs(
    dat_paths: Iterable[pathlib.Path],
    gta_paths: Iterable[pathlib.Path],
    ipl_intentions: Iterable[CreateObject],
    ide_intentions: Iterable[CreateObjectType],
    import_paths: Iterable[pathlib.Path]
):
    data_import_diffs = get_data_import_diffs(
        dat_paths,
        gta_paths
    )

    intentions_diffs = get_intentions_diffs(
        ipl_intentions,
        ide_intentions
    )

    models_import_diffs = get_models_import_diffs(
        intentions_diffs.ide_in_both,
        import_paths
    )

    diffs = Differences(
        data_import_diffs,
        intentions_diffs,
        models_import_diffs
    )
    return diffs

def get_required_by_diffs(
    diffs: Differences
):
    required_ipls = set(diffs.intentions_diffs.ipl_in_both)
    required_ides = set()

    files_by_suffix: dict[str, dict[str, pathlib.Path]] = dict()
    transform_files: set[tuple[pathlib.Path, str]] = set()

    for name, file in diffs.models_import_diffs.in_all:
        suffix = file.suffix[1:].lower()
        if suffix not in files_by_suffix:
            files_by_suffix[suffix] = dict()
        files_by_suffix[suffix][name] = file

    for intention in diffs.intentions_diffs.ide_in_both:
        line_dff = intention.object_model
        line_txd = intention.texture
        line_col = intention.object_col

        uni_dff = line_dff.lower()
        uni_txd = line_txd.lower()
        uni_col = line_col.lower()

        if uni_dff in files_by_suffix["dff"]:
            file_dff = files_by_suffix["dff"][uni_dff]
            transform_files.add((file_dff, uni_dff))

        if uni_txd in files_by_suffix["txd"]:
            file_txd = files_by_suffix["txd"][uni_txd]
            transform_files.add((file_txd, uni_txd))

        if uni_col in files_by_suffix["col"]:
            file_col = files_by_suffix["col"][uni_col]
            transform_files.add((file_col, uni_col))
        else:
            uni_col = None
        
        new_intention = CreateObjectType(
            intention.object_id,
            uni_dff,
            uni_col,
            uni_txd,
            intention.draw_distance,
            intention.flag,
            intention.time_on,
            intention.tine_off
        )

        required_ides.add(new_intention)

    return required_ipls, required_ides, transform_files

