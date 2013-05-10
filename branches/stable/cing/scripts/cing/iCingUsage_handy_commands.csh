# Do not use this code but take the python code in: $C/python/cing/Scripts/interactive/getDatesIcingRuns.py

#
# As root on nmr using tcsh.
# 
set localDir = ~i/confidential/iCingUsage

cd $D/tmp/cing
ls -l * | gawk '{if (NF=8) print $(NF-2) }' | sort -n | gawk '{if ($1!="") print}' > $localDir/t.txt

cd ano
find . -name "*.cing" -maxdepth 2 | cut -c10- | sed -e 's/.cing//' 	> $localDir/iCingProjectList.txt
sort -u $localDir/iCingProjectList.txt > $localDir/iCingProjectListUnique_2012-01-12.txt


# As jd on stella
cd $C/scripts/cing/iCingUsage/
scp i@nmr.cmbi.ru.nl:/home/i/confidential/iCingUsage/t.txt .

# Now process with Numbers file located in this directory.
# Using =FREQUENCY(C,E2:E24)

