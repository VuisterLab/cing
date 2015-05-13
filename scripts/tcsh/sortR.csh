#!/bin/tcsh -f
# Author: Jurgen F. Doreleijers
# $CINGROOT/scripts/tcsh/sortR.csh

set fnIn = $1
set fnOut = $2

gawk 'BEGIN {srand()} {print int(rand()*99999) "\t" $0}' $fnIn | sort -n | cut -f 2- > $fnOut

set lineCount = (`wc $fnOut| gawk '{print $1}'`)

echo "Randomized $lineCount lines from $fnIn to $fnOut in lieu of sort -R"
