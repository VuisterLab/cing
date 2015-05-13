#ifndef   OPTIMIZE_H

#ifndef CS_H
#include "cs.h"
#endif

float   CAResponse( float x, char res );
float   HNResponse( float x, char res );
float   HAResponse( float x, char res );
void Optimize(RESIDUE *Rz,CSHIFT *cs,long int rno);

#define   OPTIMIZE_H

#endif
