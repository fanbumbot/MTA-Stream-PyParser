from typing import Iterable
from itertools import chain

from .dat import get_dat_cleaned_rows
from .ipl import get_ipl_intentions
from .ide import get_ide_intentions

def get_gta_intentions_from_row(row: tuple[str, str]):
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

def get_gta_intentions(gta_rows: Iterable[tuple[str, str]]):
    return chain(*map(get_gta_intentions_from_row, gta_rows))

def get_gta_cleaned_rows(text: str):
    cleaned_rows = map(
        lambda x: tuple(map(
            str.strip,
            x.split(maxsplit = 1)
        )),
        get_dat_cleaned_rows(text)
    )
    return cleaned_rows