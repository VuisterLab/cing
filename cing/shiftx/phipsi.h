#ifndef PHIPSI_H

typedef struct
{
  float     **ca;
  float     **ca_dev;
  float     **cb;
  float     **co;
  float     **ha;
  float     **ha_dev;
  float     **hn;
  float     **hn_dev;
  float     **n15;
} PHIPSI;

PHIPSI  *PhiPsiContours(void);
PHIPSI  *SecondDerivatives( PHIPSI *p );
void     FreeMatrices( float **p );
void     FreePhiPsiMatrices( PHIPSI *p );
CSHIFT  *PhiPsiMatrices( RESIDUE *r, PHIPSI *p, PHIPSI *q, CSHIFT *cs, float last_psi );

#define  PHIPSI_H

#endif
