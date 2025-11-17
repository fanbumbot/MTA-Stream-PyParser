from typing import Iterable
from itertools import chain
import pathlib

def get_meta_client_file_row(path: pathlib.Path):
    relative_path = pathlib.Path("Content").joinpath(path.relative_to("input")).as_posix()
    row = f'<file src = "{relative_path}" type="client" />'
    return row

def get_meta(paths: Iterable[pathlib.Path]):
    rows = (
        '<meta>',
        '\t<info type="script" name="MTA-Stream-Map" author="Unknown" description="MTA-Stream-Map-Conversion" version="3" Streamer="1" />',
        '',
        *map(
            lambda x: "\t" + get_meta_client_file_row(x),
            paths
        ),
        '',
        '</meta>'
    )

    output = '\n'.join(rows)
    return output