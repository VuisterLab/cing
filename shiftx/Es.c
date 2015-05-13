#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "psa.h"
#include "main.h"
#include "cs.h"
#include "vector.h"
#include "hydrogens.h"

struct hconnect 
{
  char *res;
  char *hatom;
  char *connect;
  char r;
} hconnect[] = 
  {
    "GLY",	"HA2",	"CA", 'G',
    "GLY",	"HA3",	"CA", 'G',
    "ILE",	"HB",	"CB", 'I',
    "THR",	"HB",	"CB", 'T',
    "VAL",	"HB",	"CB", 'V',
    "ALA",	"HB1",	"CB", 'A',
    "ALA",	"HB2",	"CB", 'A',
    "ARG",	"HB2",	"CB", 'R',
    "ASP",	"HB2",	"CB", 'D',
    "ASN",	"HB2",	"CB", 'N',
    "CYS",	"HB2",	"CB", 'C',
    "GLU",	"HB2",	"CB", 'E',
    "GLN",	"HB2",	"CB", 'Q',
    "HIS",	"HB2",	"CB", 'H',
    "LEU",	"HB2",	"CB", 'L',
    "LYS",	"HB2",	"CB", 'K',
    "MET",	"HB2",	"CB", 'M',
    "PHE",	"HB2",	"CB", 'F',
    "PRO",	"HB2",	"CB", 'P',
    "SER",	"HB2",	"CB", 'S',
    "TRP",	"HB2",	"CB", 'W',
    "TYR",	"HB2",	"CB", 'Y',
    "ALA",	"HB3",	"CB", 'A',
    "ARG",	"HB3",	"CB", 'R',
    "ASP",	"HB3",	"CB", 'D',
    "ASN",	"HB3",	"CB", 'N',
    "CYS",	"HB3",	"CB", 'C',
    "GLU",	"HB3",	"CB", 'E',
    "GLN",	"HB3",	"CB", 'Q',
    "HIS",	"HB3",	"CB", 'H',
    "LEU",	"HB3",	"CB", 'L',
    "LYS",	"HB3",	"CB", 'K',
    "MET",	"HB3",	"CB", 'M',
    "PHE",	"HB3",	"CB", 'F',
    "PRO",	"HB3",	"CB", 'P',
    "SER",	"HB3",	"CB", 'S',
    "TRP",	"HB3",	"CB", 'W',
    "TYR",	"HB3",	"CB", 'Y',
    "HIS",	"HD1",	"ND1", 'H',
    "ILE",	"HD1",	"CD1", 'I',
    "PHE",	"HD1",	"CD1", 'F',
    "TRP",	"HD1",	"CD1", 'W',
    "TYR",	"HD1",	"CD1", 'Y',
    "LEU",	"HD11",	"CD1", 'L',
    "LEU",	"HD12",	"CD1", 'L',
    "LEU",	"HD13",	"CD1", 'L',
    "ARG",	"HD2",	"CD", 'R',
    "ASP",	"HD2",	"OD2", 'D',
    "HIS",	"HD2",	"CD2", 'H',
    "ILE",	"HD2",	"CD1", 'I',
    "LYS",	"HD2",	"CD", 'K',
    "PHE",	"HD2",	"CD2", 'F',
    "PRO",	"HD2",	"CD", 'P',
    "TYR",	"HD2",	"CD2", 'Y',
    "ASN",	"HD21",	"ND2", 'N',
    "LEU",	"HD21",	"CD2", 'L',
    "ASN",	"HD22",	"ND2", 'N',
    "LEU",	"HD22",	"CD2", 'L',
    "LEU",	"HD23",	"CD2", 'L',
    "ARG",	"HD3",	"CD", 'R',
    "ILE",	"HD3",	"CD1", 'I',
    "LYS",	"HD3",	"CD", 'K',
    "PRO",	"HD3",	"CD", 'P',
    "ARG",	"HE",	"NE", 'R',
    "HIS",	"HE1",	"CE1", 'H',
    "MET",	"HE1",	"CE", 'M',
    "PHE",	"HE1",	"CE1", 'F',
    "TRP",	"HE1",	"NE1", 'W',
    "TYR",	"HE1",	"CE1", 'Y',
    "GLU",	"HE2",	"OE2", 'E',
    "HIS",	"HE2",	"NE2", 'H',
    "LYS",	"HE2",	"CE", 'K',
    "MET",	"HE2",	"CE", 'M',
    "PHE",	"HE2",	"CE2", 'F',
    "TYR",	"HE2",	"CE2", 'Y',
    "GLN",	"HE21",	"NE2", 'Q',
    "GLN",	"HE22",	"NE2", 'Q',
    "LYS",	"HE3",	"CE", 'K',
    "MET",	"HE3",	"CE", 'M',
    "TRP",	"HE3",	"CE3", 'W',
    "CYS",	"HG",	"SG", 'C',
    "LEU",	"HG",	"CG", 'L',
    "SER",	"HG",	"OG", 'S',
    "THR",	"HG1",	"OG1", 'T',
    "VAL",	"HG11",	"CG1", 'V',
    "ILE",	"HG12",	"CG1", 'I',
    "VAL",	"HG12",	"CG1", 'V',
    "ILE",	"HG13",	"CG1", 'I',
    "VAL",	"HG13",	"CG1", 'V',
    "ARG",	"HG2",	"CG", 'R',
    "GLU",	"HG2",	"CG", 'E',
    "GLN",	"HG2",	"CG", 'Q',
    "LYS",	"HG2",	"CG", 'K',
    "MET",	"HG2",	"CG", 'M',
    "PRO",	"HG2",	"CG", 'P',
    "ILE",	"HG21",	"CG2", 'I',
    "THR",	"HG21",	"CG2", 'T',
    "VAL",	"HG21",	"CG2", 'V',
    "ILE",	"HG22",	"CG2", 'I',
    "THR",	"HG22",	"CG2", 'T',
    "VAL",	"HG22",	"CG2", 'V',
    "ILE",	"HG23",	"CG2", 'I',
    "THR",	"HG23",	"CG2", 'T',
    "VAL",	"HG23",	"CG2", 'V',
    "ARG",	"HG3",	"CG",  'R',
    "GLU",	"HG3",	"CG",  'E',
    "GLN",	"HG3",	"CG",  'Q',
    "LYS",	"HG3",	"CG",  'K',
    "MET",	"HG3",	"CG",  'M',
    "PRO",	"HG3",	"CG",  'P',
    "TYR",	"HH",	"OH",  'Y',
    "ARG",	"HH11",	"NH1", 'R',
    "ARG",	"HH12",	"NH1", 'R',
    "TRP",	"HH2",	"C22", 'W',
    "ARG",	"HH21",	"NH2", 'R',
    "ARG",	"HH22",	"NH2", 'R',
    "PHE",	"HZ",	"CZ",  'F',
    "LYS",	"HZ1",	"NZ",  'K',
    "LYS",	"HZ2",	"NZ",  'K',
    "TRP",	"HZ2",	"CZ2", 'W',
    "LYS",	"HZ3",	"NZ",  'K',
    "TRP",	"HZ3",	"CZ3",  'W'
  };

