#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "psa.h"
#include "main.h"
#include "hetatm.h"

void  ReleaseResidue( RESIDUE *r )
{
  ATOM   *q;
  
  /* Release everything except the lastc and the lastca vectors, occ_C and bfac_C. */
  
  strcpy( r->type, "NA" );
  r->num = -1;
  r->phi = r->psi = r->omega = r->chi = r->theta = NA;

  /* Release link list */
  
  while( r->atom != NULL )
  {
    q = r->atom->next;
    free( r->atom );
    r->atom = q;
  }
  r->atom = NULL;
  return;
}

ATOM  *FindAtom( ATOM *atm, char *type )
{
  ATOM   *p;
  
  p = atm;
  while( p != NULL )
  {
    if (!strcmp(p->type,type)) 
		{
			return(p);
		}
    p = p->next;
  }
  return(NULL);
}

void  CreateAtom( RESIDUE *r )
{
  ATOM    *new;

  new = (ATOM *) malloc( (unsigned) sizeof(ATOM) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(ATOM) );
  new->occupancy = 1.0;
  new->BFactor = 0.0;
  new->hIndex = -1;
  if( r->atom == NULL )  r->atom = new;
  else
  {
    new->next = r->atom;
    r->atom->last = new;
  }
  r->atom = new;
  return;
}

/* Read a line from file           */
/* returns:  1  success            */
/*           0  comment, blank     */
/*          -1  EOF                */

static  int  ReadLine( char *line, int n, FILE *fpt )
{
  int	content=0;
  char  *p;
  

  if( fgets( line, n, fpt )==NULL )  return(-1);

  /* Remove the last newline character */
  
  if( (p=strrchr( line, '\n' ))!=NULL )  *p = '\0';  

  /* Blank line or comment */

  if( strlen(line)==0 || *line == '#'  )  return(0);

  /* Check for alpha-numerical characters */
  
  p = line;
  while( *p != '\0' )
  {
    if( isalnum(*p) || *p=='{' || *p=='}' )  content++;
    p++;
  }

  if( content == 0 )  return(0);
  return(1);
}

#define  FLUSH 1
#define  KEEP  0
#define  READY 0
#define  START 1
#define  END   2

