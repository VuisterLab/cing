#!/bin/tcsh -f

# Removing imagery, mac os hidden files from project file
# Watch out when modifying this command
# Execute like:
# $CINGROOT/scripts/cing/cleanCingProject.csh
find .\
-name "*.pdf"\
 -or -name "*.gif"\
 -or -name "*.png"\
 -or -name "*.jpg"\
 -or -name "*.ps"\
 -or -name "._*"\
| xargs rm

exit 0

# Junk follows after the above exit
set list = ( 1i1s 1ka3 1tgq 1y4o )
foreach x ( $list )
    echo "Doing $x"
    tar -czf $x.cing.tgz $x.cing
end