#include <stdio.h>
#include "psa.h"
#include "main.h"
#include "nn.h"
#include "cs.h"


RES   *CreatePRO( RESIDUE *r, RES *p )
{
  RES *new;


  new = CreateRES( p );
  new->type = 'P';
  new->num = r->num;
  return(new);
}

void  ProlineEffect( CSHIFT *cs, RES *pro )
{
  RES       *p;
  CSHIFT    *q;
  int        m;

  p = pro;
  while( p != NULL )
  {
    m = p->num - 1;
    if( m >= 1 )
    {
      if( (q=FindCS( cs, m ))!=NULL )
      {
        if( q->type != 'G' && q->ca != NA )  q->ca--;
      }
    }
    p = p->next;
  }
  return;
}
