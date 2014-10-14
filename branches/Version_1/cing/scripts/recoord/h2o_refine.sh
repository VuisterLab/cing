#!/bin/sh

PROGRAM=h2o_refine.sh
VERSION=0.1
AUTHOR="Tsjerk A. Wassenaar, PhD"
YEAR="2009.01"
AFFILIATION="
University of Utrecht\n
Padualaan 8\n
3584CH Utrecht\n
The Netherlands"

DESCRIPTION="\
"

pdb=annealed.pdb
out=h2o_refined.pdb
mtf=structure.mtf
log=h2o_refine.log
num=1
ambre=""
unare=""
hbond=""
dihre=""
sym=
seed=-1
keepwater=0
theshold=0.5
cnsExec=

OPTIONS="
\t# File options:\n
\t  -f \t $pdb   \t Input coordinate file(s), annealed (PDB)\n
\t  -num\t$num   \t Number for structure from list (INT)\n
\t  -p \t $mtf   \t Structure file (MTF|PSF)\n
\t  -o \t $out   \t Output coordinate file (PDB)\n
\t  -u \t $unare \t\t Unambiguous restraints file (TBL)\n
\t  -a \t $ambre \t\t Ambiguous restraints file (TBL)\n
\t  -b \t $hbond \t\t H-bonds file (TBL)\n
\t  -d \t $dihre \t\t Dihedral restraints file (TBL)\n
\t  -g \t $log   \t Logfile (TXT)\n
\t  -x \t        \t\t Executable for processing CNS script (default: cns)\n
\t  --seed \t $seed \t\t Seed for generating random velocities (use PID if set to -1) \n
\t  --sym  \t $sym  \t\t Impose symmetry restraints \n
\t  --keepwater \t $keepwater \t\t Include water in output file \n
"

USAGE="\n$PROGRAM version $VERSION:\n\n$DESCRIPTION\n\n$OPTIONS\n\n(c)$YEAR $AUTHOR\n$AFFILIATION\n"

BAD_OPTION ()
{
  echo
  echo "Unknown option \"$1\" found on command-line"
  echo "It may be a good idea to read the usage:"
  echo -e $USAGE

  exit 1
}

NPDB=0
while [ -n "$1" ]; do
  case $1 in
    -h)       echo -e $USAGE       ; exit 0 ;;
    # File options
    -f)       pdb=$2    ; shift 2; continue ;;
    -p)       mtf=$2    ; shift 2; continue ;;
    -o)       out=$2    ; shift 2; continue ;;
    -u)       unare=$2  ; shift 2; continue ;;
    -a)       ambre=$2  ; shift 2; continue ;;
    -b)       hbond=$2  ; shift 2; continue ;;
    -d)       dihre=$2  ; shift 2; continue ;;
    -g)       log=$2    ; shift 2; continue ;;
    -x)       cnsExec=$2; shift 2; continue ;;
    --seed)   seed=$2   ; shift 2; continue ;;
    --sym)    sym=1     ; shift  ; continue ;;
    --keepwater) keepwater=1 ; shift ; continue ;;
     *)       BAD_OPTION $1;;
  esac
done

###################
## PREPROCESSING ##
###################

