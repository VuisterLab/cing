#!/bin/tcsh
# Author: Jurgen F. Doreleijers
# $C/scripts/vcing/cleanVC
# NB do not run this code on machines other than VC.

echo "Starting $C/scripts/vcing/cleanVC"
cd
\rm ls2*.tgz ls.log ls2.log
\rm startVC_2012*.log
\rm syncVCcode_*.log
cd tmp/cingTmp
\rm *_testCing_*.log
\rm vCing_*.log
echo "Finished"

