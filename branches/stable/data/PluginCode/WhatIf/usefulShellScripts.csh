# Some oneliners. Don't copy and paste unless you understand.

gawk '{printf("%4s,%8.3f,%8.3f,%4d\n", $3, $8, $9, $10)}' t.txt | sort -n -r --key=2 > t.csv


#Created by: phipsi_wi_db.csv.gz
cat */*/*.csv | gzip > ~/phipsi_wi_db.csv.gz
cat */*/*.csv | gzip > ~/chi1chi2_wi_db.csv.gz


grep "^ERROR" */*/*/*.log
grep "^ERROR" */*/*/*.log | cut -c1-7 | sort -u

# 73655 residues for chi1chi2
