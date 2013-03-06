#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include "psa.h"
#include "main.h"
/*
#include "states.h"
#include "cs.h"
#include "nn.h"
#include "ssbond.h"
#include "residue.h"
#include "hetatm.h"
#include "vector.h"
#include "phipsi.h"
#include "torison.h"
#include "hydrogens.h"
#include "rings.h"
#include "es.h"
#include "proline.h"
#include "hbond.h"
#include "optimize.h"										
#include "display.h"
#include "chi.h"
*/

void define1(RESIDUE rz[]);
void get_ca_dist(RESIDUE rz[],double ca_matrix[]);
static double get_dist(RESIDUE rz[],int indxi,int indxj);
void post_check(RESIDUE rz[]);
static double get_rmsd(double ca_matrix[], double mask[], int maskLen, int idx);
void check_beta(RESIDUE rz[],double ca_matrix[]);
void check_helix(RESIDUE rz[],double ca_matrix[]);
void hbond(RESIDUE *res, int resIdx,RESIDUE resArray[]);
int getHbondIndex(float newDist,BOND_REC bondrec[MAX_HBONDS]);
float v_get_dist(float onex,float oney,float onez,float twox,float twoy,float twoz);
void calc_hcoords(RESIDUE resArray[]);
float get_energy(RESIDUE *res1,RESIDUE *res2);
void check_mainsidebond(int didx, int dneighbour, int donor, int aidx, int acceptor, int aneighbour,RESIDUE resArray[]);
void getall_sbond(int idx,RESIDUE resArray[]);
void check_sidebond(int didx, int dneighbour, int donor, int aidx,int acceptor, int aneighbour,RESIDUE resArray[]);
void calc_bturn(RESIDUE resArray[]);
void check_ho_bond(int didx,int donor,int dneighbour,void (*bond_check)(),RESIDUE resArray[]);
void pickType(int val1_1, int val2_1, int val1_3, int val2_3, int index, char *type1, char *type3,RESIDUE resArray[]);
int checkType(int val1,int val2,int val3,int val4,int val5,int indx,char *bturn_type,int bounds[5],RESIDUE resArray[]);
void store_dist(float dist, int didx, int aidx, int donor, int neighbour,int acceptor,int aneighbour,RESIDUE resArray[]);
float angle(RESIDUE rec1,int vec1a,int vec1b, RESIDUE rec2,int vec2a,int vec2b);
void define3(RESIDUE resArray[]);
void assign_define3(RESIDUE resArray[]);
int get_beta(int residx,float phi,RESIDUE resArray[]);
int old_get_beta(int i, float phi,float psi,float lastphi,RESIDUE resArray[]);
void smooth_define3(RESIDUE resArray[]);
void smooth_helix(RESIDUE resArray[]);
void smooth_beta(RESIDUE resArray[]);
void filter_define3(RESIDUE resArray[]);
void do_consensus(RESIDUE resArray[]);
void bturn_ss(RESIDUE resArray[]);
void check_turn(int i,char *bturn,RESIDUE resArray[]);
void smooth_ss(RESIDUE resArray[]);
void do_consens_caps(int i,RESIDUE resArray[]);
void do_consens_bridge(int i,RESIDUE resArray[]);
int hbonded(int i,RESIDUE resArray[]);
void assignSS(int residx,int type,char *value,RESIDUE resArray[]);
int legitBond(RESIDUE residue,RESIDUE resArray[], int bondType);
int getType(RESIDUE resx,int type);
void do_define2(RESIDUE resArray[]);



#define COIL 0
#define BETA 1
#define HELIX 2
#define TURN 3
#define ALSO_HELIX 4
#define ALSO_BETA 5

#define DSTR(x)( strcmp(x.dstruct3, "H") == 0 ? HELIX : ( strcmp(x.dstruct3, "B") == 0 ? BETA : COIL) )


#define NUM_SKIP        5
#define LEN_HELIX_MASK  5
#define LEN_BETA_MASK 3

#define hbond_dist 3.5
#define hbond_angle 90
#define hbond_dist2 2.5
#define sidebond_dist 3.5

#define DONOR 1
#define ACCEPTOR 2

#define RAD(x)	x*M_PI/180
#define DEG(x)	x*180/M_PI

#define ABS(x)( (x)<0 ? -(x) : (x))
#define IN(x, target, range) ( (x >= (target - range)) && (x <= (target + range)) )



#ifdef _WIN32        /* SJN */
 #include "direct.h" /* SJN */
#else                /* SJN */
 #include <unistd.h> /* SJN */
#endif


static int num_res;
double	hmask[LEN_HELIX_MASK] = {0,3.75,5.36,5.02,6.11};
double	bmask[LEN_BETA_MASK] = {4.95,4.95,4.95};
double helix_rmsd = 0.22;
double beta_rmsd = 0.6;

void do_ss(RESIDUE rz[],int rno)
{
	int i,j;

	num_res = rno + 1;   // SJN: added offset of one


	calc_hcoords(rz);

	/*
	if (hbondsH2O)
	{
		read_H2O();
	}
	*/
	for (i=0; i < rno; i++) 
	{
		hbond(&rz[i], i,rz);
		getall_sbond(i,rz);
		/*
		if (hbondsH2O)
		{
			check_hbonds_water(i);
		}
		*/
	}

   calc_bturn(rz);


//	input_vadar();
		
    /*  calculate secondary structure using masks */
    define1(rz);

		do_define2(rz);
    /* calculate secondary structure, using hbond information */
    define3(rz); 

    /* calculate consensus secondary structure */
    do_consensus(rz);	

    /* incorporate the bturn info into the secondary structures */
    bturn_ss(rz);

    /* smooth all secondary structures */
    smooth_ss(rz);

}   /* do_ss */


void define1(RESIDUE rz[])
{
	double *ca_matrix;
	int i;

	/*get_input_def1();*/
	for (i=0; i<num_res; i++) {
		rz[i].ss = COIL;
	}

	ca_matrix = (double *) calloc (sizeof(double), num_res*num_res);

	if (ca_matrix == NULL) {
		fprintf(stderr,"Not enough memory for SS matrix.");
		exit(0);
	}

	get_ca_dist(rz,ca_matrix);

	check_helix(rz,ca_matrix);

	check_beta(rz,ca_matrix);

	post_check(rz);
	
	
	for (i=0; i<num_res; i++) {
		switch(rz[i].ss) {

		case HELIX:
			strcpy(rz[i].dstruct1, "H");
			break;

		case BETA:
			strcpy(rz[i].dstruct1, "B");
			break;

		case COIL:
			strcpy(rz[i].dstruct1, "C"); 
			break;
		}
	}
	
	free(ca_matrix);

}	/* do_define1 */



