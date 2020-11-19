#!/usr/bin/env python3

import re
import subprocess
import os

KATS_DIR = os.path.dirname(os.path.realpath(__file__))


os.chdir(KATS_DIR)
for file in os.listdir("."):
    if re.match("^[a-z2]+(_v[0-9]+)?$", file):
        new = subprocess.run(["shasum", "-a", "256", file], capture_output=True, text=True, check=True).stdout
        old = open(file + ".shasum", "r").read()
        if new == old:
            print(file, "\tOK")
        else:
            print(file, "\tERROR")
