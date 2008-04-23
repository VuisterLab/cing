# Some oneliners. Don't copy and paste unless you understand.

gawk '{printf("%4s,%8.3f,%8.3f,%4d\n", $3, $8, $9, $10)}' t.txt | sort -n -r --key=2 > t.csv
