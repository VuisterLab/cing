/*
	file:		util.c
	purpose:	to contain utility routines for vadar

	author:		leigh willard
	date:		4 August 1992
	place:		Protein Engineering Network of Centres of Excellence
				Department of Biochemistry
				University of Alberta
*/

#include "vmain.h"

int lastResNum; /* SJN */

#define SKIP -9

#define NAME_LOC 13
#define NAME_EXTRA_LOC 16
#define RES_LOC 17
#define CHAIN_LOC 21
#define RESNUM_LOC 23
#define RESNUM_EXTRA_LOC 26
#define COORD_LOC 30

char	lastExtra = '-';
char	resNumExtra;
int		lastresNum = -999;
int		resNumAdd;
int skip_res;
char skip_resextra;



/*.....................global variables................*/
int 	first,
		num_res;
char	defheld = '\0';
float	psiheld = 0,
		omegaheld = 0,
		rvalue = 0,
		chiheld = 0;
RESIDUE	resArray[MAX_RES_NUM];


/*...................procedure declarations...............*/
int		read_res(), 
		getNCO();
char	*read_pdb();
void	storecoords();
FILE	*create_file();



/*************************************************************
 * PURPOSE: to read in all residue information, for all residues
 * CALLER:  do_work (calc.c)
 */

void input_vadar()
{
int 	ret, counter = 0;
FILE	*pdbfp, *volfp, *areafp, *psfp, *def2fp;
int		resnum;


    pdbfp = fopen(pdbFname, "r");
    //volfp = fopen(vol_in, "r");
    //psfp = fopen(phipsi_in, "r");
    //def2fp = fopen(def2_in, "r");
    //areafp = fopen(area_in, "r");

    ret = read_res(&resArray[counter], 
		pdbfp, volfp, areafp, psfp, def2fp);
	resnum = resArray[counter].origResNum;	

    while ( ret != EOF ) {

        counter++;

		if (counter > MAX_RES_NUM) {
			printf("ERROR:  MAX_RES_NUM (set at %d) has been exceeded.\n", 
				MAX_RES_NUM);
			printf("        To increase MAX_RES_NUM, ");
			printf("change the src/libc/stdvadar.h file then recompile.\n");
			vadar_finish(FALSE);
			return;
		}

    	ret = read_res(&resArray[counter], 
			pdbfp, volfp, areafp, psfp, def2fp);
		if ( (!allChains) && (resArray[counter].origResNum < resnum) ) {
			break;
		}
		resnum = resArray[counter].origResNum;	
    }

    lastResNum = counter;

    fclose(pdbfp);
    //fclose(volfp);
    //fclose(psfp);
    //fclose(def2fp);
    //fclose(areafp);

}	/* input_vadar */


/*************************************************************
 * PURPOSE: read in one residue from the various input files 
 * PARMS:   residue to read into, file pointers
 */
int read_res(res, pdbfp, volfp, areafp, psfp, def2fp)
RESIDUE *res;
FILE	*pdbfp, *volfp, *areafp, *psfp, *def2fp;
{
int retpdb;
int	retarea, retvol, retpp, retdef2;

	//retarea = read_area(res, areafp);
	//retvol = read_vol(res, volfp);
	//retpp = read_phipsi(res, psfp);
	//retdef2 = read_define2(res, def2fp);

	/* read values from pdb file */
	retpdb = getpdb(res, pdbfp);

	/* return EOF (0) if any of the  files have reached EOF */
	/* SJN
	if ( (retvol == EOF) && (retpp == EOF) &&
		(retdef2 == EOF) && (retarea == EOF) && (retpdb == EOF) )
		return(EOF);
	*/
	if (retpdb == EOF) {
		return(EOF);
	}
	else {
		return(TRUE);
	}
}	/* read_res */



/*************************************************************
 * PURPOSE:	get one set of NOC coords (used by read_res)
 *          If this is a CYS, also get the SG coordinates.
 */
