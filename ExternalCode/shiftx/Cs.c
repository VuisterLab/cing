#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "cs.h"


CSHIFT *CopyCS(CSHIFT *cs) /* SJN */
{
	CSHIFT *newcs=NULL,*p,*next,*last;

	if (cs == NULL)
	{
		return(NULL);
	}

	p = cs;

	while (p != NULL)
	{
		newcs = CreateCS(newcs);
		next = newcs->next;
		last = newcs->last;

		memmove(newcs,p,sizeof(CSHIFT));
		newcs->next = next;
		newcs->last = last;
		p = p->next;
	}
	return(newcs);
}


CSHIFT *CreateCS( CSHIFT *cs )
{
  CSHIFT    *new;

  new = (CSHIFT *) malloc( (unsigned) sizeof(CSHIFT) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating CSHIFT link-list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(CSHIFT) );
  
  if( cs != NULL )
  {
    new->next = cs;
    cs->last = new;
  }

  return(new);
}

void  FreeCShifts( CSHIFT *cs )
{
  CSHIFT   *p;
  
  while( cs != NULL )
  {
    p = cs->next;
    free( cs );
    cs = p;
  }
  return;
}

CSHIFT  *FindCS( CSHIFT *cs, int n )
{
  CSHIFT   *p;

  p = cs;
  while( p != NULL )
  {
    if( p->n == n ) {
      return(p);
    }
    p = p->next;
  }
  return(NULL);
}

void     AddCShifts( CSHIFT *a, CSHIFT *b )
{
  CSHIFT    *p, *q;
  int i;

  p = a;
  while( p != NULL )
  {
    if( (q=FindCS( b, p->n ))!= NULL )
    {
      /* CA get the additional amount from HA */
      
      if( p->ca != NA ) 
	  {
		  p->ca += q->ca + CA_HA_FACTOR * q->ha; /* SJN WTF */
	  }
      if( p->cb != NA )
	  {
		  p->cb += q->cb;
	  }
      if( p->co != NA )
	  {
		  p->co += q->co;
	  }
      if( p->ha != NA ) 
	  {
		  p->ha += q->ha;
	  }
      if( p->hn != NA )
	  {
		  p->hn += q->hn;
	  }
 
	  for (i = 0; i < NHATOMS; i++)  // ADDNEW
	  {
		  if (p->hside[i] != NA)
		  {
			  p->hside[i] += q->hside[i];
		  }
	  }
      /* N15 gets 5 times as much from HN */
      
       if( p->n15 != NA )  p->n15 += q->n15 + N15_HN_FACTOR * q->hn;  /* SJN WTF */
    }
    p = p->next;
  }
  return;
}

void     AddCShiftsHB( CSHIFT *a, CSHIFT *b )
{
	CSHIFT    *p, *q;
	int i;
	
	p = a;
	while( p != NULL )
	{
		if( (q=FindCS( b, p->n ))!= NULL )
		{
			/* CA get the additional amount from HA */
			
			if( p->ca != NA ) 
			{	
				p->ca += q->ca + CA_HA_FACTOR * q->ha; /* SJN WTF */
			}

			if( p->ha != NA )   p->ha  += q->ha;
			if( p->hn != NA )   p->hn  += q->hn;
			
			for (i = 0; i < NHATOMS; i++)
			{
				if (p->hside[i] != NA)
				{
					p->hside[i] += q->hside[i];
				}
			}
			
			/* N15 gets some proportion (N15_HN_FACTOR) of the HN shift */
			
			if( p->n15 != NA ) 
			{
				p->n15 += N15_HN_FACTOR * q->hn; /* SJN WTF */
			}
		}
		p = p->next;
	}
	return;
}

void  AdjustCYS( CSHIFT *cs, CSHIFT *ss )
{
  CSHIFT     *p, *q;

  p = cs;
  while( p != NULL )
  {
    if( p->type == 'C' && p->ca != NA )
    {
      if( (q=FindCS( ss, p->n ))==NULL )
      {
        p->ca += 2.5;
      }
      else
      {
        p->ca = q->ca;
      }
    }
    p = p->next;
  }
  return;
}


void ProcessCShifts(CSHIFT *cs)
{
	CSHIFT *cpt;
/*
	for (cpt = cs; cpt != NULL; cpt = cpt->next)
	{
		cpt->ca += cpt->ha;
		cpt->n15 += 5.0 * cpt->hn;
	}
*/
}

/*
  added by xiaoli

  if a protein is deuterated, the shifts are all reduced by a fraction of a ppm, depending on the type of
  nucleus. 13Ca = -0.43 ppm, 13Cb = -0.82 ppm, 15N = -0.23 ppm
*/
void AdjustDeuteration(CSHIFT *cs)
{
	CSHIFT *cpt;

	for (cpt = cs; cpt != NULL; cpt = cpt->next)
	  {
	    cpt->ca -= 0.43;
	    cpt->n15 -= 0.23;
	    cpt->cb -= 0.82;
	  }
	
}

