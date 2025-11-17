from .intention.create_object_type import CreateObjectType
from .remove_comment import remove_comment

def get_ide_intentions(text: str):
    lines = filter(lambda x: len(x) != 0, map(lambda x: str.strip(remove_comment(x)), text.split("\n")))

    state = 0
    for line in lines:
        if line == "end" and state == 1:
            state = 0
            break

        if state == 1:
            yield parse_ide_object(line)

        if line == "objs":
            state = 1

def parse_ide_object(text: str):
    strings = tuple(map(str.strip, text.split(",")))
    return CreateObjectType(
        int(strings[0]),
        strings[1],
        strings[2],
        float(strings[3]),
        int(strings[4]),
        strings[5] if len(strings) >= 6 else None,
        strings[6] if len(strings) >= 7 else None
    )