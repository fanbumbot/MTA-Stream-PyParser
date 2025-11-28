from parsing.intention.create_object import CreateObject
from parsing.intention.create_object_type import CreateObjectType

import pathlib

class DataImportDifferences:
    def __init__(
        self,
        only_in_dat: set[pathlib.Path],
        only_in_gta: set[pathlib.Path],
        in_both: set[pathlib.Path]
    ):
        self.only_in_dat = only_in_dat
        self.only_in_gta = only_in_gta
        self.in_both = in_both

class IntentionsDifferences:
    def __init__(
        self,
        only_in_ipl: set[CreateObjectType],
        only_in_ide: set[CreateObject],
        ipl_in_both: set[CreateObject],
        ide_in_both: set[CreateObjectType]
    ):
        self.only_in_ipl = only_in_ipl
        self.only_in_ide = only_in_ide
        self.ipl_in_both = ipl_in_both
        self.ide_in_both = ide_in_both

class ModelsImportDifferences:
    def __init__(
        self,
        only_in_dffs: set[str],
        only_in_txds: set[str],
        only_id_cols: set[str],
        only_in_files: set[pathlib.Path],
        in_both: set[tuple[str, pathlib.Path]]
    ):
        self.only_in_dffs = only_in_dffs
        self.only_in_txds = only_in_txds
        self.only_in_cols = only_id_cols
        self.only_in_files = only_in_files
        self.in_both = in_both

class RequiredIntentionsAndFiles:
    def __init__(
        self,
        required_ipl_intentions: set[CreateObject],
        required_ide_intentions: set[CreateObjectType],
        required_files: set[pathlib.Path]
    ):
        self.required_ipl_intentions = required_ipl_intentions
        self.required_ide_intentions = required_ide_intentions
        self.required_files = required_files

class Differences:
    def __init__(
        self,
        data_import_diffs: DataImportDifferences,
        intentions_diffs: IntentionsDifferences,
        models_import_diffs: ModelsImportDifferences
    ):
        self.data_import_diffs = data_import_diffs
        self.intentions_diffs = intentions_diffs
        self.models_import_diffs = models_import_diffs