#!/usr/bin/env python
"""
Description:
    Moves pairs of planet .tif files from a GCloud bucket into 
    GEarthEngine including relevant metadata.

Usage:
    ./gcloud_to_gee.py bucket_prefix

Arguments:
    - bucket_name: name of GCloud bucket
    - dest_collection: ImageCollection being created
    - xml_directory: filepath to dir with .xml & .json files
    
Example usages: 
    Example 1: Run for St Andrews 
    ./gcloud_to_gee.py \
       planet-st_andrews-8b

Dependencies: 
     https://github.com/7yl4r/filepanther
     https://developers.google.com/earth-engine/guides/command_line 
       ee.Authenticate()
       ee.Initialize(project='imars-simm')
============================================================
Metadata is pulled from:
* the filepath
* the `.xml` file that corresponds to each pair of `.tif`s.
* the `.json` files?
The `.xml` (and `.json`?) files must be on the local machine and 
have a filename matching up with the `.tif` file in the GCloud bucket.

example GCloud `.tif` filenames:
	20201020_162847_94_2416_3B_AnalyticMS_SR_8b_harmonized_clip.tif
    20201020_162847_94_2416_3B_udm2_clip.tif
corresponding `.xml` file:
    20201020_162847_94_2416_3B_AnalyticMS_8b_metadata_clip.xml
corresponding `.json` files:
    20201020_162847_94_2416.json
    20201020_162847_94_2416_metadata.json

See [here](https://github.com/USF-IMARS/planet-processing/tree/main?tab=readme-ov-file#image-details)
for details about the expected files.
============================================================
Modified from: https://github.com/USF-IMARS/wv-land-cover/blob/master/gee-uploads/gbucket_to_gee_w_metadata_rookery_rrs.sh
============================================================
"""
echo_if_test=""  # set this to "echo " to test the script, else set to ""

import subprocess
import os
import sys

# Variables
echo_if_test = "" # set this to "echo " to test the script, else set to ""

# Ensure correct number of arguments are provided
if len(sys.argv) != 4:
    print(
        "Wrong Arguments. Usage: "
        "python gcloud_to_gee.py \\\n"
        "  <bucket> \\\n"
        "  <dest_collection> \\\n"
        "  <xml_directory>"
    )
    sys.exit(1)

bucket = sys.argv[1]
dest_collection = sys.argv[2]
xml_directory = sys.argv[3]
#asset_directory = sys.argv[3]
country = "country_name"  # Replace with actual country
generator = "generator_name"  # Replace with actual generator
classifier = "classifier_name"  # Replace with actual classifier


print(f"Checking if the collection '{dest_collection}' exists...")
# Construct the command to check or create the collection
command = (
    f"{echo_if_test} "
    f"earthengine create collection "
    f"{dest_collection}"
)

try:
    # Execute the command
    result = subprocess.getoutput(command)

    if not result:  
        print("Collection created.")
    else:
        print(f"Command result: {result}")

except subprocess.CalledProcessError as e:
    print(f"Error executing the command: {e}")


filepanther_cmd = "/path/to/filepanther"  # Replace with the actual filepanther command path
xml_reader_cmd = "/path/to/xml_reader"  # Replace with actual XML reader command

# Get the list of geotiffs in the bucket
geotiffs = subprocess.getoutput(
    f"gsutil ls gs://{bucket}/*.tif"
).splitlines()

for geotiff in geotiffs:
    filename = os.path.basename(geotiff)
    asset_id = os.path.splitext(filename)[0]

    print(f"\n*** Transferring file {asset_id} ***")
    print("*** Parsing metadata...")
    filename = filename.split("_3B_")[0]

    # Run filepanther command to parse the file and generate metadata.pickle
    parse_command = [
        'python3 -m filepanther', '-q', 'parse', filename,
        '--pattern', 
        '%Y%m%d_%H%M%S_{satellite}_{pass_id}'
        '--pickle_fpath', 'metadata.pickle'
    ]
    subprocess.run(parse_command, check=True)

    print("*** Estimating xml filename...")
    # Run filepanther command to format the xml filename pattern and convert it to uppercase
    format_command = [
        'python3 -m filepanther', '-q', 'format',
        '--pattern', 
        '%Y%m%d_%H%M%S_{satellite}_{pass_id}_3B_AnalyticMS_8b_metadata_clip.xml',
        '--pickle_file', 'metadata.pickle'
    ]
    xml_fileglob = subprocess.getoutput(
        " ".join(format_command) + " | tr '[:lower:]' '[:upper:]'"
    )

    print(f"xml fname is like: {xml_fileglob}")

    print("*** Searching for xml file...")
    # Search for the XML file
    xml_fpath = subprocess.getoutput(
        f"find {xml_directory} -name {xml_fileglob}"
    )

    if not xml_fpath:
        print("xml file not found!")
        # Log the missing XML file
        with open('missing_xml_files.log', 'a') as log_file:
            log_file.write(f"missing_xml_file, {filename}, {find_command}\n")
        sys.exit(1)
    else:
        print(f"Found file: {xml_fpath}")

    print("*** Extracting properties from .xml...")
    # Extract variables from the XML file
    xml_vars = subprocess.getoutput(
        f"python3 ./wv_classify/read_wv_xml.py {xml_fpath}")
    print(xml_vars)

    print("*** Formatting timestamp for GEE...")
    # Format the timestamp
    datetime_command = [
        'python3 -m filepanther', '-q', 'format',
        '--pattern', '%Y-%m-%dT%H:%M:%S',
        '--pickle_file', 'metadata.pickle'
    ]
    datetime = subprocess.getoutput(" ".join(datetime_command))
    print(datetime)

    print("*** Transferring image and metadata...")
    # Upload to Google Earth Engine
    earthengine_command = [
        echo_if_test,
        "earthengine", "upload", "image", geotiff,
        "-f", f"--asset_id={asset_directory}/{asset_id}",
        "--nodata_value=0",
        "--crs=EPSG:4326",
        f"-ts={datetime}"
    ] + xml_vars.split() +  # TODO: add .json vars?
    [
        f"-p country={country}",
        f"-p generator={generator}",
        f"-p classifier={classifier}"
    ]

    subprocess.run(earthengine_command, check=True)
    print("done!")
