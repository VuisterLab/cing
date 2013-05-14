#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "psa.h"
#include "vector.h"
#include "residue.h"
#include "hydrogens.h"
#include"atomnametable.h"

#ifdef _WIN32 
#include "pi.h"
#endif

struct hatoms hatoms[NHATOMS] = {
"H",	HYDRO_H		,
"HA",	HYDRO_HA	,
"HA2",	HYDRO_HA2	,
"HA3",	HYDRO_HA3	,
"HB",	HYDRO_HB	,
"HB1",	HYDRO_HB1	,
"HB2",	HYDRO_HB2	,
"HB3",	HYDRO_HB3	,
"HD1",	HYDRO_HD1	,
"HD11",	HYDRO_HD11	,
"HD12",	HYDRO_HD12	,
"HD13",	HYDRO_HD13	,
"HD2",	HYDRO_HD2	,
"HD21",	HYDRO_HD21	,
"HD22",	HYDRO_HD22	,
"HD23",	HYDRO_HD23	,
"HD3",	HYDRO_HD3	,
"HE",	HYDRO_HE	,
"HE1",	HYDRO_HE1	,
"HE2",	HYDRO_HE2	,
"HE21",	HYDRO_HE21	,
"HE22",	HYDRO_HE22	,
"HE3",	HYDRO_HE3	,
"HG",	HYDRO_HG	,
"HG1",	HYDRO_HG1	,
"HG11",	HYDRO_HG11	,
"HG12",	HYDRO_HG12	,
"HG13",	HYDRO_HG13	,
"HG2",	HYDRO_HG2	,
"HG21",	HYDRO_HG21	,
"HG22",	HYDRO_HG22	,
"HG23",	HYDRO_HG23	,
"HG3",	HYDRO_HG3	,
"HH",	HYDRO_HH	,
"HH11",	HYDRO_HH11	,
"HH12",	HYDRO_HH12	,
"HH2",	HYDRO_HH2	,
"HH21",	HYDRO_HH21	,
"HH22",	HYDRO_HH22	,
"HZ",	HYDRO_HZ	,
"HZ1",	HYDRO_HZ1	,
"HZ2",	HYDRO_HZ2	,
"HZ3",	HYDRO_HZ3	
};

#define  CH_BOND 1.0
//#define  NH_BOND 1.0
//#define  CNH     123.5
#define  NH_BOND 0.86
#define  CNH     118.9

static   VECTOR  zaxis = { 0, 0, 1 };
static   VECTOR  yaxis = { 0, 1, 0 };

/* Copyright (C) 1987,1988 Numerical Recipes Software -- RAN2 */
    
#define M 714025
#define IA 1366
#define IC 150889




static float ran2( long *idum )
{
  static long iy,ir[98];
  static int iff=0;
  int j;
 
  if (*idum < 0 || iff == 0)
  {
    iff=1;
    if ((*idum=(IC-(*idum)) % M) < 0) *idum = -(*idum);
    for (j=1;j<=97;j++)
    {
      *idum=(IA*(*idum)+IC) % M;
      ir[j]=(*idum);
    }
    *idum=(IA*(*idum)+IC) % M;
    iy=(*idum);
  }
  j=1 + 97.0*iy/M;
  if (j > 97 || j < 1)
  {
    fprintf( stderr, "Error in generating a random number...\n" );
    exit(1);
  }
  iy=ir[j];
  *idum=(IA*(*idum)+IC) % M;
  ir[j]=(*idum);
  return (float) iy/M;
}


static  float  occupancy( RESIDUE *r, char *a )
{
  ATOM     *q;

  q = r->atom;
  while( q != NULL )
  {
    if( !strcmp( q->type, a ) )  return( q->occupancy );
    q = q->next;
  }
  fprintf( stderr, "occupancy: Atom %s not found in %s%d\n", a, r->type, r->numLabel );
  fprintf( stderr, "Aborting...\n" );
  exit(1);
}

