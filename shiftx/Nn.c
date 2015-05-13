#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "psa.h"
#include "main.h"
#include "residue.h"
#include "vector.h"
#include "cs.h"
#include "nn.h"


/* SJN - matrix of nearest neighbour effects, 20x20 */
float nn_matrix[400] = 
{0.65 	,-1	,1.14 	,0.33 	,-1	,1.86 	,-1	,1.74 	,1.23 	,0.85 	,-1	,0.57 	,-1	,-1	,1.32 	,1.32 	,1.11 	,0.36 	,-1	,2.05 
,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-0.11 	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1
,-0.16 	,-1	,-1	,-0.79 	,-1	,2.29 	,-1	,-0.31 	,-0.22 	,-0.26 	,-1	,-0.03 	,-1	,-1	,-1	,0.26 	,0.59 	,0.24 	,-1	,-1
,0.05 	,-1	,0.24 	,-1	,-1	,1.16 	,-1	,0.29 	,-1.48 	,0.36 	,-1	,-1	,-1	,-0.04 	,-1	,-0.17 	,0.83 	,-1	,-1	,-1
,-1	,-1	,-1	,2.21 	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,2.65 	,0.40 	,-1	,-1
,0.71 	,-1	,-0.63 	,-0.15 	,-1	,0.13 	,-1	,-1.80 	,-2.05 	,0.04 	,-1	,2.01 	,-1	,-1	,-2.08 	,-0.68 	,-0.52 	,-1.22 	,-1	,-0.28 
,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-0.38 	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1
,-1.85 	,-1	,-0.43 	,-1.49 	,-1.23 	,-1	,-1	,0.08 	,-0.74 	,-0.34 	,-1	,-1.16 	,-1	,-1.15 	,-1.63 	,-1	,-1.18 	,-1	,-1	,-1
,-1.20 	,-1	,-1	,0.18 	,-1	,-0.82 	,-1	,-1.09 	,-1.07 	,0.46 	,-1	,0.35 	,-1	,-1	,0.57 	,0.16 	,0.34 	,-0.13 	,-1	,-1.00 
,1.38 	,-1	,0.82 	,-0.09 	,1.15 	,0.38 	,-1	,1.46 	,0.90 	,2.61 	,-1	,-1.00 	,-1	,-0.03 	,-1.26 	,1.10 	,-0.30 	,1.08 	,-1	,-1
,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-0.26 	,-1	,-1
,0.28 	,-1	,-1	,0.98 	,1.31 	,-0.29 	,-1	,-0.44 	,-1	,0.18 	,-1	,-0.56 	,-1	,0.14 	,-2.14 	,1.01 	,0.25 	,-1	,-1	,-1
,-1	,-1	,0.67 	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,1.15 	,-1	,-1	,-1	,-1
,-1.04 	,-1	,-1	,-1	,-1	,0.44 	,-1	,-1	,-1	,-0.62 	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1
,0.28 	,-1	,0.52 	,1.91 	,-1	,0.36 	,-1	,-1	,-1	,0.06 	,-1	,1.03 	,-1	,-0.14 	,-1	,-1.47 	,0.42 	,-1	,-1	,-1
,-1.69 	,-1	,-4.21 	,-1.74 	,-1	,-1	,-1	,-1	,-1	,-1.62 	,-1	,-1	,-1	,-1	,-1	,-0.60 	,-1.89 	,-0.43 	,-1	,-0.58 
,-1.65 	,-1	,-0.72 	,-1	,-1	,-1.81 	,-1	,0.58 	,-0.91 	,-1.94 	,-1	,-0.44 	,-1	,-1	,-1	,-1	,-1	,0.88 	,-1	,-1
,-1.74 	,-1	,0.10 	,-0.59 	,-1.68 	,-1.05 	,-1	,0.63 	,-2.07 	,0.29 	,-1	,1.67 	,-1	,-1	,-1.00 	,-0.78 	,-1	,-0.74 	,-1	,-1
,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1	,-1
,-1	,-1	,-1	,1.77 	,-1	,0.74 	,-1	,-1	,1.45 	,-1	,-1	,-1.21 	,-1	,-1	,1.21 	,-0.51 	,-0.64 	,-1	,-1	,-1};


