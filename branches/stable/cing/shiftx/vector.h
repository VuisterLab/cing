#ifndef  VECTOR_H

#ifndef  MAIN_H
#include "main.h"
#endif


VECTOR   cross( VECTOR a, VECTOR b );
VECTOR   normalize( VECTOR a );
VECTOR   diff( VECTOR a, VECTOR b );
VECTOR   add( VECTOR a, VECTOR b );
VECTOR   multiply( VECTOR a, float m );
double    dot( VECTOR a, VECTOR b );
VECTOR   rotate( VECTOR r, VECTOR n, float theta );
int      atm_vector( RESIDUE *r, char *alabel, VECTOR *v );
void     no_vector( char *atom, int c );
void  no_vectorA( char *atom, int c, int resno, char *res );
int      null_vector( VECTOR v );


#define  NULL_VECTOR (VECTOR) { 0.0, 0.0, 0.0 }

#define  VECTOR_H

#endif
