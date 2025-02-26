#!/bin/bash
# prints count of each image type in cwd
# (should be run from PSScene dir)

# Count specific subsets
harm_clip=$(  ls -1 *_3B_AnalyticMS_SR_8b_harmonized_clip.tif 2>/dev/null | wc -l)
clip_mask=$(  ls -1 *_3B_udm2_clip.tif                        2>/dev/null | wc -l)
unharm_clip=$(ls -1 *AnalyticMS_SR_8b_clip.tif                2>/dev/null | wc -l)
harm_noclip=$(ls -1 *_3B_AnalyticMS_SR_8b_harmonized.tif      2>/dev/null | wc -l)
noclip_mask=$(ls -1 *_3B_udm2.tif                             2>/dev/null | wc -l)

# Display counts for each subset
echo "Harmonized   noclip 8b    : $harm_noclip"
echo "Harmonized   clip   8b    : $harm_clip"
echo "UnHarmonized clip   8b    : $unharm_clip"
echo "             Clip   mask  : $clip_mask"
echo "             noclip mask  : $noclip_mask"

echo ==============================================
# Count total tif files (suppress errors if none match)
total=$(ls -1 *tif 2>/dev/null | wc -l)
echo "Total tif Files         : $total"

# Calculate the accounted for tif files and the remainder
accounted=$((harm_clip + clip_mask + unharm_clip + harm_noclip + noclip_mask))
unaccounted=$((total - accounted))

echo "Unaccounted tif Files   : $unaccounted"