/***********************************************************************
* Get a distance matrix of every CA to all other CAs
*/
void get_ca_dist(RESIDUE rz[],double ca_matrix[])
{
int i, j;

	for (i=0; i<num_res; i++)
		for (j=i+1; j<num_res; j++)

			ca_matrix[i*num_res + j] = get_dist(rz,i,j);

}	/* get_ca_dist */



/***********************************************************************
* Get distance between two points
*/
static double get_dist(RESIDUE rz[],int indxi,int indxj)
{
	double distx, disty, distz;
	double distance;
						
	distx = fabs(rz[indxi].x - rz[indxj].x);
	disty = fabs(rz[indxi].y - rz[indxj].y);
	distz = fabs(rz[indxi].z - rz[indxj].z);

	distance = sqrt( pow(distx,(double)2)+
	 pow(disty,(double)2)+
	 pow(distz,(double)2) );

	return(distance);
	
}	/* get_dist */


/***********************************************************************
* using the ca matrix, use a mask to see if a helix is present. 
*/
void check_helix(RESIDUE rz[],double ca_matrix[])
{
	int i, k;
	double rmsd;


	for (i=0; i<(num_res-LEN_HELIX_MASK+1); i++) {
		rmsd = get_rmsd(ca_matrix, hmask, LEN_HELIX_MASK, i*num_res + i);

		if (rmsd < helix_rmsd) {
			for (k=i; k<i+LEN_HELIX_MASK; k++) {
				rz[k].ss = HELIX;
				ca_matrix[i*num_res + k] = 0;
			}
		}
	}

}	/* check_helix */


/***********************************************************************
* using the ca matrix, use a mask to see if a beta is present. 
*/
void check_beta(RESIDUE rz[],double ca_matrix[])
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
					rz[i+k].ss = BETA;
					rz[j+k].ss = BETA;
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
					rz[i + k].ss = BETA;
					rz[j + (-1*k)].ss = BETA;
				}
			}
		}
	}


}	/* check_beta */


/***********************************************************************
* get the rms deviation between the mask and the array segment
*/
static double get_rmsd(double ca_matrix[], double mask[], int maskLen, int idx)
{
int k;
double rmsd;
double sum = 0;

	for (k=0; k<maskLen; k++) 
		sum += fabs(ca_matrix[idx+k] - mask[k]);

	rmsd = sum / maskLen;
	
	return(rmsd);

}	/* get_rmsd */


/***********************************************************************
* PURPOSE:	to check that if phi angle > 0 then it can not be a helix,
*			and if 0 < phi < 160 it can not be a beta.
*/
void post_check(RESIDUE rz[])
{
int i;

	for (i=0; i<num_res; i++) {
		if ( (rz[i].ss == HELIX) && (rz[i].phi > 0.0) )
			rz[i].ss = COIL;
		if ( (rz[i].ss == HELIX) && 
			( (rz[i].psi > 110) || (rz[i].phi < -110.0) ) )
			rz[i].ss = COIL;
		if ( (rz[i].ss == BETA) && (rz[i].phi > 0.0) &&
			(rz[i].phi < 160.0) )
			rz[i].ss = COIL;
	}

}	/* post_check */


void calc_hcoords(RESIDUE resArray[])
{
	int     i, j;
	float  lengthoc;
	float   ocx, ocy, ocz;

	for (i=1; i< num_res; i++) 
	{

		/* skip if the coordinates are in the input file */
		if (resArray[i].coords[H_COORD].x != NA)
			continue;

		/* calculate h atom */
		ocx = - ( resArray[i-1].coords[O_COORD].x - 
			resArray[i-1].coords[C_COORD].x);
		ocy = - ( resArray[i-1].coords[O_COORD].y - 
			resArray[i-1].coords[C_COORD].y );
		ocz = - ( resArray[i-1].coords[O_COORD].z - 
			resArray[i-1].coords[C_COORD].z );

		lengthoc = (float)sqrt((double) 
		(pow((double)ocx,(double)2) + 
		pow((double)ocy,(double)2) + 
		pow((double)ocz,(double)2)));

		resArray[i].coords[H_COORD].x = 
			resArray[i].coords[N_COORD].x + ocx/lengthoc;
		resArray[i].coords[H_COORD].y = 
			resArray[i].coords[N_COORD].y + ocy/lengthoc;
		resArray[i].coords[H_COORD].z = 
			resArray[i].coords[N_COORD].z + ocz/lengthoc;

		for (j = 0; j < MAX_HBONDS; j++)
		{
			resArray[i].hbonds[j].partner = NA;
		}
	}

}   /* calc_hcoords */




/*************************************************************
 * PURPOSE: calculate hydrogen bonds
 * INPUT:   single residue record
 */
void hbond(RESIDUE *res, int resIdx,RESIDUE resArray[])
{
int		i, index;
float	hoDist, noDist, minimum;
float	bondangle;
float	energy;

	minimum = 4;


    for (i=0; i < num_res; i++) {

		/* if some residue < hbond_dist to this rec */
		hoDist = v_get_dist(resArray[i].coords[H_COORD].x, 
			resArray[i].coords[H_COORD].y, resArray[i].coords[H_COORD].z, 
			res->coords[O_COORD].x, res->coords[O_COORD].y, 
			res->coords[O_COORD].z);
		noDist = v_get_dist(resArray[i].coords[N_COORD].x, 
			resArray[i].coords[N_COORD].y, resArray[i].coords[N_COORD].z, 
			res->coords[O_COORD].x, res->coords[O_COORD].y, 
			res->coords[O_COORD].z);

		if ( (hoDist < hbond_dist) && (hoDist < noDist) &&
			 (res->num != resArray[i].num) ) {

			/* check angle between OC and NH */
			bondangle = angle(*res, O_COORD, C_COORD, 
				resArray[i], N_COORD, H_COORD);
			
			/* set of checks to make sure it is a hbond */
			if ( (fabs((double)bondangle) < hbond_angle) && 
				 (hoDist < 
				   (hbond_dist2 + fabs((double)cos((double)RAD(bondangle)))))&&
				 (hoDist < minimum) ) {

				minimum = hoDist;

				/* get hbond energy */
				energy = get_energy(res, &resArray[i]);


				/* set hbond for current res */
				index = getHbondIndex(hoDist, res->hbonds);
				if (index != -1) {
					res->hbonds[index].partner = i;
					res->hbonds[index].dist = hoDist; 
					/* normalize bond angle */
					res->hbonds[index].angle = 180 - bondangle;
					res->hbonds[index].DA_FLAG = ACCEPTOR;
					res->hbonds[index].energy = energy; 
				}

				/* set corresponding hbond  */
				index = getHbondIndex(hoDist, resArray[i].hbonds);
				if (index != -1) {
					resArray[i].hbonds[index].partner = resIdx;
					resArray[i].hbonds[index].dist = hoDist; 
					resArray[i].hbonds[index].angle = bondangle; 
					resArray[i].hbonds[index].DA_FLAG = DONOR;
					resArray[i].hbonds[index].energy = energy;
				}

			}
		}
	}

}	/* hbond */


