
/*
	file:		stats.c
	purpose:	to do all of the statistical calculations for vadar
*/

#include "vmain.h"
#include <math.h>

#define	EQUALS(a,b) (strcmp(a,b) == 0)
#define	MATCHES(a,b) (strncmp(a,b,2) == 0)

#define EPA 0 		/* exposed polar area */
#define ENA 1		/* exposed non polar area */
#define ECA 2		/* exposed charged area */
#define MAIN 0
#define MAIN_EXP 1
#define SIDE 2
#define SIDE_EXP 3

/*...................global variables......................*/
int		begin,
		lastType,
		lastNumSequence,
		lastResNum,
		numburied,
		numpacking;
float	standardAsa[NUMAA],
		standardVol[NUMAA],
		molWeightTable[NUMAA],
		fef, expfef,
		molWeight;
