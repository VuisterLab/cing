
/*
	file: calc.c
	contains calculation routines for define1 
*/


#include "vmain.h"
#include <sys/types.h>
#include <malloc.h>
#include <math.h>

/*................global variables.................*/
DEF_REC	struc[MAX_RES_NUM];
double	hmask[LEN_HELIX_MASK];
double	bmask[LEN_BETA_MASK];


/*..................procedure declarations..................*/
static	double get_dist(), 
		get_rmsd();
void	get_input_def1(), 
		get_ca_dist(),
		post_check();


/***********************************************************************/
/* Main calculation loop
*/
void define1()
{
double *ca_matrix;
int i;

	get_input_def1();
	for (i=0; i<MAX_RES_NUM; i++) {
		struc[i].type = COIL;
	}

	ca_matrix = (double *) calloc (sizeof(double), num_res*num_res);
	if (ca_matrix == NULL) {
		perror("Not enough memory.");
		vadar_finish(TRUE);
	}

	get_ca_dist(ca_matrix);

	check_helix(ca_matrix);

	check_beta(ca_matrix);

	post_check();

	for (i=0; i<MAX_RES_NUM; i++) {
		switch(struc[i].type) {
			case HELIX: strcpy(resArray[i].dstruct1, "H"); break;
			case BETA: strcpy(resArray[i].dstruct1, "B"); break;
			case COIL: strcpy(resArray[i].dstruct1, "C"); break;
		}
	}

	free(ca_matrix);

}	/* do_define1 */



/***********************************************************************
* Get a distance matrix of every CA to all other CAs
*/
void get_ca_dist(ca_matrix)
double ca_matrix[];
{
int i, j;

	for (i=0; i<num_res; i++)
		for (j=i+1; j<num_res; j++)

			ca_matrix[i*num_res + j] = get_dist(i,j);

}	/* get_ca_dist */



/***********************************************************************
* Get distance between two points
*/
static double get_dist(indxi, indxj)
{
double distx, disty, distz;
double distance;

	distx = ABS(struc[indxi].x - struc[indxj].x);
	disty = ABS(struc[indxi].y - struc[indxj].y);
	distz = ABS(struc[indxi].z - struc[indxj].z);

	distance = sqrt( pow(distx,(double)2)+
		pow(disty,(double)2)+
		pow(distz,(double)2) );

	return(distance);
	
}	/* get_dist */


/***********************************************************************
* using the ca matrix, use a mask to see if a helix is present. 
*/
check_helix(ca_matrix )
double ca_matrix[];
{
int i, k;
double rmsd;


	for (i=0; i<(num_res-LEN_HELIX_MASK+1); i++) {
		rmsd = get_rmsd(ca_matrix, hmask, LEN_HELIX_MASK, i*num_res + i);

		if (rmsd < helix_rmsd) {
			for (k=i; k<i+LEN_HELIX_MASK; k++) {
				struc[k].type = HELIX;
				ca_matrix[i*num_res + k] = 0;
			}
		}
	}

}	/* check_helix */


/***********************************************************************
* using the ca matrix, use a mask to see if a beta is present. 
*/
check_beta(ca_matrix)
double ca_matrix[];
{
double	betaMatrix[LEN_BETA_MASK];
double	rmsd;
int		i, j, k;
int		iloc, jloc;


	/* traverse the diagonal parallel */
	for (i=0; i+LEN_BETA_MASK<=num_res; i++) {
		for (j=NUM_SKIP+i; j+LEN_BETA_MASK<=num_res; j++) {

			for (k=0; k<LEN_BETA_MASK; k++) {
				iloc = i+k;
				jloc = j+k;
				betaMatrix[k] = ca_matrix[iloc*num_res+jloc];
			}

			rmsd = get_rmsd(betaMatrix, bmask, LEN_BETA_MASK, 0);

			/* set residues to BETA */
			if (rmsd <= beta_rmsd) {
				for (k=0; k<LEN_BETA_MASK; k++) {
					struc[i+k].type = BETA;
					struc[j+k].type = BETA;
				}
			}
		}
	}

	/* this code is repeat mostly, but it would be too confusing
	 * to have another level of indirection with a subroutine    */

	/* traverse the diagonal anti-parallel */
	for (i=0; i+LEN_BETA_MASK<num_res; i++) {
		for (j=NUM_SKIP+LEN_BETA_MASK+i; j<num_res; j++) {

			for (k=0; k<LEN_BETA_MASK; k++) {
				iloc = i + k;
				jloc = j + (-1 * k);
				betaMatrix[k] = ca_matrix[iloc*num_res+jloc];
			}

			rmsd = get_rmsd(betaMatrix, bmask, LEN_BETA_MASK, 0);

			/* set residues to BETA */
			if (rmsd <= beta_rmsd) {
				for (k=0; k<LEN_BETA_MASK; k++) {
					struc[i + k].type = BETA;
					struc[j + (-1*k)].type = BETA;
				}
			}
		}
	}


}	/* check_beta */


/***********************************************************************
* get the rms deviation between the mask and the array segment
*/
static double get_rmsd(ca_matrix, mask, maskLen, idx)
double ca_matrix[];
double mask[];
int maskLen;
int idx;
{
int k;
double rmsd;
double sum = 0;

	for (k=0; k<maskLen; k++) 
		sum += ABS(ca_matrix[idx+k] - mask[k]);

	rmsd = sum / maskLen;
	
	return(rmsd);

}	/* get_rmsd */


/***********************************************************************
* PURPOSE:	to check that if phi angle > 0 then it can not be a helix,
*			and if 0 < phi < 160 it can not be a beta.
*/
void post_check()
{
int i;

	for (i=0; i<MAX_RES_NUM; i++) {
		if ( (struc[i].type == HELIX) && (resArray[i].phi > 0.0) )
			struc[i].type = COIL;
		if ( (struc[i].type == HELIX) && 
			( (resArray[i].psi > 110) || (resArray[i].phi < -110.0) ) )
			struc[i].type = COIL;
		if ( (struc[i].type == BETA) && (resArray[i].phi > 0.0) &&
			(resArray[i].phi < 160.0) )
			struc[i].type = COIL;
	}

}	/* post_check */
