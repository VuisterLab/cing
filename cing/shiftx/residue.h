#ifndef  RESIDUE_H

#ifndef MAIN_H
#include "main.h"
#endif

#ifndef HETATM_H
#include "hetatm.h"
#endif

void  ReleaseResidue( RESIDUE *r );
ATOM  *FindAtom( ATOM *atm, char *type );
void  CreateAtom( RESIDUE *r );
void  inspect_residue( RESIDUE *r );
char  iupac_code( char *code );
char  iupac_code_safe( char *code );
int   rc_idx( char res );
int  next_residue( FILE *in, RESIDUE *r, HETATM **h,int clear );

#define  RESIDUE_H

#endif