/*********************************************************************
 * PURPOSE: to calculate the hbond energy between two residues
 */
float get_energy(RESIDUE *res1,RESIDUE *res2)
{
	float energy;
	float rON, rCH, rOH, rCN;

	rON = v_get_dist(res1->coords[O_COORD].x, res1->coords[O_COORD].y, 
		res1->coords[O_COORD].z, res2->coords[N_COORD].x, 
		res2->coords[N_COORD].y, res2->coords[N_COORD].z);

	rCH = v_get_dist(res1->coords[C_COORD].x, res1->coords[C_COORD].y, 
		res1->coords[C_COORD].z, res2->coords[H_COORD].x, 
		res2->coords[H_COORD].y, res2->coords[H_COORD].z);

	rOH = v_get_dist(res1->coords[O_COORD].x, res1->coords[O_COORD].y, 
		res1->coords[O_COORD].z, res2->coords[H_COORD].x, 
		res2->coords[H_COORD].y, res2->coords[H_COORD].z);

	rCN = v_get_dist(res1->coords[C_COORD].x, res1->coords[C_COORD].y, 
		res1->coords[C_COORD].z, res2->coords[N_COORD].x, 
		res2->coords[N_COORD].y, res2->coords[N_COORD].z);


	/* formula from kabsch and sander, 1983
	 * hbond energy should be less than -0.5 kcal/mol
	 * a good hbond has ~ -3.0 kcal/mol
	 */
	energy = 332 * .42 * .20 * ( 1/rON + 1/rCH - 1/rOH - 1/rCN);

	if (energy > 0)
		energy = 0;

	return(energy);

}	/* get_energy */


/*************************************************************/
/* return the distance between two points. 
*/
float v_get_dist(float onex,float oney,float onez,float twox,float twoy,float twoz)
{
float distx, disty, distz;
float distance;

	distx = onex - twox;
	disty = oney - twoy; 
	distz = onez - twoz;

	distance = (float) sqrt((double)
	(pow((double)distx,(double)2)+
	pow((double)disty,(double)2)+
	pow((double)distz,(double)2)));

	return(distance);

}	/* get_dist */


/*********************************************************************
 * PURPOSE: get the index into the hbonds array 
 */
int getHbondIndex(float newDist,BOND_REC bondrec[MAX_HBONDS])
{
	int j, maxIdx;
	float maximum;

	maximum = 0;

	for (j=0; j<MAX_HBONDS; j++)
	{
		if (bondrec[j].partner == NA)
		{
			return(j);
		}
		else if (bondrec[j].dist > maximum) 
		{
			maximum = bondrec[j].dist; 
			maxIdx = j;
		}
	}

	if (newDist < maximum)
	{
		return(maxIdx);
	}
	else
	{
		return(-1);
	}
}	/* getHbondIndex */


/*************************************************************
 * PURPOSE: calculate all sidebond-sidebond bonds , and
 *			all sidebond-mainchain bonds.
 * INPUT:   single residue record
 */
void getall_sbond(int idx,RESIDUE resArray[])
{
	check_ho_bond(idx, N_COORD, H_COORD, check_mainsidebond,resArray);

	if (0 == strcmp(resArray[idx].type, "ARG")) {
		check_ho_bond(idx, NH1_COORD, CZ_COORD, check_sidebond,resArray);
		check_ho_bond(idx, NH2_COORD, CZ_COORD, check_sidebond,resArray);
		check_ho_bond(idx, NE_COORD, CZ_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "ASP")) {
		check_ho_bond(idx, OD1_COORD, CG_COORD, check_sidebond,resArray);
		check_ho_bond(idx, OD2_COORD, CG_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "GLU")) {
		check_ho_bond(idx, OE1_COORD, CD_COORD, check_sidebond,resArray);
		check_ho_bond(idx, OE2_COORD, CD_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "LYS")) {
		check_ho_bond(idx, NZ_COORD, CE_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "ASN")) {
		check_ho_bond(idx, ND2_COORD, CG_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "GLN")) {
		check_ho_bond(idx, NE2_COORD, CD_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "THR")) {
		check_ho_bond(idx, OG1_COORD, CB_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "TYR")) {
		check_ho_bond(idx, OH_COORD, CZ_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "SER")) {
		check_ho_bond(idx, OG_COORD, CB_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "HIS")) {
		check_ho_bond(idx, ND1_COORD, CG_COORD, check_sidebond,resArray);
		check_ho_bond(idx, NE2_COORD, CG_COORD, check_sidebond,resArray);
	}
	else if	(0 == strcmp(resArray[idx].type, "TRP")) {
		check_ho_bond(idx, NE1_COORD, CG_COORD, check_sidebond,resArray);
	}

	else return;

}	/* getall_sbond */


/*...........................................................................
 * PURPOSE: to assign b-turn designations to all residues
 */
void calc_bturn(RESIDUE resArray[])
{
int 	i, j, k;
int		t1, t3, t1p, t3p;
int		doubleH, isHbond;
int 	bounds[5];
int		partIdx;

	for (i=0; i < num_res; i++) 
		strcpy(resArray[i].bturn, "    ");

	for (i=0; i < num_res -2; i++) {


		/* only assign a bturn IF no bturn has already been
		 * assigned, AND there is not a double hydrogen bond
		 * (for all i to i+3) AND there is an hbond from 
		 * i to i+3
         */
		doubleH = TRUE;
		isHbond = FALSE;
		for (j=i; j<=i+3; j++) {
			for (k=0; k<MAX_HBONDS; k++) 
				if (resArray[j].hbonds[k].partner == NA)
					doubleH = FALSE;	
		}
		for (k=0; k<MAX_HBONDS; k++) 
		{
			partIdx = resArray[i].hbonds[k].partner;
			if (partIdx != NA)
			{
				if (resArray[partIdx].num == (resArray[i].num + 3) )
				{
					isHbond = TRUE;
				}
			}
		}


		if ((strcmp(resArray[i].bturn, "    ") == 0) &&
			(!doubleH) &&
			(isHbond) ) {

			bounds[0] = bounds[1] = 30;
			bounds[2] = bounds[3] = 30; 
			bounds[4] = 0;

			t3 = checkType(-60, -30, -60, -30, 0, i, " III", bounds,resArray);
			t3p = checkType(60, 30, 60, 30, 0, i, "III'", bounds,resArray);
			t1 = checkType(-60, -30, -90, 0, 0, i, "  I ", bounds,resArray);
			t1p = checkType(60, 30, 90, 0, 0, i, " I' ", bounds,resArray);

			/* a tturn can be I and III (conversely I' and III')
			 * at the same time.  If that is the case, check to see
			 * which one is more accurate
			 */
			if ( (t1 == TRUE) && (t3 == TRUE) )
				pickType(-90, 0, -60, -30, i, "  I ", " III",resArray);
			if ( (t1p == TRUE) && (t3p == TRUE) )
				pickType(90, 0, 60, 30, i, "  I'", "III'",resArray);

			(void) checkType(-60, 120, 80, 0, 0, i, " II ", bounds,resArray);
			(void) checkType(60, -120, -80, 0, 0, i, " II'", bounds,resArray);

			bounds[4] = 30;
			(void) checkType(-60, 120, -90, 0, 0, i, "VIa ", bounds,resArray);
			(void) checkType(-120, 120, -60, 0, 0, i, "VIb ", bounds,resArray);

		}
	}

}	/* calc_bturn */