int getpdb(res, pdbfp)
RESIDUE *res;
FILE	*pdbfp;
{
ATOM_REC atom;
char    *line;
int		prevnum;
int		status;


	line = read_pdb(pdbfp, &atom, 1);
	prevnum = atom.resNum;
	while ( (line != NULL) && ( prevnum == atom.resNum ) ) {
		storecoords(atom, res);
		line = read_pdb(pdbfp, &atom, 1);
	}

	if (line == NULL)
		return(EOF);

	/* rewind the last line that was read */
	else {
		status = fseek(pdbfp, -1*strlen(line), 1); 
		if (status != 0) {
			printf("ERROR reading pdb file.  Unable to reposition.  Exiting\n");
			exit(-1);
		}
	}

	return(1);

}   /* getpdb */


/************************************************************************
* PURPOSE:	to read in any coordinates from pdb file that
*			will be needed later.
*/
void storecoords(atom, res)
ATOM_REC atom;
RESIDUE *res;
{
int	idx;

	if ((0 == strcmp(atom.atomName, "H")) || (0 == strcmp(atom.atomName, "HN")))
		idx = H_COORD;
	else if (0 == strcmp(atom.atomName, "N"))
		idx = N_COORD;
	else if (0 == strcmp(atom.atomName, "C"))
		idx = C_COORD;
	else if (0 == strcmp(atom.atomName, "O"))
		idx = O_COORD;
	else if (0 == strcmp(atom.atomName, "NH1"))
		idx = NH1_COORD;
	else if (0 == strcmp(atom.atomName, "NH2"))
		idx = NH2_COORD;
	else if (0 == strcmp(atom.atomName, "NZ"))
		idx = NZ_COORD;
	else if (0 == strcmp(atom.atomName, "NE"))
		idx = NE_COORD;
	else if (0 == strcmp(atom.atomName, "NE1"))
		idx = NE1_COORD;
	else if (0 == strcmp(atom.atomName, "NE2"))
		idx = NE2_COORD;
	else if (0 == strcmp(atom.atomName, "ND1"))
		idx = ND1_COORD;
	else if (0 == strcmp(atom.atomName, "ND2"))
		idx = ND2_COORD;
	else if (0 == strcmp(atom.atomName, "OD1"))
		idx = OD1_COORD;
	else if (0 == strcmp(atom.atomName, "OD2"))
		idx = OD2_COORD;
	else if (0 == strcmp(atom.atomName, "OE1"))
		idx = OE1_COORD;
	else if (0 == strcmp(atom.atomName, "OE2"))
		idx = OE2_COORD;
	else if (0 == strcmp(atom.atomName, "OG"))
		idx = OG_COORD;
	else if (0 == strcmp(atom.atomName, "OG1"))
		idx = OG1_COORD;
	else if (0 == strcmp(atom.atomName, "OH"))
		idx = OH_COORD;
	else if (0 == strcmp(atom.atomName, "CG"))
		idx = CG_COORD;
	else if (0 == strcmp(atom.atomName, "CD"))
		idx = CD_COORD;
	else if (0 == strcmp(atom.atomName, "SG"))
		idx = SG_COORD;
	else if (0 == strcmp(atom.atomName, "CZ"))
		idx = CZ_COORD;
	else if (0 == strcmp(atom.atomName, "CE"))
		idx = CE_COORD;
	else if (0 == strcmp(atom.atomName, "CB"))
		idx = CB_COORD;
	else return;

	res->chain = atom.chain;
	res->origResNum = atom.origResNum;
	res->coords[idx].x = atom.x;
	res->coords[idx].y = atom.y;
	res->coords[idx].z = atom.z;

}	/* storecoords */



/************************************************************************
 * read in area info
 */
int read_area(res, areafp)
RESIDUE *res;
FILE *areafp;
{
int retarea;
char line[MAX_LINE_LEN];

	if (areafp == NULL) {
		res->asa = 0.0;
		return(EOF);
	}

	retarea = fscanf(areafp, "%d%s%f", &res->resNum, res->name, &res->asa);
	while ( (retarea != EOF) && (retarea == 0) ) {
		fgets(line, MAX_LINE_LEN-1, areafp);
		retarea = fscanf(areafp, "%d%s%f", &res->resNum, res->name, &res->asa);
	}
	fgets(line, MAX_LINE_LEN-1, areafp);
	if (retarea == EOF) {
		strcpy(res->name, "n/a");
		res->resNum = -1;
		res->asa = 0.0;
	}	

	return(retarea);

}	/* read_area */



/************************************************************************
 * read in volume info
 */
