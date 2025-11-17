import numpy as np

from .intention.create_object import CreateObject

from .remove_comment import remove_comment

def quaternion_to_euler(w, x, y, z):
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (w * y - z * x)
    if np.abs(sinp) >= 1:
        pitch = np.copysign(np.pi / 2, sinp)
    else:
        pitch = np.arcsin(sinp)

    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def get_ipl_intentions(text: str):
    lines = filter(lambda x: len(x) != 0, map(lambda x: str.strip(remove_comment(x)), text.split("\n")))

    state = 0
    for line in lines:
        if line == "end" and state == 1:
            state = 0
            break

        if state == 1:
            yield parse_ipl_object(line)

        if line == "inst":
            state = 1

def parse_ipl_object(text: str):
    strings = tuple(map(str.strip, text.split(",")))
    rx, ry, rz = quaternion_to_euler(
        float(strings[6]),
        float(strings[7]),
        float(strings[8]),
        float(strings[9]),
    )
    LOD_id = int(strings[10])
    return CreateObject(
        int(strings[0]),
        strings[1],
        int(strings[2]),
        float(strings[3]),
        float(strings[4]),
        float(strings[5]),
        rx,
        ry,
        rz,
        LOD_id if LOD_id != -1 else None
    )