/*************************************************************/
/* PURPOSE: find the angle between two vectors 
*        	for hbonds, rec1 contains O and C coords,
*		    rec2 contains N and H coords.
*/
float angle(RESIDUE rec1,int vec1a,int vec1b, RESIDUE rec2,int vec2a,int vec2b)
{
float	ocx, ocy, ocz;
float	nhx, nhy, nhz;
float	length1, length2, adotb, ang;
float	value;

	ocx = rec1.coords[vec1a].x - rec1.coords[vec1b].x;
	ocy = rec1.coords[vec1a].y - rec1.coords[vec1b].y;
	ocz = rec1.coords[vec1a].z - rec1.coords[vec1b].z;
	nhx = rec2.coords[vec2a].x - rec2.coords[vec2b].x;
	nhy = rec2.coords[vec2a].y - rec2.coords[vec2b].y;
	nhz = rec2.coords[vec2a].z - rec2.coords[vec2b].z;

	length1 = (float) sqrt((double)
	(pow((double)ocx,(double)2) + 
	pow((double)ocy,(double)2) + 
	pow((double)ocz,(double)2)));

	length2 = (float) sqrt((double)
	(pow((double)nhx,(double)2) + 
	pow((double)nhy,(double)2) + 
	pow((double)nhz,(double)2)));

	adotb = ocx*nhx + ocy*nhy + ocz*nhz;


	value = adotb / ( length1 * length2 );
	ang = (float) acos((double)value);
	ang = DEG(ang);
	return(ang);

}	/* angle */


/*********************************************************************
* PURPOSE:	to look for main chain to side chain bonds.
*/
void check_mainsidebond(int didx, int dneighbour, int donor, int aidx, int acceptor, int aneighbour,RESIDUE resArray[])
{
float	printdist;
float	dist, longdist;


	/* distance from H to O */
	dist = v_get_dist(resArray[didx].coords[dneighbour].x,
		resArray[didx].coords[dneighbour].y,
		resArray[didx].coords[dneighbour].z,
		resArray[aidx].coords[acceptor].x,
		resArray[aidx].coords[acceptor].y,
		resArray[aidx].coords[acceptor].z);


	/* distance from N to C */
	longdist = v_get_dist(resArray[aidx].coords[aneighbour].x,
		resArray[aidx].coords[aneighbour].y,
		resArray[aidx].coords[aneighbour].z,
		resArray[didx].coords[donor].x,
		resArray[didx].coords[donor].y,
		resArray[didx].coords[donor].z);


	/* distance from N to O */
	printdist = v_get_dist(resArray[didx].coords[donor].x,
		resArray[didx].coords[donor].y,
		resArray[didx].coords[donor].z,
		resArray[aidx].coords[acceptor].x,
		resArray[aidx].coords[acceptor].y,
		resArray[aidx].coords[acceptor].z);


	if ( (printdist < sidebond_dist ) && (dist < longdist) &&
		( resArray[didx].num != resArray[aidx].num) ) {

		store_dist(printdist, didx, aidx, donor, dneighbour, 
			acceptor, aneighbour,resArray);

	}

}	/* check_mainsidebond */



/*********************************************************************
* PURPOSE:	to look for sidechain sidechain bonds.
*/
void check_sidebond(int didx, int dneighbour, int donor, int aidx,int acceptor, int aneighbour,RESIDUE resArray[])
{
	float	dist, longdist;



	/* distance from donor to acceptor */
	dist = v_get_dist(resArray[didx].coords[donor].x,
		resArray[didx].coords[donor].y,
		resArray[didx].coords[donor].z,
		resArray[aidx].coords[acceptor].x,
		resArray[aidx].coords[acceptor].y,
		resArray[aidx].coords[acceptor].z);


	/* make sure that the donor is the closest */
	longdist = v_get_dist(resArray[didx].coords[dneighbour].x,
		resArray[didx].coords[dneighbour].y,
		resArray[didx].coords[dneighbour].z,
		resArray[aidx].coords[aneighbour].x,
		resArray[aidx].coords[aneighbour].y,
		resArray[aidx].coords[aneighbour].z);

/* DEBUG
if (dist < sidebond_dist) {
	printf("distance from %d to %d is %f\n", resArray[didx].resNum,
	resArray[aidx].resNum, acceptor, dist);
	printf("longer distance from %d to %d is %f\n", resArray[didx].resNum,
	resArray[aidx].resNum, acceptor, longdist);
	sleep(1);
}
*/

	if ( (dist < sidebond_dist ) && (dist < longdist) &&
		( resArray[didx].num != resArray[aidx].num) 
) {

		store_dist(dist, didx, aidx, donor, dneighbour, acceptor, aneighbour,resArray);

	}

}	/* check_sidebond */