int  next_residue( FILE *in, RESIDUE *r, HETATM **h,int clear )
{
  char                     *p, atom[5], res[15],resndx[5],label[2],sublabel; /* SJN - added resndx and label */
  static char              Line[500],FoundAtom;  /* SJN: FoundAtom is true when an atom line from the correct chain has been seen */
  int                      atom_num, res_num, status;
  static int               target=1, line_in_mem=FLUSH;
  float                    x, y, z, a, b;
  ATOM                     *q;
  static unsigned char     state=READY;
	static long current_res;		 /* SJN - what residue is currently under consideration */
	static char current_res_sub; /* SJN = subscript (if any) of current residue i.e. A,B, C... */

	/* SJN: reset all static variables for new file */
	if (clear) {
		FoundAtom = 0;
		target = 1;
		line_in_mem = FLUSH;
		state = READY;
		return(0);
	}

  /* Clear all data previously stored in RESIDUE */
  /* Except for the lastc and the lastca vectors */

  ReleaseResidue( r );  
  
  /* Skip reading the next line if line is already in memory */
  
  while( (status = (line_in_mem==FLUSH) ? ReadLine( Line, 500, in ) : 1) >= 0 )
  {
    line_in_mem = FLUSH;
    if( status == 0 ) {
			continue;
		}

    if (((p=strstr(Line,"ATOM")) == NULL || p != Line) && state == START) {
      /* Evidently this is the end of the atom list */
      state = END;
      line_in_mem = KEEP;
      return(1);
    }
      
    if( (p=strstr( Line, "TER" ))!=NULL && p==Line && state!=END && FoundAtom)
    {
      if( state == START )
      {
        state = END;
        line_in_mem = KEEP;
        return(1);
      }
      else
      {
        state = END;
      }
    }
    
    /* Build a list of oxygen from water */
    
    if( (p=strstr( Line, "HETATM" ))!=NULL && p==Line )
    {
      *h = AddWaterOxy( p, *h );
    }
    
    if( (p=strstr( Line, "ATOM" ))!=NULL && p==Line && state!=END )
    {
      p+=4;  /* SJN - modified to handle extra character after residue name */
			/*    ATOM atom_num atom residue res_num x y z junk junk */
			/* ie ATOM 1 N SER 145 1.00 1.00 1.00 etc */
      if (sscanf( p, "%d %s %s %d %f %f %f %f %f", &atom_num, atom, res, 
       &res_num, &x, &y, &z, &a, &b )!=9 ) {
			/*    ATOM atom_num atom residue chain res_num x y z junk junk */
			/* ie ATOM 1 N SER A 145 1.00 1.00 1.00 etc */
        if (sscanf( p, "%d %s %s %1s %s %f %f %f %f %f", &atom_num, atom, res, label,
         resndx, &x, &y, &z, &a, &b )!=10 ) {
          fprintf( stderr, "File format error...\n" );				
     
					fprintf( stderr, "%s\n", Line );
          exit(1);
        }
				/* SJN - deal with peculiar resnos like "1C" (see 1MKW for example) and ignore lines that aren't for */
				/* selected chain */
				else {
					sublabel = resndx[strlen(resndx)-1];

					if (!isdigit(sublabel)) {
						continue;
					}
					res_num = atoi(resndx);  
					
					if (UseChain != 0 && label[0] != UseChain) {
						continue;
					}
				}
      }
			FoundAtom = 1;
     	if (strlen(res) > 3) {
				memmove(&res[0],&res[strlen(res)-3],4);
				/*
				res[0] = res[1];
				res[1] = res[2];
				res[2] = res[3];
				res[3] = '\0';
				*/
      }
      if( state == READY )
      {																																 
        target = res_num;
        state = START;
      }
      
      /*if( res_num == target+1 ) SJN need to deal with case of missing residues */
			if (res_num > target) 
      {
        /*target++;*/
				target = res_num; 
        line_in_mem = KEEP;
				r->errflags |= RES_ERR_MISSING_RES;
        return(1);
      }
      if( r->num == -1 )
      {
        r->num = res_num;
        strcpy( r->type, res );
      }
      else
      {
        if( strcmp( r->type, res ) )
        {
          fprintf( stderr, "Unexpected change in residue type!\n" );
          fprintf( stderr, "%s\n", Line );
          fprintf( stderr, "Aborting...\n" );
          exit(1);
        }
      }

      if( (q=FindAtom( r->atom, atom ))==NULL )
      {
        CreateAtom( r );
        strcpy( r->atom->type, atom );
        r->atom->p.x = x;
        r->atom->p.y = y;
        r->atom->p.z = z;
        r->atom->occupancy = a;
        r->atom->BFactor = b;
      }
            
      continue;
    }
  }
  return(0);
}

void  inspect_residue( RESIDUE *r )
{
  ATOM      *p, *last;

  p = r->atom;
  while( p!=NULL )
  {
    /* Many (perhaps all) pdb files use "H" to represent the amide proton. */
    /* In PSA, I thought it would be nice to use "HN" to give a stronger   */
    /* indication of the relation with 15N, serving as my own reminder.    */
  
    if( !strcmp( p->type, "H" ) )  strcpy( p->type, "HN" );
    
    /* We disregard                                                 */
    /*                                                              */
    /*         "HG1"                          in Thr (T)            */
    /*         "HG"                           in Ser (S)            */
    /*         "1HH1", "2HH1", "1HH2", "2HH2" in Arg (R)            */
    /*         "HH"                           in Tyr (Y)            */
    /*         "HE1"                          in Trp (W)            */
    
    if( (!strcmp( r->type, "THR" ) && !strcmp( p->type, "HG1" )) ||
        (!strcmp( r->type, "SER" ) && !strcmp( p->type, "HG"  )) ||
        (!strcmp( r->type, "ARG" ) && strstr( p->type, "HH" )!=NULL) ||
        (!strcmp( r->type, "TYR" ) && !strcmp( p->type, "HH" )) ||
        (!strcmp( r->type, "TRP" ) && !strcmp( p->type, "HE1" ) )
      )
    {
      if( p->next != NULL )
			{
				p->next->last = p->last;
			}
      if( p->last != NULL )
      {
        p->last->next = p->next;
        last = p->last;
        free(p);
        p = last;
      }
      else
      {
        r->atom = p->next;
        free(p);
        p = r->atom;
        continue;
      }
      
    }
    
    p = p->next;
  }

  return;
}