static  float  bfactor( RESIDUE *r, char *a )
{
  ATOM     *q;

  q = r->atom;
  while( q != NULL )
  {
    if( !strcmp( q->type, a ) )  return( q->BFactor );
    q = q->next;
  }
  fprintf( stderr, "bfactor: Atom %s not found in %s%d\n", a, r->type, r->numLabel );
  fprintf( stderr, "Aborting...\n" );
  exit(1);
}

/* Add a single planar hydrogen atom */

static void  planar_hydrogen( RESIDUE *r, char *c, char *a, char *b, char *unknown,
                                float bond_length )
{
  VECTOR   center, va, vb;
  VECTOR   n, u, v, w;
  float    theta, center_occ, a_occ, b_occ, center_bfac, a_bfac, b_bfac;
  
  /* This is for error checking */
  
  if( atm_vector(r, c, &center) || atm_vector(r, a, &va) || atm_vector(r, b, &vb) )
  {
    return;
  }
  
  u = normalize( diff( vb, center ) );
  v = normalize( diff( va, center ) );
  n = normalize( cross( u, v ) );
  theta = (360.0 - 180.0*acos( dot( u, v ) )/M_PI ) / 2.0;
  
  //xiaoli begin
  
  int hIndex = -1;
  int i;
  for (i = 0; i < NHATOMS; i++)
    {
     
      if (!strcmp(hatoms[i].name,unknown))
	{
	  hIndex = hatoms[i].index;
	  //printf("xiaoli unknown = %s and hIndex=%d\n",unknown,hIndex);
	  break;
	}
    }
  
  
  //xiaoli end

  
  if (FindAtom(r->atom,unknown) == NULL)
  {
	  CreateAtom( r );
	  strcpy( r->atom->type, unknown );  
	  r->atom->p = add( center, multiply( rotate( v, n, theta ), bond_length ) );
	  //xiaoli added
	  r->atom->hIndex;
  }
  else
  {
	  return;
  }
  /* Fill in the occupancy */
  
  center_occ = occupancy(r, c);
  a_occ = occupancy(r, a);
  b_occ = occupancy(r, b);
  r->atom->occupancy = center_occ < a_occ ? center_occ : a_occ;
  if( b_occ < r->atom->occupancy )
  {
	  r->atom->occupancy = b_occ;
  }
  
  /* Fill in the B-Factor */
  
  center_bfac = bfactor(r, c);
  a_bfac = bfactor(r, a);
  b_bfac = bfactor(r, b);
  r->atom->BFactor = center_bfac > a_bfac ? center_bfac : a_bfac;
  if( b_bfac > r->atom->BFactor )
  {
	  r->atom->BFactor = b_bfac;
  }

  return;
}

/* Fills in the last missing atom on a tetrahedron */

static  void  fill_tetrahedron( RESIDUE *r, char *center, char *a, char *b,
                                char *c, char *unknown, float bond_length )
{
  VECTOR    central, va, vb, vc;
  VECTOR    n, w, v, u, missing;
  float     theta, center_occ, a_occ, b_occ, c_occ, center_bfac, 
            a_bfac, b_bfac, c_bfac;
  
  if( atm_vector(r, center, &central) || atm_vector(r, a, &va) ||
      atm_vector(r, b, &vb) || atm_vector(r, c, &vc) )
  {
    return;
  }
  
  n = normalize( diff( va, central ) );
  w = normalize( diff( vb, central ) );
  v = normalize( diff( vc, central ) );
  u = rotate( w, n, 120.0 );
  theta = 180.0*acos( dot( u, v ) )/M_PI;
  missing = (theta >= 100) ? u : rotate( u, n, 120.0 );
  

  //xiaoli begin
  char iupacCode;
  int hIndex, i;
  iupacCode = iupac_code(r->type);
  hIndex = -1;
  
  for (i = 0; i < NTRATOMS; i++)
    {
      if (tratoms[i].iupacCode == iupacCode)
	{
	  if (!strcmp(unknown,tratoms[i].pdb))
	    {
	      hIndex = tratoms[i].hatomsIndex;
	      //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
	      break;
	    }
	}
      
    }
  //xiaoli end

  if (FindAtom(r->atom,unknown) == NULL)
  {
	  CreateAtom( r );
	  strcpy( r->atom->type, unknown );  
	  r->atom->p = add( central, multiply( missing, bond_length ) );
	  //xiaoli added
	  r->atom->hIndex = hIndex;
  }
  else
  {
	  return;
  }

  /* Fill in the occupancy */
  
  center_occ = occupancy(r,center);
  a_occ = occupancy(r,a);
  b_occ = occupancy(r,b);
  c_occ = occupancy(r,c);
  r->atom->occupancy = center_occ < a_occ ? center_occ : a_occ;
  if( b_occ < r->atom->occupancy )
  {
	  r->atom->occupancy = b_occ;
  }
  if( c_occ < r->atom->occupancy ) 
  {
	  r->atom->occupancy = c_occ;
  }

  /* Fill in the BFactor */

  center_bfac = bfactor(r,center);
  a_bfac = bfactor(r,a);
  b_bfac = bfactor(r,b);
  c_bfac = bfactor(r,c);
  r->atom->BFactor = center_bfac > a_bfac ? center_bfac : a_bfac;

  if( b_bfac > r->atom->BFactor ) 
  {
	  r->atom->BFactor = b_bfac;
  }
  if( c_bfac > r->atom->BFactor ) 
  {
	  r->atom->BFactor = c_bfac;
  }

  return;
}