/*********************************************************************
* PURPOSE:	to check the hydrogen and all possible acceptors for
*			bonds.
*/
void check_ho_bond(int didx,int donor,int dneighbour,void (*bond_check)(),RESIDUE resArray[])
{
int i;

    for (i=0; i < num_res; i++) {
		
		if (0 == strcmp(resArray[i].type, "SER"))
			(*bond_check)(didx, dneighbour, donor, i, OG_COORD, CB_COORD,resArray);

		else if (0 == strcmp(resArray[i].type, "THR"))
			(*bond_check)(didx, dneighbour, donor, i, OG1_COORD, CB_COORD,resArray);

		else if (0 == strcmp(resArray[i].type, "ASN"))
			(*bond_check)(didx, dneighbour, donor, i, OD1_COORD, CG_COORD,resArray);
	
		else if (0 == strcmp(resArray[i].type, "GLN"))
			(*bond_check)(didx, dneighbour, donor, i, OE1_COORD, CD_COORD,resArray);

		else if (0 == strcmp(resArray[i].type, "ASP")) {
			(*bond_check)(didx, dneighbour, donor, i, OD1_COORD, CG_COORD,resArray);
			(*bond_check)(didx, dneighbour, donor, i, OD2_COORD, CG_COORD,resArray);
		}

		else if (0 == strcmp(resArray[i].type, "GLU")) {
			(*bond_check)(didx, dneighbour, donor, i, OE1_COORD, CD_COORD,resArray);
			(*bond_check)(didx, dneighbour, donor, i, OE2_COORD, CD_COORD,resArray);
		}

		else if (0 == strcmp(resArray[i].type, "TYR"))
			(*bond_check)(didx, dneighbour, donor, i, OH_COORD, CZ_COORD,resArray);

		else if (0 == strcmp(resArray[i].type, "HIS")) {
			(*bond_check)(didx, dneighbour, donor, i, ND1_COORD, CG_COORD,resArray);
			(*bond_check)(didx, dneighbour, donor, i, NE2_COORD, CG_COORD,resArray);
		}

		if (donor != N_COORD)
			(*bond_check)(didx, dneighbour, donor, i, O_COORD, C_COORD,resArray);

	}

}	/* check_ho_bond */




/*...........................................................................
 * PURPOSE: to check if the phi psi angles are within bounds of
 *			the given b-turn.
 */
int checkType(int val1,int val2,int val3,int val4,int val5,int indx,char *bturn_type,int bounds[5],RESIDUE resArray[])
{

	if ( IN(resArray[indx+1].phi, val1, bounds[0]) && 
		IN(resArray[indx+1].psi, val2, bounds[1]) &&
		IN(resArray[indx+2].phi, val3, bounds[2]) &&
		IN(resArray[indx+2].psi, val4, bounds[3]) )  { 

			if ( (bounds[4] == 0) ||
				( (bounds[4] != 0) && 
				IN(resArray[indx+1].omega, val5, bounds[4]) ) ) {


				strcpy(resArray[indx].bturn, bturn_type);
				strcpy(resArray[indx+1].bturn, bturn_type);
				strcpy(resArray[indx+2].bturn, bturn_type);
				strcpy(resArray[indx+3].bturn, bturn_type);
				return(TRUE);
			}
	}
	return(FALSE);

}	/* checkType */


/*...........................................................................
 * PURPOSE: to check if the turn is closer to a type 1 or type 3 
 */
void pickType(int val1_1, int val2_1, int val1_3, int val2_3, int index, char *type1, char *type3,RESIDUE resArray[])
{
	double diff1, diff3;

	diff1 = ABS(resArray[index+2].phi - val1_1) +
	        ABS(resArray[index+2].psi - val2_1) ;

	diff3 = ABS(resArray[index+2].phi - val1_3) +
	        ABS(resArray[index+2].psi - val2_3) ;

	if (diff1 < diff3) {
		strcpy(resArray[index].bturn, type1);
		strcpy(resArray[index+1].bturn, type1);
		strcpy(resArray[index+2].bturn, type1);
		strcpy(resArray[index+3].bturn, type1);
	}
	else {
		strcpy(resArray[index].bturn, type3); 
		strcpy(resArray[index+1].bturn, type3); 
		strcpy(resArray[index+2].bturn, type3); 
		strcpy(resArray[index+3].bturn, type3); 
	}
}


/*********************************************************************
* PURPOSE:	to store the bond distances.
*/
void store_dist(float dist, int didx, int aidx, int donor, int dneighbour,int acceptor,int aneighbour,RESIDUE resArray[])
{
	int index;

	/* if this distance is less than the stored sidebond */			
	index = getHbondIndex(dist, resArray[didx].sidebond);
	if (index != -1)
	{

	/* set hbond for current res */
		resArray[didx].sidebond[index].partner = aidx;
		resArray[didx].sidebond[index].dist = dist; 
		resArray[didx].sidebond[index].DA_FLAG = ACCEPTOR;
		resArray[didx].sidebond[index].donor = donor;
		resArray[didx].sidebond[index].dneighbour = dneighbour;
		resArray[didx].sidebond[index].acceptor = acceptor;
		resArray[didx].sidebond[index].aneighbour = aneighbour;

		/* set donor hbond */
		index = getHbondIndex(dist, resArray[aidx].sidebond);
		if (index != -1)
		{
			resArray[aidx].sidebond[index].partner = didx;
			resArray[aidx].sidebond[index].dist = dist; 
			resArray[aidx].sidebond[index].DA_FLAG = DONOR;
		}
	}

}	/* store_dist */



/*********************************************************************
 * PURPOSE: compute secondary structure based on hydrogen bonds 
 */
void define3(RESIDUE resArray[])
{

	assign_define3(resArray);
	smooth_define3(resArray);
	filter_define3(resArray);

}


/*********************************************************************
 * PURPOSE: to assign H, B, and C
 */
void assign_define3(RESIDUE resArray[])
{
int i;
float phi, psi, lastphi = 0;
float dist0, dist1;

	for (i = 0; i < num_res; i++)
	{

		psi = resArray[i].psi;
		phi = resArray[i].phi;

		if (resArray[i].hbonds[0].partner != NA)
		{
			dist0 = ABS(resArray[resArray[i].hbonds[0].partner].num - resArray[i].num); 
		}
		if (resArray[i].hbonds[1].partner != NA)
		{
			dist1 = ABS(resArray[resArray[i].hbonds[1].partner].num - resArray[i].num);
		}
		/* HELIX */
		if ( (resArray[i].hbonds[0].partner != NA) &&
			(resArray[i].hbonds[1].partner != NA) &&

			( ( ( (dist0 == 3) || (dist0 == 4) ) && (dist1 > 1) ) ||
				( ( (dist1 == 3) || (dist1 == 4) ) && (dist0 > 1) ) ) &&

			( psi < 100 ) )

			strcpy(resArray[i].dstruct3, "H");


		/* BETA */
		/* else if (old_get_beta(i, phi, psi, lastphi)); */
		else if (get_beta(i, phi,resArray));

		/* COIL */
		else strcpy(resArray[i].dstruct3, "C");

		lastphi = phi;
			
	}

}	/* assign_define3 */


/*********************************************************************
 * PURPOSE:	to assign the betas
 */
