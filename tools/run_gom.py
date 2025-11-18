#!/usr/bin/env python3
import sys
from gulfofmexico import run_file

if len(sys.argv) != 2:
    print("Usage: python3 run_gom.py <file.gom>")
    sys.exit(1)

run_file(sys.argv[1])
