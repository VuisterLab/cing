#!/bin/sh

PROGRAM="extended.sh"
VERSION=0.1
AUTHOR="Tsjerk A. Wassenaar, PhD"
YEAR="2008.10"
AFFILIATION="
University of Utrecht\n
Padualaan 8\n
3584CH Utrecht\n
The Netherlands"

DESCRIPTION="\
"

mtf=structure.mtf
out=extended.pdb
log=extended.log
try=10

OPTIONS="
\t# File options:\n
\t  -f \t $pdb \t Input structure file (MTF|PSF)\n
\t  -o \t $out \t Output coordinate file (PDB)\n
\t  -g \t $log \t Logfile (TXT)\n
\t  -n \t $try \t Number of tries (INT)\n
\t  -x \t      \t Executable for processing CNS script (default: cns)\n
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
    -f)       mtf=$2    ; shift 2; continue ;;
    -o)       out=$2    ; shift 2; continue ;;
    -g)       log=$2    ; shift 2; continue ;;
    -n)       try=$2    ; shift 2; continue ;;
    -x)       cnsExec=$2; shift 2; continue ;;
     *)       BAD_OPTION $1;;
  esac
done

###################
## PREPROCESSING ##
###################

# Store directory of this script as run
[[ ${0%/*} != $0 ]] && SDIR=`cd ${0%/*} && pwd` || SDIR=`pwd`
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

evaluate( \$max_trial = 10 )

 evaluate ( \$log_level = quiet )
 ! par_nonbonded defined to avoid error messages
 evaluate ( \$par_nonbonded = "PROLSQ" )

 structure @$mtf end

 parameter
    @@parallhdg5.3.pro
    @@ion.param
 end

{ Set force constants for S-S bond lengths and angles to zero  }
parameter
   bonds ( name SG ) ( name SG ) 0. 1. 
end


igroup interaction=(all) (all) end

ident (x) ( all )
do (x=x/5.) ( all )
do (y=random(0.5) ) ( all )
do (z=random(0.5) ) ( all )

flags exclude * include bond angle impr dihe vdw end
parameter
   nbonds
      rcon=50. nbxmod=-3 repel=0.8 cutnb=6. 
      rexp=2 irexp=2 inhibit=0.0 wmin=0.1 tolerance=0.5
   end
end

evaluate (\$count=1) 
while (\$count < 10 ) loop l1
   do (x=x+gauss(0.1)) ( all ) 
   do (y=y+gauss(0.1)) ( all ) 
   do (z=z+gauss(0.1)) ( all ) 
   minimize powell nstep=200 nprint=10 end
   evaluate (\$count=\$count+1)
end loop l1

evaluate (\$accept=false) 
evaluate (\$trial=1) 
while (\$accept=false) loop accp

   for \$1 in id ( tag ) loop resi
      igroup 
         interaction=( byresidue (id \$1 ) and not name SG ) 
                     ( not name SG ) 
      end
      evaluate (\$accept=true) 
      print thres=0.1 bonds
      if (\$violations > 0) then
         evaluate (\$accept=false) 
      end if
      print thres=10. angles 
      evaluate (\$angles=\$result)
      if (\$violations > 0) then
         evaluate (\$accept=false) 
      end if
      print thres=10. improper
      if (\$violations > 0) then
         evaluate (\$accept=false) 
      end if
      if (\$accept=false) then
         do (x=x+gauss(0.3)) ( byresidue (id \$1 ) ) 
         do (y=y+gauss(0.3)) ( byresidue (id \$1 ) ) 
         do (z=z+gauss(0.3)) ( byresidue (id \$1 ) ) 
      end if
   end loop resi

   igroup interaction=( all ) ( all ) end

   parameter
      nbonds
         rcon=50. nbxmod=-3 repel=3. cutnb=10. 
      end
   end
   flags exclude angle improper end
   
   minimize powell nstep=200 nprint=10 end

   parameter
      nbonds
         rcon=50. nbxmod=-3 repel=0.8 cutnb=6. 
      end
   end
   flags include angle improper end
   
   evaluate (\$count=1) 
   while (\$count < 5 ) loop l2
      do (x=x+gauss(0.05)) ( all ) 
      do (y=y+gauss(0.05)) ( all ) 
      do (z=z+gauss(0.05)) ( all ) 
      minimize powell nstep=200 nprint=10 end
      evaluate (\$count=\$count+1)
   end loop l2
   
   parameter
      nbonds
         rcon=50. nbxmod=3 repel=0.8 cutnb=6. 
      end
   end
   
   minimize powell nstep=300 nprint=10 end   
   minimize powell nstep=300 nprint=10 end

   igroup interaction=( not name SG ) ( not name SG ) end
   energy end

   evaluate (\$accept=true) 

   print thres=0.05 bonds
   evaluate (\$bonds=\$result)
   if (\$violations > 0) then
      evaluate (\$accept=false) 
   end if

   print thres=10. angles 
   evaluate (\$angles=\$result)
   if (\$violations > 0) then
      evaluate (\$accept=false) 
   end if

   print thres=10. improper
   evaluate (\$impr=\$result)
   if (\$violations > 0) then
      evaluate (\$accept=false) 
   end if

   print thres=180. dihedral 
   evaluate (\$dihe=\$result)

   evaluate (\$trial=\$trial + 1) 
   if (\$trial > $try ) then
      exit loop accp
   end if

end loop accp

remarks extended strand(s) generation
remarks input molecular structure file=$mtf 
remarks final rms deviations (excluding disulfide bonds): 
remarks    bonds=	 \$bonds[F8.4] A  
remarks    angles=	 \$angles[F8.4] degrees
remarks    impropers= \$impr[F8.4] degrees
remarks    dihedrals= \$dihe[F8.4] degrees (not used in some parameter sets!)
remarks final van der Waals (repel) energy=\$vdw kcal/mole

write coordinates output=$out end  

stop

EOF