int get_beta(int residx,float phi,RESIDUE resArray[])
{
	int i;
	int dist;
	int partidx;
	int partnum;

	for (i=0; i<MAX_HBONDS; i++) {
		partidx = resArray[residx].hbonds[i].partner;
		if (partidx != NA)
		{
			partnum = resArray[partidx].num;
		}
		dist = ABS(partnum - resArray[residx].num);
		if ( (partidx != NA ) &&
			(dist > 4) && 
			(resArray[residx].dstruct3[0] != 'H')  &&
			(phi < 0) )
		{

			strcpy(resArray[residx].dstruct3, "B");
			return(TRUE);
		}					
	}


	/* look also for beta smoothing in the smoothing calculations */	

	return(FALSE);

}	/* get_beta */


/*********************************************************************
 * PURPOSE:	to assign the betas
 * NOTE:    this routine has been replaced by get_beta.
 */
int old_get_beta(int i, float phi,float psi,float lastphi,RESIDUE resArray[])
{

	psi = resArray[i].psi;
	phi = resArray[i].phi;

	if ( legitBond(resArray[i],resArray, BETA) &&
		(((phi < -40) && (phi > -180)) || ((phi > 160) && (phi <= 180))) && 
		(((psi > 70) && (psi < 180)) || ((psi < -170) && (psi > -180)))) 
		{
			strcpy(resArray[i].dstruct3, "B");
			if ( (DSTR(resArray[i-1]) != BETA) &&
			     (DSTR(resArray[i-2]) != BETA) && (lastphi <-100) )
				strcpy(resArray[i-1].dstruct3, "B");
			return(TRUE);
		}

	/* also BETA */
	if ( legitBond(resArray[i],resArray, ALSO_BETA) && (phi < -95) ) {
		strcpy(resArray[i].dstruct3, "B");
		return(TRUE);
	}

	return(FALSE);

}	/* old_get_beta */


/*********************************************************************
* PURPOSE: smooth out secondary structures
*/
void smooth_define3(RESIDUE resArray[])
{

	smooth_helix(resArray);
	smooth_beta(resArray);

}	/* smooth_define3 */


/*********************************************************************
* PURPOSE:	to smooth helices
*/
void smooth_helix(RESIDUE resArray[])
{
int i;
float phi, psi;

	/* check for pattern of HCHH or HHCH */
	for (i=0; i<num_res-3; i++) {

		psi = resArray[i].psi;
		phi = resArray[i].phi;

		if ( (DSTR(resArray[i]) == HELIX) && 
			(DSTR(resArray[i+1]) == COIL) &&
			(DSTR(resArray[i+2]) == HELIX) &&
			(DSTR(resArray[i+3]) == HELIX) ) {

			if ( (phi<0) && (psi < 0) )

				strcpy(resArray[i+1].dstruct3, "H");
			
		}
		else if ( (DSTR(resArray[i]) == HELIX) && 
			(DSTR(resArray[i+1]) == HELIX) &&
			(DSTR(resArray[i+2]) == COIL) &&
			(DSTR(resArray[i+3]) == HELIX) ) {

			if ( (phi<0) && (psi < 0) ) 

				strcpy(resArray[i+2].dstruct3, "H");
			
		}
	}

	for (i=1; i<num_res-1; i++) {
		if ( (DSTR(resArray[i-1]) != HELIX) && 
			(DSTR(resArray[i]) == HELIX) && 
			 (DSTR(resArray[i+1]) != HELIX) )

			strcpy(resArray[i].dstruct3, "C");
	}

}	/* smooth_helix */


/*********************************************************************
* PURPOSE:	to smooth the beta's
*/
void smooth_beta(RESIDUE resArray[])
{
int i;

	for (i=1; i<num_res-1; i++) {
		if ( (DSTR(resArray[i-1]) == BETA) && 
			(DSTR(resArray[i]) == COIL) && 
			(DSTR(resArray[i+1]) == BETA) ) {
		
			if ( (resArray[i].phi < 0) &&
				(resArray[i].psi > 0) )
				strcpy(resArray[i].dstruct3, "B");
		}
	}

}	/* smooth_beta */


/*********************************************************************
* PURPOSE:	to smooth the beta's
* NOTE:		this routine is replaced by smooth_beta
*/
void old_smooth_beta(RESIDUE resArray[])
{
int i;

	for (i=1; i<num_res-1; i++) {
		if ( (DSTR(resArray[i-1]) == BETA) && (DSTR(resArray[i]) == COIL) && 
			 (DSTR(resArray[i+1]) == BETA) )
			strcpy(resArray[i].dstruct3, "B");
	}

	for (i=1; i<num_res-1; i++) {
		if ( (DSTR(resArray[i-1]) != BETA) && (DSTR(resArray[i]) == BETA) && 
			 (DSTR(resArray[i+1]) != BETA) )
			strcpy(resArray[i].dstruct3, "C");
	}

}	/* smooth_beta */


/*********************************************************************
* PURPOSE: to filter out the seconary structure
*/
void filter_define3(RESIDUE resArray[])
{
int i, j;
int strucCount = 1;
int strucLast = 0;

	for (i=1; i<=num_res; i++) {
		if ( DSTR(resArray[i]) == DSTR(resArray[i-1]) )
			strucCount++;
		else {
			if ( (strucLast == HELIX) && (strucCount < 3) )
				for (j=i-1; j>=i-strucCount; j--)
					strcpy(resArray[j].dstruct3, "C");
			if ( (strucLast == BETA) && (strucCount < 3) )
				for (j=i-1; j>=i-strucCount; j--)
					strcpy(resArray[j].dstruct3, "C");
			strucCount = 1;
		}
		strucLast = DSTR(resArray[i]);
	}

}	/* filter_define3 */


/*********************************************************************
 * PURPOSE: to see if there is a hydrogen bond that is legitimate
 * 			for a HELIX or BETA
 * CALLER:  define3
 */
int legitBond(RESIDUE residue,RESIDUE resArray[],int bondType)
{
int i, bondDist;
int bond3, bond4;

	bond3 = bond4 = FALSE;

	for (i=0; i<MAX_HBONDS; i++) {
		if (residue.hbonds[i].partner == NA) 
		{
			bondDist = 0;
		}
		else
		{
			bondDist = ABS((resArray[residue.hbonds[i].partner].num - residue.num /* SJN FIX */));
		}
		switch (bondType) {
			case HELIX:  
				if ( (bondDist > 2) && (bondDist < 6) )
					return(TRUE);
				 break;
			case ALSO_HELIX:  
				if (bondDist == 3)
					bond3 = TRUE;
				if (bondDist == 4)
					bond4 = TRUE;
				if (bond3 && bond4)
					return(TRUE);
				break;
			case BETA:   
				if ( bondDist > 2 )
					return(TRUE);
				 break;	
			case ALSO_BETA: 
				if ( bondDist >= 6 )
					return(TRUE);
				break;
		}
	}

	return(FALSE);

}	/* legitBond */


/*********************************************************************
 * PURPOSE: to calculate a consensus secondary structure
 */