[[ ${pdb##*.} == "list" ]] && pdb=$( sed -n ${num}p $pdb )

[ $unare ] && UNAMBIGUOUS_RESTRAINTS="noe class dist @@$unare end"   || UNAMBIGUOUS_RESTRAINTS=""
[ $ambre ] && AMBIGUOUS_RESTRAINTS="noe class ambi @@$ambre end"     || AMBIGUOUS_RESTRAINTS=""
[ $hbond ] && HBOND_RESTRAINTS="noe class hbon @@$hbond end"         || HBOND_RESTRAINTS=""
[ $dihre ] && DIHEDRAL_RESTRAINTS="restraints dihedral @@$dihre end" || DIHEDRAL_RESTRAINTS=""

[ $sym   ] && bSymRestraints="TRUE" || bSymRestraints="FALSE"
[ $dihre ] && bDihRestraints="TRUE" || bDihRestraints="FALSE"

[[ $seed < 0 ]]       && seed=$$
[[ $keepwater == 1 ]] && keepwater=TRUE || keepwater=FALSE

## SYMMETRY RESTRAINTS

if [ $sym ]; then
  SYMMETRY="
! Define NCS restraints for symmetrical dimers
!
ncs restraints
  initialize
  group
    equi (resid $SYMSTART : $SYMEND and segid $SEGID_A)
    equi (resid $SYMSTART : $SYMEND and segid $SEGID_B)
    weight = 1.0
  end
  ?
end

! Define symmetry restraints for symmetrical dimers
!
do (store5 = 1) (all)
show sum (store5) (all)
evaluate (\$Natoms = \$result)

noe class symm end

evaluate (\$istart = $SYMSTART)
evaluate (\$iend   = $SYMEND)
evaluate (\$icount = 0)

while (\$istart < \$iend) loop gensym

  evaluate (\$resid1 = \$istart)
  evaluate (\$resid2 = \$iend - \$icount)

  noe
    ! distance pair \$resid1 to \$resid2
    assign (resid \$resid1 and name CA  and segid $SEGID_A)
           (resid \$resid2 and name CA  and segid $SEGID_B) 0 0 0
    assign (resid \$resid1 and name CA  and segid $SEGID_B)
           (resid \$resid2 and name CA  and segid $SEGID_A) 0 0 0
  end

  evaluate (\$icount = \$icount + 1)
  evaluate (\$istart = \$istart + 1)

end loop gensym

noe
  potential  symm symmetry
  scale      symm 10.0
  sqconstant symm 1.0
  sqexponent symm 2
  soexponent symm 1
  rswitch    symm 0.5
  sqoffset   symm 0.0
  asymptote  symm 1.0
end
"
else
  SYMMETRY=""
fi

if [ `sed -e "{/^ENDMDL/{d;n};/^END/!d;q;}" $pdb` ]; then END=""; else END=END; fi

CWD=`pwd`

# Try to set the CNS environment if no executable is given
if [ -z $cnsExec ]; then
  source $VO_ENMR_EU_SW_DIR/BCBR/cns/1.2-para/set_cns.bash
  cnsExec=`which cns`
fi

##########################
## DOING THE REAL STUFF ##
##########################

$cnsExec > $log << EOF

set abort normal end

flags exclude * end
flags include bonds end
flags include angle end
flags include improper end
flags include dihedrals end
flags include vdw end
flags include elec end
flags include noe end

if ( $bDihRestraints = TRUE) then flags include cdih end end if
if ( $bSymRestraints = TRUE) then flags include ncs  end end if

structure @@$mtf end     
 
!load the topology files:
   topology
       @@topallhdg5.3.pro
       @@topallhdg5.3.sol
       @@carbohydrate.top
   end

!read the parameter files:
   evaluate (\$par_nonbonded = "OPLSX")
   parameter
       @@parallhdg5.3.pro
       @@carbohydrate.param
   end
  parameter 
    @@parallhdg5.3.sol
    nbonds
      nbxmod=5 atom cdiel shift 
      cutnb=9.5 ctofnb=8.5 ctonnb=6.5 eps=1.0 e14fac=0.4 inhibit 0.25
      wmin=0.5
      tolerance  0.5
    end
  end

! read coordinate and copy to reference coordinate set
coor @@$pdb $END

do (refx = x) (all)
do (refy = y) (all)
do (refz = z) (all)

! generate water layer
do (segid = "PROT") (segid "    ")

!-------@SCRIPTS:protocols/generate_water.cns

eval (\$boxlength = 18.856)   ! length of Brooks' water box
eval (\$thickness = 8)        ! maxi. initial water-protein distance (heavy atoms)
eval (\$pw_dist = 4.0)        ! mini. initial water-protein distance (heavy atoms)
eval (\$water_diam = 2.4)     ! diameter of water molecule
eval (\$dyncount = 1)         ! iteration number (usually 1)

eval (\$water = "WAT" + encode(\$dyncount))

!--------------------------------------------------
! read in the same box of water several times, and move it around
! so as to cover all the space around the site of interest.
! take into account box offset

show max (x) ((not resn tip3) and not resn ani)
evaluate (\$xmax = \$result)
show min (x) ((not resn tip3) and not resn ani)
evaluate (\$xmin = \$result)

show max (y) ((not resn tip3) and not resn ani)
evaluate (\$ymax = \$result)
show min (y) ((not resn tip3) and not resn ani)
evaluate (\$ymin = \$result)

show max (z) ((not resn tip3) and not resn ani)
evaluate (\$zmax = \$result)
show min (z) ((not resn tip3) and not resn ani)
evaluate (\$zmin = \$result)

! loop over several iterations of water filling and dynamics

!--------------------------------------------------
! read in the same box of water several times, and move it around
! so as to cover all the space around the site of interest.
! take into account box offset

! determine how many boxes are necessary in each dimension
eval (\$xbox = int( (\$xmax - \$xmin + 2 * (\$thickness + \$water_diam)) / \$boxlength  + 0.5))
eval (\$ybox = int( (\$ymax - \$ymin + 2 * (\$thickness + \$water_diam)) / \$boxlength  + 0.5))
eval (\$zbox = int( (\$zmax - \$zmin + 2 * (\$thickness + \$water_diam)) / \$boxlength  + 0.5))

eval (\$xmtran =  \$xmax + \$thickness - \$boxlength/2 + \$water_diam)
eval (\$ymtran =  \$ymax + \$thickness - \$boxlength/2 + \$water_diam)
eval (\$zmtran =  \$zmax + \$thickness - \$boxlength/2 + \$water_diam)

eval (\$xcount=0)
eval (\$xtrans = \$xmin - \$thickness - \$water_diam - \$boxlength/2 )
while ( \$xtrans < \$xmtran ) loop wat1
  eval (\$xcount=\$xcount+1)
  eval (\$xtrans = \$xtrans + \$boxlength)

  eval (\$ycount=0)
  eval (\$ytrans = \$ymin - \$thickness - \$water_diam - \$boxlength/2 )
  while (\$ytrans < \$ymtran) loop wat2
    eval (\$ycount=\$ycount+1)
    eval (\$ytrans = \$ytrans + \$boxlength)

    eval (\$zcount=0)                  
    eval (\$ztrans = \$zmin - \$thickness - \$water_diam - \$boxlength/2 )
    while (\$ztrans < \$zmtran) loop wat3
      eval (\$zcount=\$zcount+1)
      eval (\$ztrans = \$ztrans + \$boxlength)


      segment
        name="    "
        chain coordinates @@boxtyp20.pdb end
      end
      coor @@boxtyp20.pdb 
      do (segid=W000) (segid "    ")
      coor sele=(segid W000) translate vector = (\$xtrans \$ytrans \$ztrans) end

      ! all new water oxygens
      ident (store1) (segid W000 and name oh2) 
      ! all new water oxygens close to a protein heavy atom
      ident (store2) (store1 and (not (resn tip3 or resn ani or hydro)) around \$pw_dist)
      ! all new water oxygens close to old water oxygens
      ident (store3) (store1 and (segid wat# and not hydro) around \$water_diam)
      ! all new water oxygens further than thickness away from a protein heavy atom
      ident (store4) (store1 and not (not (resn tip3 or resn ani or hydro)) around \$thickness)
      delete sele= (byres (store2 or store3 or store4)) end
  
      ! give waters unique segid name
      eval (\$segid= "W" 
             + encode(\$xcount) + encode(\$ycount) + encode(\$zcount))
      do (segid = \$segid) (segid W000)

    end loop wat3
  end loop wat2
end loop wat1

! now, give waters a unique resid so that we get the segid to play around with
ident (store1) (all)
show min (store1) (segid w*)
do (store1 = store1 - \$result + 1) (segid w*)
do (resid = encode(int(store1/3 -0.1) +1)) (segid w* and not segid wat#)
do (segid = \$water) (segid w* and not segid wat#)

! shave off any waters that left
delete sele= (byres (name oh2 and not (not (resn tip3 or resn ani or hydro)) around \$thickness)) end

!-------/@SCRIPTS:protocols/generate_water.cns
do (segid = "    ") (segid "PROT")

set seed $seed end

!-- Handle/reset restraints (if any): allocate space for NOEs
noe reset nrestraints = 300000 ceiling 1000 end

$UNAMBIGUOUS_RESTRAINTS
$AMBIGUOUS_RESTRAINTS
$HBOND_RESTRAINTS

noe
  averaging   * sum
  potential   * soft
  scale       *  1.0
  sqconstant  *  1.0
  sqexponent  *  2
  soexponent  *  1
  sqoffset    *  0.0
  msoexponent *  1
  rswitch     *  1.0
  mrswitch    *  1.0
  asymptote   *  2.0
  masymptote  * -0.1
  avexpo hbond 20
end

restraints dihedral nassign 2000 end
$DIHEDRAL_RESTRAINTS
restraints dihedral ? end

$SYMMETRY_RESTRAINTS

evaluate ( \$rswitch        =  0.5 )
evaluate ( \$mrswitch       =  0.5 )
evaluate ( \$asym2          =  0.1 )
evaluate ( \$masym2         = -0.1 )
evaluate ( \$k_noe          = 50  )

noe
    rswitch ambi \$rswitch
    rswitch dist \$rswitch
    rswitch hbon \$rswitch

    mrswitch ambi \$mrswitch
    mrswitch dist \$mrswitch
    mrswitch hbon \$mrswitch

    asym ambi \$asym2
    asym dist \$asym2
    asym hbon \$asym2

    masym ambi \$masym2
    masym dist \$masym2
    masym hbon \$masym2

    scale ambi \$k_noe
    scale dist \$k_noe
    scale hbon \$k_noe
end

restraints dihedral scale=200 end 

! since we do not use SHAKe, increase the water bond angle energy constant
parameter angle (resn tip3) (resn tip3) (resn tip3) 500 TOKEN end

! reduce improper and angle force constant for some atoms

! taken from Chris
evaluate (\$kbonds = 1000)
evaluate (\$kchira = 5)
! taken from Chris

evaluate (\$kangle = 50)
evaluate (\$kimpro = 5)
evaluate (\$komega = 5)
parameter
   angle    (not resn tip3)(not resn tip3)(not resn tip3) \$kangle  TOKEN
   improper (all)(all)(all)(all) \$kimpro  TOKEN TOKEN
end

! fix the protein for initial minimization
fix sele = (not resn tip3) end
minimize powell nstep=40 drop=100 end

! release protein and restrain harmonically
fix sele = (not all) end
do (refx=x) (all)
do (refy=y) (all)
do (refz=z) (all)
restraints harmonic 
   exponent = 2
end
do (harm = 0)  (all)
do (harm = 10) (not name h*)
do (harmonic=20.0)(resname ANI and name OO)
do (harmonic=0.0) (resname ANI and name Z )
do (harmonic=0.0) (resname ANI and name X )
do (harmonic=0.0) (resname ANI and name Y )

igroup
  interaction (not resname ANI) (not resname ANI)
  interaction ( resname ANI) ( resname ANI)
end

minimize powell nstep=40 drop=10 end
do (refx=x) (not resname ANI)
do (refy=y) (not resname ANI)
do (refz=z) (not resname ANI)

minimize powell nstep=40 drop=10 end
do (refx=x) (not resname ANI)
do (refy=y) (not resname ANI)
do (refz=z) (not resname ANI)

do (mass  =  100) (all)
do (mass  = 1000) (resname ani)
do (fbeta =    0) (all)
do (fbeta =   20. {1/ps} ) (not resn ani)                
evaluate (\$kharm = 50) 
! heat to 500 K
for \$bath in (100 200 300 400 500) loop heat
   do (harm = \$kharm) (not name h* and not resname ANI)
   do (vx=maxwell(\$bath)) (all)
   do (vy=maxwell(\$bath)) (all)
   do (vz=maxwell(\$bath)) (all)  
   dynamics cartesian
      nstep=200 timest=0.003 {ps}       
      temperature=\$bath  tcoupling = true
      nprint=50 
   end 
   evaluate (\$kharm = max(0, \$kharm - 4))
   do (refx=x) (not resname ANI)
   do (refy=y) (not resname ANI)
   do (refz=z) (not resname ANI)
end loop heat

! refinement at high T:
igroup
  interaction (not resname ANI) (not resname ANI) weights * 1 dihed 2 end
  interaction ( resname ANI) ( resname ANI) weights * 1 end
end

do (harm = 0)  (not resname ANI)
do (vx=maxwell(\$bath)) (all)
do (vy=maxwell(\$bath)) (all)
do (vz=maxwell(\$bath)) (all)  
dynamics cartesian
   nstep=2000 timest=0.004{ps}      
   temperature=\$bath  tcoupling = true
   nprint=50 
end 

igroup
  interaction (not resname ANI) (not resname ANI) weights * 1 dihed 3 end
  interaction ( resname ANI) ( resname ANI) weights * 1  end
end

! cool 
evaluate (\$bath = 500)
while (\$bath ge 25) loop cool

   !taken from Chris Spronk CMBI
   evaluate (\$kbonds    = max(225,\$kbonds / 1.1))
   evaluate (\$kangle    = min(200,\$kangle * 1.1))
   evaluate (\$kimpro    = min(200,\$kimpro * 1.4))
   evaluate (\$kchira    = min(800,\$kchira * 1.4))
   evaluate (\$komega    = min(80,\$komega * 1.4))
   !taken from Chris Spronk CMBI

   parameter
      !taken from Chris Spronk CMBI*
      bond     (not resn tip3 and not name H*)(not resn tip3 and not name H*) \$kbonds  TOKEN
      angle    (not resn tip3 and not name H*)(not resn tip3 and not name H*)(not resn tip3 and not name H*) \$kangle  TOKEN
      improper (all)(all)(all)(all) \$kimpro  TOKEN TOKEN
      !VAL: stereo CB
      improper (name HB and resn VAL)(name CA and resn VAL)(name CG1 and resn VAL)(name CG2 and resn VAL) \$kchira TOKEN TOKEN
      !THR: stereo CB
      improper (name HB and resn THR)(name CA and resn THR)(name OG1 and resn THR)(name CG2 and resn THR) \$kchira TOKEN TOKEN
      !LEU: stereo CG
      improper (name HG and resn LEU)(name CB and resn LEU)(name CD1 and resn LEU)(name CD2 and resn LEU) \$kchira TOKEN TOKEN
      !ILE: chirality CB
      improper (name HB and resn ILE)(name CA and resn ILE)(name CG2 and resn ILE)(name CG1 and resn ILE) \$kchira TOKEN TOKEN
      !chirality CA
      improper (name HA)(name N)(name C)(name CB) \$kchira TOKEN TOKEN

      improper (name O)  (name C) (name N) (name CA) \$komega TOKEN TOKEN
      improper (name HN) (name N) (name C) (name CA) \$komega TOKEN TOKEN
      improper (name CA) (name C) (name N) (name CA) \$komega TOKEN TOKEN
      improper (name CD) (name N) (name C) (name CA) \$komega TOKEN TOKEN
   end
   !taken from Chris Spronk CMBI*

   do (vx=maxwell(\$bath)) (all)
   do (vy=maxwell(\$bath)) (all)
   do (vz=maxwell(\$bath)) (all)
   dynamics cartesian
      nstep=200 timest=0.004{ps}      
      temperature=\$bath  tcoupling = true                       
      nprint=50 
   end 

   evaluate (\$bath = \$bath - 25)
end loop cool

!final minimization:
mini powell nstep 200 end
                        
igroup interaction 
   (not resname TIP* and not resname ANI) 
   (not resname TIP* and not resname ANI) 
end

noe reset end

\$UNAMBIGUOUS_RESTRAINTS
\$AMBIGUOUS_RESTRAINTS
\$HBOND_RESTRAINTS

noe
  averaging   * sum
  potential   * soft
  scale       *  1.0
  sqconstant  *  1.0
  sqexponent  *  2
  soexponent  *  1
  sqoffset    *  0.0
  msoexponent *  1
  rswitch     *  1.0
  mrswitch    *  1.0
  asymptote   *  2.0
  masymptote  * -0.1
  avexpo hbond 20
end

restraints dihedral nassign 2000 end
\$DIHEDRAL_RESTRAINTS
restraints dihedral ? end

!-- VIOLATIONS

flags exclude * include noe bonds angles dihedrals impropers elec end
if ( $bDihRestraints = FALSE) then
  evaluate (\$cdih = 0)
else
  flags include cdih end
end if

energy end

display <NOE $seed>
print threshold=$threshold noe
display </NOE $seed>

evaluate (\$rms_noe=\$result)
evaluate (\$violations_noe=\$violations)

print thres=0.05 bonds
evaluate (\$rms_bonds=\$result)

print thres=5. angles
evaluate (\$rms_angles=\$result)

print thres=5. impropers
evaluate (\$rms_impropers=\$result)

print thres=30. dihedrals
evaluate (\$rms_dihedrals=\$result)

if ( $bDihRestraints = TRUE ) then
  display <DIHEDRAL $seed>
  print threshold=0.000001 cdih
  display </DIHEDRAL \$current>
  evaluate (\$rms_cdih=$seed)
  evaluate (\$violations_cdih=\$violations)
end if

coupl print thres=1.0 class c1 end

remarks initial random number seed: $seed
remarks ===============================================================
remarks            overall,bonds,angles,improper,dihe,vdw,elec,noe,cdih
remarks energies: \$ener, \$bond, \$angl, \$impr, \$dihe, \$vdw, \$elec, \$noe, \$cdih
remarks ===============================================================
remarks            bonds,angles,impropers,dihe,noe,cdih
remarks rms-dev.: \$rms_bonds,\$rms_angles,\$rms_impropers,\$rms_dihedrals,\$rms_noe,\$rms_cdih
remarks ===============================================================
remarks               noe,cdih
remarks               >$threshold,>0.000001
remarks violations.: \$violations_noe, \$violations_cdih
remarks ===============================================================
remarks SUMMARY: noe \$noe   cdih \$cdih
remarks ===============================================================

coor sele= (not name h* and not resn ani) orient end
do (q=1) (all)

if ( $keepwater eq TRUE ) then
  write coordinates sele=(all) output=$out end
else
  write coordinates sele=(not resn TIP3) output=$out end
end if 

stop

EOF