NN_ATOM    resolve_atom( char *label )
{
  NN_ATOM      target;
  char         residue[20], *p;

  if( (p=strchr( label, ':' ))==NULL )
  {
    fprintf( stderr, "Syntax error in atom specification: %s\n", label );
    exit(1);
  }
  p++;
  strcpy( target.atom, p );
  strncpy( residue, label, strlen(label)-strlen(p) );
  sscanf( residue, "%d", &target.res_num );

  /* Initialize positional vector to a null vector */

  target.p.x = 0.0;
  target.p.y = 0.0;
  target.p.z = 0.0;

  return(target);
}

ATM  *CreateATM( ATM *atom )
{
  ATM    *new;

  new = (ATM *) malloc( (unsigned) sizeof(ATM) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(ATM) );
  if( atom != NULL )
  {
    atom->last = new;
    new->next  = atom;
  }
  new->hIndex = -1;
  return(new);
}

static void  FreeATM( ATM *atom )
{
  ATM     *p;
  
  while( atom != NULL )
  {
    p = atom->next;
    free( (char *) atom );
    atom = p;
  }
  return;
}

RES  *CreateRES( RES *res )
{
  RES    *new;

  new = (RES *) malloc( (unsigned) sizeof(RES) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(RES) );
  if( res != NULL )
  {
    res->last = new;
    new->next = res;
  }
  return(new);
}


void  FreeRES( RES *r )
{
  RES    *p;
  
  while( r != NULL )
  {
    FreeATM( r->atom );
    p = r->next;
    free( (char *) r );
    r = p;
  }
  return;
}

RES   *AddResidue( RESIDUE *r, RES *pro, NN_ATOM *target )
{
  RES   *new;
  ATOM  *p;

  new = CreateRES( pro );

  /* Transfer the residue info */
  
  new->type = iupac_code( r->type );
  new->num = r->num;

  /* Transfer the atomic information */
  
  p = r->atom;
  while( p!=NULL )
  {
    if( target!=NULL && r->num==target->res_num && !strcmp( p->type, target->atom ) )
    {
      /* Found the target */
    
      target->p = p->p;
      
      /* Exclude target from the link-list */
    }
    else
    {
      new->atom = CreateATM( new->atom );
      strcpy( new->atom->type, p->type );
      new->atom->r = p->p;
	  new->atom->hIndex = p->hIndex;
    }
    p = p->next;
  }

  return(new);
}

static  NEIGHBOR  *CreateNeighbor( NEIGHBOR *nn )
{
  NEIGHBOR    *new;

  new = (NEIGHBOR *) malloc( (unsigned) sizeof(NEIGHBOR) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating NEIGHBOR link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(NEIGHBOR) );
  if( nn != NULL )
  {
    nn->last = new;
    new->next = nn;
  }
  return(new);
}

void  FreeNeighbor( NEIGHBOR *nn )
{
  NEIGHBOR    *p;
  
  while( nn != NULL )
  {
    p = nn->next;
    free( (char *) nn );
    nn = p;
  }
  return;
}

NEIGHBOR  *search_neighbors( RES *pro, NN_ATOM target_atom, float radius )
{
  NEIGHBOR     *new=NULL;
  RES          *p;
  ATM          *q;
  VECTOR       s;
  float        dis;


  while( pro != NULL )
  {
    q = pro->atom;
    
    /* Forward to the end of the link-list                 */
    /* This is just to make the order the atoms look nicer */
    
    while( q->next != NULL )  q = q->next;
    
    while( q != NULL )
    {
      s = diff( q->r, target_atom.p );
      dis = sqrt(dot( s, s ));
      
      if( dis <= radius )
      {
        new = CreateNeighbor( new );
        new->res_type = pro->type;
        new->res_num = pro->num;
        strcpy( new->atom, q->type );
        new->dis = dis;
      }
      q = q->last;
    }

    /* Remove this residue and the associated atoms */

    while( pro->atom != NULL )
    {
      q = pro->atom->next;
      free( pro->atom );
      pro->atom = q;
    }
    p = pro->next;
    free( pro );
    pro = p;
  }

  return(new);
}

