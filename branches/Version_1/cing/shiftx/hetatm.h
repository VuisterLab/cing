#ifndef   HETATM_H

#ifndef   VECTOR_H
#include  "vector.h"
#endif

typedef struct HETATM
{
  VECTOR            r;
  float             BFactor;
  float             occupancy;
  int               id;
  struct HETATM     *next;
  struct HETATM     *last;
} HETATM;

HETATM   *AddWaterOxy( char *buff, HETATM *p );
void      FreeWaterOxy( HETATM *h );

#define    HETATM_H

#endif
