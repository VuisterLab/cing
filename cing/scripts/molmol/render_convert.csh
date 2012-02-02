#!/bin/tcsh -f
# USE: render_convert.csh pov_ray_file tmp_dir pdb_id
# render a pov ray file and convert it to a number of sizes and formats
# quite large

set pov_file       = $1
set tmp_dir        = $2
set id             = $3
set results_dir    = $4
set povray_path    = $5
set convert_path   = $6
set log            = $tmp_dir/$id"_render_convert".log
set tga_tmp        = $tmp_dir/$id.tga
set testing        = 0
set useHiRes       = 0 # DEFAULT 0

# No changes below
###############################################
cd $results_dir
# check if we got the right amount of parameters
if ( $# != 6 ) then
   echo "ERROR: Not the right number of arguments: got $# in stead of 6"
   goto usage
endif

if ( ! -e $tmp_dir ) then
   echo "ERROR: temporary dir doesn't exist: $tmp_dir"
   goto error
endif

if ( ! -e $pov_file ) then
   echo "ERROR: pov file doesn't exist: $pov_file of $id"
   goto error
endif

# Clean up
if ( -e $tga_tmp ) then
   \rm $tga_tmp
endif

if ( -e $log ) then
   \rm $log
endif

start:
# -D turns rendering on screen off
# +A0.3 turns on anti aliasing with threshold 0.3 on.

set widthCount = 760
set heightCount = 532
if ( $useHiRes ) then
    set widthCount = 1520
    set heightCount = 1064
endif

set povray_dir = $povray_path:h
$povray_path -L$povray_dir/include +A0.3 -D +I$pov_file +O$tga_tmp +W$widthCount +H$heightCount >& $log
#$povray_dir/povray -L$povray_dir/include +A0.3 -D +I$pov_file +O$tga_tmp +W3040 +H2128 >& $log
set sts = $status
if ( $sts ) then
    echo "ERROR: exit status $sts of povray indicates error of $id"
    goto error
endif

if ( ! -e $tga_tmp ) then
    echo "ERROR: no tga image file was created by rendering of povray of $id"
    goto error
endif

$convert_path                   $tga_tmp   $id.gif  >>& $log

#convert -geometry 50%     $tga_tmp  $id"_big".gif  >>& $log
#convert -geometry 25%     $tga_tmp        $id.gif  >>& $log
#convert -geometry 50x35   $tga_tmp  $id"_pin".gif  >>& $log

if ( ! -e $id.gif ) then
    echo "ERROR: no gif image file was created by convert of $id"
    goto error
endif

if ( 1 ) then # DEFAULT: 1
    echo "DEBUG: trying to remove the temporary stuff: $tga_tmp $log"
    # Don't remove input and log file if no picture file was created.
    \rm -f $tga_tmp
    \rm -f $log
endif

exit ( 0 )

error:
    if ( -e $log ) then
        echo "ERROR: from log file of $id"
        grep -i error $log
        if ( $status ) then
            # present tail if no error was grepped.
            tail $log
        endif
    endif
    exit 1

usage:
    echo "ERROR: USE: render_convert.csh pov_file tmp_dir pdb_id results_dir "
    exit ( 2 )
