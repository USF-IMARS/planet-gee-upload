#!/usr/bin/env python3
"""
Prints out a table of which files are available per granule.

Usage:
  python printGranuleTable.py my_data_dir

Example output:
granule,8b,8b_clip,8b_harm,8b_clip_harm,udm2,udm2_clip,meta.json,xml,others
20241031_161446_28_24d7,1,0,0,0,1,0,1,1,
20241030_482680_23_59v8,0,1,0,0,0,0,0,1,20241030_482680_23_59v8_8b_mmetadata.json|20241030_482680_23_59v8_udm2.tif
"""

import os
import sys
import re
import pandas as pd

from upload_row import upload_row

def main():
    if len(sys.argv) != 3:
        print("Usage: python printGranuleTable.py my_roi my_data_dir")
        sys.exit(1)

    roi = sys.argv[1]
    data_dir = sys.argv[2]
    if not data_dir or not roi:
        print("Error: any([DATA_DIR, ROI]) environment variables are not set.")
        return 0

    # Define expected file types and the corresponding regex patterns.
    # Each pattern captures the granule ID as the part before the fixed suffix.
    expected_patterns = {
        '8b':           re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b\.tif$'),
        '8b_clip':      re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b_clip\.tif$'),
        '8b_harm':      re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b_harmonized\.tif$'),
        '8b_clip_harm': re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b_harmonized_clip\.tif$'),
        'udm2':         re.compile(r'^(?P<granule>.+)_3B_udm2\.tif$'),
        'udm2_clip':    re.compile(r'^(?P<granule>.+)_3B_udm2_clip\.tif$'),
        'meta.json':    re.compile(r'^(?P<granule>.+)_metadata\.json$'),
        'xml':          re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_8b_metadata\.xml$'),
        'xml_clip':     re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_8b_metadata_clip\.xml$'),
        'json':         re.compile(r'^(?P<granule>.+)\.json'),
    }
    
    # Dictionary to store granule info.
    # Each granule id maps to a dict with keys for each expected file type (defaulting to 0)
    # and an 'others' key that will be a list of extra file names.
    granule_data = {}

    # Walk through all files in the given directory (recursively)
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            full_path = os.path.join(root, file)
            matched = False
            # Check if file matches one of the expected patterns.
            for filetype, pattern in expected_patterns.items():
                m = pattern.match(file)
                if m:
                    granule = m.group('granule')
                    if granule not in granule_data:
                        # Initialize all expected types to 0 and others to an empty list.
                        granule_data[granule] = {ft: 0 for ft in expected_patterns.keys()}
                        granule_data[granule]['others'] = []
                    granule_data[granule][filetype] = 1
                    matched = True
                    break
            if not matched:
                # For files that don't match any expected pattern, try to extract a granule id heuristically.
                # Here we assume the granule id is given by the first four underscore-separated parts.
                parts = file.split('_')
                if len(parts) >= 4:
                    granule = '_'.join(parts[:4])
                    if granule not in granule_data:
                        granule_data[granule] = {ft: 0 for ft in expected_patterns.keys()}
                        granule_data[granule]['others'] = []
                    granule_data[granule]['others'].append(file)
                # Files that do not even have 4 parts are ignored.

    # Build rows for our table.
    rows = []
    # Define the column order.
    columns = ["granule", "8b", "8b_clip", "8b_harm", "8b_clip_harm", "udm2", "udm2_clip", "meta.json", "xml", "xml_clip", "json", "others", "uploaded"]
    
    for granule in sorted(granule_data.keys()):
        entry = granule_data[granule]
        # Join any 'others' files using '|' as separator.
        others_str = "|".join(entry['others']) if entry['others'] else ""
        row = {
            "granule": granule,
            "8b": entry['8b'],
            "8b_clip": entry['8b_clip'],
            "8b_harm": entry['8b_harm'],
            "8b_clip_harm": entry['8b_clip_harm'],
            "udm2": entry['udm2'],
            "udm2_clip": entry['udm2_clip'],
            "meta.json": entry['meta.json'],
            "xml": entry['xml'],
            "xml_clip": entry['xml_clip'],
            "json": entry['json'],
            "others": others_str,
            "uploaded": 0
        }
        row["uploaded"] = upload_row(row, expected_patterns, roi, data_dir) #, test=True)
        
        rows.append(row)
    
    df = pd.DataFrame(rows, columns=columns)
    # Print CSV formatted table (without index)
    print(df.to_csv(index=False))

if __name__ == '__main__':
    main()
