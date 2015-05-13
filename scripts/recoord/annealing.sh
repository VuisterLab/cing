#!/bin/sh

PROGRAM=annealing.sh
VERSION=0.3
AUTHOR="Tsjerk A. Wassenaar, PhD"
YEAR="2009.01"
AFFILIATION="
University of Utrecht\n
Padualaan 8\n
3584CH Utrecht\n
The Netherlands"

DESCRIPTION="\
"

pdb=in.pdb
out=annealed.pdb
mtf=structure.mtf
log=annealing.log
ambre=""
unare=""
hbond=""
dihre=""
sym=
n=10
start=1
threshold=0.5
stepfac=1
cnsExec=

OPTIONS="
\t# File options:\n
\t  -f \t $pdb   \t Input coordinate file, extended(PDB)\n
\t  -p \t $mtf   \t Structure file (MTF|PSF)\n
\t  -o \t $out   \t Output coordinate file (PDB, GMX)\n
\t  -u \t $unare \t\t Unambiguous restraints file (TBL)\n
\t  -a \t $ambre \t\t Ambiguous restraints file (TBL)\n
\t  -b \t $hbond \t\t H-bonds file (TBL)\n
\t  -d \t $dihre \t\t Dihedral restraints file (TBL)\n
\t  -g \t $log   \t Logfile (TXT)\n
\t  -n \t $n     \t\t Number of structures to generate\n
\t  -x \t        \t\t Executable for processing CNS script (default: cns)\n
\t  --sym \t $sym \t\t Impose symmetry restraints \n
\t  --double   \t\t Double number of MD steps
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

while [ -n "$1" ]; do
  case $1 in
    -h)       echo -e $USAGE       ; exit 0 ;;
    # File options
    -f)       pdb=$2    ; shift; shift; continue ;;
    -p)       mtf=$2    ; shift; shift; continue ;;
    -o)       out=$2    ; shift; shift; continue ;;
    -u)       unare=$2  ; shift; shift; continue ;;
    -a)       ambre=$2  ; shift; shift; continue ;;
    -b)       hbond=$2  ; shift; shift; continue ;;
    -d)       dihre=$2  ; shift; shift; continue ;;
    -g)       log=$2    ; shift; shift; continue ;;
    -n)       n=$2      ; shift; shift; continue ;;
    -x)       cnsExec=$2; shift 2; continue ;;
    -start)   start=$2  ; shift; shift; continue ;;
    --sym)    sym=1     ; shift; continue ;;
    --double) stepfac=2 ; shift; continue;;
     *)       BAD_OPTION $1;;
  esac
done

###################
## PREPROCESSING ##
###################

teller=1
base=`basename $out .pdb`

[ $unare ] && UNAMBIGUOUS_RESTRAINTS="noe class dist @@$unare end"   || UNAMBIGUOUS_RESTRAINTS=""
[ $ambre ] && AMBIGUOUS_RESTRAINTS="noe class ambi @@$ambre end"     || AMBIGUOUS_RESTRAINTS=""
[ $hbond ] && HBOND_RESTRAINTS="noe class hbon @@$hbond end"         || HBOND_RESTRAINTS=""
[ $dihre ] && DIHEDRAL_RESTRAINTS="restraints dihedral @@$dihre end" || DIHEDRAL_RESTRAINTS=""

[ $sym   ] && bSymRestraints="TRUE" || bSymRestraints="FALSE"
[ $dihre ] && bDihRestraints="TRUE" || bDihRestraints="FALSE"

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

procedure setparam ( 
  tolerance=1.0;
  repel_radius=1.0;
  repel_rexpo=4;
  repel_irexp=1;
  repel_rcons=20;
)
  parameter nbonds
       repel=&repel_radius
       rexp=&repel_rexpo irexp=&repel_irexp rcon=&repel_rcons
       nbxmod=5 wmin=0.01 cutnb=6.0 ctonnb=2.99 ctofnb=3.
       tolerance=&tolerance
  end end
endprocedure

!-- END OF CNS PROCEDURES 

evaluate( \$factorProtocol = $stepfac  )

