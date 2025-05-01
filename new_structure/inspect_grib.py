#!/usr/bin/env python3

import eccodes
import sys
from pathlib import Path

def inspect_grib(grib_file):
    """Inspect a GRIB2 file and print its contents."""
    with open(grib_file, 'rb') as f:
        while True:
            msg = eccodes.codes_grib_new_from_file(f)
            if msg is None:
                break
                
            print("\nMessage:")
            print(f"- shortName: {eccodes.codes_get(msg, 'shortName')}")
            print(f"- paramId: {eccodes.codes_get(msg, 'paramId')}")
            print(f"- typeOfLevel: {eccodes.codes_get(msg, 'typeOfLevel')}")
            print(f"- level: {eccodes.codes_get(msg, 'level')}")
            print(f"- stepType: {eccodes.codes_get(msg, 'stepType')}")
            
            eccodes.codes_release(msg)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python inspect_grib.py <grib_file>")
        sys.exit(1)
        
    grib_file = sys.argv[1]
    if not Path(grib_file).exists():
        print(f"Error: File {grib_file} does not exist")
        sys.exit(1)
        
    inspect_grib(grib_file) 