static  void  hydrogen_pair( RESIDUE *r, char *a, char *b, char *c, 
                             float bond_length, char *label1, char *label2 )
{
  VECTOR    va, vc;
  VECTOR    n, w, u;
  float     a_occ, b_occ, c_occ, a_bfac, b_bfac, c_bfac, Occupancy, Bfactor;

  if( atm_vector(r, b, &u) || atm_vector(r, a, &va) || atm_vector(r, c, &vc) )
  {
    return;
  }

  n = normalize( diff( vc, u ) );
  w = multiply( normalize( diff( va, u ) ), bond_length );
  
 //xiaoli begin
  char iupacCode;
  int hIndex, i;
  iupacCode = iupac_code(r->type);
  hIndex = -1;
  
  for (i = 0; i < NTRATOMS; i++)
    {
      if (tratoms[i].iupacCode == iupacCode)
	{
	  if (!strcmp(label1,tratoms[i].pdb))
	    {
	      hIndex = tratoms[i].hatomsIndex;
	      //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
	      break;
	    }
	}
      
    }
  //xiaoli end

  if (FindAtom(r->atom,label1) == NULL)
  {
	  CreateAtom( r );
	  strcpy( r->atom->type, label1 );  
	  r->atom->p = add( u, rotate( w, n, 120.0 ) );
	  
	  //xiaoli added
	  r->atom->hIndex = hIndex;
	  
  }
  /* Fill in the occupancy */
  
  a_occ = occupancy(r,a);
  b_occ = occupancy(r,b);
  c_occ = occupancy(r,c);
  r->atom->occupancy = a_occ < b_occ ? a_occ : b_occ;
  if( c_occ < r->atom->occupancy )  
  {
	  r->atom->occupancy = c_occ;
  }
  Occupancy = r->atom->occupancy;
  
  /* Fill in the B-Factor */
  
  a_bfac = bfactor(r,a);
  b_bfac = bfactor(r,b);
  c_bfac = bfactor(r,c);
  r->atom->BFactor = a_bfac > b_bfac ? a_bfac : b_bfac;
  if( c_bfac > r->atom->BFactor )
  {
	  r->atom->BFactor = c_bfac;
  }
  Bfactor = r->atom->BFactor;
  

  //xiaoli begin
 
  hIndex = -1;
  
  for (i = 0; i < NTRATOMS; i++)
    {
      if (tratoms[i].iupacCode == iupacCode)
	{
	  if (!strcmp(label2,tratoms[i].pdb))
	    {
	      hIndex = tratoms[i].hatomsIndex;
	      //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
	      break;
	    }
	}
      
    }
  //xiaoli end
  
  
  if (FindAtom(r->atom,label2) == NULL)
  {
	  CreateAtom( r );
	  strcpy( r->atom->type, label2 );  
	  r->atom->p = add( u, rotate( w, n, -120.0 ) );  
	  r->atom->occupancy = Occupancy;
	  r->atom->BFactor = Bfactor;
	  
	  //xiaoli added
	  r->atom->hIndex = hIndex;
  }
  return;
}