! Steps
evaluate( \$high_steps     =  2000 )
evaluate( \$cool_steps     =  8000 * $stepfac )
evaluate( \$tad_steps      =  2000 * $stepfac )
! Temperature
evaluate( \$tadinit_t      = 10000 )
evaluate( \$tadfactor      =     8 )
evaluate( \$high_t         =  2000 )
evaluate( \$med_t          =  1000 )
evaluate( \$low_t          =    50 )
evaluate( \$delta_t        = 0.003 )
evaluate( \$final1_t       =  1000 )
evaluate( \$final2_t       =    50 )

evaluate( \$rswitch        =  0.5 )
evaluate( \$mrswitch       =  0.5 )
evaluate( \$asym1          =  1.0 )
evaluate( \$masym1         = -1.0 )
evaluate( \$asym2          =  0.1 )
evaluate( \$masym2         = -0.1 )

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
evaluate (\$whichMD="Torsion")
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

!-- Read the parameter files (set par_nonbonded to PROLSQ to avoid warnings):
evaluate( \$par_nonbonded = "PROLSQ") 
parameter @@parallhdg5.3.pro end
set echo on message on end

!-- Read structures:
structure @@$mtf end
coor @@$pdb $END

do (refx=x) (all)
do (refy=y) (all)
do (refz=z) (all)

