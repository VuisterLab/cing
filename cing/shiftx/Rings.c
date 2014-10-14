#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "psa.h"
#include "main.h"
#include "cs.h"
#include "rings.h"
#include "residue.h"
#include "vector.h"
#include "nn.h"
#include "hydrogens.h"

static RING  *CreateRing( RING *ring )
{
  RING    *new;

  new = (RING *) malloc( (unsigned) sizeof(RING) );
  if( new == NULL )
    {
      fprintf( stderr, "Memory allocation failure in creating RING link-list.\n" );
      fprintf( stderr, "Aborting...\n" );
      exit(1);
    }
  memset( new, 0, sizeof(RING) );
  if( ring != NULL )
    {
      ring->last = new;
      new->next = ring;
    }
  return(new);
}

void  FreeRings( RING *ring )
{
  RING    *p;
  
  /* Release RING link list */
  
  while( ring != NULL )
    {
      p = ring->next;
      free( ring );
      ring = p;
    }
  return;
}

void  aromatic_ring( RESIDUE *r, RING **ring )
{
  int         i;
  char        res;
  RING *rr;

  res = iupac_code(r->type);
  rr = *ring;
  /* Locate the vortices */

  switch(res)
    {
    case 'F':
    case 'Y':	 
      *ring = CreateRing( *ring );
      (*ring)->res_num = r->num;
      (*ring)->res_type = res;
      (*ring)->members = 6;


      if (atm_vector( r, "CG",  &((*ring)->r[0]) ) ||
	  atm_vector( r, "CD2", &((*ring)->r[1]) ) ||
	  atm_vector( r, "CE2", &((*ring)->r[2]) ) ||
	  atm_vector( r, "CZ",  &((*ring)->r[3]) ) ||
	  atm_vector( r, "CE1", &((*ring)->r[4]) ) ||
	  atm_vector( r, "CD1", &((*ring)->r[5]) )    )
	{
	  free(*ring);
	  *ring = rr;
	  r->errflags |= RES_ERR_MISSING_RING_MEMBERS;
	  return;
	  /*
	    fprintf( stderr, "Missing ring member in %d%s. (Code 1)\n", r->num, r->type );
	    exit(1);
	  */
	}
      (*ring)->normal = normalize( cross( diff( (*ring)->r[1], (*ring)->r[0] ),
					  diff( (*ring)->r[5], (*ring)->r[0] ) ) );
      switch(res)
	{
	case 'F':  (*ring)->I = 1.05;
	  break;
	case 'Y':  (*ring)->I = 0.92;
	  break;
	}
      break;

    case 'W':  /* The 6-member ring */
      *ring = CreateRing( *ring );
      (*ring)->res_num = r->num;
      (*ring)->res_type = res;
      (*ring)->members = 6;

      if( atm_vector( r, "CD2", &((*ring)->r[0]) ) ||
	  atm_vector( r, "CE3", &((*ring)->r[1]) ) ||
	  atm_vector( r, "CZ3", &((*ring)->r[2]) ) ||
	  atm_vector( r, "CH2", &((*ring)->r[3]) ) ||
	  atm_vector( r, "CZ2", &((*ring)->r[4]) ) ||
	  atm_vector( r, "CE2", &((*ring)->r[5]) )    )
	{
	  free(*ring);
	  *ring = rr;
	  r->errflags |= RES_ERR_MISSING_RING_MEMBERS;
	  return;
	  /*
	    fprintf( stderr, "Missing ring member in %d%s.(Code 2)\n", r->num, r->type );
	    exit(1);
	  */
	}
      (*ring)->normal = normalize( cross( diff( (*ring)->r[1], (*ring)->r[0] ),
					  diff( (*ring)->r[5], (*ring)->r[0] ) ) );
      (*ring)->I = 1.04;
 
      /* The 5-member ring */

      *ring = CreateRing( *ring );
      (*ring)->res_num = r->num;
      (*ring)->res_type = res;
      (*ring)->members = 5;
      if( atm_vector( r, "CG" , &((*ring)->r[0]) ) ||
	  atm_vector( r, "CD2", &((*ring)->r[1]) ) ||
	  atm_vector( r, "CE2", &((*ring)->r[2]) ) ||
	  atm_vector( r, "NE1", &((*ring)->r[3]) ) ||
	  atm_vector( r, "CD1", &((*ring)->r[4]) )    )
	{
	  free(*ring);
	  *ring = rr;
	  r->errflags |= RES_ERR_MISSING_RING_MEMBERS;
	  return;
	  /*
	    fprintf( stderr, "Missing ring member in %d%s.(Code 3)\n", r->num, r->type );
	    exit(1);
	  */
	}
      (*ring)->normal = normalize( cross( diff( (*ring)->r[1], (*ring)->r[0] ),
					  diff( (*ring)->r[4], (*ring)->r[0] ) ) );
      (*ring)->I = 0.90;
      break;

    case 'H':
      *ring = CreateRing( *ring );
      (*ring)->res_num = r->num;
      (*ring)->res_type = res;
      (*ring)->members = 5;
 
      if( atm_vector( r, "CG" , &((*ring)->r[0]) ) ||
	  atm_vector( r, "ND1", &((*ring)->r[1]) ) ||
	  atm_vector( r, "CE1", &((*ring)->r[2]) ) ||
	  atm_vector( r, "NE2", &((*ring)->r[3]) ) ||
	  atm_vector( r, "CD2", &((*ring)->r[4]) )    )
	{
	  free(*ring);
	  *ring = rr;
	  r->errflags |= RES_ERR_MISSING_RING_MEMBERS;
	  return;
	  /*
	    fprintf( stderr, "Missing ring member in %d%s.(Code 4)\n", r->num, r->type );
	    exit(1);
	  */
	}
       
      (*ring)->normal = normalize( cross( diff( (*ring)->r[1], (*ring)->r[0] ),
					  diff( (*ring)->r[4], (*ring)->r[0] ) ) );
      (*ring)->I = 0.43;
      break;
    }
  return;
}