static  void   hydrogen_triplet( RESIDUE *r, char *a, char *c, float bond_length, 
								char *label1, char *label2, char *label3, long *seed )
{
	float    theta, phi, spin;
	VECTOR   n, u, v, w, center, va;
	float    Occupancy, Bfactor;
	char iupacCode;
	int hIndex, i;
	/* Normalization */
	
	if( atm_vector(r, c, &center) || atm_vector(r, a, &va) )  return;
	n = normalize( diff( va, center ) );
	
	/* Phi is measure respect to the positive x-axis */
	
	if( n.x==0 && n.y==0 )  phi = 0.0;
	else
	{
		phi = 180.0*acos(n.x/sqrt(n.x*n.x+n.y*n.y))/M_PI;
		if( n.y < 0 )  phi *= -1.0;
	}
	
	/* Theta is measured with respect to the z-axis */
	
	if( n.x==0 && n.y==0 && n.z==0 )  theta = 0.0;
	else
	{
		theta = 180.0*acos(n.z/sqrt(n.x*n.x+n.y*n.y+n.z*n.z))/M_PI;
	}
	
	/* Rotate the k-vector about the y axis by 109 degrees */
	
	w = rotate( zaxis, yaxis, 109.0 );
	
	/* Rotate this vector by a random amount about the z-axis */
	
	w = rotate( w, zaxis, 2*M_PI*ran2(seed) );
	
	/* Now rotate the coordinates so that the z-axis aligns with n */
	
	w = rotate( w, yaxis, theta );
	w = rotate( w, zaxis, phi );
	
	/* Rotate w about n first by 120 degrees and then by -120 */
	/* degrees to get the other two unit vectors              */
	
	u = rotate( w, n,  120.0 );
	v = rotate( w, n, -120.0 );
	
	/* Scale the unit vectors and add to the central atom */
	
	u = add( center, multiply( u, bond_length ) );
	v = add( center, multiply( v, bond_length ) );
	w = add( center, multiply( w, bond_length ) );
	
	/* Occupancy and B-Factor */
	
	Occupancy = occupancy(r, c);
	Bfactor = bfactor(r, c);

	//xiaoli begin

	iupacCode = iupac_code(r->type);
	hIndex = -1;

	for (i = 0; i < NTRATOMS; i++)
	  {
	    if (tratoms[i].iupacCode == iupacCode)
	      {
		if (!strcmp(label1,tratoms[i].pdb))
		  {
		    hIndex = tratoms[i].hatomsIndex;
		    //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
		    break;
		  }
	      }
	    
	  }
	//xiaoli end


	
	/* Add u, v, w to the atomic list */
	
	if (FindAtom(r->atom,label1) == NULL)
	{
		CreateAtom( r );
		strcpy( r->atom->type, label1 );
		r->atom->p = u;
		r->atom->occupancy = Occupancy;
		r->atom->BFactor = Bfactor;
		
		//xiaoli added
		r->atom->hIndex = hIndex;
		
	}
	
	
	//xiaoli begin
	
	hIndex = -1;
	
	for (i = 0; i < NTRATOMS; i++)
	  {
	    if (tratoms[i].iupacCode == iupacCode)
	      {
		if (!strcmp(label2,tratoms[i].pdb))
		  {
		    hIndex = tratoms[i].hatomsIndex;
		    //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
		    break;
		  }
	      }
	    
	  }
	//xiaoli end
	
	if (FindAtom(r->atom,label2) == NULL)
	{
		CreateAtom( r );
		strcpy( r->atom->type, label2 );
		r->atom->p = v;
		r->atom->occupancy = Occupancy;
		r->atom->BFactor = Bfactor;
		//xiaoli added
		r->atom->hIndex = hIndex;
	
	}
	

	//xiaoli begin
	
	hIndex = -1;
	
	for (i = 0; i < NTRATOMS; i++)
	  {
	    if (tratoms[i].iupacCode == iupacCode)
	      {
		if (!strcmp(label3,tratoms[i].pdb))
		  {
		    hIndex = tratoms[i].hatomsIndex;
		    //printf("xiaoli rtype = %s, label1=%s and hIndex=%d\n", r->type,label1, hIndex);
		    break;
		  }
	      }
	    
	  }
	//xiaoli end

	if (FindAtom(r->atom,label3) == NULL)
	{
		
		CreateAtom( r );
		strcpy( r->atom->type, label3 );
		r->atom->p = w;
		r->atom->occupancy = Occupancy;
		r->atom->BFactor = Bfactor;
		//xiaoli added
		r->atom->hIndex = hIndex;
	}
	



	

	//printf("xiaoli r->atom=%s, r->atom->type=%s\n", r->atom, r->atom->type);
	return;
}

