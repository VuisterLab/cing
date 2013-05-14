#!/bin/tcsh -f

# USE: $C/scripts/molmol/molmol_hires_image.csh pdb_id
# calls molmol_image.csh and render_convert.csh
# to produce a hi-resolution gif.
# Before using adjust the one parameter useHiRes in render_convert.csh

echo "Starting molmol_hires_image.csh"
set id             = $1
set pdb_file       = $id.pdb
set tmp_dir        = .
set molgrapDir     = $C/scripts/molmol
set backcolor      = cing_turqoise
set executableMm   = $WS/molmolM/molmol
set mac_dir        = $molgrapDir


echo "Starting molmol_image.csh"
$molgrapDir/molmol_image.csh $pdb_file $tmp_dir $id $molgrapDir $backcolor $executableMm $mac_dir
if ( $status ) then
    echo "ERROR in first step"
    exit 1
endif

set pov_file       = $id.pov
set results_dir    = .
set povray_path    = povray
set convert_path   = convert
echo "Starting render_convert.csh"
$molgrapDir/render_convert.csh $pov_file $tmp_dir $id $results_dir $povray_path $convert_path

echo "Finished."
