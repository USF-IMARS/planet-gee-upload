# planet-processing

## image details
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
   
## GCloud
Each region has two gcloud storage buckets:
* `planet-{region name}-8b` : 8 band spectral images
* `planet-{region name}-masks` : masks for each corresponding spectral image

### uploading to GCloud
#### automation
```bash
ROI=st_andrews
LOGS_DIR=~/repos/planet-processing/logs
SCRIPTS_DIR=~/repos/planet-processing/scripts
DATA_DIR=~/Downloads/${ROI}/

# unzip all the years
cd ${DATA_DIR}
unzip *_psscene_analytic_8b_sr_udm2.zip
DATA_DIR=$(pwd)/PSScene/

# === gcloud uploads
# NOTE: must create the buckets first!
gcloud storage cp ${DATA_DIR}*harmonized_clip.tif gs://planet-${ROI}-8b | \
    tee ${LOGS_DIR}/${ROI}_8b_gcloud_upload.log

gcloud storage cp ${DATA_DIR}*udm2_clip.tif gs://planet-${ROI}-masks | \
    tee ${LOGS_DIR}/${ROI}_masks_gcloud_upload.log

# === gee transfers
cd ${SCRIPTS_DIR}

./gcloud_to_gee.sh planet-${ROI}-8b projects/imars-simm/assets/planet_${ROI} ${DATA_DIR} | \
    tee ${LOGS_DIR}/${ROI}_8b_gcloud_to_gee.log

./gcloud_to_gee.sh planet-${ROI}-masks projects/imars-simm/assets/planet_${ROI}_masks ${DATA_DIR} | \
    tee ${LOGS_DIR}/${ROI}_masks_gcloud_to_gee.log
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