if ( \$WhichMD = "Torsion" ) then
  !-- @SCRIPTS:protocols/torsiontop.cns
  !-- Initialize torsion angle topology

  dyna tors
    topology
      maxlength=1000
      maxtree=50
      maxchain=3000
      maxbond=7

      maxj 50
      kdihmax = 23.
  
      {- remove disulfide bond links -}
      for \$ss_rm_id_1 in id ( name SG ) loop SSRM
        for \$ss_rm_id_2 in id ( name SG and bondedto ( id \$ss_rm_id_1 )  ) loop SSR2
          if (\$ss_rm_id_1 > \$ss_rm_id_2) then
            free bond ( id \$ss_rm_id_1 ) ( id \$ss_rm_id_2 )
          end if
        end loop SSR2
      end loop SSRM
 
      {- keep prolines as rigid bodies -}
      fix group ( resn PRO and not (name c or name o) )
 
      {- free a bond in sugar rings to have control over which bond is broken by torsion topology -}
      for \$nucl in id ( tag and ( resn THY or resn CYT or resn GUA or resn ADE or resn URI )) loop nucl
        free bond ( byres (id \$nucl) and name C3' ) ( byres (id \$nucl) and name C4' )
      end loop nucl
 
      {- free a bond in carbohydrates to have control over which bond is broken by torsion topology -}
      for \$nucl in id ( tag and ( resn NAG or resn GAL or resn GLC or resn FUC or resn SIA or resn XYL or resn MAN )) loop nucl
        free bond ( byres (id \$nucl) and name C3 ) ( byres (id \$nucl) and name C4 )
      end loop nucl

      {- keep nucleic acid bases rigid -}        
      fix group ( resn THY and not(name c#' or name h#' or name o#p or name o#' or name p or name h#t or name o#t))
      fix group ( resn CYT and not(name c#' or name h#' or name o#p or name o#' or name p or name h#t or name o#t))         
      fix group ( resn GUA and not(name c#' or name h#' or name o#p or name o#' or name p or name h#t or name o#t))
      fix group ( resn ADE and not(name c#' or name h#' or name o#p or name o#' or name p or name h#t or name o#t))
      fix group ( resn URI and not(name c#' or name h#' or name o#p or name o#' or name p or name h#t or name o#t))

    end
    ?
  end
end if

do (fbeta=20)  (all)
do (mass=100)  (all)
do (mass=1000) (resname ani)

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

evaluate( \$current = $start )
evaluate( \$aantal  = $start + $n - 1 )

!-- Automatic check to assess need for further refinement
!-- Use double steps if first ten structures do not include
!-- one without NOE violations < -0.5 A
evaluate( \$is_ok   = FALSE ) 
evaluate( \$smult   = 1     )
evaluate( \$restart = FALSE )

while ( \$current le \$aantal ) loop do_anneal

  if ( \$current eq 11 ) then
    if ( \$restart eq FALSE ) then
      if ( \$is_ok eq FALSE ) then
        evaluate( \$smult   = 2 )
        evaluate( \$current = $start )
        evaluate( \$restart = TRUE )
	display ## No structure found without violations < -0.5; Restarting with double number of steps for refinement
	system touch DOUBLE_STEPS
      end if
    end if
  end if

  !-- Restore original coordinates

  do (x=refx) (all)
  do (y=refy) (all)
  do (z=refz) (all)

  !-- (Re)set energy flags:
  flags exclude * include bonds angles dihedrals impropers vdw noe end
  if ( $bDihRestraints = TRUE) then flags include cdih end end if 
  if ( $bSymRestraints = TRUE) then flags include ncs  end end if

  !-- (Re)set parameters:
  parameter 
    bonds (all) (all) 1000.0 TOKEN
    bond (name sg) (name sg) 0.0 TOKEN
    angles (all) (all) (all) 500.0 TOKEN
    angle (all) (name sg) (name sg)  0.0 TOKEN
    impropers (all) (all) (all) (all) 500 TOKEN TOKEN
  end

  !-- Restore noe parameters
  noe 
    scale     * 1.0
    rswitch   * 1.0
    mrswitch  * 1.0
    asymptote * 2.0
  end

  !-- Start run with random rotations of backbone torsion angles (phi/psi)

  evaluate (\$seed = \$current) 
  set seed \$seed end

  ! The store1 is set to 1 for all atoms that have already been rotated.
  do (store1=0) (all) 
  do (store2=0) (all)

  ! loop through all ca atoms.
  for \$id in id (name ca) loop do_rotate

    show element (segid) (id \$id)
    evaluate (\$seg = \$result)

    do (store2=1) (byres (id \$id))

    evaluate (\$phi = random()*360-180)              
    evaluate (\$psi = random()*360-180)            

    ! all atoms up to the present ca are held fixed for phi rotation
    do (store1=1) ((store2 and (name n or name hn or name ht* or name ca)))

    ! rotate phi
    coor 
      rotate sele= (attribute store1=0) 
      center (head (store2 and name ca))
      axis   (head (store2 and name ca)
      tail   (store2 and name n)) \$phi
    end

    ! fix the sidechain of the current residue for psi rotation
    do (store1=1) ((store2 and not (name c or name o or name ot#)))

    ! rotate psi
    coor 
      rotate sele= (attribute store1=0 and segid \$seg) 
      center (head (store2 and name c) )
      axis   (head (store2 and name c)
      tail (store2 and name ca)) \$psi
    end

    ! fix all of current residue
    do (store1=1) (store2) 
    do (store2=0) (byres (id \$id))

  end loop do_rotate

  !-- Get initial energy
  energy end

  evaluate (\$ini_flt = 5.0)

  ident (store1) 
    (((resn Gly or resn Val or resn Ile) and (name CA or name CG1 )) or 
     ((resn Leu or resn Phe or resn Tyr) and (name CA or name CD1 )) or
     ((resn Pro or resn Asn or resn Asp) and (name CA or name CG  )) or
     ((resn Met or resn Cys) and (name CA or name SD or name SG )) or
     ((resn Ser or resn Ala) and (name CA or name CB  )) or
     (resn Trp  and (name CA or name CE2 )) or
     (resn Thr  and (name CA or name CG2 )) or
     (resn His  and (name CA or name CD2 )) or
     ((resn Gln or resn Glu or resn Lys or resn Arg) and (name CA or name CD  )) or
     ((resn CYT or resn THY or resn URI) and (name C1' or name C2 )) or
     ((resn ADE or resn GUA or resn PUR) and (name C1' or name C6 )))

  if (\$whichMD = "Cartesian") then

    flags exclude dihed end

    evaluate ( \$ncycle = 10)
    evaluate ( \$nstep1 = int( \$high_steps / \$ncycle )+1 ) 
  
    do (vx = maxwell(\$high_t)) (all)
    do (vy = maxwell(\$high_t)) (all)
    do (vz = maxwell(\$high_t)) (all)
  
    evaluate (\$ini_noe = 10.0)
    evaluate (\$fin_noe = 50.0)
    evaluate (\$ini_amb =  1.0)
    evaluate (\$k_noe = \$ini_noe)
    evaluate (\$noe_fac = (\$fin_noe/\$ini_noe)^(1/\$ncycle))
     
    noe 
      masym ambi -2.0  
      masym dist -2.0 
    end
  
    parameter nbonds 
      atom cutnb 12 tolerance 4 repel=1.25 wmin 0.5
      rexp=4 irexp=1 rcon=1. nbxmod 4 ctonnb 0.9 ctofnb 1.0
    end end
  
    igroup
      interaction (all) (not store1) weights * 1 angl 1.0 impr 1.0 vdw 0.0 elec 0 end
      interaction (store1) (store1)  weights * 1 angl 1.0 impr 1.0 vdw 0.1 elec 0 end
    end
  
    restraints dihedral scale=5 end
    flags exclude noe end
    minimize powell nstep=500 drop=10. nprint=25 end
    flags include noe end
  
    evaluate (\$hightemp_count = 0)
    while (\$hightemp_count < \$ncycle) loop anne  
      evaluate (\$hightemp_count = \$hightemp_count + 1)
      evaluate (\$k_noe = \$k_noe * \$noe_fac)
    
      noe scale dist \$k_noe scale ambi \$ini_amb scale hbon \$ini_amb end
  
      evaluate (\$k_vdw = \$k_noe * 0.002)
      igroup
        interaction (all) (not store1) weights * 1 angl 1.0 impr 1.0 vdw   0.0 elec 0 end
        interaction (store1) (store1)  weights * 1 angl 1.0 impr 1.0 vdw \$k_vdw elec 0 end
      end
       
      dynamics  cartesian
        nstep=\$nstep1  timestep=\$delta_t
        tcoupling=true  temperature=\$carinit_t  nprint=50 
        ntrfrq=9999     cmremove=true            cmperiodic=0
      end
  
      evaluate ( \$critical = \$temp/\$carinit_t)
      if (\$critical > 1.5) then
        mini powell nstep 100 end
        do (vx=maxwell(\$high_t)) ( all )
        do (vy=maxwell(\$high_t)) ( all )
        do (vz=maxwell(\$high_t)) ( all )
      end if
    end loop anne
      
    noe 
      masym ambi -0.1  
      masym dist -0.1 
    end
  
else  !-- Torsion angle dynamics (standard protocol)

  {* 1 ======================================= high temperature dynamics *}

  parameter bond (name C1') (name C2') 5.0 TOKEN end
  flags exclude dihed end

  !-- @SCRIPTS:protocols/sa_ltad_hightemp4.cns (nstep=\$high_steps;SaProtocol=\$SaProtocol;Data=\$Data;)

  noe 
      rswitch ambi \$rswitch
      rswitch dist \$rswitch
      rswitch hbon \$rswitch
  
      mrswitch ambi \$mrswitch
      mrswitch dist \$mrswitch
      mrswitch hbon \$mrswitch
  
      asym ambi \$asym1
      asym dist \$asym1
      asym hbon \$asym1
  
      masym ambi \$masym1
      masym dist \$masym1
      masym hbon \$masym1
  end
  
  evaluate (\$k_vdw = 0.005)
  evaluate (\$bath = \$tadinit_t)
  evaluate (\$timestep = \$delta_t * \$tadfactor)

  do (vx = maxwell(10)) (all)
  do (vy = maxwell(10)) (all)
  do (vz = maxwell(10)) (all)
  
  parameter nbonds 
     atom cutnb 12 tolerance 4 repel=1.25 wmin 0.5
     rexp=4 irexp=1 rcon=1. nbxmod 4 ctonnb 0.9 ctofnb 1.0
  end end
  
  igroup
     inter (all) (not store1) weights * 1 angl 1.0 impr 1.0 vdw 0.0 elec 0 end
     inter (store1) (store1)  weights * 1 angl 1.0 impr 1.0 vdw \$k_vdw elec 0 end
  end
     
  restraints dihedral scale 5 end 
  noe scale dist 0 scale ambi 0 scale hbon 0 end
  minimize powell nstep=200 drop=10.  nprint=25 end
  
  noe 
     scale dist 10 ! &Data.unamb_hot 
     scale ambi 10 ! &Data.amb_hot
     scale hbon 10 ! &Data.hbond_hot
  end
  
  dyna tors
    reassign TRUE
    timestep=\$timestep
    nstep=\$high_steps
    nprint=\$high_steps
    ntrfrq=0
    tcoupling = true
    tbath = \$bath
  end

  {* 2 ============================================ cooling 1 *}

  evaluate (\$ncycle = 10)

  !-- We still don't need impropers
  flags include bonds angles end

  call setparam ( tolerance=2.0; )  
  
  evaluate ( \$asy      = \$asym1  )
  evaluate ( \$masy     = \$masym1 )
  evaluate ( \$asy_add  = (\$asym2  - \$asym1)/\$ncycle)
  evaluate ( \$masy_add = (\$masym2 - \$masym1)/\$ncycle)
  
  noe 
      rswitch ambi \$rswitch
      rswitch dist \$rswitch
      rswitch hbon \$rswitch
  
      mrswitch ambi \$mrswitch
      mrswitch dist \$mrswitch
      mrswitch hbon \$mrswitch
  
      asym ambi \$asym1
      asym dist \$asym1
      asym hbon \$asym1
  
      masym ambi \$masym1
      masym dist \$masym1
      masym hbon \$masym1
  end 
  
  restraints dihedral scale=25 end
  
  evaluate (\$tempstep = (\$tadinit_t - \$final2_t)/\$ncycle)
  ! removed division by tadfactor
  evaluate (\$calcsteps = int( \$smult * \$tad_steps / (\$ncycle) ) )  
  evaluate (\$timestep = \$delta_t * \$tadfactor)
  
  evaluate (\$ini_con=  0.001)       
  evaluate (\$fin_con=  1)
  evaluate (\$k_vdw = \$ini_con)
  evaluate (\$k_vdwfact = (\$fin_con/\$ini_con)^(1/\$ncycle))
  
  evaluate (\$ini_flt = 5)
  evaluate (\$fin_flt = 500)
  evaluate (\$k_flt = \$ini_flt)
  evaluate (\$flt_fac = (\$fin_flt/\$ini_flt)^(1/\$ncycle))
  
  evaluate (\$k_noe     = 10) ! (\$k_unamb= &Data.unamb_cool1_ini)
  evaluate (\$noe_fac   = (50/10)^(1/\$ncycle)) ! (\$unamb_fac = (&Data.unamb_cool1_fin/&Data.unamb_cool1_ini)^(1/\$ncycle))
  
  evaluate (\$bath  = \$tadinit_t)
  do (vx=maxwell(4.0)) ( all )
  do (vy=maxwell(4.0)) ( all )
  do (vz=maxwell(4.0)) ( all )
  
  evaluate (\$reassign = TRUE)
  evaluate (\$i_cool = 0)
  while (\$i_cool < \$ncycle) loop cool
  
        evaluate (\$i_cool=\$i_cool+1)
  
        evaluate (\$bath  = \$bath  - \$tempstep)       
        evaluate (\$k_vdw = min(\$fin_con,\$k_vdw*\$k_vdwfact))
        evaluate (\$k_flt = \$k_flt * \$flt_fac )
        evaluate (\$k_noe = \$k_noe * \$noe_fac )
        evaluate (\$asy   = \$asy   + \$asy_add )
        evaluate (\$masy  = \$masy  + \$masy_add)
  
        parameter
          bond  (name sg) (name sg) \$k_flt TOKEN
          angle (all) (name sg) (name sg)  \$k_flt TOKEN
          bond  (name C1') (name C2') \$k_flt TOKEN
        end
  
        igroup 
          interaction (not name h*) (not name h*) weights * 1 vdw \$k_vdw end
          interaction (name h*) (all) weights * 1 vdw 0 elec 0 end
        end

        noe 
           scale dist \$k_noe
           scale ambi \$k_noe 
           scale hbon \$k_noe
 
           asym ambi \$asy
           asym dist \$asy
           asym hbon \$asy

           masym ambi \$masy
           masym dist \$masy
           masym hbon \$masy
        end
  
        dyna tors
           reassign \$reassign
           timestep=\$timestep
           nstep=\$calcsteps
           nprint=\$calcsteps
           ntrfrq=0
           tcoupling = true  tbath = \$bath
        end

        evaluate (\$reassign = FALSE)
  end loop cool

  !-- END of @SCRIPTS:protocols/sa_ltad_cool1.cns(SaProtocol=\$SaProtocol;Data=\$Data;Toppar=\$Toppar;)

  ! Here part for TAD ends
end if

!--QQQ--

{* 3 ============================================ cooling 2 *}


!-- @SCRIPTS:protocols/sa_l_cool1.cns(SaProtocol=\$SaProtocol;Data=\$Data;Toppar=\$Toppar;) 

  ! cartesian dynamics cooling
  
  evaluate (\$ncycle = (\$high_t - \$med_t)/ 50 ) ! &SAProtocol.tempstep = 50 
  evaluate (\$nstep = int( \$smult * \$cool_steps / \$ncycle)) 
  
  evaluate (\$ini_con = 0.01)        
  evaluate (\$fin_con =  1)
  evaluate (\$ini_flt = 5)           
  evaluate (\$fin_flt = 500)
        
  evaluate (\$k_vdw     = \$ini_con)
  evaluate (\$k_vdwfact = (\$fin_con/\$ini_con)^(1/\$ncycle))
  evaluate (\$k_flt     = \$ini_flt)
  evaluate (\$flt_fac   = (\$fin_flt/\$ini_flt)^(1/\$ncycle))
  
  evaluate (\$k_noe     = 10)
  evaluate (\$noe_fac   = (50/10)^(1/\$ncycle))
  
  noe 
      rswitch ambi \$rswitch
      rswitch dist \$rswitch
      rswitch hbon \$rswitch
  
      mrswitch ambi \$mrswitch
      mrswitch dist \$mrswitch
      mrswitch hbon \$mrswitch
  
      asym ambi \$asym1
      asym dist \$asym1
      asym hbon \$asym1
  
      masym ambi \$masym1
      masym dist \$masym1
      masym hbon \$masym1
  end 
  
  ! restraints dihedral   scale=&Data.dihedrals_cool1   end  
  restraints dihedral scale=25 end  
  
  evaluate (\$fin_noe = 50.0)   
  evaluate (\$k_noe = \$fin_noe)
  
  call setparam ( tolerance=0.5; )
     
  evaluate (\$bath  = \$high_t)
  do (vx=maxwell(\$bath)) ( all )
  do (vy=maxwell(\$bath)) ( all )
  do (vz=maxwell(\$bath)) ( all ) 
  
  evaluate (\$i_cool = 0)
  while (\$i_cool < \$ncycle) loop cool
        evaluate (\$i_cool=\$i_cool+1)
        evaluate (\$bath  = \$bath  - 50) ! evaluate (\$bath  = \$bath  - &Saprotocol.tempstep)       
        evaluate (\$k_vdw=min(\$fin_con,\$k_vdw*\$k_vdwfact))
        evaluate (\$k_flt = \$k_flt*\$flt_fac)
        evaluate (\$k_noe = \$k_noe*\$noe_fac)
  
        parameter
          bond  (name sg) (name sg)        \$k_flt TOKEN
          angle (all) (name sg) (name sg)  \$k_flt TOKEN
          bond  (name C1') (name C2')      \$k_flt TOKEN 
        end
  
        igroup 
          interaction  (not name h*) (not name h*) weights * 1 vdw \$k_vdw elec 0 end 
          interaction  (name h*) (all) weights * 1 vdw 0 elec 0 end 
        end

        noe scale dist \$k_noe scale ambi \$k_noe scale hbon \$k_noe end
  
        dynamics  cartesian
           nstep=\$nstep time=\$delta_t
           tcoup=true  temperature=\$bath  nprint=\$nstep    
           ntrfrq=99999  cmremove=true  cmperiodic=0
        end
  
        evaluate ( \$critical = \$temp / \$bath)
        if (\$critical > 1.2) then
           mini powell nstep 100 end
           do (vx=maxwell(\$bath)) ( all )
           do (vy=maxwell(\$bath)) ( all )
           do (vz=maxwell(\$bath)) ( all )
        end if
  
  end loop cool

!-- END of @SCRIPTS:protocols/sa_l_cool1.cns(SaProtocol=\$SaProtocol;Data=\$Data;Toppar=\$Toppar;) 

!--QQQ--

  flags include dihed end

!-- @SCRIPTS:protocols/sa_ls_cool2.cns(SaProtocol=\$SaProtocol;Data=\$Data;Toppar=\$Toppar;)

  evaluate (\$tempstep = 50)
  evaluate (\$ncycle   = (\$med_t - \$low_t) / \$tempstep)
  
  evaluate (\$k_vdw   =  1.0)
  evaluate (\$k_noe   = 50  )
  
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
  
  flags include improper end

  call setparam ()
  parameter nbonds ? end end

  igroup interaction  (all) (all) weights * 1 vdw \$k_vdw elec 0 end end
  
  evaluate (\$tempstep = 50)
  evaluate (\$nstep = int( \$smult * \$cool_steps / \$ncycle ) )
  
  evaluate (\$bath  = \$med_t)
  do (vx=maxwell(\$bath)) ( all )
  do (vy=maxwell(\$bath)) ( all )
  do (vz=maxwell(\$bath)) ( all )
    
  evaluate (\$i_cool = 0)
  while (\$i_cool < \$ncycle) loop cool
       evaluate (\$i_cool=\$i_cool+1)
       evaluate (\$bath = \$bath - \$tempstep)
  
       igroup 
          interaction  (all) (all) weights * 1 vdw 1.0000 end 
       end
       ! restraints dihe scale &Data.dihedrals_cool2 end
       restraints dihe scale 200 end
  
       dynamics  cartesian
           nstep=\$nstep time=\$delta_t
           tcoup=true temperature=\$bath nprint=\$nstep  
           ntrfrq=9999  cmremove=true  cmperiodic=0
       end
  
       evaluate ( \$critical = \$temp / \$bath)
       if (\$critical > 1.2) then
          mini powell nstep 100 end
          do (vx=maxwell(\$bath)) ( all )
          do (vy=maxwell(\$bath)) ( all )
          do (vz=maxwell(\$bath)) ( all )
       end if
  
  end loop cool

!--QQQ--

!-- END of @SCRIPTS:protocols/sa_ls_cool2.cns(SaProtocol=\$SaProtocol;Data=\$Data;Toppar=\$Toppar;)

{* 4 =========================== final minimization *}

  call setparam ()
  parameter nbonds ? end end

  igroup interaction  (all) (all) weights * 1 vdw 1.0 elec 0 end end

  minimize powell nstep=200 drop=10.0 nprint=25 end
   
{* 5 =========================== write out the final structure *}

!-- VIOLATIONS 

noe
  scale       * 50.0
  rswitch     *  0.5
  asymptote   *  0.1
  masymptote  * -0.1
  mrswitch    *  0.5
end

flags exclude * include noe bonds angles dihedrals impropers end
if ( $bDihRestraints = FALSE) then 
  evaluate (\$cdih = 0) 
else
  flags include cdih end
end if 
! flags include elec end

parameter
  bonds         (all)     (all)           1000.0 TOKEN
  bonds     (name sg) (name sg)              0.0 TOKEN
  angles        (all)     (all)     (all)  500.0 TOKEN
  angles        (all) (name sg) (name sg)    0.0 TOKEN
  impropers     (all)  (all)  (all)  (all) 500.0 TOKEN TOKEN
end

energy end

!-- Test for violations < -0.5
!-- Only test when no structure has passed the test yet
if ( \$is_ok = FALSE ) then
  print threshold=0.5
  if ( \$violations eq 0 ) then
    evaluate( \$is_ok = TRUE )
  end if
end if

display <NOE \$current>
print threshold=$threshold noe 
display </NOE \$current>

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
  display <DIHEDRAL \$current>
  print threshold=0.000001 cdih
  display </DIHEDRAL \$current>
  evaluate (\$rms_cdih=\$result)
  evaluate (\$violations_cdih=\$violations)
end if

coupl print thres=1.0 class c1 end
  
remarks initial random number seed: \$seed
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
evaluate( \$out = "$base" + encode(\$current) + ".pdb" )
write coordinates sele=(all) output=\$out end

evaluate  ( \$current = \$current + 1 )

end loop do_anneal

stop

EOF

