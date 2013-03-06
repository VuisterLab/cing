#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "main.h"
#include "display.h"
#include "cs.h"
#include "nn.h"
#include "optimize.h"


DISPLAY_DATA   *CreateDisplayData( int len, int prop, int nuc )
{
  DISPLAY_DATA  *new=NULL;
  int           i;

  if( (new=(DISPLAY_DATA *) malloc( (unsigned) sizeof(DISPLAY_DATA) ))==NULL )
  {
    fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
    exit(1);  
  }
  
  /* Initialize numerical constants */
  
  new->length = len;
  new->properties = prop;
  new->nucleus = nuc;
  new->fill = 0;
  
  /* Create 1-D integer vector for storing ID number */
  
  if( (new->num = (int *) malloc( (unsigned) len*sizeof(int) ))==NULL )
  {
    fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
    exit(1);  
  }
  memset( new->num, 0, (unsigned) len*sizeof(int) );
  
  /* Create 1-D char vector for sequence information */
  
  if( (new->res = (char *) malloc( (unsigned) len*sizeof(char) ))==NULL )
  {
    fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
    exit(1);  
  }
  memset( new->res, 0, (unsigned) len*sizeof(char) );

  /* Create 2-D float matrix for break-down of chemical shifts */

  if( (new->cs = (float **) malloc( (unsigned) len*sizeof(float *) ))==NULL )
  {
    fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
    exit(1);  
  }
  for( i=0; i<len; i++ )
  {
    if( (new->cs[i] = (float *) malloc( (unsigned) (prop+1)*sizeof(float) ))==NULL )
    {
      fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
      exit(1);  
    }
    memset( new->cs[i], 0, (unsigned) (prop+1)*sizeof(float) );
  }
  
  /* Create 2-D char matrix for labels appearing in the header */
  
  if( (new->label = (char **) malloc( (unsigned) (prop+1)*sizeof(char *) ))==NULL )
  {
    fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
    exit(1);
  }
  for( i=0; i<(prop+1); i++ )
  {
    if( (new->label[i] = (char *) malloc( (unsigned) LABEL_SIZE*sizeof(char) ))==NULL )
    {
      fprintf( stderr, "Memory allocation failure in CreateDisplayData().\n" );
      exit(1);  
    }
    memset( new->label[i], 0, (unsigned) LABEL_SIZE*sizeof(char) );
  }
  
  return(new);
}

void  display_selected_nucleus( DISPLAY_DATA *d )
{
  int   i, j;
  char  nucleus[5];

  /* Print Header Information */

  switch(d->nucleus)
  {
    case N_HA:    strcpy( nucleus, "HA" );
                  break;
    case N_HN:    strcpy( nucleus, "HN" );
                  break;
    case N_N15:   strcpy( nucleus, "N15" );
                  break;
    case N_CA:    strcpy( nucleus, "CA" );
                  break;
    case N_CB:    strcpy( nucleus, "CB" );
                  break;
    case N_CO:    strcpy( nucleus, "CO" );
                  break;
    default:      strcpy( nucleus, "Unknown" );
  }
#ifndef _DEBUG
  fprintf( stdout, "Chemical Shift Predictions for %s\n", nucleus );
  fprintf( stdout, "---------------------------------------------------------------\n" );
  fprintf( stdout, "PHIPSI = Predictions based on Phi-Psi dependency surfaces.\n" );
  fprintf( stdout, "RC     = *Ring-current effects.\n" );
  fprintf( stdout, "HB     = *Hydrogen-bonding effects.\n" );
  fprintf( stdout, "ES     = *Electrostatic effects.\n" );
  fprintf( stdout, "PRO    = *Effects due to short-range interactions with prolines (for CA only).\n" );
  fprintf( stdout, "S.CHN  = *Effects due to self-interactions with sidechains (for CA only).\n" );
  fprintf( stdout, "SS     = *Effects due to presence of di-sulfide bonds (for CA only).\n" );
  fprintf( stdout, "N.N.   = *Nearest-neighbor effects (for N15 only).\n" );
  fprintf( stdout, "OPT    = *Optimization (for CA, HA and HN only).\n" );
  fprintf( stdout, "ALL    = Overall predictions.\n" );
  fprintf( stdout, "*      = Net contributions only.\n" );
  fprintf( stdout, "---------------------------------------------------------------\n\n" );
#endif  

  fprintf( stdout, "NUM RES  PHIPSI      " );
  for( i=1; i<d->fill; i++ )
  {
    fprintf( stdout, "%-9s", d->label[i] );
  }
  putchar( '\n' );

#ifndef _DEBUG
  fprintf( stdout, "--- --- ---------  " );
  for( i=1; i<d->fill; i++ )
  {
    fprintf( stdout, "%-9s", "-------" );
  }
  putchar( '\n' );
#endif

  for( i=0; i<d->length; i++ )
  {
    fprintf( stdout, "%-3d %2c ", d->num[i], d->res[i] );
    for( j=0; j<d->fill; j++ )
    {
      if( d->cs[i][j] == NA )  d->cs[i][j] = 0.0;
      fprintf( stdout, "%9.4f", d->cs[i][j] );
    }
    putchar( '\n' );
  }
  return;
}