#define NHCONNECT (sizeof(hconnect)/sizeof(struct hconnect))

typedef struct ESHIFT
{
  char            type;
  unsigned int    n;
  float           ca;
  float           ha;
  float           hn;
  float			  hside[NHATOMS];   // ADDNEW
} ESHIFT;


#define  EPSILON    -1.0E-12

/* Charges are in electrostatic units */

#define  QC          0.9612E-10
#define  QO         -1.39374E-10
#define  QN         -0.7209E-10


static float  es( ATM *a, ATM *b, ATM *c, float q )
{
  float      d;
  VECTOR     u, v, r;

  if( a == NULL || b == NULL )  return(0.0);

  u = normalize( diff( b->r, a->r ) );
  r = diff( b->r, c->r );
  v = normalize( r );
  d = dot( r, r );
  
  /* This works well for HA */

  /*if( sqrt(d) > 3.0 )  return(0.0);*/
  if (d > 9.0) 
    {   /* SJN - a little speedup here */
      return(0.0);
    }

  /* Compute the electrostatic shift in ppm                             */
  /* In accordance with Buckingham (Canadian Journal of Chemistry,      */
  /* vol 38 (1960) 300 - 307),                                          */
  /*                                                                    */
  /* electric screening constant sigma is                               */
  /*                                                                    */
  /* sigma = 2E-12 * Ez - 1.0E-18 * E^2                                 */
  /*                                                                    */
  /* where electric field is expressed in electrostatic units (esu)     */
  /* in which case, charges are expressed in esu and distances in       */
  /* cm. To convert this screening constant to chemical shift in PPM,   */
  /* multiply it by 1.0E+6. To understand the about equation, you MUST  */
  /* read Buckingham's paper. Reading others do no justice to the       */
  /* original derivation.                                               */
  
  return( -(EPSILON)*q*dot(u,v)*1.0E+22/d );
}


