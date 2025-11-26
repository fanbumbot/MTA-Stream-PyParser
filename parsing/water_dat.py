
from typing import Iterable

from .intention.create_water import CreateWater, Point
from .dat import get_dat_cleaned_rows

def get_water_intentions_from_row(row: str):
    numbers = [x.strip() for x in row.split()]
    if len(numbers) != 22 and len(numbers) != 29:
        raise Exception("Unknown format")
    
    points = map(
        lambda index: Point(
            float(numbers[index]),
            float(numbers[index+1]),
            float(numbers[index+2])
        ),
        range(0, len(numbers)-1, 7)
    )
    type = int(numbers[-1])
    intention = CreateWater(tuple(points), type)
    return intention


def get_water_intentions(water_rows: Iterable[str]):
    return map(get_water_intentions_from_row, water_rows)

def get_water_cleaned_rows(text: str):
    return filter(lambda x: x != "processed", get_dat_cleaned_rows(text))
