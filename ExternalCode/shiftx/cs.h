#ifndef CS_H

#ifndef MAIN_H
#include "main.h"
#endif

#define   N_HA    0
#define   N_HN    1
#define   N_N15   2
#define   N_CA    3
#define   N_CB    4
#define   N_CO    5

typedef struct CSHIFT
{
	char            type;
	unsigned int    n;
	float           ca;
	float           cb;
	float           ha;
	float           co;
	float           hn;
	float           n15;
	float			hside[NHATOMS];
	float           hb;
	/* ADDNEW */
	struct CSHIFT   *next, *last;
} CSHIFT;

CSHIFT   *CreateCS( CSHIFT *cs );
CSHIFT   *CopyCS( CSHIFT *oldcs );
void     FreeCShifts( CSHIFT *cs );
CSHIFT   *FindCS( CSHIFT *cs, int n );
void     AddCShifts( CSHIFT *a, CSHIFT *b );
void     AddCShiftsHB( CSHIFT *a, CSHIFT *b );
void     AdjustCYS( CSHIFT *cs, CSHIFT *ss );
void ProcessCShifts(CSHIFT *cs);

#define    CS_H

#endif