void do_consensus(RESIDUE resArray[])
{
	int i;

	for (i=0; i<num_res; i++) {
		if ( (strcmp(resArray[i].dstruct1, resArray[i].dstruct2)==0) ||
			(strcmp(resArray[i].dstruct1, resArray[i].dstruct3)==0) )
			strcpy(resArray[i].consens, resArray[i].dstruct1);

		else if (strcmp(resArray[i].dstruct2, resArray[i].dstruct3)==0)
			strcpy(resArray[i].consens, resArray[i].dstruct2);

		else strcpy(resArray[i].consens, "C");

	}

}	/* do_consensus */


/*********************************************************************
 * PURPOSE: to set all four of the secondary structures to C for the
 *          middle two res's in any I, I', II, II' turn.
 */
void bturn_ss(RESIDUE resArray[])
{
int i;

    for (i=0; i<(num_res-4); i++) {

        check_turn(i, "  I ",resArray);
        check_turn(i, " I' ",resArray);
        check_turn(i, " II ",resArray);
        check_turn(i, " II'",resArray);

    }

}   /* bturn_ss */


/*********************************************************************
 * PURPOSE: subroutine used by bturn_ss
 */
void check_turn(int i,char *bturn,RESIDUE resArray[])
{
int j;
int same = TRUE;

    for (j=i; j<i+4; j++)
        same = same && (strcmp(resArray[j].bturn, bturn) == 0);

/*  the one exception to this rule is for turns of type I
 *  where there are hydrogen bonds
 */
    if ( (strcmp(bturn, "  I ") == 0) && (hbonded(i,resArray)) ) ;

    else if (same) {
        strcpy(resArray[i+1].dstruct1, "C");
        strcpy(resArray[i+1].dstruct2, "C");
        strcpy(resArray[i+1].dstruct3, "C");
        strcpy(resArray[i+1].consens, "C");
        strcpy(resArray[i+2].dstruct1, "C");
        strcpy(resArray[i+2].dstruct2, "C");
        strcpy(resArray[i+2].dstruct3, "C");
        strcpy(resArray[i+2].consens, "C");
    }

}   /* check_turn */


/*********************************************************************
 * PURPOSE: smooth all of the secondary structures
 */
void smooth_ss(RESIDUE resArray[])
{
int i, j;
int ss_type;
int strucCount;
int strucThis, strucLast;

    for (ss_type=0; ss_type<4; ss_type++) {

        strucCount = 0;
        strucLast = getType(resArray[0], ss_type);

        for (i=1; i<=num_res; i++) {

            strucThis = getType(resArray[i], ss_type);
            if ( strucThis == strucLast)
                strucCount++;
            else {
                if ( (strucLast == HELIX) && (strucCount < 3) )
                    for (j=i-1; j>=i-strucCount; j--)
                        assignSS(j, ss_type, "C",resArray);
                if ( (strucLast == BETA) && (strucCount < 3) )
                    for (j=i-1; j>=i-strucCount; j--)
                        assignSS(j, ss_type, "C",resArray);
                strucCount = 1;
            }
            strucLast = strucThis;
        }
    }

    /* include helix caps and beta bridges */
    for (i=0; i<num_res; i++) {
        do_consens_caps(i,resArray);
        do_consens_bridge(i,resArray);
    }

}   /* smooth_ss */



/*********************************************************************
* PURPOSE:  to place a helix n-cap on the consensus and the other
*			structures.
*/
void do_consens_caps(int i,RESIDUE resArray[])
{
	short j;
	short diff3, diff4;
	int diff;

	/* placing helix N-cap
	 * look for CCHHH
	 * then look at the i+1 position
	 */
	if (i+4 > num_res)
		return;

	if ( (strcmp(resArray[i].consens, "C") == 0) &&
	     (strcmp(resArray[i+1].consens, "C") == 0) &&
	     (strcmp(resArray[i+2].consens, "H") == 0) &&
	     (strcmp(resArray[i+3].consens, "H") == 0) &&
	     (strcmp(resArray[i+4].consens, "H") == 0) ) 
	{


		diff3 = diff4 = FALSE;
		for (j=0; j<MAX_HBONDS; j++) 
		{
			if (resArray[i + 1].hbonds[j].partner != NA)
			{
				diff = ABS(resArray[resArray[i + 1].hbonds[j].partner].num - resArray[i + 1].num);

				if (diff == 3)
				{
					diff3 = TRUE;
				}
				else if (diff == 4)
				{
					diff4 = TRUE;
				}

			}

			/*
			if ( (resArray[i+1].hbonds[j].partner != NA) &&
			   (ABS(resArray[i+1].hbonds[j].partner - resArray[i+1].num) == 3))
			{
				diff3 = TRUE;
			}
			if ( (resArray[i+1].hbonds[j].partner != NA) &&
			   (ABS(resArray[i+1].hbonds[j].partner - resArray[i+1].num) == 4))
			{
				diff4 = TRUE;
			}
			*/
		}

		if ( (diff3 && diff4) && (resArray[i+1].phi < 0) &&
			(resArray[i+1].psi > 90) ) {
			strcpy(resArray[i+1].dstruct1, "H");
			strcpy(resArray[i+1].dstruct2, "H");
			strcpy(resArray[i+1].dstruct3, "H");
			strcpy(resArray[i+1].consens, "H");
		}
	}

}	/* do_consens_caps */


/*********************************************************************
* PURPOSE:  to assign short beta bridges, on the consensus and
*			the other structures.
*/
void do_consens_bridge(int i,RESIDUE resArray[])
{
	short j, diff4;

	/* placing helix N-cap
	 * look for CCC
	 * then look at the i+1 position
	 */
	if (i+2 > num_res)
	{
		return;
	}

	if ( (strcmp(resArray[i].consens, "C") == 0) &&
	     (strcmp(resArray[i+1].consens, "C") == 0) &&
	     (strcmp(resArray[i+2].consens, "C") == 0) ) {

		diff4 = FALSE;
		for (j=0; j<MAX_HBONDS; j++) {
			if ( (resArray[i+1].hbonds[j].partner != NA) &&
			(ABS(resArray[resArray[i+1].hbonds[j].partner].num - resArray[i+1].num) > 4) )
			{
				diff4 = TRUE;
			}
		}

		if ( diff4 && 
			( resArray[i].phi < 0 ) &&
			( resArray[i+1].phi < 0 ) &&
			( resArray[i+2].phi < 0 ) &&
			( ABS(resArray[i].psi) > 90 ) &&
			( ABS(resArray[i+1].psi) > 90 ) &&
			( ABS(resArray[i+2].psi) > 90 ) ) { 

			strcpy(resArray[i].dstruct1, "B");
			strcpy(resArray[i].dstruct2, "B");
			strcpy(resArray[i].dstruct3, "B");
			strcpy(resArray[i].consens, "B");

			strcpy(resArray[i+1].dstruct1, "B");
			strcpy(resArray[i+1].dstruct2, "B");
			strcpy(resArray[i+1].dstruct3, "B");
			strcpy(resArray[i+1].consens, "B");

			strcpy(resArray[i+2].dstruct1, "B");
			strcpy(resArray[i+2].dstruct2, "B");
			strcpy(resArray[i+2].dstruct3, "B");
			strcpy(resArray[i+2].consens, "B");
		}
	}

}	/* do_consens_bridge */


