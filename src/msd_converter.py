import json
import os
import subprocess

BASE_DIR = os.path.dirname(__file__)
MSD_EXE = os.path.join(BASE_DIR, "msd.exe")


def parse_hitobjects(osu_file, mod="NM"):
    hitobjects = []
    in_section = False

    with open(osu_file, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()

            if line == "[HitObjects]":
                in_section = True
                continue

            if not in_section or not line:
                continue

            parts = line.split(",")
            x = int(parts[0])
            time = int(parts[2])
            obj_type = int(parts[3])

            if mod == "DT":
                time = int(time * 2 / 3)
            elif mod == "HT":
                time = int(time * 4 / 3)

            hitobjects.append({"x": x, "time": time, "type": obj_type})

    return hitobjects


def osu_to_etterna_rows(hitobjects, keycount=4):
    rows = {}
    column_width = 512 / keycount

    for obj in hitobjects:
        time = round(obj["time"] / 1000.0, 4)
        column = int(obj["x"] // column_width)
        rows[time] = rows.get(time, 0) | (1 << column)
        # LN releases are intentionally ignored (obj_type & 128)

    return [{"notes": rows[t], "time": t} for t in sorted(rows)]


def calculate_msd(notes):
    p = subprocess.Popen(
        [MSD_EXE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    output, err = p.communicate(json.dumps(notes))

    if err:
        print("MSD ERROR:", err)

    return json.loads(output)