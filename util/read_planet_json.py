#!/usr/env python                                                                                                         
from datetime import datetime
import json

def read_planet_json(filename, output_format="gee_props"):
    """ read metadata values from json file                                     
    """
    # Read the JSON file
    with open(filename, 'r') as file:
        data = json.load(file)

    # Extract the 'properties' dictionary
    metadata = data.get('properties', {})
    
    
    if output_format == "gee_props":
        res = ""
        for key in metadata:
            try:
                val = str(metadata[key]).replace(" ", "_")
            except:
                val = metadata[key]
            res += f" -p {key}={val} "
        return res
    else:
        raise ValueError(
            f"user requested unknown output_format '{output_format}'"
        )

if __name__ == "__main__":
    #import pprint                                      
    import sys
    #pp = pprint.PrettyPrinter(indent=2)                            
    fpath = sys.argv[1]
    #pp.pprint(                                   
    #    read_wv_xml(fpath, output_format="dict")                 
    #)                                                                 
    print(read_planet_json(fpath, output_format="gee_props"))

