from typing import Iterable
import pathlib

def get_meta_client_file_row(file_transformation: tuple[pathlib.Path, str]):
    main_dir_by_suffix = {
        "dff": "models",
        "txd": "textures",
        "col": "coll"
    }
    suffix = file_transformation[0].suffix[1:].lower()
    main_dir = pathlib.Path("Content").joinpath(pathlib.Path(main_dir_by_suffix[suffix]))
    relative_path = main_dir.joinpath(pathlib.Path(f"{file_transformation[1]}.{suffix}")).as_posix()

    row = f'<file src = "{relative_path}" type="client" />'
    return row

def get_meta(transform_files: Iterable[tuple[pathlib.Path, str]]):
    rows = (
        '<meta>',
        '\t<info type="script" name="MTA-Stream-Map" author="Unknown" description="MTA-Stream-Map-Conversion" version="3" Streamer="1" />',
        '',
        '\t<script src="Settings/CWaterData.lua" type="client" />',
        '',
        *map(
            lambda x: "\t" + get_meta_client_file_row(x),
            transform_files
        ),
        '',
        '</meta>'
    )

    output = '\n'.join(rows)
    return output