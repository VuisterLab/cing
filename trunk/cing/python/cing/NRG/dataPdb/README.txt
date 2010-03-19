The optimalization needed to do all PDB entries instead of the NMR only is:

- Buy a 2 Tb disk?
- Include NMR related entries.
- Exclude many temporary files only saves 5 Mb on 47 Mb total for 1cjg for instance.
- Compression brings back 86 to 42 Mb (a factor of 2 only) because most is compressed image files anyway.
- Get WhatCheck results from e.g.:
	http://www.cmbi.ru.nl/pdbreport/d6/2d6p
	/mnt/structure_data/raw/pdbreport/d6/2d6p
	with files;
		check.db.bz2
		pdbout.txt


