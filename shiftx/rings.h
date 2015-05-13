#ifndef  RINGS_H

#ifndef MAIN_H
#include "main.h"
#endif

#ifndef CS_H
#include "cs.h"
#endif

typedef struct RING
{
  int                      res_num;
  int                      members;
  char                     res_type;
  VECTOR                   r[6];
  VECTOR                   normal;
  float                    I;
  struct RING              *next, *last;
} RING;

void    aromatic_ring( RESIDUE *r, RING **ring );
void    FreeRings( RING *ring );
void    RingShiftedAtoms( RESIDUE *r, RES **list );
CSHIFT  *RingCurrent( RING *ring, RES *list );

#define HNRC    7.058954
#define HARC    5.13048
#define HSRC    5.13048		// ADDNEW
#define N15RC   1.0        /* Uncalibrated */
#define CARC    1.5
#define CBRC    1.0        /* Uncalibrated */
#define CORC    1.0        /* Uncalibrated */

#define RINGS_H

#endif
