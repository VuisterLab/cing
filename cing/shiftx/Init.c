/*
	file: 		init.c
	purpose:	set up variables, read in parameter file for vadar 

*/


#include <stdlib.h>
#include "vmain.h"


/*...................global variables..................*/
int		interactive, statsType, 
		radType, hDisplay, 
		mainDisplay, sideDisplay, 
		statsDisplay, graphDisplay,
		qualityDisplay, atomDisplay, 
		bigfile,
		allChains, hbond_angle, hbondsH2O;
double	hbond_dist, hbond_dist2, 
		sidebond_dist, ssbond_dist,
		beta_rmsd, helix_rmsd;



/*................procedure calls..................*/
extern	FILE *get_parms_file();
void 	read_parms_file(),
		find_lib();



/*********************************************************************
 * PURPOSE: obtain the parameter file and read it. 
 * CALLER:  setup_vadar (main.c), do_vadar (calc.c)
 */
void init_parms()
{
FILE 	*parmsfp;
char parmVer[MAX_LINE_LEN];
char errstr[MAX_LINE_LEN];


	find_lib();

	parmsfp = get_parms_file(parmsFname);
	if (parmsfp == NULL) {
		printf("ERROR:  cannot find parameter file\n");
		vadar_finish(TRUE);
	}

	/* make sure the parameter file is the correct version */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Could not find parameter file version.");
	fscanf(parmsfp, "%s", parmVer);
	if ( 0 != strcmp(parmVer, PARM_VERSION) ) {
		sprintf(errstr, "Your parameter file, version %s, is out of date.\n",
		parmVer);
		strcat(errstr, "             The current version is ");
		strcat(errstr, PARM_VERSION);
		show_err(TRUE, "vadar.parms", errstr);
	}

	read_parms_file(parmsfp);
	fclose(parmsfp);

}	/* init_parms */


/*********************************************************************
 * PURPOSE: Read each parameter.
 * CALLER:  init_parms
 */
void read_parms_file(parmsfp)
FILE *parmsfp;
{
	char	maskName[MAX_LINE_LEN];
	int		i;

	/* get interactive flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &interactive);

	/* get hydrogen display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &hDisplay);

	/* get main chain display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &mainDisplay);

	/* get side chain display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &sideDisplay);

	/* get quality display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &qualityDisplay);

	/* get stats display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &statsDisplay);

	/* get graphical display flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &graphDisplay);

	/* get area/volume atom output flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &atomDisplay);

	/* get allchains flag.  0 means that only the first chain is processed */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &allChains);

	/* get bigfile flag. */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &bigfile);

	/* get hbonds to water flag */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &hbondsH2O);

	/* get hbond distance */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%lf", &hbond_dist);

	/* get hbond angle */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &hbond_angle);

	/* get second distance check */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%lf", &hbond_dist2);

	/* get ssbond distance */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%lf", &ssbond_dist);

	/* get sidechain bond distance */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%lf", &sidebond_dist);

	/* get vanderwaals radius type */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &radType);

    /* masks for identifying secondary structure */
    for (i = 0; i<2; i++) {
        if (read_prompt(parmsfp) == FALSE)
            show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
        fscanf(parmsfp, "%s", maskName);
        if ( strcmp(maskName, "BETA") == 0)
            fscanf(parmsfp, "%lf%lf%lf", &bmask[0], &bmask[1], &bmask[2]);
        else if ( strcmp(maskName, "HELIX") == 0)
            fscanf(parmsfp, "%lf%lf%lf%lf%lf", &hmask[0], &hmask[1],
            &hmask[2], &hmask[3], &hmask[4]);
        else show_err(TRUE, VAD_MODULE, "Could not find BETA/HELIX MASKS.");
    }

    /* rmsd errors */
    for (i=0; i<2; i++) {
        if (read_prompt(parmsfp) == FALSE)
            show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
        fscanf(parmsfp, "%s", maskName );
        if ( strcmp(maskName, "BETA_RMSD") == 0)
            fscanf(parmsfp, "%lf", &beta_rmsd);
        else if ( strcmp(maskName, "HELIX_RMSD") == 0)
            fscanf(parmsfp, "%lf", &helix_rmsd);
        else show_err(TRUE, VAD_MODULE, "Could not find BETA/HELIX RMSD's.");
    }

	/* get type of stats definitions */
	if (read_prompt(parmsfp) == FALSE)
		show_err(TRUE, VAD_MODULE, "Parameter expected but not found.");
	fscanf(parmsfp, "%d", &statsType);


}	/* read_parms_file */
