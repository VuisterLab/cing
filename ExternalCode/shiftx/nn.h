#ifndef NN_H

#ifndef MAIN_H
#include "main.h"
#endif

#ifndef  VECTOR_H
#include "vector.h"
#endif

#ifndef CS_H
#include "cs.h"
#endif

typedef struct
{
  int      res_num;
  char     atom[6];
  VECTOR   p;
} NN_ATOM;

typedef struct NEIGHBOR
{
  char                 res_type;
  int                  res_num;
  char                 atom[5];
  float                dis;
  struct NEIGHBOR      *next, *last;
} NEIGHBOR;

NN_ATOM    resolve_atom( char *label );
RES        *AddResidue( RESIDUE *r, RES *pro, NN_ATOM *target );
NEIGHBOR   *search_neighbors( RES *pro, NN_ATOM target_atom, float radius );
void       display_neighbors( NEIGHBOR *nn, int sort );
RES        *CreateRES( RES *res );
ATM        *CreateATM( ATM *atom );
void       FreeRES( RES *r );
void	   DeleteRES(RES *r);
void       FreeNeighbor( NEIGHBOR *nn );
float      AddtoNextN15( char res );
void       NearestNeighborEffect( CSHIFT *cs );

#define    NN_H

#endif

