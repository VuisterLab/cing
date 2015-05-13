
#include "vmain.h"


int old_get_beta();
void assign_define3(),
	smooth_define3(),
	smooth_helix(),
	smooth_beta(),
	filter_define3();


/*********************************************************************
 * PURPOSE: compute secondary structure based on hydrogen bonds 
 */
void define3()
{

	assign_define3();
	smooth_define3();
	filter_define3();

}


/*********************************************************************
 * PURPOSE: to assign H, B, and C
 */
void assign_define3()
{
int i;
float phi, psi, lastphi = 0;
float dist0, dist1;

	for (i = 0; i<lastResNum; i++) {

		psi = resArray[i].psi;
		phi = resArray[i].phi;

		if (resArray[i].hbonds[0].partner != VOID)
			dist0 = ABS(resArray[resArray[i].hbonds[0].partner].resNum -
			resArray[i].resNum);
		if (resArray[i].hbonds[1].partner != VOID)
			dist1 = ABS(resArray[resArray[i].hbonds[1].partner].resNum - 
			resArray[i].resNum);

		/* HELIX */
		if ( (resArray[i].hbonds[0].partner != VOID) &&
			(resArray[i].hbonds[1].partner != VOID) &&

			( ( ( (dist0 == 3) || (dist0 == 4) ) && (dist1 > 1) ) ||
				( ( (dist1 == 3) || (dist1 == 4) ) && (dist0 > 1) ) ) &&

			( psi < 100 ) )

			strcpy(resArray[i].dstruct3, "H");


		/* BETA */
		/* else if (old_get_beta(i, phi, psi, lastphi)); */
		else if (get_beta(i, phi));

		/* COIL */
		else strcpy(resArray[i].dstruct3, "C");

		lastphi = phi;
			
	}

}	/* assign_define3 */


/*********************************************************************
 * PURPOSE:	to assign the betas
 */
int get_beta(residx, phi)
int residx;
float phi;
{
int i;
int dist;
int partidx;
int partnum;

	for (i=0; i<MAX_HBONDS; i++) {
		partidx = resArray[residx].hbonds[i].partner;
		if (partidx != VOID)
			partnum = resArray[partidx].resNum;
		dist = ABS(partnum - resArray[residx].resNum);
		if ( (partidx != VOID ) &&
			(dist > 4) && 
			(resArray[residx].dstruct3[0] != 'H')  &&
			(phi < 0) ) {

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
int old_get_beta(i, phi, psi, lastphi)
int i;
float phi, psi, lastphi;
{

	psi = resArray[i].psi;
	phi = resArray[i].phi;

	if ( legitBond(resArray[i],i, BETA) &&
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
	if ( legitBond(resArray[i],i, ALSO_BETA) && (phi < -95) ) {
		strcpy(resArray[i].dstruct3, "B");
		return(TRUE);
	}

	return(FALSE);

}	/* old_get_beta */


/*********************************************************************
* PURPOSE: smooth out secondary structures
*/
void smooth_define3()
{

	smooth_helix();
	smooth_beta();

}	/* smooth_define3 */


/*********************************************************************
* PURPOSE:	to smooth helices
*/
void smooth_helix()
{
int i;
float phi, psi;

	/* check for pattern of HCHH or HHCH */
	for (i=0; i<lastResNum-3; i++) {

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

	for (i=1; i<lastResNum-1; i++) {
		if ( (DSTR(resArray[i-1]) != HELIX) && 
			(DSTR(resArray[i]) == HELIX) && 
			 (DSTR(resArray[i+1]) != HELIX) )

			strcpy(resArray[i].dstruct3, "C");
	}

}	/* smooth_helix */


/*********************************************************************
* PURPOSE:	to smooth the beta's
*/
void smooth_beta()
{
int i;

	for (i=1; i<lastResNum-1; i++) {
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
void old_smooth_beta()
{
int i;

	for (i=1; i<lastResNum-1; i++) {
		if ( (DSTR(resArray[i-1]) == BETA) && (DSTR(resArray[i]) == COIL) && 
			 (DSTR(resArray[i+1]) == BETA) )
			strcpy(resArray[i].dstruct3, "B");
	}

	for (i=1; i<lastResNum-1; i++) {
		if ( (DSTR(resArray[i-1]) != BETA) && (DSTR(resArray[i]) == BETA) && 
			 (DSTR(resArray[i+1]) != BETA) )
			strcpy(resArray[i].dstruct3, "C");
	}

}	/* smooth_beta */


/*********************************************************************
* PURPOSE: to filter out the seconary structure
*/
void filter_define3()
{
int i, j;
int strucCount = 1;
int strucLast = 0;

	for (i=1; i<=lastResNum; i++) {
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
int legitBond(RESIDUE residue, int resIdx, int bondType)
{
int i, bondDist;
int bond3, bond4;

	bond3 = bond4 = FALSE;

	for (i=0; i<MAX_HBONDS; i++) {

		bondDist = ABS((residue.hbonds[i].partner - residue.resNum));
		if (residue.hbonds[i].partner == VOID) 
			bondDist = 0;
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
