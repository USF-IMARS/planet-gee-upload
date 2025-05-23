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

```bash
# === variables
# NOTE: must create ROI project and buckets first! (see above)
#       Expected buckets : planet-${ROI}-8b, planet-${ROI}-masks, planet-${ROI}-8b-unharmonized


# !!! NOTE: for st_andrews cannot use ${ROI} because `_` vs `-`
ROI=tti
LOGS_DIR=~/repos/planet-processing/logs
SCRIPTS_DIR=~/repos/planet-processing/scripts
DATA_DIR=~/Downloads/${ROI}

# ==============================================================
# === unzip all the years
# ==============================================================
cd ${DATA_DIR}
for file in *_psscene_analytic_8b_sr_udm2.zip; do
  unzip -o "$file" | \
    tee -a ${LOGS_DIR}/${ROI}_unzip.log
done
# ==============================================================
# ==============================================================
# === gcloud uploads
# ==============================================================
# === Ensure cloud project is correct before uploading:
# check
gcloud config get-value project

# switch gcloud project as needed:
gcloud config set project imars-simm-${ROI}

# do the uploads
python ${SCRIPTS_DIR}/uploadGranules.py ${ROI} ${DATA_DIR}
#   If you see a lot of "missing too many files", this means
#   updates will be needed to support those image packagings.

# ==============================================================
# === gee transfers
# ==============================================================
cd ${SCRIPTS_DIR}

# harmonized
./gcloud_to_gee.sh planet-${ROI}-8b projects/imars-simm-${ROI}/assets/planet_${ROI} planet-${ROI}-metadata

# masks
./gcloud_to_gee.sh planet-${ROI}-masks projects/imars-simm-${ROI}/assets/planet_${ROI}_masks planet-${ROI}-metadata

# unharmonized
./gcloud_to_gee.sh planet-${ROI}-8b-unharmonized projects/imars-simm-${ROI}/assets/planet_${ROI}_unharmonized planet-${ROI}-metadata

```

#### Gcloud upload logs
* granule tracking [here](https://docs.google.com/spreadsheets/d/16VKUw_P8NyzpNOJX2-ZFevSHShgf7ZxWn1EaWsKGqck/edit?gid=0#gid=0)
* older order-based gsheet [here](https://docs.google.com/spreadsheets/d/1FgX-tFABzozvQL9BFV2L31StNqP6RoWcjXp4T_JCUVI/edit?usp=sharing).
