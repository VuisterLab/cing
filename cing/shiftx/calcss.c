
/*
	file: ss.c
	contains calculation routines for the secondary structure 
*/


#include "vmain.h"

/*********************************************************************
 * PURPOSE: to calcualte all of the secondary structures,
 *          including the consensus and smoothing
 */
void do_ss()
{
	int i,j;

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


