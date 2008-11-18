#!/bin/csh -f

# USE: molmol_image.csh pdb_file tmp_dir pdb_id
# make a pov ray file in a temporary directory as these files can become
# quite large
echo "DEBUG: 0"
set mac_file       = molmol_images.mac
set log_file       = molmol_images.log
set pdb_file       = $1
set tmp_dir        = $2
set id             = $3
set molgrapDir     = $4
set backcolor      = $5
set executableMm   = $6
set mac_dir        = $7
set try            = 1
set mul            = 1
#setenv MOLMOLHOME $6 needs to be set to a directory and done outside of Cing, e.g. in .cshrc

set mac_file       = $tmp_dir"/"$id"_"$mac_file
set log_file       = $tmp_dir"/"$id"_"$log_file

echo "DEBUG: 1"

# check if we got the right amount of parameters
if ( $# != 7 ) then
   echo "ERROR: Not the right number of arguments: got $# in stead of 7"
   goto usage
endif

if ( ! -e $tmp_dir ) then
   echo "ERROR: temporary dir doesn't exist"
   goto error
endif

if ( ! -e $pdb_file ) then
   echo "ERROR: pdb file doesn't exist"
   goto error
endif

# Clean up
if ( -e $mac_file ) then
   \rm $mac_file
endif

if ( -e $log_file ) then
   \rm $log_file
endif

if ( 1 ) then
    echo "molmol_image.csh found pdb_file   :" $pdb_file >  $log_file
    echo "molmol_image.csh found tmp_dir    :" $tmp_dir  >> $log_file
    echo "molmol_image.csh found id         :" $id       >> $log_file
endif
echo "DEBUG: 2"

start:
# Make the MOLMOL macro


# Estimate size for precision:
set list = (`\ls -l $pdb_file`)
set exp = (`head -100 $pdb_file|egrep "^EXPDTA *NMR"`)
if ( $#exp == 0 ) then
    # Assume X-ray and theoretical models have only heavy atoms
    set mul = 2
  endif
else
  echo "WARNING: no EXPDTA record found in pdb file"
  echo "WARNING: assuming model is from NMR because safest in context"
endif
echo "DEBUG: 3"

# 1 kB per 1 amino acid residue for NMR; approximately
# Anything below   100 aminoacids will be at resolution 3
# Anything below  1000 at 2
# Anything below 20000 at 1
# Anything 20000 and above at 0 (only 1 entry 1htq; next largest one in bytes is 1jj2)
# For 1jj2 rendering takes: Total Time:    0 hours  4 minutes  30.0 seconds (270 seconds)
# 8 Mb -> estimated 8000 residues at resolution 1.
set precision = 0

@ size_cor = $list[5] * $mul

if ( $size_cor <20000000 ) then
    set precision = 1
endif
if ( $size_cor < 1000000 ) then
    set precision = 2
endif
if ( $size_cor <  100000 ) then
    set precision = 3
endif

#echo "Assuming multiplication factor:   $mul"       >> $log_file
echo "Precision for pov file:           $precision" >> $log_file
echo "DEBUG: 4"

# Notes for the macro file:
# -1- No empty lines allowed.
echo "InitAll yes" > $mac_file
echo "PathNames '' '' '' '' '/Users/jd/progs/molmolM/setup/PdbAtoms' '/Users/jd/progs/molmolM/setup/PropDef' '/Users/jd/progs/molmolM/setup/pdb.lib' '' ''" >> $mac_file
if ( $backcolor == "bmrb_yellow" ) then
    echo "BackColor 1 1 0.79688" >> $mac_file
else
    if ( $backcolor == "white" ) then
        echo "BackColor 1 1 1" >> $mac_file
    else
	    if ( $backcolor == "cing_turqoise" ) then
	    	# 250 250 246 from cing header image picked.
	        echo "BackColor 0.9609375 0.9765625 0.9765625" >> $mac_file
	    else
        	echo "ERROR: color not found for: $backcolor"
        	goto usage
        endif
    endif
endif
echo "DEBUG: 5"

cat >> $mac_file << EOD
Rendering 1 1 0 1 1 1 1 1
DrawPrec $precision $precision
PlotPar 21 29.7 1500 1000 950 0 1 1 0 $precision 1 50
ReadPdb $pdb_file
SelectAtom ''
SelectBond ''
SelectRes  ''
SelectMol  ''
EOD

# Don't show the terminii residues. ACE and NH2; put on a kill list.
if ( $try == 1 ) then
    cat >> $mac_file << EOD
CalcAtom 'H'
CalcAtom 'HN'
DefPropRes 'aa'     ':ALA*,ARG*,ASN*,ASP*,CYS*,GLN*,GLU*,GLY*,HIS*,ILE*,LEU*,LYS*,MET*,PHE*,PRO*,SER*,THR*,TRP*,TYR*,VAL*'
DefPropRes 'na'     ':A,C,T,G,U,DA,DC,DT,DU,DG,RADE,RCYT,RGUA,ADE,CYT,GUA,THY,URA,RURA,DURA,DADE,DCYT,DGUA,DTHY'
DefPropRes 'kill'   ':ACE,NH2'
DefPropRes 'hoh'    ':HOH'
DefPropRes 'cation' ':AG,AU,AU3,AL,CA,CD,CU,CU1,FE,FE2,K,LI,MG,MN,MN3,MO,NA,NI,PB,ZN,ZN2'
DefPropRes 'anion'  ':F,CL,BR'
DefPropRes 'ion'    'cation | anion'
DefPropRes 'ligand' '! (aa | na | kill | hoh | ion  )'
SelectBond ''
StyleBond invisible
SelectAtom ''
SelectBond ''
SelectRes  'aa'
CalcSecondary
XMacStand ribbon.mac
SelectRes  'na'
XMacStand $mac_dir/schem_dna.mac
SelectAtom 'res.cation'
ColorAtom 0 1 0
SelectAtom 'res.anion'
ColorAtom 1 0 0
SelectAtom 'res.hoh'
ColorAtom 0.498 1 0.831
RadiusAtom 0.4
SelectAtom 'res.ion'
RadiusAtom 1
SelectAtom 'res.ion | res.hoh'
StyleAtom sphere
SelectAtom 'res.ligand'
CalcBond 1 1 1
SelectBond 'res1.ligand | res2.ligand'
XMacStand ball_stick.mac
EOD
else
    cat >> $mac_file << EOD
StyleAtom invisible
StyleBond invisible
SelectAtom 'bb'
SelectBond 'bb'
XMacStand ball_stick.mac
EOD
endif

cat >> $mac_file << EOD
AutoScale
PlotPov $tmp_dir/$id.pov
Quit no
EOD
#WriteDump $tmp_dir/$id.mml

if ( -e $MOLMOLHOME/dump ) then
    \rm -f $MOLMOLHOME/dump
endif
echo "DEBUG: 6"

# Run the stuff through molmol
setenv MOLMOLDEV TTY/NO
$executableMm -t -f - < $mac_file >>& $log_file
set molmol_status = $status
echo "DEBUG: 7"

if ( $molmol_status ) then
    if ( $try == 1 ) then
        echo "WARNING: molmol crashed on the first try; trying simple render before giving up on $id."
        set try = 2
        goto start
    endif
    echo "ERROR: molmol crashed for the second (simpler) try; giving up on $id."
    goto error
endif
sync
if ( ! -e $tmp_dir/$id.pov ) then
    if ( $try == 1 ) then
        echo "WARNING: no pov file on first try; trying simple render before giving up on $id."
        set try = 2
        goto start
    endif
    echo "ERROR: no pov file on the second (simpler) try; giving up"
    echo "ERROR: no pov image file was created"
    goto error
endif


# Remove the temporary stuff
# Don't remove input and log file if no pov file was created.
# DEBUG: uncomment next line
#\rm -f $mac_file $log_file

exit 0

error:
    if ( -e $log_file ) then
        echo "ERROR: follows the last lines from molmol povray file generation:"
        tail -5 $log_file
    endif
    echo "ERROR: instead of rendering to pov file copied a default pov file."
    cp $molgrapDir/default_image.pov $tmp_dir/$id.pov
    exit 0

usage:
    echo "# USE: molmol_image.csh pdb_file tmp_dir pdb_id scripts_dir back_ground_color molmolExecutable"
    exit 2


####



