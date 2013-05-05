#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "psa.h"
#include "main.h"
#include "vector.h"
#include "residue.h"
#include "cs.h"
#include "sidechain.h"

#ifdef _WIN32 
  #include "pi.h"
#endif

float  dihedral_angle( VECTOR a, VECTOR b, VECTOR c, VECTOR d )
{
  VECTOR    u, v, w, s, t;
  float     theta,dotp;

  u = diff( a, b );
  v = diff( c, b  );
  w = normalize( cross( u, v ) );
  u = diff( b, c );
  v = diff( d, c );
  s = normalize( cross( u, v) );

  dotp=dot(w,s);

  if (fabs(dotp) < 1.00000)
  {
	theta = (acos( dotp )/M_PI) * 180;
  }
  else
  {
	  theta = dotp > 0.0 ?  0.0 : 180.0;
  }
  if( dot( cross( w, s ), u ) > 0 )  theta *= -1.0;

 if (isnan(theta))
 {
	printf("");
}
  return(theta);
}

static float ring_orientation( RESIDUE *r, char res )
{
  VECTOR    CA;
  VECTOR    center, CG, CD1, CD2, CE1, CE2, CZ, ND1, NE1, NE2;
  VECTOR    u, v;

  /* This presumably is the partner of the ring */

  if( atm_vector(r, "CA", &CA) )  return(NA);
  
  
  if( res=='F' || res=='Y' )
  {
    /* The ring */

    if( atm_vector(r, "CG",  &CG)  )  return(NA);
    if( atm_vector(r, "CD1", &CD1) )  return(NA);
    if( atm_vector(r, "CD2", &CD2) )  return(NA);
    if( atm_vector(r, "CE1", &CE1) )  return(NA);
    if( atm_vector(r, "CE2", &CE2) )  return(NA);
    if( atm_vector(r, "CZ",  &CZ)  )  return(NA);
 
    /* Center of the ring */
 
    center.x = (CG.x + CD1.x + CD2.x + CE1.x + CE2.x + CZ.x) / 6.0;
    center.y = (CG.y + CD1.y + CD2.y + CE1.y + CE2.y + CZ.y) / 6.0;
    center.z = (CG.z + CD1.z + CD2.z + CE1.z + CE2.z + CZ.z) / 6.0;

    /* Vector normal to the ring */

    v = normalize( cross( diff( CD1, CG ), diff( CD2, CG ) ) );
  }
  else
  {
    if( res=='H' )
    {
      /* The ring */

      if( atm_vector(r, "CG",  &CG)  )  return(NA);
      if( atm_vector(r, "ND1", &ND1) )  return(NA);
      if( atm_vector(r, "CD2", &CD2) )  return(NA);
      if( atm_vector(r, "CE1", &CE1) )  return(NA);
      if( atm_vector(r, "NE2", &NE2) )  return(NA);
 
      /* Center of the ring */
 
      center.x = (CG.x + ND1.x + CD2.x + CE1.x + NE2.x ) / 5.0;
      center.y = (CG.y + ND1.y + CD2.y + CE1.y + NE2.y ) / 5.0;
      center.z = (CG.z + ND1.z + CD2.z + CE1.z + NE2.z ) / 5.0;

      /* Vector normal to the ring */

      v = normalize( cross( diff( ND1, CG ), diff( CD2, CG ) ) );
    }
    else
    {
      if( res=='W' )
      {
        /* The ring */

        if( atm_vector(r, "CG",  &CG)  )  return(NA);
        if( atm_vector(r, "CD1", &CD1) )  return(NA);
        if( atm_vector(r, "CD2", &CD2) )  return(NA);
        if( atm_vector(r, "NE1", &NE1) )  return(NA);
        if( atm_vector(r, "CE2", &CE2) )  return(NA);
 
        /* Center of the ring */
 
        center.x = (CG.x + CD1.x + CD2.x + NE1.x + CE2.x ) / 5.0;
        center.y = (CG.y + CD1.y + CD2.y + NE1.y + CE2.y ) / 5.0;
        center.z = (CG.z + CD1.z + CD2.z + NE1.z + CE2.z ) / 5.0;

        /* Vector normal to the ring */

        v = normalize( cross( diff( CD1, CG ), diff( CD2, CG ) ) );
      }
    }
  }
    
  u = normalize( diff( CA, center ) );

  return( pow(dot(u, v), 2.0) );
}

