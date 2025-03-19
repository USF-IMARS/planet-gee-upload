import os
import re
import subprocess

def py_rx_2_find_rx(regex):
    # convert python regex object to regex string for unix `find`
    # Original Python regex
    pattern = re.compile(r'^(?P<granule>.+)_3B_AnalyticMS_SR_8b\.tif$')

    # Get the raw pattern string
    raw_pattern = pattern.pattern  # "^(?P<granule>.+)_3B_AnalyticMS_SR_8b\.tif$"

    # Replace the named group syntax with a standard group
    regex_no_named = raw_pattern.replace("(?P<granule>", "(")
    # Now regex_no_named is "^(.+)_3B_AnalyticMS_SR_8b\.tif$"

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
        
    commands = []
    # handle each 1 in the row
    if row['8b'] == 1 and row['udm2'] == 1 and row['meta.json'] == 1 and row['xml'] == 1:
        print('# CSDA unharmonized unclipped')
        commands.append(
            f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
            f"-type f "
            f"-regex '{py_rx_2_find_rx(glob_map['8b'])}') "
            f"gs://planet-{roi}-8b-unharmonized "
        )
        commands.append(
            f"{ECHO} gcloud storage cp $(find {data_dir}  -regextype posix-extended "
            f"-type f "
            f"-regex '{py_rx_2_find_rx(glob_map['udm2'])}') "
            f"gs://planet-{roi}-masks "
        )
        commands.append(
            f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
            f"-type f "
            f"-regex '{py_rx_2_find_rx(glob_map['meta.json'])}') "
            f"gs://planet-{roi}-metadata "
        )
        commands.append(
            f"{ECHO} gcloud storage cp $(find {data_dir} -regextype posix-extended "
            f"-type f "
            f"-regex '{py_rx_2_find_rx(glob_map['xml'])}') "
            f"gs://planet-{roi}-metadata "
        )

        
    else:
        print('{row["granule_id"]} missing too many files.')
        
    for command in commands:
        # Run the command
        print(command)
        try:
            result = subprocess.run(command, shell=True)
            if result.returncode == 0:
                return 1
            else:
                return 0
        except Exception as e:
            print(f"Exception occurred while running command: {e}")
            return 0