int read_vol(res, volfp)
RESIDUE *res;
FILE *volfp;
{
int retvol;
char line[MAX_LINE_LEN];
	

    if (volfp == NULL) {
        res->vol = 0.0;
        return(EOF); 
    }

	retvol = fscanf(volfp, "%*d%*s%f", &res->vol);
	while ( (retvol!= EOF) && (retvol == 0) ) {
		fgets(line, MAX_LINE_LEN-1, volfp);
		retvol = fscanf(volfp, "%*d%*s%f", &res->vol);
	}
	fgets(line, MAX_LINE_LEN-1, volfp);
	if (retvol == EOF)
		res->vol = 0.0;

	return(retvol);

}	/* read_vol */



/************************************************************************
 * read phipsi info 
 * Phipsi may not match with the others, since ACE residues
 * are missing an N, so it is important to make sure that
 * the residues here match with the ones in area.
 */
int read_phipsi(res, psfp)
RESIDUE *res;
FILE *psfp;
{
int retpp;
int phinum;
char line[MAX_LINE_LEN];

    if (psfp == NULL) {
        res->phi = res->psi = res->omega = 0.0;
        return(EOF);
    }

	/* check to see if we have already read the input */
	if (phiheld != 0) {
		res->phi = phiheld;
		res->psi = psiheld;
		res->omega = omegaheld;
		res->chi = chiheld;
		phiheld = 0;
		retpp = 1;
	}

	/* otherwise read next line in */
	else {
		retpp = fscanf(psfp, "%d%*s%f%f%f%f", &phinum, 
		&res->phi, &res->psi, &res->omega, &res->chi);
		while ( (retpp != EOF) && (retpp == 0)) {
			fgets(line, MAX_LINE_LEN-1, psfp);
			retpp = fscanf(psfp, "%d%*s%f%f%f%f", &phinum, 
			&res->phi, &res->psi, &res->omega, &res->chi);
		}
		if (retpp == EOF)
			return(EOF);
		fgets(line, MAX_LINE_LEN-1, psfp);

		if (retpp != 5)
			res->chi = VOID;

		if (phinum != res->resNum) {
			phiheld = res->phi;
			psiheld = res->psi;
			omegaheld = res->omega;
			chiheld = res->chi;
			res->phi = res->psi = res->omega = 360.0;
			res->chi = VOID;
		}
		if (retpp == EOF) {
			res->phi = res->psi = res->omega = 360.0;
			res->chi = VOID;
		}
	}

	return(retpp);

}	/* read_phipsi */


/************************************************************************
 * read define2 info
 */
int read_define2(res, def2fp)
RESIDUE *res;
FILE *def2fp;
{
int retdef2, defnum;
char line[MAX_LINE_LEN];


    if (def2fp == NULL) {
        strcpy(res->dstruct2, "C");
        return(EOF); 
    }


	/* check to see if we have already read the input */
	if (defheld != '\0') {
		res->dstruct2[0] = defheld;
		res->dstruct2[1] = '\0';
		defheld = '\0';
		retdef2 = 1;
	}


	else {
		retdef2 = fscanf(def2fp, "%d%*s%s", &defnum, res->dstruct2);
		while ( (retdef2 != EOF) && (retdef2 == 0) ) {
			fgets(line, MAX_LINE_LEN-1, def2fp);
			retdef2 = fscanf(def2fp, "%d%*s%s", &defnum, res->dstruct2);
		}
		if (retdef2 == EOF)
			return(EOF);
		fgets(line, MAX_LINE_LEN-1, def2fp);

		if (defnum != res->resNum) {
			defheld = res->dstruct2[0];
			strcpy(res->dstruct2, "C");
		}

		if (first)
			strcpy(res->dstruct2, "C");
		first = FALSE;
		if (retdef2 == EOF)
			strcpy(res->dstruct2, "C");
	}

	return(retdef2);

}	/* read_define2 */