char  iupac_code( char *code )
{
  if( !strcmp( code, "ALA" ) )  return('A');
  if( !strcmp( code, "CYS" ) )  return('C');
  if( !strcmp( code, "ASP" ) )  return('D');
  if( !strcmp( code, "GLU" ) )  return('E');
  if( !strcmp( code, "PHE" ) )  return('F');
  if( !strcmp( code, "GLY" ) )  return('G');
  if( !strcmp( code, "HIS" ) )  return('H');
  if( !strcmp( code, "ILE" ) )  return('I');
  if( !strcmp( code, "LYS" ) )  return('K');
  if( !strcmp( code, "LEU" ) )  return('L');
  if( !strcmp( code, "MET" ) )  return('M');
  if( !strcmp( code, "ASN" ) )  return('N');
  if( !strcmp( code, "PRO" ) )  return('P');
  if( !strcmp( code, "GLN" ) )  return('Q');
  if( !strcmp( code, "ARG" ) )  return('R');
  if( !strcmp( code, "SER" ) )  return('S');
  if( !strcmp( code, "THR" ) )  return('T');
  if( !strcmp( code, "VAL" ) )  return('V');
  if( !strcmp( code, "TRP" ) )  return('W');
  if( !strcmp( code, "TYR" ) )  return('Y');
  fprintf( stderr, "Unknown three-letter code --- %s!\n", code );
  exit(1);
}

char  iupac_code_safe( char *code )   // Return IUPAC code without freaking out about unknown three letter codes
{
  if( !strcmp( code, "ALA" ) )  return('A');
  if( !strcmp( code, "CYS" ) )  return('C');
  if( !strcmp( code, "ASP" ) )  return('D');
  if( !strcmp( code, "GLU" ) )  return('E');
  if( !strcmp( code, "PHE" ) )  return('F');
  if( !strcmp( code, "GLY" ) )  return('G');
  if( !strcmp( code, "HIS" ) )  return('H');
  if( !strcmp( code, "ILE" ) )  return('I');
  if( !strcmp( code, "LYS" ) )  return('K');
  if( !strcmp( code, "LEU" ) )  return('L');
  if( !strcmp( code, "MET" ) )  return('M');
  if( !strcmp( code, "ASN" ) )  return('N');
  if( !strcmp( code, "PRO" ) )  return('P');
  if( !strcmp( code, "GLN" ) )  return('Q');
  if( !strcmp( code, "ARG" ) )  return('R');
  if( !strcmp( code, "SER" ) )  return('S');
  if( !strcmp( code, "THR" ) )  return('T');
  if( !strcmp( code, "VAL" ) )  return('V');
  if( !strcmp( code, "TRP" ) )  return('W');
  if( !strcmp( code, "TYR" ) )  return('Y');
  return('X');
}

int  rc_idx( char res )
{
  int     i;

  switch(res)
  {
    case 'A':     i = 0;
                  break;
    case 'C':     i = 1;
                  break;
    case 'D':     i = 2;
                  break;
    case 'E':     i = 3;
                  break;
    case 'F':     i = 4;
                  break;
    case 'G':     i = 5;
                  break;
    case 'H':     i = 6;
                  break;
    case 'I':     i = 7;
                  break;
    case 'K':     i = 8;
                  break;
    case 'L':     i = 9;
                  break;
    case 'M':     i = 10;
                  break;
    case 'N':     i = 11;
                  break;
    case 'P':     i = 12;
                  break;
    case 'Q':     i = 13;
                  break;
    case 'R':     i = 14;
                  break;
    case 'S':     i = 15;
                  break;
    case 'T':     i = 16;
                  break;
    case 'V':     i = 17;
                  break;
    case 'W':     i = 18;
                  break;
    case 'Y':     i = 19;
                  break;
    default:      fprintf( stderr, "Unknown residue %c\n", res );
                  fprintf( stderr, "Aborting...\n" );
                  exit(1);
  }
  return(i);
}


