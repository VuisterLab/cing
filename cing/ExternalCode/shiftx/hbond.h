#ifndef  HBOND_H

#ifndef MAIN_H
#include "main.h"
#endif

#ifndef HETATM_H
#include "hetatm.h"
#endif

#ifndef CS_H
#include "cs.h"
#endif

typedef struct   HBOND
{
  int            res_d,    res_r;
  char           aa_d,     aa_r;
  char           atm_d[5], atm_r[5];
  float          dis;
  struct HBOND   *next, *last;
  double energy;
} HBOND;


void       Donor( RESIDUE *r, RES **d );
void       Receptor( RESIDUE *r, RES **recp );
void       AddToReceptor( RES **r, HETATM *w );
void       FreeHBond( HBOND *hb );
HBOND     *HydrogenBonds( RES *donor, RES *receptor );
CSHIFT    *HBondShifts( HBOND **hb,RESIDUE *Rz,int rno );
CSHIFT    *HBondShifts2(HBOND **hb,RESIDUE *Rz,int rno );

#define  HBOND_H

#endif