static float fork_orientation( RESIDUE *r, char res )
{
  VECTOR    CA, center, CB, CG1, CG2, CD1;
  VECTOR    u, v;

  if( atm_vector(r, "CA",  &CA)  )  return(NA);
  if( atm_vector(r, "CB",  &CB)  )  return(NA);
  if( atm_vector(r, "CG1", &CG1) )  return(NA);
  if( atm_vector(r, "CG2", &CG2) )  return(NA);
    
  switch(res)
  {
    case 'V':  center.x = (CB.x + CG1.x + CG2.x) / 3.0;
               center.y = (CB.y + CG1.y + CG2.y) / 3.0;
               center.z = (CB.z + CG1.z + CG2.z) / 3.0;
               break;
    case 'I':  if( atm_vector(r, "CD1",  &CD1)  )  return(NA);
               center.x = (CB.x + CG1.x + CG2.x + CD1.x ) / 4.0;
               center.y = (CB.y + CG1.y + CG2.y + CD1.y ) / 4.0;
               center.z = (CB.z + CG1.z + CG2.z + CD1.z ) / 4.0;
               break;
    default:   fprintf( stderr, "Unable to compute fork orientation for %c\n", res );
               exit(1);
  }
  
  u = normalize( diff( CA, center ) );
  v = normalize( cross( diff( CG1, CB ), diff( CG2, CB ) ) );
  
  return( pow( dot(u, v), 2.0 ) );
}


void  torison_angles( RESIDUE *r )
{
	VECTOR    N, CA, O, C, CG;
	VECTOR    lastc, lastca;
	VECTOR    u, w, s;
	VECTOR    CB, XG;            /* XG = the gamma atom */
	float     theta;
	char      res;
	int       return_code;
  
	/*
  if( atm_vector(r, "N",  &N)  )  no_vectorA( "N",  1 , r->num, r->type );
  if( atm_vector(r, "CA", &CA) )  no_vectorA( "CA", 1 , r->num, r->type  );
  if( atm_vector(r, "C",  &C)  )  no_vectorA( "C",  1 , r->num, r->type  );
  if( atm_vector(r, "O",  &O)  )  no_vectorA( "O",  1 , r->num, r->type  );
  */

	/* SJN: deal with missing atoms gracefully */
	if( atm_vector(r, "N",  &N)   
	 || atm_vector(r, "CA", &CA) 
	 || atm_vector(r, "C",  &C)
	 || atm_vector(r, "O",  &O)) 
	{
		r->omega = NA;
		r->phi = 360.0;
		r->psi = 360.0;
		r->theta = NA;
		r->chi = NA;
		r->errflags |= RES_ERR_MISSING_ATOMS;
		return;
	}
	
	lastc = r->lastc;
	lastca = r->lastca;

  /* Compute the last (i-1) Omega */
  
	r->omega = NA;
	if (!null_vector( r->lastc ) && !null_vector( r->lastca ))
	{
		r->omega = dihedral_angle( lastca, lastc, N, CA );
	}
  
  /* Compute Phi */
  
	r->phi = NA;
	r->psi = NA;
	if (!null_vector(r->lastc))
	{
		r->phi = dihedral_angle( lastc, N, CA, C );  
	}
  

	if (!null_vector(r->nextn)) 
	{
		r->psi = dihedral_angle(N, CA, C, r->nextn);
	}
  /* Compute Psi: This is specially treated because the N(i+1) atomic position */
  /* is not yet available.                                                     */

  /*	
  u = normalize( diff( N, CA ) );
  v = normalize( diff( C, CA ) );
  w = normalize( cross( u, v ) );
  
  u = multiply( v, -1.0 );
  v = normalize( diff( O, C ) );
  s = normalize( cross( v, u ) );  
  */

	/*	
  u = normalize( diff( CA, C ) );
  w = normalize( cross( diff( N, CA ), diff( C, CA ) ) );
  s = normalize( cross( diff( O, C ), u ) );

  theta = (acos( dot( w, s ) )/M_PI) * 180;
  if( dot( cross( w, s ), u ) > 0 )
	{
		theta *= -1.0;
	}
  r->psi = theta;    
  */
  
  /* Compute CHI for selected residues */
  
	res = iupac_code( r->type );
	r->chi2 = -777;  // code for "missing atoms" rather than "doesn't have one"

	if( res == 'G' || res == 'A') 
	{
		r->chi = NA;
		r->chi2 = NA;
	}
	else
	{
		if( atm_vector(r, "CB", &CB) )  
		{
			/* SJN: Rather than bailing out here, just note the possible error and carry on */
			r->chi = NA;
			r->errflags |= RES_ERR_NO_CB;
      /*no_vectorA( "CB", 1, r->num, r->type  );*/
		}
		switch( res )
		{
			case 'V':
				return_code = atm_vector(r, "CG1", &XG);
				break;
			case 'C':  
				return_code = atm_vector(r, "SG", &XG);
                break;
			case 'T':  
				return_code = atm_vector(r, "OG1", &XG);
                break;
			case 'I':  
				return_code = atm_vector(r, "CG1", &XG);
                break;
			case 'S':  
				return_code = atm_vector(r, "OG", &XG);
                break;
			default:   
				return_code = atm_vector(r, "CG", &XG);
		}
    
		if (return_code)
		{
			r->chi = NA;
		}
		else 
		{
			r->chi = dihedral_angle( XG, CB, CA, N );
		}

	/* Chi2 Calculations */
		if (res == 'C' || res == 'S')
		{
			r->chi2 = NA;
		}
		else if (!atm_vector(r, "CG", &CG))
		{
			return_code = 1;

			switch (res)
			{
				case 'R':
				case 'Q':
				case 'E':
				case 'K':
				case 'P':
					return_code = atm_vector(r, "CD", &XG);
					break;
				case 'N':
				case 'D':
					return_code = atm_vector(r, "OD1", &XG);
					break;
				case 'H':
					return_code = atm_vector(r, "ND1", &XG);
					break;
				case 'L':
				case 'W':
				case 'F':
				case 'Y':
					return_code = atm_vector(r, "CD1", &XG);
					break;
				case 'M':
					return_code = atm_vector(r, "SD", &XG);
					break;
			}

			if (return_code)
			{
				r->chi2 = -777;
			}
			else 
			{
				r->chi2 = dihedral_angle(XG, CG, CB, CA);
			}
		}
		else if (!atm_vector(r, "CG1", &CG))
		{
			return_code = 1;

			switch (res)
			{
			case 'I':
				return_code = atm_vector(r, "CD1", &XG);
				break;

			case 'V':
				return_code = atm_vector(r, "1HG1", &XG);
				break;
			}
			if (return_code)
			{
				r->chi2 = -777;
			}
			else
			{
				r->chi2 = dihedral_angle(XG, CG, CB, CA);
			}
		}
		if (!atm_vector(r, "CG2", &CG))
		{
			return_code = 1;
			
			switch (res)
			{
			case 'I':
			case 'T':
			case 'V':
				return_code = atm_vector(r, "1HG2", &XG);
				break;
			}		
			
			if (return_code)
			{
				r->chi22 = -777;
			}
			else
			{
				r->chi22 = dihedral_angle(XG, CG, CB, CA);
			}
		}
	}
 
  /* Compute theta only for PHE, TYR, HIS and VAL */
  
  switch( res )
  {
    case 'F':    r->theta = ring_orientation( r, 'F' );
                 break;
    case 'Y':    r->theta = ring_orientation( r, 'Y' );
                 break;
    case 'H':    r->theta = ring_orientation( r, 'H' );
                 break;
    case 'W':    r->theta = ring_orientation( r, 'W' );
                 break;
    case 'V':    r->theta = fork_orientation( r, 'V' );
                 break;
    case 'I':    r->theta = fork_orientation( r, 'I' );
                 break;
    default:     r->theta = NA;
  }
  
  return;
}

