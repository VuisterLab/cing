-- * Run by command like:
-- python -u $CINGROOT/python/cing/NRG/runSqlForSchema.py nrgcing    $CINGROOT/python/cing/NRG/sql/loadDB-CING_psql.sql    $D/NRG-CING/pgsql

delete from casdcing.cingentry;

-- $cwd is replace by absolute path.
COPY casdcing.cingentry ( entry_id,name,bmrb_id,casd_id,pdb_id,is_solid,is_paramagnetic,is_membrane,is_multimeric,chothia_class,protein_count,dna_count,rna_count,dna_rna_hybrid_count,is_minimized,software_collection,software_processing,software_analysis,software_struct_solution,software_refinement,in_recoord,in_casd,in_dress,ranges,res_count,model_count,distance_count,dihedral_count,rdc_count,peak_count,cs_count,cs1h_count,cs13c_count,cs15n_count,wi_angchk,wi_bbcchk,wi_bmpchk,wi_bndchk,wi_c12chk,wi_chichk,wi_flpchk,wi_hndchk,wi_inochk,wi_nqachk,wi_omechk,wi_pl2chk,wi_pl3chk,wi_plnchk,wi_quachk,wi_ramchk,wi_rotchk,pc_gf,pc_gf_phipsi,pc_gf_chi12,pc_gf_chi1,noe_compl4,rog )
FROM '$cwd/casdcing.cingentry.csv' 	CSV HEADER;
COPY casdcing.cingchain 	FROM '$cwd/casdcing.cingchain.csv' 	 CSV HEADER;
COPY casdcing.cingresidue 	FROM '$cwd/casdcing.cingresidue.csv' CSV HEADER;
COPY casdcing.cingatom 		FROM '$cwd/casdcing.cingatom.csv' 	 CSV HEADER;