void    display_neighbors( NEIGHBOR *nn, int sort )
{
  NEIGHBOR    *p, *q;
  float       min_dis;
  char        label[20];

  if( sort == TRUE )
  {
    while( nn != NULL )
    {
      p = nn;
      min_dis = 1.0E+30;
      while( p!=NULL )
      {
        if( p->dis < min_dis )
        {
          q = p;
          min_dis = p->dis;
        }
        p = p->next;
      }
      sprintf( label, "%c%d:", q->res_type, q->res_num );
      fprintf( stdout, "%-10s%10s   %.4f\n", label, q->atom, q->dis );
      if( q->next != NULL )  q->next->last = q->last;
      if( q->last != NULL )  q->last->next = q->next;
      else  nn = q->next;
      free(q);
    }
  }
  else
  {
    p = nn;
    while( p!=NULL )
    {
      sprintf( label, "%c%d:", p->res_type, p->res_num );
      fprintf( stdout, "%-10s%10s   %.4f\n", label, p->atom, p->dis );
      q = p->next;
      free(p);
      p = q;
    }
  }
  return;
}


#define   AVE_NH   125.0

float    AddtoNextN15( char res )
{
  switch(res)
  {
    case 'A':  return( 123.2 - AVE_NH );
               break;
    case 'C':  return( 126.7 - AVE_NH );
               break;
    case 'D':  return( 124.8 - AVE_NH );
               break;
    case 'E':  return( 125.2 - AVE_NH );
               break;
    case 'F':  return( 126.4 - AVE_NH );
               break;
    case 'G':  return( 124.0 - AVE_NH );
               break;
    case 'H':  return( 125.8 - AVE_NH );
               break;
    case 'I':  return( 128.2 - AVE_NH );
               break;
    case 'K':  return( 125.6 - AVE_NH );
               break;
    case 'L':  return( 125.0 - AVE_NH );
               break;
    case 'M':  return( 125.1 - AVE_NH );
               break;
    case 'N':  return( 124.7 - AVE_NH );
               break;
    case 'P':  return( 124.4 - AVE_NH );
               break;
    case 'Q':  return( 125.3 - AVE_NH );
               break;
    case 'R':  return( 125.4 - AVE_NH );
               break;
    case 'S':  return( 125.9 - AVE_NH );
               break;
    case 'T':  return( 126.4 - AVE_NH );
               break;
    case 'V':  return( 127.9 - AVE_NH );
               break;
    case 'W':  return( 126.8 - AVE_NH );
               break;
    case 'Y':  return( 126.8 - AVE_NH );
               break;
  }
  fprintf( stderr, "AddtoNextN15: unknown residue - %c\n", res );
  exit(1);
}

void  NearestNeighborEffect( CSHIFT *cs )  /* SJN */
{
  CSHIFT    *p;
  float     nn_effect=0.0;
  int lastidx=-1;

  p = cs;
  while( p != NULL )
  {
    if (p->next != NULL) {
      nn_effect = nn_matrix[rc_idx(p->next->type) * 20 + rc_idx(p->type)];
      if (nn_effect != -1.0) {
        p->n15 -= nn_effect;
      }
    }
  
    /*
    if( nn_effect != 0.0 && p->n15 != NA ) {
      p->n15 += nn_effect;
    }
    nn_effect = AddtoNextN15( p->type );
    
    lastidx = rc_idx(p->type);
		*/
    p = p->next;
  }
  return;
}