/* ri = position of the i-th member in the ring                  */
/* rj = position of the j-th member in the ring                  */
/* p  = position of proton                                       */
/* po = position of proton projected onto the plane of the ring. */
/* n  = unit vector normal to the plane of the ring.             */

/*static*/  float  pairwise_gfactor( VECTOR ri, VECTOR rj, VECTOR p, VECTOR po, 
				     VECTOR n )
{
  float   dis, area, proj, sij;
  float   b, h;
  VECTOR  u, v, w, qi, qj, m;
  int     s;

  /* Calculate the distance factor */

  qi = diff( p, ri );
  qj = diff( p, rj );
  dis = pow(sqrt(dot( qi, qi )),-3.0) + pow(sqrt(dot( qj, qj )),-3.0);
  
  /* Compute the projected area */
  
  u = diff( rj, ri );
  b = sqrt(dot(u,u));
  v = diff( po, ri );
  w = normalize( rotate( u, n, 90.0 ) );
  h = fabs( dot( v, w ) );
  area = (b*h) / 2.0;
  
  /* Determine the sign */
  
  qi = diff( ri, po );
  qj = diff( rj, po );
  m = cross( qi, qj );
  s = (dot( m, n ) < 0 ) ?  1 : -1;
  
  return(s*area*dis);
}

static  float  ring_current_shift( RING *r, ATM *atm, int resno ) // SJN DEBUG
{
  float    G=0.0, rc_factor;
  int      i;
  VECTOR   u, v, w;
	
  /*    Compute the projection of the proton on the molecular plane   */
	
  u = diff( atm->r, r->r[0] );
  v = multiply( r->normal, dot( u, r->normal ) );
  w = add( r->r[0], diff( u, v ) );
	
  /* Be carefull here. This is not supposed to be a double summation. */
  /* It is only a sum over the close circuit in accordance with       */
  /*                                                                  */
  /* C.W. Haign and R.B. Mallion, Progress in NMR Spectroscopy, V13   */
  /* (1980) 303.                                                      */
  /*                                                                  */
  /* For a six-member ring, the sum is 1-2, 2-3, 3-4, 4-5, 5-6, 6-1.  */
  /* For a five-member ring, it is 1-2, 2-3, 3-4, 4-5, 5-1.           */
  /*                                                                  */
  /* Be very careful with papers published by other authors: they do  */
  /* not give accurate information on the Haign-Mallion theory.       */
	
  for( i=0; i<r->members-1; i++ )
    {
      G += pairwise_gfactor( r->r[i], r->r[i+1], atm->r, w, r->normal );
    }
	
  /* Close the loop */
	
  G += pairwise_gfactor( r->r[r->members-1], r->r[0], atm->r, w, r->normal );
	
  if( !strcmp(atm->type, "HN") )
    {
      rc_factor = HNRC;
    }
  else if( !strcmp(atm->type, "HA") || !strcmp(atm->type, "1HA") || !strcmp(atm->type, "2HA")
	   || !strcmp(atm->type,"HA2") || !strcmp(atm->type,"HA3"))
    {
      rc_factor = HARC;
    }
  else if( !strcmp(atm->type, "CA") )  
    {
      rc_factor = CARC;
      //		printf("%d %d %f %f %f\n",resno,r->res_num,rc_factor , r->I,  G);
    }
  else if( !strcmp(atm->type, "N15")  || !strcmp(atm->type,"N") )
    {
      rc_factor = N15RC;
    }
  else if( !strcmp(atm->type, "CB") )
    {
      rc_factor = CBRC;
    }
  else if( !strcmp(atm->type, "CO") )
    {
      rc_factor = CORC;
    }
  else 
    {
      rc_factor = HSRC;  // ADDNEW
    }
  return( rc_factor*r->I*G);
}

