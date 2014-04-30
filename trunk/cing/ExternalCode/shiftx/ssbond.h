#ifndef  SSBOND_H

#ifndef  VECTOR_H
#include "vector.h"
#endif

typedef struct SSBOND
{
  int              resA;
  char			   insCodeA;	
  int              resB;
  char			   insCodeB;
  VECTOR           CA_A;
  VECTOR           SG_A;
  VECTOR           CA_B;
  VECTOR           SG_B;
  struct SSBOND   *next;
} SSBOND;

void  ReadSSPairs( FILE *fpt, SSBOND **ss, char useChain );
void     FreeSSBond( SSBOND  *ss );
void     ReadSSCoordinates( RESIDUE *r, SSBOND *bonds );
CSHIFT   *DiSulfideBonds( SSBOND *bonds );
typedef struct CYSres
{
     int res;
     float CA[3];
     float SG[3];
     char chain;
     
} CYSres;
#define SSBOND_H

#endif
