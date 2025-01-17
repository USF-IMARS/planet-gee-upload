#!/bin/bash

# Description:
#     Moves pairs of planet .tif files from a GCloud bucket into 
#     GEarthEngine including relevant metadata.

# Usage:
#     ./gcloud_to_gee.sh bucket_prefix dest_collection xml_directory

# Arguments:
#     - bucket_prefix: name of GCloud bucket
#     - dest_collection: ImageCollection being created
#     - xml_directory: filepath to dir with .xml & .json files

# Example usages:
#     Example 1: Run for St Andrews 8b 
#       ./gcloud_to_gee.sh planet-st_andrews-8b projects/imars-simm/assets/planet_st_andrews ~/Downloads/stAndrew/StAndrew/PSScene/
#     Example 2: Run for St Andrews masks
#       ./gcloud_to_gee.sh planet-st_andrews-masks projects/imars-simm/assets/planet_st_andrews_masks ~/Downloads/stAndrew/StAndrew/PSScene/ | tee ../logs/StAndrew_2020_masks_gcloud_to_gee.log 
# Dependencies:
#      https://github.com/7yl4r/filepanther
#      https://developers.google.com/earth-engine/guides/command_line
#        ee.Authenticate()
#        ee.Initialize(project='imars-simm')

# Ensure correct number of arguments are provided

country="USA"  # Replace with actual country
generator="IMaRS"  # Replace with actual generator
classifier="NA"  # Replace with actual classifier

echo_if_test=""  # set this to "echo " to test the script, else set to ""

if [ "$#" -ne 3 ]; then
    echo "Wrong Arguments. Usage: "
    echo "./gcloud_to_gee.sh <bucket> <dest_collection> <xml_directory>"
    exit 1
fi

bucket="$1"
dest_collection="$2"
xml_directory="$3"

echo "Checking if the collection '$dest_collection' exists..."
# Check if the collection exists and create it if not
command="${echo_if_test} earthengine create collection $dest_collection"
result=$($command)

if [ -z "$result" ]; then  # If the result is empty, collection was created
    echo "Collection created."
else
    echo "Command result: $result"
fi

xml_reader_cmd="python3 ../util/read_planet_xml.py "
json_reader_cmd="python3 ../util/read_planet_json.py "
filepanther_cmd="python3 -m filepanther "

# Get the list of geotiffs in the bucket
geotiffs=$(gsutil ls gs://$bucket/*.tif)

for geotiff in $geotiffs; do
    filename=$(basename "$geotiff")
    asset_id="${filename%.*}"

    echo "*** Transferring file $asset_id ***"
    echo "*** Parsing metadata..."
    filename_no_ext=$(echo "$filename" | sed 's/_3B_.*//')
    # Run filepanther command to parse the file and generate metadata.pickle
    $filepanther_cmd -q parse "$filename_no_ext" \
        --pattern "%Y%m%d_%H%M%S_{satellite}_{pass_id}" \
        --pickle_fpath metadata.pickle

    echo "*** Estimating xml filename..."
    # Run filepanther command to format the xml filename pattern and convert it to uppercase
    xml_fileglob=$($filepanther_cmd -q format \
        --pattern "%Y%m%d_%H%M%S_{satellite}_{pass_id}_3B_AnalyticMS_8b_metadata_clip.xml" \
        --pickle_file metadata.pickle)

    echo "xml fname is like: ${xml_fileglob}"

    echo "*** Searching for xml file..."
    # Search for the XML file
    xml_fpath=$(find "$xml_directory" -name "$xml_fileglob")

    if [ -z "$xml_fpath" ]; then
        echo "xml file not found!"
        # Log the missing XML file
        echo "missing_xml_file, $filename, find $xml_directory -name $xml_fileglob" >> missing_xml_files.log
        #exit 1
    else
        echo "Found file: $xml_fpath"

        echo "*** Extracting properties from .xml..."
	# Extract variables from the XML file
	xml_vars=$($xml_reader_cmd "$xml_fpath")
	echo "$xml_vars"

	echo "*** Estimating json filename..."
	# Run filepanther command to format the filename pattern and convert it to uppercase                              
	json_fileglob=$($filepanther_cmd -q format \
	    --pattern "%Y%m%d_%H%M%S_{satellite}_{pass_id}_metadata.json" \
	    --pickle_file metadata.pickle)

	echo "json fname is like: ${json_fileglob}"

	echo "*** Searching for json file..."
	# Search for the json file  
	json_fpath=$(find "$xml_directory" -name "$json_fileglob")

	if [ -z "$json_fpath" ]; then
            echo "json file not found!"
            # Log the missing json file   
            echo "missing_json_file, $filename, find $xml_directory -name $json_fileglob" >> missing_json_files.log
            #exit 1
	else
            echo "Found file: $json_fpath"

	    echo "*** Extracting properties from .json..."
	    json_vars=$($json_reader_cmd "$json_fpath")
	    echo "$json_vars"
    
	    echo "*** Formatting timestamp for GEE..."
	    # Format the timestamp
	    datetime=$($filepanther_cmd -q format \
		--pattern "%Y-%m-%dT%H:%M:%S" \
		--pickle_file metadata.pickle)

	    echo "$datetime"

	    echo "*** Transferring image and metadata..."
	    # Upload to Google Earth Engine
	    ${echo_if_test} earthengine --project="imars-simm" upload image "$geotiff" \
			    -f --asset_id="$dest_collection/$filename_no_ext" \
			    --nodata_value=0 \
			    -ts="$datetime" \
			    $xml_vars \
			    $json_vars \
			    -p country="$country" \
			    -p generator="$generator" \
			    -p classifier="$classifier"
	    # TODO: add json vars?
	    echo "done!"
	    echo ""
	fi
    fi
done