static  ESHIFT es_shift( RES *protein, RES *target )
{
  RES       *res;
  ATM       *atm, *CA=NULL, *HA=NULL, *N=NULL, *HN=NULL, *HS[NHATOMS], *HSPARTNER; // ADDNEW
  ESHIFT    eshift={0, 0, 0, 0, 0};
  float     charge;
  int       oxy, i, j;

  for (i = 0; i < NHATOMS; i++)   // ADDNEW
    {
      HS[i] = NULL;
      eshift.hside[i] = 0;
    }
  /* Identify the target residue number, CA and HA */

  eshift.type = target->type;
  eshift.n = target->num;
  atm = target->atom;
  while( atm != NULL )
    {
      if( !strcmp( atm->type, "CA" ) )
	{
	  CA = atm;
	}
      else if( !strcmp( atm->type, "HA" ) )  
	{
	  HA = atm;
	  HS[HYDRO_HA] = atm;
	}
      else if( !strcmp( atm->type, "N" ) )  
	{
	  N = atm;
	}
      else if( !strcmp( atm->type, "HN" ) )
	{
	  HN = atm;
	  HS[HYDRO_H] = atm;
	}
      else   // ADDNEW
	{
	  if (atm->hIndex != -1)
	    {
	      HS[atm->hIndex] = atm;
	    }
	  /*
	    for (i = 0; i < NHATOMS; i++)
	    {
	    if (!strcmp(atm->type,hatoms[i].name))
	    {
	    HS[i] = atm;
	    break;
	    }
	    }
	  */
	}
      atm = atm->next;
    }

  if ((CA==NULL || HA==NULL) && (N==NULL || HN==NULL))
    {
      return(eshift);
    }


  /* Calculate overall electrostatic shift */
  
  res = protein;
  while( res != NULL )
    {
      /* Exclude nearest-neighbor interactions */
	  
      if( abs(res->num - eshift.n) > 1 )
	{
	  atm = res->atom;
	  while( atm != NULL )
	    {
	      /* Check the type of atom before calling "es" */
	      /* --- it is an expensive operation           */
			  
	      oxy = 0;
	      if( !strcmp( atm->type, "O" ) )
		{
		  charge = QO;
		  oxy = 1;
		}
	      else 
		{
		  if( !strcmp( atm->type, "C" ) )
		    {
		      charge = QC;
		    }
		  else 
		    {
		      if( !strcmp( atm->type, "N" ) ) 
			{
			  charge = QN;
			}
		      else 
			{
			  if( strstr( atm->type, "OD" )!=NULL || strstr( atm->type, "OE" )!=NULL   ) 
			    {
			      charge = QO;
			    }
			  else 
			    {
			      charge = 0.0;
			    }
			}
		    }
		}
			  
	      if( charge != 0.0 ) 
		{
		  eshift.ha += es( CA, HA, atm, charge );
		  if (eshift.ha != 0.0)
		    {
		      j = j; // SJN DEBUG
		    }

		  eshift.ca += es( N, CA, atm, charge );
				  
		  for (i = 0; i < NHATOMS; i++)   // ADDNEW
		    {
		      if (HS[i] != NULL)
			{
			  for (j = 0 ; j < NHCONNECT; j++)
			    {
			      if (hconnect[j].r == target->type && !strcmp(hatoms[i].name,hconnect[j].hatom))
				{
				  break;
				}
			    }
			  if (j != NHCONNECT)
			    {
			      HSPARTNER = target->atom;
			      while (HSPARTNER != NULL)
				{
				  if (!strcmp(HSPARTNER->type,hconnect[j].connect))
				    {
				      break;
				    }
				  HSPARTNER = HSPARTNER->next;
				}
							  
			      if (HSPARTNER != NULL)
				{
				  eshift.hside[i] += es(HSPARTNER, HS[i], atm, charge);
				  if (eshift.hside[i] != 0.0)
				    {
				      j = j;	
				    }
				}
			    }
			}
		    }
		  if( !oxy ) 
		    {
		      eshift.hn += es( N, HN, atm, charge );
		    }
		}
			  
	      atm = atm->next;
	    }
	}
      res = res->next;
    }
  eshift.hside[HYDRO_H] = eshift.hn;
  eshift.hside[HYDRO_HA] = eshift.ha;
  
  return(eshift);
}

CSHIFT  *Electrostatics( RES *p )
{
  RES        *res;
  CSHIFT     *cs=NULL;
  ESHIFT     es;
  int i;
  
  res = p;
  
  while( res != NULL )
    {
      cs = CreateCS( cs );
      es = es_shift( p, res );
      cs->type = es.type;
      cs->n = es.n;
      cs->ca = es.ca;
      cs->ha = es.ha;
      cs->hn = es.hn;
      for (i = 0; i < NHATOMS; i++)
	{
	  cs->hside[i] = es.hside[i];
	}
      res = res->next;
    }

  return(cs);
}
