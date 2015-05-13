Directory Content

entryCodeListProteinsSite1  The entries for which validation is done at:
    http://proteins.dyndns.org/Education/Validation/index.html

PDB.LIS                     Contains the same entries as the What If database is
    basing it's quality scores on. It's generated in whatif by the command:
    DINDEX.
    Considering the size (469 chains) it must be like the culled dataset described
    below for R-factor<0.19 and Resolution<1.3 on February 28 2009.
    http://swift.cmbi.kun.nl/whatif/select/HTML/PDB.LIS-20090228-1.3-0.19
    Indeed, only 6 chains different!
    So it is not the set of 555 used before.

obsoleteSince2009-02-28.LIS
	25 entries that have since that time become obsolete

PDB_WI_SELECT_Rfactor0.21_Res2.0_2009-02-28_noObs.LIS
	Contains the set of chains for which the R factor is at least as good as 2.1 and
	the X-ray resolution is at least as good as 2.0 Angstrom. It was derived from
	the PDB on 2009-02-28. Finally, it excludes 25 entries that have since that time become obsolete.
	See above.
	The entries were determined simply by a script like:
	cing.Scripts.smallScriptCollection#findMissingCsv
	The original list came from: http://swift.cmbi.kun.nl/whatif/select/SELECT_2.html
	(Very hard to find; try from Gert's http://swift.cmbi.ru.nl/gv/start/)
	It is listed there as February 28 2009 hence the above date in the title.

PDB_WI_SELECT_Rfactor0.19_Res1.3_2009-02-28_noObs.LIS
	Excludes: 1f9y 2b3n 2ozi

PDB.LIS-20090228-2.0-0.21.txt
	The original list came from: http://swift.cmbi.kun.nl/whatif/select/SELECT_2.html