/************************************************************************
* PURPOSE: to see if there are double hydrogen bonds
*/
int hbonded(int i,RESIDUE resArray[])
{
    if ( (resArray[i+1].hbonds[0].partner != NA) &&
       (resArray[i+1].hbonds[1].partner != NA) &&
       (resArray[i+2].hbonds[0].partner != NA) &&
       (resArray[i+2].hbonds[1].partner != NA) )
	{
		return(TRUE);
	}
    else
	{
		return(FALSE);
	}

}   /* hbonded */


/*********************************************************************
 * PURPOSE: assign the structure fo residue.
 */
void assignSS(int residx,int type,char *value,RESIDUE resArray[])
{

	switch (type) {
		case 0: strcpy(resArray[residx].dstruct1, value); break;
		case 1: strcpy(resArray[residx].dstruct2, value); break;
		case 2: strcpy(resArray[residx].dstruct3, value); break;
		case 3: strcpy(resArray[residx].consens, value); break;
	}

}	/* assignSS */


/*********************************************************************
 * PURPOSE: return the type of ss structure for residue.
 */
int getType(RESIDUE resx,int type)
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



/*************************************************************/
/* Main calculation loop
*/
void do_define2(RESIDUE resArray[])
{
int		i, j;
int		ret;
int		strucCount, strucLast;
float	lastphi;
float	phi, psi;

	lastphi = 0.0;

	/*
	print_run(outfp);
	fprintf(stdout, "   Calculating secondary structure...\n");
	*/

	for (i=0; i<num_res; i++)
	{
		resArray[i].ss = COIL;
	}
	/*
	i = 0;
	ret = get_phipsi(i, &phi, &psi);
	*/
	
	for (i=0; i < num_res; i++) 
	{
		if ( (resArray[i].phi < -34) && (resArray[i].phi > -120) &&
			 (resArray[i].psi >-80) && (resArray[i].psi < 6) )
		{
			resArray[i].ss = HELIX; 
		}

		if ( (resArray[i].ss == HELIX) && (resArray[i-1].ss != HELIX) &&
			(resArray[i-2].ss != HELIX) &&
			(lastphi <-55) && (lastphi >-90) )
		{
			resArray[i-1].ss = HELIX;
		}

		if ( ( (resArray[i].phi < -40) && (resArray[i].phi > -180) || ( (resArray[i].phi > 160) && (resArray[i].phi <= 180) ) ) 
			&&	
			( ((resArray[i].psi > 70) && (resArray[i].psi < 180) ) || ((resArray[i].psi < -170) && (resArray[i].psi > -180)) ) )
			resArray[i].ss = BETA;

		if ( (resArray[i].ss == BETA) && (resArray[i-1].ss != BETA) &&
			(resArray[i-2].ss != BETA) &&
			(lastphi <-100) )
			resArray[i-1].ss = BETA;

		lastphi = resArray[i].phi;
	}			

	/* filter */
	strucCount = 1;
	strucLast = 0;
	for (i=1; i< num_res; i++) {
		if ( (resArray[i].ss == resArray[i-1].ss) )
		{
			strucCount++;
		}
		else
		{
			if ( (strucLast == HELIX) && (strucCount <= 3) )
			{
				for (j=i-1; j>=i-strucCount; j--)
				{
					resArray[j].ss = COIL;
				}
			}
			if ( (strucLast == BETA) && (strucCount <= 2) )
			{
				for (j=i-1; j>=i-strucCount; j--)
				{
					resArray[j].ss = COIL;
				}
			}
			strucCount = 1;
		}
		strucLast = resArray[i].ss;
	}

	for (i=0; i<num_res; i++) 
	{
		switch(resArray[i].ss) {

		case HELIX:
			strcpy(resArray[i].dstruct2, "H");
			break;

		case BETA:
			strcpy(resArray[i].dstruct2, "B");
			break;

		case COIL:
			strcpy(resArray[i].dstruct2, "C"); 
			break;
		}
	}


	/*
	output_all(outfp);
	fprintf(stdout, "   Done define2 program.\n\n");
	fprintf(stdout, "-----------------------------------------------------------------\n");
	*/
}


int CheckHBond(RESIDUE *rrez,RESIDUE *drez,double *energy,int oindex,int cindex)
{
	double	hoDist, noDist;
	double	bondangle;

	hoDist = v_get_dist(drez->coords[H_COORD].x, 
		drez->coords[H_COORD].y, drez->coords[H_COORD].z, 
		rrez->coords[oindex].x, rrez->coords[oindex].y, 
		rrez->coords[oindex].z);
	noDist = v_get_dist(drez->coords[N_COORD].x, 
		drez->coords[N_COORD].y, drez->coords[N_COORD].z, 
		rrez->coords[oindex].x, rrez->coords[oindex].y, 
		rrez->coords[oindex].z);

	if ( (hoDist < hbond_dist) && (hoDist < noDist) && ( rrez->num != drez->num) ) 
	{
		/* check angle between OC and NH */
		bondangle = angle(*rrez, oindex, cindex,*drez, N_COORD, H_COORD);
			
		/* set of checks to make sure it is a hbond */
		if ( (fabs((double)bondangle) < hbond_angle)
		 && (hoDist <  (hbond_dist2 + fabs((double)cos((double)RAD(bondangle)))))) 
		{
			*energy = get_energy(rrez, drez);
			return(1);
		}
	}
	return(0);
}

/* Much like the preceding, but checks distances only --- no bond angles */
int CheckSolventHBond(RESIDUE *drez,double ox,double oy,double oz)
{
	double	hoDist, noDist;
	double	bondangle;

	hoDist = v_get_dist(drez->coords[H_COORD].x, 
		drez->coords[H_COORD].y, drez->coords[H_COORD].z, 
		ox, oy, oz);
	noDist = v_get_dist(drez->coords[N_COORD].x, 
		drez->coords[N_COORD].y, drez->coords[N_COORD].z, 
		ox, oy, oz);

	if ( (hoDist < hbond_dist) && (hoDist < noDist)) 
	{
		return(1);
	}
	return(0);
}

