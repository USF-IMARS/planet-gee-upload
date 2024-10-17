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
```
tylar@tylar-laptop:~/Downloads/stAndrew$ ls
StAndrew.zip

tylar@tylar-laptop:~/Downloads/stAndrew$ unzip StAndrew.zip 
Archive:  StAndrew.zip
  inflating: StAndrew/StAndrew_2021_psscene_analytic_8b_sr_udm2.zip  
  inflating: StAndrew/StAndrew_2020_psscene_analytic_8b_sr_udm2.zip  
  inflating: StAndrew/StAndrew_2022_psscene_analytic_8b_sr_udm2.zip  
  inflating: StAndrew/StAndrew_2023_psscene_analytic_8b_sr_udm2.zip  
  inflating: StAndrew/StAndrew_2024_psscene_analytic_8b_sr_udm2.zip  

tylar@tylar-laptop:~/Downloads/stAndrew$ cd StAndrew

tylar@tylar-laptop:~/Downloads/stAndrew/StAndrew$ unzip StAndrew_2020_psscene_analytic_8b_sr_udm2.zip 
Archive:  StAndrew_2020_psscene_analytic_8b_sr_udm2.zip
 extracting: PSScene/20201020_162847_94_2416_3B_udm2_clip.tif  
 extracting: PSScene/20200807_153714_73_2277_3B_udm2_clip.tif  
 extracting: PSScene/20200926_154240_98_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif  
 extracting: PSScene/20200502_153600_39_2259_3B_udm2_clip.tif  
[...]

tylar@tylar-laptop:~/Downloads/stAndrew$ cd PSScene

tylar@tylar-laptop:~/Downloads/stAndrew/StAndrew/PSScene$ gcloud storage cp *harmonized_clip.tif gs://planet-st_andrews-8b
WARNING: Destination has a default storage class other than "STANDARD", hence parallel composite upload will not be performed. If you would like to disable this check, run: gcloud config set storage/parallel_composite_upload_compatibility_check=False
Copying file://20200501_153640_81_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif to gs://planet-st_andrews-8b/20200501_153640_81_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif
Copying file://20200501_153643_04_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif to gs://planet-st_andrews-8b/20200501_153643_04_2257_3B_AnalyticMS_SR_8b_harmonized_clip.tif
[...]
```
