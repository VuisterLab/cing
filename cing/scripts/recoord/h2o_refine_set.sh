#!/bin/sh

PROGRAM=h2o_refine_set.sh
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

PDB=(annealed.pdb)
out=h2o_refined_%03d.pdb
mtf=structure.mtf
log=
ambre=""
unare=""
hbond=""
dihre=""
sym=
keepwater=
num=50
cnsExec=

OPTIONS="
\t# File options:\n
\t  -f \t $pdb   \t Input coordinate file(s), refined (PDB, multi)\n
\t  -p \t $mtf   \t Structure file (MTF|PSF)\n
\t  -o \t $out   \t Output coordinate file (PDB)\n
\t  -u \t $unare \t\t Unambiguous restraints file (TBL)\n
\t  -a \t $ambre \t\t Ambiguous restraints file (TBL)\n
\t  -b \t $hbond \t\t H-bonds file (TBL)\n
\t  -d \t $dihre \t\t Dihedral restraints file (TBL)\n
\t  -g \t $log   \t Logfile (TXT)\n
\t  -n \t $num   \t\t Number of structures to refine with water\n
\t  -x \t        \t\t Executable for processing CNS script (default cns)\n
\t  --sym \t $sym \t\t Impose symmetry restraints \n
\t  --keepwater \t\t\t Keep water in output pdb files \n
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
    -f)       
      while [[ -n "$2" && ${2:0:1} != "-" ]]; do
        PDB[ $(( NPDB++ )) ]=$2; shift
      done
      shift; continue ;;
    -p)       mtf=$2    ; shift; shift; continue ;;
    -o)       out=$2    ; shift; shift; continue ;;
    -u)       unare=$2  ; shift; shift; continue ;;
    -a)       ambre=$2  ; shift; shift; continue ;;
    -b)       hbond=$2  ; shift; shift; continue ;;
    -d)       dihre=$2  ; shift; shift; continue ;;
    -g)       log=$2    ; shift; shift; continue ;;
    -n)       num=$2    ; shift; shift; continue ;;
    -x)       cnsExec=$2; shift 2; continue ;;
    --sym)    sym=1     ; shift; continue ;;
    --keepwater) keepwater=1; shift; continue ;;
     *)       BAD_OPTION $1;;
  esac
done

###################
## PREPROCESSING ##
###################

# Passing through arguments
[[ $unare ]]          && unare="-u $unare"
[[ $ambre ]]          && ambre="-a $ambre"
[[ $dihre ]]          && dihre="-d $dihre"
[[ $hbond ]]          && hbond="-b $hbond"
[[ $sym == 1  ]]      && sym="--sym" 
[[ $keepwater == 1 ]] && keepwater="--keepwater"

opts="$unare $ambre $dihre $hbond $sym $keepwater"

[[ $log ]] || log=${out%.pdb}.log

## Select best $num structures in terms of energy:
echo ${PDB[@]}
PDB=(`grep energies ${PDB[@]} | sort -n +2 | sed -e s/:.*$// -e ${num}q`)

CWD=`pwd`

##########################
## DOING THE REAL STUFF ##
##########################

[[ -d `dirname $out` ]] || echo mkdir -p `dirname out`

cnt=1
for pdb in ${PDB[@]}
do
  ( source h2o_refine.sh -f $pdb -p $mtf -o `printf $out $cnt` -g `printf $log $cnt` $opts )
  : $(( cnt++ ))
done

