# planet-processing
This repository contains scripts for uploading the planet superdove imagery into google earth engine for the imars-simm project.
More information on the project [here](https://github.com/cperaltab/Seagrass_mapping).
With thanks to FWC & the NASA CSDA program. 

## Image Storage
Images are stored in box.com folder `Seagrass/PlanetImages` then uploaded to different Google Cloud buckets for each region and image type.

## image details
Images come in two flavors: harmonized and unharmonized.

### Harmonized
each image comes with 5 files:
* `*_3B_AnalyticMS_8b_metadata_clip.xml`
  * ps:Footprint
  * gml:centerOf
  * ps:spatialReferenceSystem
  * ps:radiometricScaleFactor for each band
* `*_3B_AnalyticMS_SR_8b_harmonized_clip.tif`
  * 8 spectral bands
* `*_3B_udm2_clip.tif`
  * 8 mask bands including cloud score & confidence
* `*.json`
  * metadata about sat images, band info, 
* `*_metadata.json`
  * metadata about sat scene

### Unharmonized
Unharmonized 8b files resemble the harmonized structure but without the `_harmonized_` part of each filename.
Mask files are identical.

### unclipped
8B and mask files that have not been clipped match the harmonized structure but without the `_clip_` part of each filename.
 
## GCloud
Each region has three gcloud storage buckets:
* `planet-{region name}-8b` : 8 band spectral images
* `planet-{region name}-masks` : masks for each corresponding spectral image
* `planet-{region name}-metadata` : xml & json files corresponding to images

The buckets are configured with the settings:
* single region (us central (iowa))
* storage class coldline

### uploading to GCloud
#### automation
NOTE: Images are now organized under regional gcloud projects `imars-simm-$ROI`.
      The project may need to be set in the earthengine and gcloud CLIs.
      We are still figuring out the details.

```bash
ROI=st_andrews
LOGS_DIR=~/repos/planet-processing/logs
SCRIPTS_DIR=~/repos/planet-processing/scripts
DATA_DIR=~/Downloads/${ROI}

# unzip all the years
cd ${DATA_DIR}
for file in *_psscene_analytic_8b_sr_udm2.zip; do
  unzip -o "$file" | \
    tee -a ${LOGS_DIR}/${ROI}_unzip.log
done

# === gcloud uploads
# NOTE: must create the buckets first!

# NOTE: This only works for
#         * latest CSDA unharmonized images
#         * planet harmonized+clipped downloads
#       If you see a lot of "missing too many files", this means
#       updates will be needed to support those image packagings.
python ${SCRIPTS_DIR}/uploadGranules.py ${ROI} ${DATA_DIR}

# === gee transfers
cd ${SCRIPTS_DIR}

# harmonized
./gcloud_to_gee.sh planet-${ROI}-8b projects/imars-simm-${ROI}/assets/planet_${ROI} planet-${ROI}-metadata

# unharmonized
./gcloud_to_gee.sh planet-${ROI}-8b-unharmonized projects/imars-simm-${ROI}/assets/planet_${ROI}_unharmonized planet-${ROI}-metadata

# masks
./gcloud_to_gee.sh planet-${ROI}-masks projects/imars-simm-${ROI}/assets/planet_${ROI}_masks planet-${ROI}-metadata

```

#### GCloud upload example
```
tylar@tylar-laptop:~/Downloads/stAndrew$ unzip StAndrew.zip 
Archive:  StAndrew.zip
  inflating: StAndrew/StAndrew_2021_psscene_analytic_8b_sr_udm2.zip  
  inflating: StAndrew/StAndrew_2020_psscene_analytic_8b_sr_udm2.zip  
[...]

tylar@tylar-laptop:~/Downloads/stAndrew/StAndrew$ unzip StAndrew_2020_psscene_analytic_8b_sr_udm2.zip 
Archive:  StAndrew_2020_psscene_analytic_8b_sr_udm2.zip
 extracting: PSScene/20201020_162847_94_2416_3B_udm2_clip.tif  
 extracting: PSScene/20200807_153714_73_2277_3B_udm2_clip.tif  
[...]


tylar@tylar-laptop:~/Downloads/stAndrew/StAndrew/PSScene$ gcloud storage cp *harmonized_clip.tif gs://planet-st_andrews-8b
WARNING: Destination has a default storage class other than "STANDARD", hence parallel composite upload will not be performed. If you would like to disable this check, run: gcloud config set storage/parallel_composite_upload_compatibility_check=False
Copying file://20200501_153640_81_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif to gs://planet-st_andrews-8b/20200501_153640_81_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif
Copying file://20200501_153643_04_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif to gs://planet-st_andrews-8b/20200501_153643_04_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif
[...]
  Completed files 13/13 | 4.2GiB/4.2GiB | 1.3MiB/s                                                                        
Average throughput: 1.4MiB/s

tylar@tylar-laptop:~/Downloads/stAndrew/StAndrew/PSScene$ gcloud storage cp *udm2_clip.tif gs://planet-st_andrews-masks
Copying file://20200501_153640_81_2257_3B_udm2_clip.tif to gs://planet-st_andrews-masks/20200501_153640_81_2257_3B_udm2_clip.tif
Copying file://20200501_153643_04_2257_3B_udm2_clip.tif to gs://planet-st_andrews-masks/20200501_153643_04_2257_3B_udm2_clip.tif
[...]
  Completed files 13/13 | 75.6MiB/75.6MiB | 5.3MiB/s                                                                      
Average throughput: 2.5MiB/s

```

#### Gcloud upload log
See gsheet [here](https://docs.google.com/spreadsheets/d/1FgX-tFABzozvQL9BFV2L31StNqP6RoWcjXp4T_JCUVI/edit?usp=sharing).
