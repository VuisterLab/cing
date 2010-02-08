	--table=brief_summary \
	exptl/@method
	--table='*initial_of_center' \

pg_dump \
	--no-owner \
	--no-tablespaces \
	--table='*initial_of_center' \
	--table='*initial_of_center' \
	--file=pdbj2nrgcing.dump \
	-n pdbj -U pdbj pdbmlplus

-- ignore the warnings
cat pdbj2nrgcing.dump | psql nrgcing nrgcing1

