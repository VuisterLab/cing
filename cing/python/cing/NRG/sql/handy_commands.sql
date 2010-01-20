select * from tmptable;

select * from entry;

UPDATE entry,tmpTable  SET entry.pdbx_SG_project_XXXinitial_of_center = tmpTable.par WHERE entry.pdb_id = tmpTable.pdb_id;

insert entry(pdb_id) values ('1brv'),('1sjg');