/*
void    SideChainOrientation( RESIDUE *r, CSHIFT **cs )
{
  char  res;

  res = iupac_code( r->type );
  if( res!='F' && res!='Y' && res!='H' && res!='W' && res!='V' && res!='T' && 
      res!='I' )
  {
      return;
  }

  *cs = CreateCS( *cs );
  (*cs)->type = res;
  (*cs)->n = r->num;
  
  switch(res)
  {
    case 'V':  (*cs)->ca = (r->theta==NA) ? 0.0 : 17.92*r->theta - 6.25;
               break;
    case 'I':  (*cs)->ca = (r->theta==NA) ? 0.0 : 7.22*r->theta - 2.59;
               break;
    case 'T':  if( r->chi>0.0 && r->chi<100.0 )  (*cs)->ca = -1.0;
               else
               {
                 if( r->chi>-100 && r->chi<0.0 )  (*cs)->ca = 1.0;
               }
               break;
    default:   (*cs)->ca = (r->theta==NA) ? 0.0 : 17.36*r->theta - 1.89;
  }
  return;
}
*/

void	SideChainOrientation( RESIDUE *r, CSHIFT **cs )
{
	char  res,ridx,chi_idx;

	return;  /* This is now subsumed by optimize.c */

	res = iupac_code( r->type );
 
	if (res == 'A' || res == 'G')
	{
		return;
	}

	*cs = CreateCS( *cs );
	(*cs)->type = res;
	(*cs)->n = r->num;

	ridx = rc_idx(res);

	if (r->chi >= 0.0 && r->chi < 120.0)
	{
		chi_idx = 0;
	}
	else if (r->chi >= 120.0 && r->chi < 240.0)
	{
		chi_idx = 1;
	}
	else
	{
		chi_idx = 2;
	}

	(*cs)->ca = CA_CHI[ridx][chi_idx];
	(*cs)->cb = CB_CHI[ridx][chi_idx];
	(*cs)->co = CO_CHI[ridx][chi_idx];
	(*cs)->n15 = N15_CHI[ridx][chi_idx];
    return;
}