/****************************************************************/
/* get next CA value from pdb file
*
*/
get_input_def1()
{
int         i = 0;
char 		*ret;
ATOM_REC    atom;
FILE		*pdbfp;

    pdbfp = fopen(pdbFname, "r");
	if (pdbfp == NULL) {
		printf("ERROR:  cannot open parameter file\n");
		vadar_finish(TRUE);
	}

    ret  = read_pdb(pdbfp, &atom, 0);
    while (ret != NULL) {

        if (strcmp(atom.atomName, "CA") == 0) {
            strcpy(struc[i].name, atom.resName);
            struc[i].num = atom.resNum;
						struc[i].chain = atom.chain;
            struc[i].x = atom.x;
            struc[i].y = atom.y;
            struc[i].z = atom.z;
            i++;
						if (i > MAX_RES_NUM) {
							printf("ERROR:  MAX_RES_NUM (set at %d) has been exceeded.\n", 
							MAX_RES_NUM);
							printf("        To increase MAX_RES_NUM, ");
							printf("change the src/libc/stdvadar.h file then recompile.\n");
							vadar_finish(TRUE);
						}
				}
		    ret  = read_pdb(pdbfp, &atom, 0);
		}
		num_res = i;
		fclose(pdbfp);

}   /* get_input_def1 */


/***************************************************************************
* PURPOSE:	to print for the user a list of all output files created.
*/
void print_output_fnames()
{

	if (bigfile) {
    	printf("\t%s\n", resultsFname);
	}

	if (! bigfile ) {
		printf("\t%s.main\n", resultsFname);
		printf("\t%s.side\n", resultsFname);
		printf("\t%s.bond\n", resultsFname);
		printf("\t%s.stats\n", resultsFname);
	}

    if (graphDisplay == 1) {
		printf("\t%s.mol\n", resultsFname);
	}

    if (graphDisplay == 2) {
		printf("\t%s.ss\n", resultsFname);
	}

    if (atomDisplay) {
		printf("\t%s.areaatom\n", resultsFname);
		printf("\t%s.volatom\n", resultsFname);
    }

}	/* print_output_fnames */


/***************************************************************************
* PURPOSE: 	to check for the existance of a file
*/
void check_exist(suffix, exists)
char *suffix;
char *exists;
{
char fname[MAX_LINE_LEN];

	sprintf(fname, "%s%s", resultsFname, suffix);

	if (checkExist(fname))
		sprintf(exists+strlen(exists), "        %s\n", fname);

}	/* check_exist */


/***************************************************************************
* PURPOSE:	to check to see which output files already exist.
*/
int check_existing()
{
char exists[MAX_LINE_LEN*10];

	exists[0] = '\0';

	if (bigfile)
		check_exist("", exists);
	else {
		check_exist(".main", exists);
		check_exist(".side", exists);
		check_exist(".bond", exists);
		check_exist(".stats", exists);
	}
	if (graphDisplay == 1)
		check_exist(".mol", exists);
    if (graphDisplay == 2)
		check_exist(".ss", exists);
    if (atomDisplay) {
		check_exist(".areaatom", exists);
		check_exist(".volatom", exists);
	}

	if (exists[0] != '\0') {
		printf("\n    These file(s) already exist:\n%s", exists);
		printf(">>  Okay to overwrite them? (y/n) ");
		gets(exists);	
		gets(exists);	
		if ( (exists[0] == 'n') || (exists[0] == 'N') )
			return(-1);
	}

	return(0);

}	/* check_existing */


/************************************************************************
* PURPOSE:	to open the output files.
*/
void open_output_files()
{
char fname[MAX_LINE_LEN];

	if (bigfile) {
		outfp[0] = outfp[1] = outfp[2] = outfp[3] = fopen(resultsFname, "w");
		if (outfp[0] == NULL) {
			printf("ERROR: cannot open output file %s.\n", resultsFname);
			exit(-1);
		}
	}

	else {
		sprintf(fname, "%s.main", resultsFname);
		outfp[FPMAIN] = fopen(fname, "w");
		if (outfp[FPMAIN] == NULL) {
			printf("ERROR: cannot open output file %s.\n", fname);
			exit(-1);
		}

		sprintf(fname, "%s.side", resultsFname);
		outfp[FPSIDE] = fopen(fname, "w");
		if (outfp[FPSIDE] == NULL) {
			printf("ERROR: cannot open output file %s.\n", fname);
			exit(-1);
		}

		sprintf(fname, "%s.bond", resultsFname);
		outfp[FPBOND] = fopen(fname, "w");
		if (outfp[FPBOND] == NULL) {
			printf("ERROR: cannot open output file %s.\n", fname);
			exit(-1);
		}

		sprintf(fname, "%s.stats", resultsFname);
		outfp[FPSTATS] = fopen(fname, "w");
		if (outfp[FPSTATS] == NULL) {
			printf("ERROR: cannot open output file %s.\n", fname);
			exit(-1);
		}

		sprintf(fname, "%s.mol", resultsFname);
		outfp[FPMOL] = fopen(fname, "w");
		if (outfp[FPMOL] == NULL) {
			printf("ERROR: cannot open output file %s.\n", fname);
			exit(-1);
		}
	}

}	/* open_output_files */


