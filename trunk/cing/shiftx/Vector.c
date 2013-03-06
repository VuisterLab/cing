#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "vector.h"

#ifdef _WIN32 
  #include "pi.h"
#endif

VECTOR  cross( VECTOR a, VECTOR b )
{
  VECTOR   c;

  c.x = a.y*b.z - b.y*a.z;
  c.y = a.z*b.x - a.x*b.z;
  c.z = a.x*b.y - a.y*b.x;
  return(c);
}

VECTOR  normalize( VECTOR a )
{
  VECTOR   c;
  float    mag;
  
  mag = sqrt(a.x*a.x + a.y*a.y + a.z*a.z);
  c.x = a.x/mag;
  c.y = a.y/mag;
  c.z = a.z/mag;
  return(c);
}

VECTOR  diff( VECTOR a, VECTOR b )
{
  VECTOR    c;

  c.x = a.x - b.x;
  c.y = a.y - b.y;
  c.z = a.z - b.z;
  return(c);
}

VECTOR  add( VECTOR a, VECTOR b )
{
  VECTOR    c;

  c.x = a.x + b.x;
  c.y = a.y + b.y;
  c.z = a.z + b.z;
  return(c);
}

VECTOR  multiply( VECTOR a, float m )
{
  VECTOR    c;
  
  c.x = a.x*m;
  c.y = a.y*m;
  c.z = a.z*m;  
  return(c);
}

double  dot( VECTOR a, VECTOR b )
{
  return( a.x*b.x + a.y*b.y + a.z*b.z );
}

VECTOR  rotate( VECTOR r, VECTOR n, float theta )
{
  VECTOR    q;
  float     A, B, C;

  if( theta == 180 || theta == -180 )
  {
    A = -1.0;
    C = 0.0;
  }
  else
  {
    theta *= M_PI/180;
    A = cos(theta);
    C = sin(theta);
  }
  B = dot( n, r )*(1.0 - A);
  q.x = A*r.x + B*n.x - C*(r.y*n.z - r.z*n.y);
  q.y = A*r.y + B*n.y - C*(r.z*n.x - r.x*n.z);
  q.z = A*r.z + B*n.z - C*(r.x*n.y - r.y*n.x);
  return(q);
}


int  atm_vector( RESIDUE *r, char *alabel, VECTOR *v )
{
  ATOM    *q;

  q = r->atom;
  
  while( q != NULL )
  {
    /* printf("%s ",q->type); */
    if( !strcmp( q->type, alabel ) )
    {
      *v = q->p;
      return(0);
    }
    q = q->next;
  }
  /* gets(alabel); */
  return(1);  
}

void  no_vector( char *atom, int c )
{
  fprintf( stderr, "Vector for %s not found!\n", atom );
  if( c )
  {
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  return;
}

void  no_vectorA( char *atom, int c, int resno, char *res )
{
  fprintf( stderr, "Vector for %s not found! (res %s #%d)\n", atom, res, resno );
  if( c )
  {
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  return;
}


int  null_vector( VECTOR v )
{
  if( v.x == 0.0 && v.y == 0.0 && v.z == 0.0 )
    return(1);
  else
    return(0);
}
