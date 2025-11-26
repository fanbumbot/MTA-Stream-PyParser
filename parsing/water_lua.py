from typing import Iterable

from .intention.create_water import CreateWater, Point

WATER_TEMPLATE = """Water = {
%s
}

for i,v in pairs(Water) do
    local water = createWater (unpack(v))
    local x,y,z = getElementPosition(water)
    setElementPosition(water,x,y,z)
end
"""

def get_cord_str(cord: float):
    return str(cord)

def get_point_str(point: Point):
    return ",".join(map(get_cord_str, point))

def get_water_intention_str(intention: CreateWater):
    return ",".join(map(get_point_str, intention.points))

def get_water_lua(water_intentions: Iterable[CreateWater]):
    return WATER_TEMPLATE % (
        "{" +
            "},\n{".join(map(get_water_intention_str, water_intentions)) +
        "},"
    )