import os
import re
import subprocess

def py_rx_2_find_rx(pattern, granule_id):
    # convert python regex object to regex string for unix `find`
    # Original Python regex

    # Get the raw pattern string
    raw_pattern = pattern.pattern  # "^(?P<granule>.+)_3B_AnalyticMS_SR_8b\.tif$"

    # Replace the named group syntax with a standard group
    regex_no_named = raw_pattern.replace("(?P<granule>.+)", granule_id)
    # Now regex_no_named is "^{granule_id}_3B_AnalyticMS_SR_8b\.tif$"

    # Since find's regex matches the entire path, remove the caret and prepend '.*\/'
    find_regex = ".*\/" + regex_no_named.lstrip("^")
    # find_regex becomes ".*\/(.+)_3B_AnalyticMS_SR_8b\.tif$"

    return find_regex
    
def upload_row(row, glob_map, roi, data_dir, test=False):
    """
    Given a DataFrame row, run the gcloud upload command using the ROI specified in the row.

    test=True does not upload the file
    
    Example usage:
        # ROI=tti
        # DATA_DIR=~/Downloads/tti
        upload_row(
          row={
            'granule_id': ...,
            'udm2': 1,
            '8b': 1,
            'meta.json': 1,
            'xml': 1,
            'others': ''
          },
          glob_map={
            '8b':           re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b\.tif$'),
            'udm2':         re.compile(r'^(?P<granule>.+)_3B_udm2\.tif$'),
            'meta.json':    re.compile(r'^(?P<granule>.+)_metadata\.json$'),
            'xml':          re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_8b_metadata\.xml$'),
          }
        )
    
    Returns:
        1 if the upload command is successful (exit code 0), 0 otherwise.
    """
    if test != False:
        ECHO = 'echo'
    else:
        ECHO = ''

    # commands for each filetype
    cmd_8b = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['8b'], row['granule'])}') "
         f"gs://planet-{roi}-8b-unharmonized "
    )
    cmd_mask = (
         f"{ECHO} gcloud storage cp $(find {data_dir}  -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['udm2'], row['granule'])}') "
         f"gs://planet-{roi}-masks "
    )
    cmd_meta_json = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['meta.json'], row['granule'])}') "
         f"gs://planet-{roi}-metadata "        
    )
    cmd_json = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['json'], row['granule'])}') "
         f"gs://planet-{roi}-metadata "
    )        
    cmd_xml = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['xml'], row['granule'])}') "
         f"gs://planet-{roi}-metadata "
    )
    cmd_8b_clip_harm = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['8b_clip_harm'], row['granule'])}') "
         f"gs://planet-{roi}-8b "
    )
    cmd_mask_clip = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['udm2_clip'], row['granule'])}') "
         f"gs://planet-{roi}-masks "
    )
    cmd_xml_clip = (
         f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
         f"-type f "
         f"-regex '{py_rx_2_find_rx(glob_map['xml_clip'], row['granule'])}') "
         f"gs://planet-{roi}-metadata "
    )
    commands = []
    # === handle each row according to what files are there
    if all(row[key] == 1 for key in['8b', 'udm2', 'meta.json', 'xml']):
        # unharmonized file like from CSDA 2025-03
        print('# CSDA unharmonized unclipped')
        commands.append(cmd_8b)
        commands.append(cmd_mask)
        commands.append(cmd_meta_json)
        commands.append(cmd_xml)
    elif all(row[key] == 1 for key in['8b_clip_harm', 'udm2_clip', 'json', 'meta.json', 'xml_clip']):
        # unharmonized & clipped like from planet download 2025
        print("# planet harmonized+clipped")
        commands.append(cmd_8b_clip_harm)
        commands.append(cmd_mask_clip)
        commands.append(cmd_xml_clip)
        commands.append(cmd_json)
        commands.append(cmd_meta_json)
        
    else:
        print(f'{row["granule"]} missing too many files.')
        return 0
        
    for command in commands:
        # Run the command
        print(command)
        try:
            result = subprocess.run(command, shell=True)
            if result.returncode != 0:
                print('error occurred while uploading')
                return 0
        except Exception as e:
            print(f"Exception occurred while running command: {e}")
            return 0
    return 1