void  FreeDisplayData( DISPLAY_DATA *d )
{
  int    i;

  free( (char *) d->num );
  free( (char *) d->res );
  for( i=0; i<d->length; i++ )  free( (char *) d->cs[i] );
  free( (char *) d->cs );
  for( i=0; i<(d->properties+1); i++ )  free( (char *) d->label[i] );
  free( (char *) d->label );
  free( (char *) d );
  return;
}

void  InitializeDisplayData( DISPLAY_DATA *d, CSHIFT *cs, char *label )
{
  CSHIFT    *p;
  int        i=0;

  strcpy( d->label[d->fill], label );
  p = cs;
  while( p->next != NULL )  p = p->next;
  while( p != NULL )
  {
    d->num[i] = p->n;
    d->res[i] = p->type;
    switch(d->nucleus)
    {
      case N_HA:   d->cs[i][d->fill] = p->ha;
                   break;
      case N_HN:   d->cs[i][d->fill] = p->hn;
                   break;
      case N_N15:  d->cs[i][d->fill] = p->n15;
                   break;
      case N_CA:   d->cs[i][d->fill] = p->ca;
                   break;
      case N_CB:   d->cs[i][d->fill] = p->cb;
                   break;
      case N_CO:   d->cs[i][d->fill] = p->co;
                   break;
      default:     d->cs[i][d->fill] = 0.0;
    }
    i++;
    p = p->last;
  }
  d->fill++;
  return;
}

void  FillDisplayData( DISPLAY_DATA *d, CSHIFT *cs, char *label, int t )
{
  CSHIFT    *p;
  int       i;
  
  strcpy( d->label[d->fill], label );
  for( i=0; i<d->length; i++ )
  {
    if( (p=FindCS( cs, d->num[i] ))!=NULL )
    {
      switch(d->nucleus)
      {
        case N_HA:   d->cs[i][d->fill] = p->ha;
                     break;
        case N_HN:   d->cs[i][d->fill] = p->hn;
                     break;
        case N_N15:  d->cs[i][d->fill] = p->n15;
                     if( t )  d->cs[i][d->fill] += N15_HN_FACTOR * p->hn; /* SJN WTF */
                     break;
        case N_CA:   d->cs[i][d->fill] = p->ca;
                     if( t )  d->cs[i][d->fill] += CA_HA_FACTOR * p->ha; /* SJN WTF */
                     break;
        case N_CB:   d->cs[i][d->fill] = p->cb;
                     break;
        case N_CO:   d->cs[i][d->fill] = p->co;
                     break;
        default:     d->cs[i][d->fill] = 0.0;
      }
    }
  }
  d->fill++;
  return;
}

void  FillDisplayDataHB( DISPLAY_DATA *d, CSHIFT *cs )
{
  CSHIFT    *p;
  int       i;
  
  if( d->nucleus != N_HN && d->nucleus != N_HA && d->nucleus != N_N15 )
  {
    return;
  }
  
  strcpy( d->label[d->fill], "HB" );
  for( i=0; i<d->length; i++ )
  {
    if( (p=FindCS( cs, d->num[i] ))!=NULL )
    {
      switch(d->nucleus)
      {
        case N_HA:   d->cs[i][d->fill] = p->ha;
                     break;
        case N_HN:   d->cs[i][d->fill] = p->hn;
                     break;
        case N_N15:  d->cs[i][d->fill] = N15_HN_FACTOR * p->hn;
                     break;
        default:     d->cs[i][d->fill] = 0.0;
      }
    }
  }
  d->fill++;
  return;
}