static  void  ARG( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 2 HG to CG */
  
  hydrogen_pair( r, "CB", "CG", "CD", CH_BOND, "1HG", "2HG" );

  /* Attach 2 HD to CD */
  
  hydrogen_pair( r, "CG", "CD", "NE", CH_BOND, "1HD", "2HD" );

  return;
}


static  void  GLN( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 2 HG to CG */
  
  hydrogen_pair( r, "CB", "CG", "CD", CH_BOND, "1HG", "2HG" );

  return;
}

static  void  PRO( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 2 HG to CG */
  
  hydrogen_pair( r, "CB", "CG", "CD", CH_BOND, "1HG", "2HG" );

  /* Attach 2 HD to CD */
  
  hydrogen_pair( r, "CG", "CD", "N", CH_BOND, "1HD", "2HD" );

  return;
}

static  void  ASN( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  return;
}

static  void  LYS( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 2 HG to CG */
  
  hydrogen_pair( r, "CB", "CG", "CD", CH_BOND, "1HG", "2HG" );

  /* Attach 2 HD to CD */
  
  hydrogen_pair( r, "CG", "CD", "CE", CH_BOND, "1HD", "2HD" );

  /* Attach 2 HE to CE */
  
  hydrogen_pair( r, "CD", "CE", "NZ", CH_BOND, "1HE", "2HE" );

  return;
}

static  void  GLU( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 2 HG to CG */
  
  hydrogen_pair( r, "CB", "CG", "CD", CH_BOND, "1HG", "2HG" );

  return;
}

static  void  CYS( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "SG", CH_BOND, "1HB", "2HB" );

  return;
}

static  void  SER( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "OG", CH_BOND, "1HB", "2HB" );

  return;
}


static  void  ASP( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  return;
}

static  void  PHE( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Add planar hydrogens */

  planar_hydrogen( r, "CD1", "CG", "CE1", "HD1", CH_BOND );
  planar_hydrogen( r, "CE1", "CD1", "CZ", "HE1", CH_BOND );
  planar_hydrogen( r, "CZ", "CE1", "CE2", "HZ", CH_BOND );
  planar_hydrogen( r, "CE2", "CZ", "CD2", "HE2", CH_BOND );
  planar_hydrogen( r, "CD2", "CE2", "CG", "HD2", CH_BOND );

  return;
}

static  void  TRP( RESIDUE *r )   /* W */
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Add planar hydrogens */

  planar_hydrogen( r, "CD1", "CG", "NE1", "HD1", CH_BOND );
  planar_hydrogen( r, "CZ2", "CE2", "CH2", "HZ2", CH_BOND );
  planar_hydrogen( r, "CH2", "CZ2", "CZ3", "HH2", CH_BOND );
  planar_hydrogen( r, "CZ3", "CE3", "CH2", "HZ3", CH_BOND );
  planar_hydrogen( r, "CE3", "CD2", "CZ3", "HE3", CH_BOND );

  return;
}

static  void  TYR( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Add planar hydrogens */
  
  planar_hydrogen( r, "CD1", "CG", "CE1", "HD1", CH_BOND );
  planar_hydrogen( r, "CE1", "CD1", "CZ", "HE1", CH_BOND );
  planar_hydrogen( r, "CD2", "CG", "CE2", "HD2", CH_BOND );
  planar_hydrogen( r, "CE2", "CD2", "CZ", "HE2", CH_BOND );

  return;
}

