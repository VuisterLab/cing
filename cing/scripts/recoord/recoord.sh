#!/bin/sh

PROGRAM=recoord.sh
VERSION=0.1g 
AUTHOR="Tsjerk A. Wassenaar, PhD"
YEAR="2008.xx"
AFFILIATION="
University of Utrecht\n
Padualaan 8\n
3584CH Utrecht\n
The Netherlands"

DESCRIPTION="\
"

pdb=in.pdb
cns=cns.pdb
psf=cns.psf
ext=ext.pdb
ann=ann.pdb
ref=h2o_%03d.pdb
ambre=""
unare=""
hbond=""
dihre=""
sym=
keepwater=
sel=""
n1=100
n2=50
cnsExec=

OPTIONS="
\t# File options:\n
\t  -f \t $pdb      Input coordinate file (PDB)\n
\t  -u \t $unare \t Unambiguous restraints file (TBL)\n
\t  -a \t $ambre \t Ambiguous restraints file (TBL)\n
\t  -b \t $hbond \t H-bonds file (TBL)\n
\t  -d \t $dihre \t Dihedral restraints file (TBL)\n
\t  -n1\t $n1    \t Number of structures to anneal\n
\t  -n2\t $n2    \t Number of structures to refine\n
\t  -x \t        \t Executable for processing CNS scripts (default: cns)
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
    -h)      echo -e $USAGE       ; exit 0 ;;
    # File options
    -f)      pdb=$2    ; shift 2; continue ;;
    -c)      cns=$2    ; shift 2; continue ;;
    -p)      psf=$2    ; shift 2; continue ;;
    -u)      unare=$2  ; shift 2; continue ;;
    -a)      ambre=$2  ; shift 2; continue ;;
    -b)      hbond=$2  ; shift 2; continue ;;
    -d)      dihre=$2  ; shift 2; continue ;;
    -g)      log=$2    ; shift 2; continue ;;
    -n1)     n1=$2     ; shift 2; continue ;;
    -n2)     n2=$2     ; shift 2; continue ;;
    -x)      cnsExec=$2; shift 2; continue ;;
    --sym)   sym=1     ; shift;   continue ;;
    --keepwater) keepwater=1; shift; continue ;;
     *)       BAD_OPTION $1;;
  esac
done

wd=`dirname $pdb`
pdb=`basename $pdb`
base=`basename $pdb .pdb`

# Passing through arguments
[[ $unare ]]          && unare="-u $unare"
[[ $ambre ]]          && ambre="-a $ambre"
[[ $dihre ]]          && dihre="-d $dihre"
[[ $hbond ]]          && hbond="-b $hbond"
[[ $sym == 1  ]]      && sym="--sym" 
[[ $keepwater == 1 ]] && keepwater="--keepwater"

restraints="$unare $ambre $dihre $hbond $sym"

cd $wd

# Try to set the CNS environment if no executable is given
if [ -z $cnsExec ]; then
  source $VO_ENMR_EU_SW_DIR/BCBR/cns/1.2-para/set_cns.bash
  cnsExec=`which cns`
fi

echo "Generating CNS structure and topology"
(source generate.sh  -f $pdb -p $base-cns.psf -o $base-cns.pdb -g 01-generate.log -x $cnsExec)
#echo "JFD mods 1: exit"
#exit 1

echo "Now generating extended structure"
(source extended.sh  -f $base-cns.psf -o $base-extended.pdb -g 02-extended.log -x $cnsExec)
#echo "JFD mods 2: exit"
#exit 1

echo -n "Simulated annealing of $n1 structures"
(source annealing.sh -f $base-extended.pdb -p $base-cns.psf -o $base-annealed-.pdb \
                     -g 03-annealing.log -n $n1 $restraints -x $cnsExec)
echo
#echo "JFD mods 3: exit"
#exit 1

echo % $base

echo "Violation analysis of annealed structures"
python violations.py 03-annealing.log > 03-violations.log

echo "Writing list of annealed structures, sorted on increasing potential energy"
#grep energies $base-annealed-*.pdb | sort -n +2 > $base-annealed.list
#echo "JFD mods 4: sort"
grep energies $base-annealed-*.pdb | sort -n --key=2 > $base-annealed.list

tar cfz run.tgz *

if [ $n2 -gt 0 ]; then
    echo "Refining $n2 best structures"
    echo % $base $base-annealed-*.pdb
    echo ###
    for ((i=1; i<=$n2; i++)); do
      ANN=`sed -ne ${num}s/:.*$//p $base-annealed.list`
      REF=${ANN/annealed/h2o-refined}
      (source h2o_refine.sh -f $ANN -p $base-cns.psf -o $REF -g ${REF%.pdb}.log -x $cnsExec $keepwater $restraints)
    done
    echo "Violation analysis of refined structures"
    python violations.py $base-refined-*.log > 04-violations.log
fi


