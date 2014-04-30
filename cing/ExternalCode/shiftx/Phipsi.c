#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "cs.h"
#include "phipsi.h"
#include "matrices.h"
#include "rc.h"
#include "residue.h"
#include "cspline.h"

static  float   phi[MATRIX_ROWS+1], psi[MATRIX_COLUMNS+1];

static  float **Matrix( float mat[][MATRIX_COLUMNS] )
{
  float   **new;
  int     i;

  if( (new=(float **) malloc( (unsigned) MATRIX_ROWS*sizeof(float *) ) )
      == NULL
    )
  {
    fprintf( stderr, "Memory allocation failure in creating pointers to"
             "rows of phi-psi matrices.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  new--;
  for( i=1; i<=MATRIX_ROWS; i++ )
  {
    new[i] = mat[i-1];
    new[i]--;
  }
  return(new);
}

static float **Derivative( float **m )
{
  float    **new, f, y;
  int      i;

  new = (float **) malloc( (unsigned) MATRIX_ROWS*sizeof(float *) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating 2nd-derivative matrix...\n" );
    exit(1);
  }
  new--;
  for( i=1; i<=MATRIX_ROWS; i++ )
  {
    new[i] = (float *) malloc( (unsigned) MATRIX_COLUMNS * sizeof(float) );
    if( new[i] == NULL )
    {
      fprintf( stderr, "Memory allocation failure in creating row vectors for 2nd-derivative matrix...\n" );
      exit(1);
    }
    new[i]--;
  }

  /* Initialize the Phi and Psi vectors */

  f = START;
  for( i=1; i<=MATRIX_COLUMNS; i++ )
  {
    phi[i] = f;
    f += ANGULAR_INC;
  }
  y = START;
  for( i=1; i<=MATRIX_ROWS; i++ )
  {
    psi[i] = y;
    y += ANGULAR_INC;
  }

  /* Construct the cubic spline and compute the second-derivative */

  splie2( psi, phi, m, MATRIX_ROWS, MATRIX_COLUMNS, new );
  
  return(new);
}

PHIPSI  *PhiPsiContours(void)
{
  PHIPSI  *new;
  int      i, j;

  new = (PHIPSI *) malloc( (unsigned) sizeof(PHIPSI) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating pointers to"
             "phi-psi matrices.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(PHIPSI) );

  /* Alpha-Carbon */
  
  new->ca = Matrix( CA );
  
  /* Alpha-Carbon Deviation Matrix */

  new->ca_dev = Matrix( CA_DEV );
  
  /* Beta-Carbon */
  
  new->cb = Matrix( CB );
  
  /* CO Matrix */
  
  new->co = Matrix( CO );

  /* Alpha-Hydrogen */
  
  new->ha = Matrix( HA );
  
  /* Deviation matrix for Alpha-Hydrogens */
  
  new->ha_dev = Matrix( HA_DEV );

  /* Amide-Hydrogen */
  
  new->hn = Matrix( HN );
  
  /* Deviation matrix for Amide-Hydrogens */
  
  new->hn_dev = Matrix( HN_DEV );

  /* Nitrogen */
  
  new->n15 = Matrix( N15 );

  return(new);
}

PHIPSI  *SecondDerivatives( PHIPSI *p )
{
  PHIPSI  *new;

  new = (PHIPSI *) malloc( (unsigned) sizeof(PHIPSI) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating pointers to"
             "phi-psi matrices.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(PHIPSI) );

  /* Alpha-Carbon */
  
  new->ca = Derivative( p->ca );
  
  /* Alpha-Carbon Deviation Matrix */

  new->ca_dev = Derivative( p->ca_dev );
  
  /* Beta-Carbon */
  
  new->cb = Derivative( p->cb );
  
  /* CO Matrix */
  
  new->co = Derivative( p->co );

  /* Alpha-Hydrogen */
  
  new->ha = Derivative( p->ha );
  
  /* Deviation matrix for Alpha-Hydrogens */
  
  new->ha_dev = Derivative( p->ha_dev );

  /* Amide-Hydrogen */
  
  new->hn = Derivative( p->hn );
  
  /* Deviation matrix for Amide-Hydrogens */
  
  new->hn_dev = Derivative( p->hn_dev );
  
  /* Nitrogen */
  
  new->n15 = Derivative( p->n15 );

  return(new);
}

void     FreeMatrices( float **p )
{
  int    i;

  if( p == NULL )  return;
  
  p++;
  for( i=0; i<MATRIX_ROWS; i++ )
  {
    p[i]++;
    free( (char *) p[i] );
  }
  free( (char *) p );
  
  return;
}


void     FreePhiPsiMatrices( PHIPSI *p )
{
	int    i;
	
	if( p == NULL )
	{
		return;
	}
	FreeMatrices( p->ca );
	FreeMatrices( p->ca_dev );
	FreeMatrices( p->cb );
	FreeMatrices( p->co );
	FreeMatrices( p->ha );
	FreeMatrices( p->ha_dev );
	FreeMatrices( p->hn );
	FreeMatrices( p->hn_dev );
	FreeMatrices( p->n15 );
	
	free( (char *) p );
	return;
}

CSHIFT   *PhiPsiMatrices( RESIDUE *r, PHIPSI *p, PHIPSI *q, CSHIFT *cs, float last_psi )
{
	CSHIFT   *new;
	float    f, y, v, dev;
	int      idx, i;
	
	f = r->phi;
	if( f != NA )
	{
		if( f > 180 )
		{
			f -= 360.0;
		}
		if( f < -180 )
		{
			f += 360.0;
		}
	}
	
	y = r->psi;
	if( y != NA )
	{
		if( y > 180)   y -= 360.0;
		if( y < -180 ) y += 360.0;
	}
	
	/* Create CSHIFT */
	
	new = CreateCS( cs );
	new->type = iupac_code( r->type );
	new->n = r->num;
	idx = rc_idx(new->type);
	
	if (CARC[idx] != 0.0)
	{
		new->ca = CARC[idx];
	}
	else
	{
		new->ca = NA;
	}
	
    if (CBRC[idx] != 0.0)
	{
		new->cb = CBRC[idx];
	}
	else
	{
		new->cb = NA;
	}
	
	if (CORC[idx] != 0.0)
	{
		new->co = CORC[idx];
	}
	else
	{
		new->co = NA;
	}
	
	if (HARC[idx] != 0.0)
	{
		new->ha = HARC[idx];
	}
	else
	{
		new->ha = NA;
	}
	
	if (HNRC[idx] != 0.0)
	{
		new->hn = HNRC[idx];
	}
	else
	{
		new->hn = NA;
	}
	
	if (N15RC[idx] != 0.0)
	{
		new->n15 = N15RC[idx];
	}
	else
	{
		new->n15 = NA;
	}
	
	if (HBRC[idx] != 0.0)
	{
		new->hb = HBRC[idx];
	}
	else
	{
		new->hb = HBRC[idx];
	}
	for (i = 0; i < NHATOMS; i++)
	{
		if (HSRC[i][idx] != 0.0)
		{
			new->hside[i] = HSRC[i][idx];
		}
		else
		{
			new->hside[i] = NA;
		}
	}
	/* ADDNEW */
	
	return(new);  // SJN - using phi/psi-type matrices elsewhere
	
	/* Fill in the chemical shifts */
	
	if( CARC[idx] != 0.0 )
	{
		if( y != NA && f != NA )
		{
		/* ORIGINAL, with phi and psi transposed.
		I've now reversed phi and psi in all the following calculations to better fit
		my matrix format 
		splin2( psi, phi, p->ca, q->ca, MATRIX_ROWS, MATRIX_COLUMNS, y, f, &(new->ca) );
		splin2( psi, phi, p->ca_dev, q->ca_dev, MATRIX_ROWS, MATRIX_COLUMNS, y, f, &dev );
			*/
			splin2( psi, phi, p->ca, q->ca, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->ca) );
			splin2( psi, phi, p->ca_dev, q->ca_dev, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &dev );
			new->ca += dev;
			/* SJN
			if( new->type == 'G' )
			{
			if( f > 0 )
			{
			new->ca = 1.18314*new->ca + 0.18314*CARC[idx] - 8.363816;
			}
			else
			{
			new->ca = 0.603014*new->ca - 0.396986*CARC[idx] + 18.161814;
			}
			}
			*/
		}
		new->ca += CARC[idx];
	}
	else
	{
		new->ca = NA;
	}
	
	if( CBRC[idx] != 0.0 )
	{
		if( y != NA && f != NA )
		{
			splin2( psi, phi, p->cb, q->cb, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->cb) );
		}
		new->cb += CBRC[idx];
	}
	else
	{
		new->cb = NA;
	}
	
	if( HARC[idx] != 0.0 )
	{
		if( y != NA && f != NA )
		{
			splin2( psi, phi, p->ha, q->ha, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->ha) );
			splin2( psi, phi, p->ha_dev, q->ha_dev, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &dev );
			new->ha -= dev;
		}
		
		new->ha += HARC[idx];
	}
	else
	{
		new->ha = NA;
	}
	
	if( CORC[idx] != 0.0 )
	{
		if( y != NA && f != NA )
		{
			splin2( psi, phi, p->co, q->co, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->co) );
		}
		new->co += CORC[idx];
	}
	else
	{
		new->co = NA;
	}
	
	if( N15RC[idx] != 0.0 )
	{
		if( last_psi != NA && f != NA )
		{
			/* SJN TODO: re-adapt to phi/psi-1 */
			//      splin2( psi, phi, p->n15, q->n15, MATRIX_ROWS, MATRIX_COLUMNS, last_psi, f, &(new->n15) );
			splin2( psi, phi, p->n15, q->n15, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->n15) );
		}
		new->n15 += N15RC[idx];
	}
	else
	{
		new->n15 = NA;
	}
	
	if( HNRC[idx] != 0.0 )
	{
		if( last_psi != NA && f != NA )
		{
			/* SJN TODO_ re-adapt this to an appropriate phi/psi matrix */
			/*
			splin2( psi, phi, p->hn, q->hn, MATRIX_ROWS, MATRIX_COLUMNS, last_psi, f, &(new->hn) );
			splin2( psi, phi, p->hn_dev, q->hn_dev, MATRIX_ROWS, MATRIX_COLUMNS, last_psi, f, &dev );
			*/
			splin2( psi, phi, p->hn, q->hn, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &(new->hn) );
			splin2( psi, phi, p->hn_dev, q->hn_dev, MATRIX_ROWS, MATRIX_COLUMNS, f, y, &dev );
			new->hn += dev;
		}
		new->hn += HNRC[idx];
	}
	else
	{
		new->hn = NA;
	}
	
	return(new);
}