static  void  HIS( RESIDUE *r )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach planar hydrogen HD2 to CD2 */
  
  planar_hydrogen( r, "CD2", "CG", "NE2", "HD2", CH_BOND );

  /* Attach planar hydrogen HE1 to CE1 */
  
  planar_hydrogen( r, "CE1", "ND1", "NE2", "HE1", CH_BOND );

  return;
}

static  void  ILE( RESIDUE *r, long *seed )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach HB to CB */
  
  fill_tetrahedron( r, "CB", "CA", "CG1", "CG2", "HB", CH_BOND );

  /* Attach 3 1HG2 to CG2 */

  hydrogen_triplet( r, "CB", "CG2", CH_BOND, "1HG2", "2HG2", "3HG2", seed );

  /* Attach 1HG1 and 2HG1 to CG1 */

  hydrogen_pair( r, "CB", "CG1", "CD1", CH_BOND, "1HG1", "2HG1" );

  /* Attach 3 1HD1 to CD1 */

  hydrogen_triplet( r, "CG1", "CD1", CH_BOND, "1HD1", "2HD1", "3HD1", seed );

  return;
}

static  void  LEU( RESIDUE *r, long *seed )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );
  
  /* Attach 2 HB to CB */
  
  hydrogen_pair( r, "CA", "CB", "CG", CH_BOND, "1HB", "2HB" );

  /* Attach 3 1HD1 to CD1 */
  
  hydrogen_triplet( r, "CG", "CD1", CH_BOND, "1HD1", "2HD1", "3HD1", seed );
  
  /* Attach 3 1HD2 to CD2 */
  
  hydrogen_triplet( r, "CG", "CD2", CH_BOND, "1HD2", "2HD2", "3HD2", seed );

  /* Attach HG to CG */

  fill_tetrahedron(r, "CG", "CB", "CD1", "CD2", "HG", CH_BOND );

  return;
}

static  void  VAL( RESIDUE *r, long *seed )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );

  /* Attach HB to CB */

  fill_tetrahedron( r, "CB", "CA", "CG1", "CG2", "HB", CH_BOND );

  /* Attach 3 1HG1 to CG1 */
  
  hydrogen_triplet( r, "CB", "CG1", CH_BOND, "1HG1", "2HG1", "3HG1", seed );
  
  /* Attach 3 1HG2 to CG2 */
  
  hydrogen_triplet( r, "CB", "CG2", CH_BOND, "1HG2", "2HG2", "3HG2", seed );

  return;
}

static  void  THR( RESIDUE *r, long *seed )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );
  
  /* Attach HB */

  fill_tetrahedron( r, "CB", "CA", "OG1", "CG2", "HB", CH_BOND );

  /* Attach 3 hydrogens to CG2 */

  hydrogen_triplet( r, "CB", "CG2", CH_BOND, "1HG2", "2HG2", "3HG2", seed );
  
  return;
}

static  void  ALA( RESIDUE *r, long *seed )
{
  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );
  
  /* Attach 3 HB to CB */

  hydrogen_triplet( r, "CA", "CB", CH_BOND, "1HB", "2HB", "3HB", seed );
  
  return;
}

static  void  GLY( RESIDUE *r )
{
  hydrogen_pair( r, "C", "CA", "N", CH_BOND, "1HA", "2HA" );
  return;
}

static  void  MET( RESIDUE *r, long *seed )
{
  /* Attach 3 hydrogens to CE */

  hydrogen_triplet( r, "SD", "CE", CH_BOND, "1HE", "2HE", "3HE", seed );
  
  /* Attach two hydrogens to CB */
  
  hydrogen_pair( r, "CG", "CB", "CA", CH_BOND, "1HB", "2HB" );
  
  /* Attach two hydrogen to CG */

  hydrogen_pair( r, "SD", "CG", "CB", CH_BOND, "1HG", "2HG" );

  /* Attach HA to CA */

  fill_tetrahedron( r, "CA", "N", "C", "CB", "HA", CH_BOND );
  
  return;
}

