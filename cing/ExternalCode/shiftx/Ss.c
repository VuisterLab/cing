
/*
	file: ss.c
	contains calculation routines for the secondary structure 
*/


#include "vmain.h"

void do_consensus(),
	bturn_ss(),
	check_turn(),
	smooth_ss();

			 
/*********************************************************************
 * PURPOSE: to calcualte all of the secondary structures,
 *          including the consensus and smoothing
 */
void do_ss(char *infile)
{
	int i,j;

	strcpy(pdbFname,infile);  /* SJN */

 	/* initialize residue array */
	for (i=0; i<MAX_RES_NUM; i++) {
		strcpy(resArray[i].name, "");
		resArray[i].resNum = -1;
		for (j=0; j<MAX_HBONDS; j++) {
			resArray[i].sidebond[j].partner = VOID;
			resArray[i].hbonds[j].partner = VOID;
		}
		resArray[i].ssbond = resArray[i].ssdist = VOID;
		for (j=0; j<NUM_COORDS; j++)
		{
			resArray[i].coords[j].x = resArray[i].coords[j].y =
			resArray[i].coords[j].z = VOID;
		}
	}
	input_vadar();
		
    /*  calculate secondary structure using masks */
    define1();

    /* calculate secondary structure, using hbond information */
    define3();

    /* calculate consensus secondary structure */
    do_consensus();

    /* incorporate the bturn info into the secondary structures */
    bturn_ss();

    /* smooth all secondary structures */
    smooth_ss();

}   /* do_ss */


/*********************************************************************
 * PURPOSE: to calculate a consensus secondary structure
 */
void do_consensus()
{
int i;

	for (i=0; i<lastResNum; i++) {

		if ( (strcmp(resArray[i].dstruct1, resArray[i].dstruct2)==0) ||
			(strcmp(resArray[i].dstruct1, resArray[i].dstruct3)==0) )
			strcpy(resArray[i].consens, resArray[i].dstruct1);

		else if (strcmp(resArray[i].dstruct2, resArray[i].dstruct3)==0)
			strcpy(resArray[i].consens, resArray[i].dstruct2);

		else strcpy(resArray[i].consens, "C");

	}

}	/* do_consensus */


/*********************************************************************
* PURPOSE:  to place a helix n-cap on the consensus and the other
*			structures.
*/
void do_consens_caps(i)
int i;
{
short j;
short diff3, diff4;

	/* placing helix N-cap
	 * look for CCHHH
	 * then look at the i+1 position
	 */
	if (i+4 > lastResNum)
		return;

	if ( (strcmp(resArray[i].consens, "C") == 0) &&
	     (strcmp(resArray[i+1].consens, "C") == 0) &&
	     (strcmp(resArray[i+2].consens, "H") == 0) &&
	     (strcmp(resArray[i+3].consens, "H") == 0) &&
	     (strcmp(resArray[i+4].consens, "H") == 0) ) {

		diff3 = diff4 = FALSE;
		for (j=0; j<MAX_HBONDS; j++) {
			if ( (resArray[i+1].hbonds[j].partner != VOID) &&
			   (ABS(resArray[i+1].hbonds[j].partner-resArray[i+1].resNum) == 3))
				diff3 = TRUE;
			if ( (resArray[i+1].hbonds[j].partner != VOID) &&
			   (ABS(resArray[i+1].hbonds[j].partner-resArray[i+1].resNum) == 4))
				diff4 = TRUE;
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
void do_consens_bridge(i)
int i;
{
short j, diff4;

	/* placing helix N-cap
	 * look for CCC
	 * then look at the i+1 position
	 */
	if (i+2 > lastResNum)
		return;

	if ( (strcmp(resArray[i].consens, "C") == 0) &&
	     (strcmp(resArray[i+1].consens, "C") == 0) &&
	     (strcmp(resArray[i+2].consens, "C") == 0) ) {

		diff4 = FALSE;
		for (j=0; j<MAX_HBONDS; j++) {
			if ( (resArray[i+1].hbonds[j].partner != VOID) &&
			(ABS(resArray[i+1].hbonds[j].partner-resArray[i+1].resNum) > 4) )
				diff4 = TRUE;
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


/*********************************************************************
 * PURPOSE: to set all four of the secondary structures to C for the
 *          middle two res's in any I, I', II, II' turn.
 */
void bturn_ss()
{
int i;

    for (i=0; i<(lastResNum-4); i++) {

        check_turn(i, "  I ");
        check_turn(i, " I' ");
        check_turn(i, " II ");
        check_turn(i, " II'");

    }

}   /* bturn_ss */


/*********************************************************************
 * PURPOSE: subroutine used by bturn_ss
 */
void check_turn(i, bturn)
int i;
char *bturn;
{
int j;
int same = TRUE;

    for (j=i; j<i+4; j++)
        same = same && (strcmp(resArray[j].bturn, bturn) == 0);

/*  the one exception to this rule is for turns of type I
 *  where there are hydrogen bonds
 */
    if ( (strcmp(bturn, "  I ") == 0) && (hbonded(i)) ) ;

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


/************************************************************************
* PURPOSE: to see if there are double hydrogen bonds
*/
int hbonded(i)
int i;
{
    if ( (resArray[i+1].hbonds[0].partner != VOID) &&
       (resArray[i+1].hbonds[1].partner != VOID) &&
       (resArray[i+2].hbonds[0].partner != VOID) &&
       (resArray[i+2].hbonds[1].partner != VOID) )
       return(TRUE);
    else return(FALSE);

}   /* hbonded */


/*********************************************************************
 * PURPOSE: smooth all of the secondary structures
 */
void smooth_ss()
{
int i, j;
int ss_type;
int strucCount;
int strucThis, strucLast;

    for (ss_type=0; ss_type<4; ss_type++) {

        strucCount = 0;
        strucLast = getType(resArray[0], ss_type);

        for (i=1; i<=lastResNum; i++) {

            strucThis = getType(resArray[i], ss_type);
            if ( strucThis == strucLast)
                strucCount++;
            else {
                if ( (strucLast == HELIX) && (strucCount < 3) )
                    for (j=i-1; j>=i-strucCount; j--)
                        assignSS(j, ss_type, "C");
                if ( (strucLast == BETA) && (strucCount < 3) )
                    for (j=i-1; j>=i-strucCount; j--)
                        assignSS(j, ss_type, "C");
                strucCount = 1;
            }
            strucLast = strucThis;
        }
    }

    /* include helix caps and beta bridges */
    for (i=0; i<lastResNum; i++) {
        do_consens_caps(i);
        do_consens_bridge(i);
    }

}   /* smooth_ss */