/*************************************************************/
/* setup output file
*/
int set_output_fp()
{
int ret;


    /* get name of file*/
    printf(">>  Enter basename for output files: ");
    fscanf(stdin, "%s", resultsFname);

    printf("\n    Output file(s) created will be:\n");
	print_output_fnames();
	

	ret = check_existing();

	open_output_files();

    return(ret);

}   /* get_output_fp */


/*********************************************************************
* PURPOSE:  to find the r value from the comments of the pdb file.
*/
void get_rvalue(pdbfp)
FILE *pdbfp;
{
char line[MAX_LINE_LEN];
char *idx = 0;

    fgets(line, MAX_LINE_LEN-1, pdbfp);

    idx = strstr(line, "R VALUE IS");
    if (idx) {
        sscanf(idx, "%*s%*s%*s%f", &rvalue);
        return;
    }

    idx = strstr(line, "VALUE IS");
    if (idx) {
        sscanf(idx, "%*s%*s%f", &rvalue);
        return;
    }

    idx = strstr(line, "R VALUE OF");
    if (idx) {
        sscanf(idx, "%*s%*s%*s%f", &rvalue);
        return;
    }

    idx = strstr(line, "R VALUE");
    if (idx) {
        sscanf(idx, "%*s%*s%f", &rvalue);
        return;
    }

}   /* get_rvalue */



/*************************************************************/
/* read one atom from pdb file, excluding H atoms
*/
char *read_pdb(pdbfp, atom, hflag) 
FILE 		*pdbfp;
ATOM_REC	*atom;
int hflag;
{
int ret;
char line[MAX_LINE_LEN];

	ret = read_one_pdb(pdbfp, atom, line);
	if (hflag)
		while ((ret != NULL) && (ret == SKIP) )
			ret = read_one_pdb(pdbfp, atom, line);

	else
		while ((ret != NULL) && ((ret == SKIP) || (atom->atomName[0] == 'H')) )
			ret = read_one_pdb(pdbfp, atom, line);

	if (ret == NULL)
		return(NULL);
	else return(line);

}	/* read_pdb */


/***************************************************************************
* PURPOSE:  to read one atom record (line) from the pdb file
*/
int read_one_pdb(pdbfp, atom, line)
FILE 		*pdbfp;
ATOM_REC	*atom;
char 		*line;
{
char *ret;
static float Nx, Ny, Nz;


	/* read one line in */

	ret = fgets(line, MAX_LINE_LEN-1, pdbfp);
	while ( 0 != strncmp(line, "ATOM", 4) ) {
		if (ret == NULL)
			return(NULL);
		ret = fgets(line, MAX_LINE_LEN-1, pdbfp);
	}
	if (ret == NULL)
		return(NULL);

	/* atom name */

	sscanf(line+NAME_LOC, "%3s", atom->atomName); 
	if (strcmp(atom->atomName, "AE1") == 0) strcpy(atom->atomName, "OE1");
	if (strcmp(atom->atomName, "AE2") == 0) strcpy(atom->atomName, "NE2");
	if (strcmp(atom->atomName, "AD1") == 0) strcpy(atom->atomName, "OD1");
	if (strcmp(atom->atomName, "AD2") == 0) strcpy(atom->atomName, "ND2");
	/* this is a check for an atom name of the form NNNX, where
	 * NNN is the atom name, and X is a character (A or B) only
	 * the A atoms should be read (the B's are duplicates)
     */
	if ( (line[NAME_EXTRA_LOC] != ' ') && (line[NAME_EXTRA_LOC] != 'A') )
		return(read_one_pdb(pdbfp, atom, line));
	/* also ignore hydrogen atom's - those starting with H */
	if (line[NAME_LOC-1] == 'H')
		return(read_one_pdb(pdbfp, atom, line));


	/* residue name */
	sscanf(line+RES_LOC, "%3s", atom->resName); 


	/* chain indicator */
	sscanf(line+CHAIN_LOC, "%c", &atom->chain);


	/* x, y, and z coordinates */
	sscanf(line+COORD_LOC,  "%f%f%f", &(atom->x), &(atom->y), &(atom->z));


	if (SKIP == get_res_num(line, atom, Nx, Ny, Nz))
		return(SKIP);


	if (strcmp(atom->atomName, "N") == 0) {
		Nx = atom->x;
		Ny = atom->y;
		Nz = atom->z;
	}

	return(1);

}	/* read_one_pdb */