void  add_hydrogens( RESIDUE *r, long *seed )
{
  VECTOR    ref, phi_normal, hydro, C, CA, N;
  float     occ_CA, occ_N, occ_C;
  float     bfac_CA, bfac_N, bfac_C;
  char      res;
  ATOM *h;

  res = iupac_code(r->type);

  if ((h = FindAtom(r->atom,"H")) != NULL)  // Standardize labelling of amide hydrogens to HN SJN Apr 2/01
    { 
      //printf("xiaoli h->type=%s\n",h->type); 
	  strcpy(h->type,"HN");
	  h->hIndex = HYDRO_H;
	
  }

  if (FindAtom(r->atom,"HN") == NULL && FindAtom(r->atom,"H") == NULL)
  {
	  /* Attach the amide hydrogen (HN), This is done for all residues */

	  if( r->lastc.x != 0.0 && r->lastc.y != 0.0 && r->lastc.z != 0.0 && 
		  res != 'P' )
	  {
		if( atm_vector(r, "N",  &N) || atm_vector(r, "CA", &CA)  || atm_vector(r, "C",  &C) )
		{
			r->errflags |= RES_ERR_MISSING_ATOMS;
			return;
		}
			/* SJN - modified error handling 
			if( atm_vector(r, "N",  &N)  )  no_vector( "N",  1 );
		if( atm_vector(r, "CA", &CA) )  no_vector( "CA", 1 );
		if( atm_vector(r, "C",  &C)  )  no_vector( "C",  1 );
			*/

		/* A normalized unit vector defining the reference plane */
 
		ref = normalize( cross( diff( C, CA ), diff( N, CA ) ) );

		/* A unit vector defining the phi plane */
 
		phi_normal =  normalize( cross( diff( CA, N ), diff( r->lastc, N ) ) );
 
		hydro = multiply( normalize( diff( r->lastc, N ) ), NH_BOND );

		CreateAtom( r );
		strcpy( r->atom->type, "HN" );
		r->atom->hIndex = HYDRO_H;
		/* I've checked this and it does in fact create a C-N-H angle of CNH degrees with an HN distance of NH_BOND */
		r->atom->p = add( N, rotate( hydro, phi_normal, CNH ) );
		r->coords[H_COORD].x = r->atom->p.x;
		r->coords[H_COORD].y = r->atom->p.y;
		r->coords[H_COORD].z = r->atom->p.z;
   
		/* Position of HN depends on CA, N and the last C                       */
		/* Its occupancy is therefore chosen to be the lowest of the three.     */
		/* B-factor on the other hand is chosen to be the highest of the three. */
    
		occ_CA = occupancy(r,"CA");
		occ_N = occupancy(r,"N");
		r->atom->occupancy = occ_CA < occ_N ? occ_CA : occ_N;
    
		bfac_CA = bfactor(r,"CA");
		bfac_N = bfactor(r,"N");
		r->atom->BFactor = bfac_CA > bfac_N ? bfac_CA : bfac_N;
		r->atom->hIndex = 0;
	  }
  }
  
  /* The following is done for specific residues */
  
  switch(res)
  {
    case 'M':  MET( r, seed );
               break;
    case 'G':  GLY( r );
               break;
    case 'A':  ALA( r, seed );
               break;
    case 'T':  THR( r, seed );
               break;
    case 'V':  VAL( r, seed );
               break;
    case 'L':  LEU( r, seed );
               break;
    case 'I':  ILE( r, seed );
               break;
    case 'H':  HIS( r );
               break;
    case 'Y':  TYR( r );
               break;
    case 'W':  TRP( r );
               break;
    case 'F':  PHE( r );
               break;
    case 'D':  ASP( r );
               break;
    case 'S':  SER( r );
               break;
    case 'C':  CYS( r );
               break;
    case 'E':  GLU( r );
               break;
    case 'K':  LYS( r );
               break;
    case 'N':  ASN( r );
               break;
    case 'P':  PRO( r );
               break;
    case 'Q':  GLN( r );
               break;
    case 'R':  ARG( r );
               break;
    default:   fprintf( stderr, "Critical error: unknown residue %c\n", res );
               fprintf( stderr, "Aborting...\n" );
               exit(1);
  }
  return;
}
