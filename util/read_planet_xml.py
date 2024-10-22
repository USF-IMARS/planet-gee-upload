#!/usr/env python
from xml.etree import ElementTree
from datetime import datetime


def read_planet_xml(filename, output_format="gee_props"):
    """ read metadata values from xml file
    params
    ------
    filename : filepath
        The .xml file to read
    output_format : str
        The format to return output.
        Note that "list" output may not support all metadata.
        valid values:
            "list" - [param1Value, param2Value]
            "dict" - {param1:value, param2:value]
    """
    metadata = {}
    # Extract calibration factors & acquisition time from
    # metadata for each band
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    metaDataProperty = root.find('gml:metaDataProperty')
    # Define the namespace
    namespaces = {
        'eop': 'http://earth.esa.int/eop',
        'ps':  "http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level",
        'opt': "http://earth.esa.int/opt",
    }

    # Extract the attributes 
    # Assumes this uniquely identifies each tag.
    # If there is more than one match, only the first gets included.
    desired_attribs = [
        './/eop:acquisitionType',
        './/eop:processorVersion',
        './/ps:versionIsd',
        ['.//eop:Platform', './/eop:serialIdentifier'],
        ['.//eop:Platform', './/eop:orbitType'],
        ['.//eop:Instrument', './/eop:shortName'],
        './/eop:orbitDirection',
        './/eop:incidenceAngle',
        './/opt:illuminationAzimuthAngle',
        './/opt:illuminationElevationAngle',
        './/ps:azimuthAngle',
        './/ps:spaceCraftViewAngle',
        './/ps:acquisitionDateTime',
        './/ps:radiometricCorrectionApplied',
        './/ps:geoCorrectionLevel',
        './/ps:elevationCorrectionApplied',
        './/ps:atmosphericCorrectionApplied',
        './/opt:cloudCoverPercentage',
        './/ps:unusableDataPercentage',
        {
            'tag': './/ps:reflectanceCoefficient',
            'parent': './/ps:bandSpecificMetadata',
            'iteration_id': './/ps:bandNumber',
        },
        './/ps:radiometricScaleFactor',
    ]

    def cleanAttr(a): # trims off the .//*:
        return a.split(':')[-1]

    for attrib in desired_attribs:
        if isinstance(attrib, list):
            # handle the lists of tags as single multi-tag
            parent_element = root.find(attrib[0], namespaces)
            if parent_element is not None:
                child_element_text = parent_element.find(attrib[1], namespaces).text
            else:
                child_element_text = "None"
            
            metadata_name = f"{cleanAttr(attrib[0])}_{cleanAttr(attrib[1])}"
            metadata[metadata_name] = child_element_text
        elif isinstance(attrib, dict):
            # handle dict as a layered multi-part taken from multiple tags
            for i in root.findall(attrib['parent'], namespaces):
                iter_id = i.find(attrib['iteration_id'], namespaces).text
                val = i.find(attrib['tag'], namespaces).text
                metadata[
                    f"{cleanAttr(attrib['tag'])}_"
                    f"{cleanAttr(attrib['iteration_id'])}_"
                    f"{iter_id}"
                ] = val

        else:  # handle string as single tag
            metadata[cleanAttr(attrib)] = root.find(attrib, namespaces).text

    # metadata["IMD_NUMROWS"]    = int(imd.find('NUMROWS').text)
    # metadata["IMD_NUMCOLUMNS"] = int(imd.find('NUMCOLUMNS').text)
    # BANDNAMES = [
    #     'BAND_C', 'BAND_B', 'BAND_G', 'BAND_Y', 'BAND_R', 'BAND_RE',
    #     'BAND_N', 'BAND_N2'
    # ]
    # for band in BANDNAMES:
    #     metadata[f"ABSCALFACTOR_{band}"] = float(
    #         imd.find(band).find('ABSCALFACTOR').text
    #     )
    # # Extract Acquisition Time from metadata
    # metadata["FIRSTLINETIME"] = datetime.strptime(
    #     imd.find('IMAGE').find('FIRSTLINETIME').text,
    #     # "2017-12-22T16:48:10.923850Z"
    #     "%Y-%m-%dT%H:%M:%S.%fZ"
    # )
    # # Extract Mean Sun Elevation angle from metadata.Text(18:26))
    # # Extract Mean Off Nadir View angle from metadata
    # for param in [
    #     "MEANSUNEL", "MEANSUNAZ",
    #     "MEANSATEL", "MEANSATAZ",
    #     "MEANOFFNADIRVIEWANGLE", "CLOUDCOVER",
    #     "MEANINTRACKVIEWANGLE", "MEANCROSSTRACKVIEWANGLE", "MEANOFFNADIRVIEWANGLE"
    # ]:
    #     metadata[param] = float(imd.find("IMAGE").find(param).text)
    # for param in [
    #     "SATID", "MODE", "SCANDIRECTION",
    # ]:
    #     metadata[param] = imd.find("IMAGE").find(param).text

    # for param in [
    #     "FILENAME"
    # ]:
    #     metadata[param] = root.find("TIL").find("TILE").find(param).text
        
    # if output_format == "list":
    #     szB = [
    #         metadata["IMD_NUMROWS"],
    #         metadata["IMD_NUMCOLUMNS"],
    #         0
    #     ]
    #     kf = [
    #         metadata[f"ABSCALFACTOR_{band}"] for band in BANDNAMES
    #     ]
    #     aq_dt = metadata["FIRSTLINETIME"]
    #     aqyear = aq_dt.year
    #     aqmonth = aq_dt.month
    #     aqday = aq_dt.day
    #     aqhour = aq_dt.hour
    #     aqminute = aq_dt.minute
    #     aqsecond = aq_dt.second
    #     sunel = metadata['MEANSUNEL']
    #     satview = metadata['MEANOFFNADIRVIEWANGLE']
    #     sunaz = metadata['MEANSUNAZ']
    #     sensaz = metadata['MEANSATAZ']
    #     satel = metadata['MEANSATEL']
    #     cl_cov = metadata['CLOUDCOVER']
    #     return (
    #         szB, aqmonth, aqyear, aqhour, aqminute, aqsecond, sunaz, sunel,
    #         satel, sensaz, aqday, satview, kf, cl_cov
    #     )
    # elif output_format == "dict":
    #     return metadata
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
    print(read_planet_xml(fpath, output_format="gee_props"))