int get_res_num(line, atom, Nx, Ny, Nz)
char		*line;
ATOM_REC	*atom;
float Nx, Ny, Nz;
{


	sscanf(line+RESNUM_LOC, "%d", &atom->origResNum); 
	atom->resNum = atom->origResNum;


	/* there may be a character here.  This happens when an extra res
	 * is added to the pdb file, but instead of renumbering the file,
	 * a character such as A is added to the res num.  But, we must
	 * renumber the pdb file if this happens, for the programs to run.
	 * It is also possible that this is a duplicate residue (alternate).
	 * If so, it will have the same coordinates as the previous residue,
	 * and then this residue should be discarded.
	 */
	resNumExtra = line[RESNUM_EXTRA_LOC];
	if ( (resNumExtra != lastExtra ) && (lastExtra != '-') &&
		(atom->resNum == lastresNum) ) {
		if (duplicate_res(atom, Nx, Ny, Nz)) {
			return(SKIP);
		}
		else resNumAdd++;
	}
	lastExtra = resNumExtra;
	lastresNum = atom->resNum;
	atom->resNum += resNumAdd;

	return(1);

}	/* get_res_num */


int duplicate_res(atom, Nx, Ny, Nz)
ATOM_REC *atom;
float Nx, Ny, Nz;
{

	if ( (atom->x == Nx) && (atom->y == Ny) && (atom->z == Nz) ) {
		skip_res = atom->resNum;
		skip_resextra = resNumExtra;
		return(TRUE);
	}

	if ( (atom->resNum == skip_res) && (resNumExtra == skip_resextra) ) {
		return(TRUE);
	}
	return(FALSE);

}	/* duplicate_atom */


/*************************************************************/
/* check to see if a file exists
*/
int checkExist(fname)
char    *fname;
{
FILE    *fp;

	fp = fopen(fname, "r");
	if ( fp  == NULL )
		return(FALSE);
	fclose(fp);
	return(TRUE);

}	/* check_exist */


/*********************************************************************
 * PURPOSE: assign the structure fo residue.
 */
void assignSS(residx, type, value)
int residx, type;
char *value;
{

	switch (type) {
		case 0: strcpy(resArray[residx].dstruct1, value); break;
		case 1: strcpy(resArray[residx].dstruct2, value); break;
		case 2: strcpy(resArray[residx].dstruct3, value); break;
		case 3: strcpy(resArray[residx].consens, value); break;
	}

}	/* assignSS */


int getType(resx, type)
RESIDUE resx;
int type;
{
int ret;

	switch (type) {
		case 0: ret = strcmp(resx.dstruct1, "H") == 0 ? HELIX : 
			( ret = strcmp(resx.dstruct1, "B") == 0 ? BETA : COIL ) ;
			break;
		case 1: ret = strcmp(resx.dstruct2, "H") == 0 ? HELIX : 
			( ret = strcmp(resx.dstruct2, "B") == 0 ? BETA : COIL ) ;
			break;
		case 2: ret = strcmp(resx.dstruct3, "H") == 0 ? HELIX : 
			( ret = strcmp(resx.dstruct3, "B") == 0 ? BETA : COIL ) ;
			break;
		case 3: ret = strcmp(resx.consens, "H") == 0 ? HELIX : 
			( ret = strcmp(resx.consens, "B") == 0 ? BETA : COIL ) ;
			break;
	}

	return(ret);

}	/* getType */

int vadar_finish(int what)
{
	exit(0);  /* SJN */
}