void  RingShiftedAtoms( RESIDUE *r, RES **list )
{
  ATOM    *p;
  int i;   // ADDNEW

  *list = CreateRES( *list );
  (*list)->num = r->num;
  (*list)->type =  iupac_code( r->type );
	
  p = r->atom;
  while( p != NULL )
    {
      /*
	for (i = 0; i < NHATOMS; i++) // ADDNEW
	{
	if (!strcmp(p->type,hatoms[i].name))
	{
	break;
	}
	}
      */

      //printf("p->type=%s\n", p->type);
      
      if (p->hIndex != -1 ||
	  //if(i != NHATOMS ||
	  !strcmp( p->type, "CA" )  || !strcmp( p->type, "HA" )  || 
	  !strcmp( p->type, "1HA" ) || !strcmp( p->type, "2HA" ) || 
	  !strcmp( p->type, "HN" )  || !strcmp( p->type, "CB" )  || 
	  !strcmp( p->type, "CO" )  || !strcmp( p->type, "N" )      )
	{
	  (*list)->atom = CreateATM( (*list)->atom );
	  strcpy( (*list)->atom->type, p->type );
	  (*list)->atom->hIndex = p->hIndex;
	  (*list)->atom->r = p->p;
	}
      p = p->next;
    }
  return;
}

CSHIFT  *RingCurrent( RING *ring, RES *list )
{
  RES             *p;
  ATM             *q;
  RING            *r;
  float            overall;
  CSHIFT          *cs=NULL, cpt;
  char            atom[5];
  int i;
	
  p = list;  
  while( p != NULL )
    {
      cs = CreateCS( cs );
      cs->n = p->num;
      cs->type = p->type;
      q = p->atom;
      while( q != NULL )
	{
	  overall = 0.0;
	  r = ring;
	  while( r != NULL )
	    {
	      /* Self-interaction is included */
				
	      /*
		if( r->res_num == p->num )
		{
		r = r->next;
		continue;
		}
	      */
				
	      overall += ring_current_shift( r, q ,p->num);
	      /*
		if (!strcmp(q->type,"CA"))
		{
		printf("%d %f\n",p->num,overall);
		}
	      */
	      r = r->next;
	    }
	  if( overall < 0 ) 
	    {
	      overall *= 1.1;
	    }
			
	  strcpy( atom, q->type );
	  
	  if (q->hIndex != -1)
	    {
	      cs->hside[q->hIndex] = overall;
	    }
			
	  q = q->next;
			
	  if( !strcmp( atom, "CA" ) )
	    {
	      cs->ca = overall;
	      continue;
	    }
	  if( !strcmp( atom, "CB" ) )
	    {
	      cs->cb = overall;
	      continue;
	    }
	  if( !strcmp( atom, "HA" ) || !strcmp( atom, "1HA" ) || !strcmp( atom, "2HA"))
	    {
	      if( cs->ha == 0 )
		{
		  cs->ha = overall;
		}
	      else
		{
		  cs->ha = (cs->ha + overall)/2.0;
		}
	      continue;
	    }
	  if( !strcmp( atom, "CO" ) )
	    {
	      cs->co = overall;
	      continue;
	    }
	  if( !strcmp( atom, "HN" ) )
	    {
	      cs->hn = overall;
	      continue;
	    }
	  if( !strcmp( atom, "N" ) )
	    {
	      cs->n15 = overall;
	      continue;
	    }
	  /*
	    for (i = 0; i < NHATOMS; i++)   // ADDNEW
	    {
	    if (!strcmp(atom,hatoms[i].name))
	    {
	    cs->hside[i] = overall;
	    continue;
	    }
	    }
	  */
	}
      p = p->next;
    } 
  return(cs);
}