void  FillDisplayDataCYS( DISPLAY_DATA *d, CSHIFT *orig, CSHIFT *ss )
{
  CSHIFT    *p, *q;
  int       i;
  
  if( d->nucleus != N_CA )  return;
  
  strcpy( d->label[d->fill], "SS" );
  for( i=0; i<d->length; i++ )
  {
    if( d->res[i] == 'C' )
    {
      if( (q=FindCS( orig, d->num[i] ))==NULL || q->ca==NA )  continue;
      if( (p=FindCS( ss, d->num[i] ))==NULL )
      {
        d->cs[i][d->fill] = 2.5;
      }
      else
      {
        d->cs[i][d->fill] = p->ca - q->ca;
      }
    }
  }
  d->fill++;
  return;
}


void  FillDisplayDataPRO( DISPLAY_DATA *d, RES *pro )
{
  RES       *p;
  int        m, i;

  if( d->nucleus != N_CA )  return;
  strcpy( d->label[d->fill], "PRO" );

  p = pro;
  while( p != NULL )
  {
    m = p->num - 1;
    if( m >= 1 )
    {
      for( i=0; i<d->length; i++ )
      {
        if( d->num[i] == m )
        {
          if( d->res[i] != 'G' )  d->cs[i][d->fill] = -1;
          break;
        }
      }
    }
    p = p->next;
  }

  d->fill++;
  return;
}

void  FillDisplayDataNN( DISPLAY_DATA *d )
{
  int     i;
  float   nn_effect=0.0;

  if( d->nucleus != N_N15 )  return;
  
  strcpy( d->label[d->fill], "N.N." );
  for( i=0; i<d->length; i++ )
  {
    if( nn_effect != 0.0 )  d->cs[i][d->fill] = nn_effect;
    nn_effect = AddtoNextN15( d->res[i] );
  }
  d->fill++;
  return;
}


void FillDisplayDataOPT( DISPLAY_DATA *d, CSHIFT *cs , CSHIFT *oldcs)
{
  int     i;
  CSHIFT  *p,*p2;

  /*
	if( d->nucleus!=N_CA && d->nucleus!=N_HN && d->nucleus!=N_HA )  
	{
		return;
	}
*/
	
	strcpy( d->label[d->fill], "OPT" );
  
	for( i=0; i<d->length; i++ )
	{
		if ((p=FindCS( cs, d->num[i] ))==NULL )
		{
			continue;
		}
		if ((p2 = FindCS(oldcs,d->num[i])) == NULL)
		{
			continue;
		}
		switch(d->nucleus)
		{
		case N_CA:    
			if( p->ca != NA && p2->ca != NA)
            {
				d->cs[i][d->fill] = p->ca - p2->ca;
			}
            break;

		case N_HN:    
			if( p->hn != NA && p2->hn != NA)
            {
				d->cs[i][d->fill] = p->hn - p2->hn;
            }
            break;

		case N_HA:    
			if( p->ha != NA && p2->ha != NA)
            {
				d->cs[i][d->fill] = p->ha - p2->ha;
            }
            break;

		case N_N15:    
			if( p->n15 != NA && p2->n15 != NA)
            {
				d->cs[i][d->fill] = p->n15 - p2->n15;
            }
            break;

		case N_CB:    
			if( p->cb != NA && p2->cb != NA)
            {
				d->cs[i][d->fill] = p->cb - p2->cb;
            }

		case N_CO:    
			if( p->co != NA && p2->co != NA)
            {
				d->cs[i][d->fill] = p->co - p2->co;
            }
            break;
		}

    
  }
  d->fill++;
  return;
}


/* SJN DEBUG
  if( d->nucleus!=N_CA && d->nucleus!=N_HN && d->nucleus!=N_HA )  return;
  strcpy( d->label[d->fill], "OPT" );
  
  for( i=0; i<d->length; i++ )
  {
    if( (p=FindCS( cs, d->num[i] ))==NULL )  continue;
    switch(d->nucleus)
    {
      case N_CA:    if( p->ca != NA )
                    {
                      d->cs[i][d->fill] = CAResponse( p->ca, p->type ) - p->ca;
                    }
                    break;
      case N_HN:    if( p->hn != NA )
                    {
                      d->cs[i][d->fill] = HNResponse( p->hn, p->type ) - p->hn;
                    }
                    break;
      case N_HA:    if( p->ha != NA )
                    {
                      d->cs[i][d->fill] = HAResponse( p->ha, p->type ) - p->ha;
                    }
                    break;
    }
  }
  d->fill++;
  
  return;
}*/
