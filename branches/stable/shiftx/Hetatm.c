#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "hetatm.h"

HETATM   *AddWaterOxy( char *buff, HETATM *p )
{
  static  id=1;
  char    *s, atm[5], mol[5],chain[5]="\0", label;  /* SJN */
  int     line, atm_num;
  float   x, y, z, bfactor, occupancy;
  HETATM  *new;

  s = buff;
  s += 6;
  sscanf(s,"%5d",&line);
  sscanf( s, "%5d%4[a-zA-Z0-9* ]", &line, atm);
  sscanf( s, "%5d%*c%4[a-zA-Z0-9* ]%*c%3[a-zA-Z0-9* ]", &line, atm,mol);

  if (sscanf( s, "%5d%*c%4[a-zA-Z0-9* ']%*c%3s%*c%c%4d%*c%8f%8f%8f%6f%6f", &line, atm, mol,&label, &atm_num, &x, 
              &y, &z, &occupancy, &bfactor ) != 10 )	{
	  /*
		if (sscanf( s, "%6d%5[a-zA-Z0-9 ]%s %s %d %f %f %f %f %f", &line, atm, mol, chain, &atm_num, &x, 
			&y, &z, &occupancy, &bfactor ) != 10 )	{   /* SJN */
			fprintf( stderr, "File format error found on the following line:\n" );
			fprintf( stderr, "%s\n", buff );
			fprintf( stderr, "Aborting...\n" );
			exit(1);
//		}
  }

  /* Strip off leading and trailing blanks in the atom name */
	while (atm[0] == ' ')
	{
		memmove(atm,&atm[1],strlen(atm));
	}
	while (atm[strlen(atm)-1] == ' ')
	{
		atm[strlen(atm)-1] = '\0';
	}
/*
	if (chain[0] != '\0' && toupper(chain[0]) != 'A')
	{
		printf("Chain Error\n");
	}
	*/
  if( strcmp( atm, "O" ) || strcmp( mol, "HOH" ) || (chain[0] != '\0' && toupper(chain[0]) != 'A')) {  /* SJN */
		return(p);
  }

  new = (HETATM *) malloc( (unsigned) sizeof(HETATM) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating HETATM link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(HETATM) );
  new->r.x = x;
  new->r.y = y;
  new->r.z = z;
  new->BFactor = bfactor;
  new->occupancy = occupancy;
  new->id = id;
  id++;
  if( p != NULL )
  {
    p->last = new;
    new->next = p;
  }
  return(new);
}

void  FreeWaterOxy( HETATM *h )
{
  HETATM *p;
  
  while( h != NULL )
  {
    p = h->next;
    free(h);
    h = p;
  }
  return;
}
