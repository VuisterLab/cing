#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "psa.h"
#include "main.h"
#include "nn.h"
#include "vector.h"
#include "residue.h"
#include "hetatm.h"
#include "cs.h"
#include "hbond.h"

#define HNMAXBONDLENGTH 3.5

void  Donor( RESIDUE *r, RES **d )
{
  VECTOR   ha, hn;
  
  
  *d = CreateRES( *d );
  (*d)->type = iupac_code( r->type );
  (*d)->num = r->num;
  
  if( !atm_vector( r, "HA", &ha ) && !null_vector(ha) )
  {
    (*d)->atom = CreateATM( (*d)->atom );
    strcpy( (*d)->atom->type, "HA" );
    (*d)->atom->r = ha;  /* SJN - TODO - this shouldn't work right */
	(*d)->atom->hIndex = HYDRO_HA;
  }

  /* GLY */

  if( !atm_vector( r, "1HA", &ha ) && !null_vector(ha) )
  {
    (*d)->atom = CreateATM( (*d)->atom );
    strcpy( (*d)->atom->type, "1HA" );
    (*d)->atom->r = ha;	 /* SJN - TODO - this shouldn't work right */
	(*d)->atom->hIndex = HYDRO_HA2;
  }
  if( !atm_vector( r, "2HA", &ha ) && !null_vector(ha) )
  {
    (*d)->atom = CreateATM( (*d)->atom );
    strcpy( (*d)->atom->type, "2HA" );
    (*d)->atom->r = ha;  /* SJN - TODO - this shouldn't work right */
	(*d)->atom->hIndex = HYDRO_HA3;
  }

  if( !atm_vector( r, "HN", &hn ) && !null_vector(hn) )
  {
    (*d)->atom = CreateATM( (*d)->atom );
    strcpy( (*d)->atom->type, "HN" );
    (*d)->atom->r = hn;    /* SJN - TODO - this shouldn't work right */
	(*d)->atom->hIndex = HYDRO_H;
  }  

  return;
}

void  Receptor( RESIDUE *r, RES **recp )
{
  VECTOR    o, od1, od2, oe1, oe2, og, og1, oh;
  RES *p;

  *recp = CreateRES( *recp );
  (*recp)->type = iupac_code( r->type );
  (*recp)->num = r->num;

  if( !atm_vector( r, "O", &o ) && !null_vector(o) )
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "O" );
    (*recp)->atom->r = o;
  }


  if( !atm_vector( r, "OD1", &od1 ) && !null_vector(od1) )
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OD1" );
    (*recp)->atom->r = od1;
   }
  if( !atm_vector( r, "OD2", &od2 ) && !null_vector(od2) )
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OD2" );
    (*recp)->atom->r = od2;
  }
  if( !atm_vector( r, "OE1", &oe1 ) && !null_vector(oe1) )
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OE1" );
    (*recp)->atom->r = oe1;
	(*recp)->atom->hIndex = -1;
  }
  if( !atm_vector( r, "OE2", &oe2 ) && !null_vector(oe2) )
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OE2" );
    (*recp)->atom->r = oe2;
	(*recp)->atom->hIndex = -1;
  }
  if (!atm_vector(r, "OG", &og) && !null_vector(og))  // SJN
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OG" );
    (*recp)->atom->r = og;
	(*recp)->atom->hIndex = -1;
  }
  if (!atm_vector(r, "OG1", &og1) && !null_vector(og1))  // SJN
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OG1" );
    (*recp)->atom->r = og1;
  }
  if (!atm_vector(r, "OH", &oh) && !null_vector(oh))  // SJN
  {
    (*recp)->atom = CreateATM( (*recp)->atom );
    strcpy( (*recp)->atom->type, "OH" );
    (*recp)->atom->r = oh;
  }

  if ((*recp)->atom == NULL)
  {
	  p = *recp;
	  if ((*recp)->next != NULL)
	  {
		  (*recp)->next->last = NULL;
	  }
	  *recp = (*recp)->next;
	  free(p);
  }
  return;
}

void  AddToReceptor( RES **r, HETATM *w )
{
  HETATM    *p;

  p = w;
  while( p!=NULL )
  {
    *r = CreateRES( *r );
    (*r)->type = 'X';
    (*r)->num = -(p->id);
    (*r)->atom = CreateATM( (*r)->atom );
    strcpy( (*r)->atom->type, "O" );
    (*r)->atom->r = p->r;
  
    p = p->next;
  }
  return;
}

static  HBOND  *CreateHBond( HBOND *hb )
{
  HBOND    *new;

  new = (HBOND *) malloc( (unsigned) sizeof(HBOND) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating HBOND link list.\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(HBOND) );
  if( hb != NULL )
  {
    hb->last = new;
    new->next = hb;
  }
  return(new);
}


void  FreeHBond( HBOND *hb )
{
  HBOND  *p;


  while( hb != NULL )
  {
    p = hb->next;
    free( hb );
    hb = p;
  }
  return;
}


HBOND    *HydrogenBonds( RES *donor, RES *receptor )
{
  HBOND   *new=NULL;
  RES     *d, *r;
  ATM     *p, *q;
  float   distance, cutoff;
  VECTOR  u;
  double energy;
  RESIDUE *rrez, *drez;
  int oindex,cindex;
  /* Looks complicated :-) But it simply does pairwise calculations */
  /* between atoms on the donor and the receptor lists.             */

  /* The purpose of this is to pick out the most probable bonds i.e.*/
  /* distance < cutoff.                                             */

  d = donor;
  while( d!=NULL )
  {
    p = d->atom;
    while( p!=NULL )
    {
      r = receptor;
      while( r!=NULL )
      {
        if( (r->num < 0 || abs(r->num - d->num) >= 1)) 
			/* The previous line excludes self-interactions */
        {
          q = r->atom;
          while( q!=NULL )
          {
            if( !strcmp( p->type, "HA"  ) || 
                !strcmp( p->type, "1HA" ) ||
                !strcmp( p->type, "2HA" )   )
            {
              /* HA's do not form hydrogen-bond with water */
              
              if( r->num < 0 || abs(r->num - d->num) == 1)
              {
                q = q->next;
                continue;
              }
              cutoff = 2.77208;
            }
            else
            {
              if( !strcmp( p->type, "HN" ) ) 
			  {
				  cutoff = HNMAXBONDLENGTH;
			  }
              else
              { 
                fprintf( stderr, "Unknown donor atom %s\n", p->type );
                fprintf( stderr, "Aborting...\n" );
                exit(1);
              }
            }
            u = diff( p->r, q->r );
            distance = sqrt(dot( u, u ));
						/* SJN - can speed this up by squaring the cutoffs TODO */
            if( distance <= cutoff )
            {
				energy = 0.0;
				/* Apply some more constraints if this is an NH - OC bond */
				if (!strcmp(p->type,"HN"))
				{
					if (r->num >= 0)
					{
						rrez = FindResidue(r->num);
						drez = FindResidue(d->num);

						switch (q->type[1])
						{

						case 0:
							cindex = C_COORD;
							oindex = O_COORD;
							break;

						case 'D':
							cindex = CG_COORD;  // OD1 or OD2

							if (q->type[2] == '1')
							{
								oindex = OD1_COORD;
							}
							else
							{
								oindex = OD2_COORD;
							}
							break;

						case 'E':
							cindex = CD_COORD;  // OE1 or OE2

							if (q->type[2] == '1')
							{
								oindex = OE1_COORD;
							}
							else
							{
								oindex = OE2_COORD;
							}
							break;

						case 'G':  // OG or OG1
							cindex = CB_COORD;

							if (q->type[2] == '1')
							{
								oindex = OG1_COORD;
							}
							else
							{
								oindex = OG_COORD;
							}
							break;
			
						case 'H':
							cindex = CZ_COORD;
							oindex = OH_COORD;
							break;
						}

						if (!CheckHBond(rrez,drez,&energy,oindex,cindex))
						{
							q = q->next;
							continue;
						}
					}
					else // it's a solvent oxygen
					{
						/*
						if (drez != FindResidue(d->num))
						{
							if (CheckSolventHBond(drez,r->atom->r.x,r->atom->r.y,r->atom->r.z)
							 != CheckSolventHBond(FindResidue(d->num),r->atom->r.x,r->atom->r.y,r->atom->r.z))
							{
								printf("DOH!\n");
							}
						}
						*/
						drez = FindResidue(d->num);   // SJN FIX
						if (!CheckSolventHBond(drez,r->atom->r.x,r->atom->r.y,r->atom->r.z))
						{
							q = q->next;
							continue;
						}
					}
				}
              new = CreateHBond( new );
              new->res_d = d->num;
              new->res_r = r->num;
              new->aa_d  = d->type;
              new->aa_r  = r->type;
              strcpy( new->atm_d, p->type );
              strcpy( new->atm_r, q->type );
              new->dis = distance;
			  new->energy = energy;
//			  fprintf(stdout,"DN:%d RN:%d DT:%s RT:%s %f\n",d->num,r->num,p->type,q->type,distance);
            }
            q = q->next;
          }
        }
        r = r->next;
      }
      p = p->next;
    }
    d = d->next;
  }
  return(new);
}

static  HBOND  *RemoveHBond( HBOND *hb, HBOND *p )
{
  if( p->next != NULL )  p->next->last = p->last;
  if( p->last != NULL )  p->last->next = p->next;
  else  hb = p->next;
  free(p);
  return(hb);
}

CSHIFT    *HBondShifts( HBOND **hb,RESIDUE *Rz,int rno )
{
  CSHIFT  *new=NULL, *cs;
  HBOND   *p, *q, t;
  float   min_dis, shift, r;
  int i,flag;

  while( *hb != NULL )
  {
	  p = *hb;
	  min_dis=1.0E+30;
	  while( p!=NULL )
	  {
		  if( p->dis < min_dis )
		  {
			  q = p;
			  min_dis = p->dis;
		  }
		  p = p->next;
	  }
	  
	  /* So now q points to the target hydrogen-bond.                  */
	  /* Must check if the residue already exists to avoid duplicates. */
	  
	  cs = FindCS( new, q->res_d );
	  if( cs == NULL )
	  {
		  cs = new = CreateCS(new);
		  new->type = q->aa_d;
		  new->n = q->res_d;
	  }
	  
	  r = q->dis;    
	  if( !strcmp( q->atm_d, "HA" ) || !strcmp( q->atm_d, "1HA" ) ||
		  !strcmp( q->atm_d, "2HA" ) )
	  {
		  flag = 0;
		  for (i = 0; i <= rno; i++)
		  {
			  if (Rz[i].num == cs->n)
			  {
				  if (q->atm_d[0] == 'H' || q->atm_d[0] == '1')
				  {
					  Rz[i].ha1dist = q->dis;
					  flag++;
				  }
				  else
				  {
					  Rz[i].ha2dist = q->dis;
					  flag++;
				  }
			  }
			  else if (Rz[i].num == q->res_r)
			  {
				  Rz[i].rdist = q->dis;
				  flag++;
			  }
			  if (flag == 2)
			  {
				  break;
			  }
		  }
		  if( q->dis > 2.60756 )
		  {
			  r = 2.60756;
		  }
		  if( q->dis < 2.26808 )
		  {
			  r = 2.26808;      
		  }
		  
		  shift = 0.147521/r - (1.65458E-05)/pow(r, 1.5) - 0.000134668/(r*r) + 
			  0.0598561/pow(r, 2.5) + 15.6855/(r*r*r) - 0.673905;
		  if( cs->ha == 0 )
		  {
			  cs->ha = shift;
		  }
		  else
		  {
			  /* This must be GLY then */
			  /* Take the average.     */		
			  cs->ha = (cs->ha + shift)/2.0;
		  }
		  cs->hside[HYDRO_HA] = cs->ha;
	  }
	  else
	  {
		  if( !strcmp( q->atm_d, "HN" ) )
		  {
			  flag = 0;
			  for (i = 0; i <= rno; i++)
			  {
				  if (Rz[i].num == cs->n)
				  {
					  Rz[i].hndist = q->dis;
					  Rz[i].hnPartner = q->res_r;
					  strcpy(Rz[i].hnPartnerType,q->atm_r);
					  flag++;
				  }
				  else if (Rz[i].num == q->res_r)
				  {
					  flag++;
					  if (!strcmp(q->atm_r,"O"))  // Don't do this for OD and OE atoms
					  {
						  Rz[i].rdist = q->dis;
					  }
				  }
				  if (flag == 2)
				  {
					  break;
				  }
			  }
			  /*
			  if( q->dis > 2.315912 )
			  {
			  r = 2.315912;
			  }
			  if( q->dis < 1.8229   )
			  {
			  r = 1.8229;
			  }
			  
				cs->hn = - (12.580791/r + 0.030857/pow(r, 1.5) -0.000033/(r*r) + 
				0.023198/pow(r, 2.5) - 6.080736);
			  */
			  // cs->hn = 4.6399 / r - 2.1434;
			  cs->hn =9.7464/(r * r * r) - 0.9887;
			  cs->hside[HYDRO_H] = cs->hn;
			  /*
			  r = (q->dis - 1.5486) / 0.02576;
			  cs->hn = (-12.5199 - 2 * 15.1780 * cos(2 * M_PI * r / 70) - 2 * 6.2018 * sin(2 * M_PI * r / 70)) / 70;
			  */
		  }
		  else
		  {
			  fprintf( stderr, "Unsupported atom found in hydrogen-bond calculation.\n" );
			  fprintf( stderr, "Aborting...\n" );
			  exit(1);
		  }
	  }
	  
	  t = *q;
	  
	  /* Now we got the target hydrogen bond, let's reduce the list */
	  
	  *hb = RemoveHBond( *hb, q );
	  p = *hb;
	  while( p != NULL )
	  {
		  if( ((p->res_d == t.res_d) && !strcmp( p->atm_d, t.atm_d )) ||
			  ((p->res_r == t.res_r) && !strcmp( p->atm_r, t.atm_r ))    )
		  {
			  q = p->next;
			  *hb = RemoveHBond( *hb, p );
			  p = q;
			  continue;
		  }
		  p = p->next;
	  }
  }
  
  return(new);
}

CSHIFT    *HBondShifts2(HBOND **hb, RESIDUE *Rz,int rno )
{
  CSHIFT  *new=NULL, *cs;
  HBOND   *p, *q, t;
  float   min_dis, shift, r;
  int i,flag, whichBond;

	while( *hb != NULL )
	{
		p = *hb;
		min_dis=1.0E+30;
		while( p!=NULL )
		{
			if( p->dis < min_dis )
			{
				q = p;
				min_dis = p->dis;
			}
			p = p->next;
		}

#ifdef _DEBUG		
		printf("S %d %d %s %s %f\n",q->res_d,q->res_r,q->atm_d,q->atm_r,q->dis);
#endif

		/* So now q points to the target hydrogen-bond.                  */
		/* Must check if the residue already exists to avoid duplicates. */

		cs = FindCS( new, q->res_d );
		if( cs == NULL )
		{
		  cs = new = CreateCS(new);
		  new->type = q->aa_d;
		  new->n = q->res_d;
		}
		r = q->dis;    
		if( !strcmp( q->atm_d, "HA" ) || !strcmp( q->atm_d, "1HA" ) ||
			!strcmp( q->atm_d, "2HA" ) )
		{
			flag = 0;
			for (i = 0; i <= rno; i++)
			{
				if (Rz[i].num == new->n)
				{
					if (q->atm_d[0] == 'H' || q->atm_d[0] == '1')
					{
						Rz[i].ha1dist = q->dis;
						flag++;
					}
					else
					{
						Rz[i].ha2dist = q->dis;
						flag++;
					}
				}
				else if (Rz[i].num == q->res_r)
				{
					Rz[i].rdist = q->dis;
					flag++;
				}
				if (flag == 2)
				{
					break;
				}
			}
			if( q->dis > 2.60756 )
			{
				r = 2.60756;
			}
			if( q->dis < 2.26808 )
			{
				r = 2.26808;      
			}
			shift = 0.147521/r - (1.65458E-05)/pow(r, 1.5) - 0.000134668/(r*r) + 
				  0.0598561/pow(r, 2.5) + 15.6855/(r*r*r) - 0.673905;
			if( cs->ha == 0 )
			{
				cs->ha = shift;
			}
			else
			{
			/* This must be GLY then */
			/* Take the average.     */
      
				cs->ha = (cs->ha + shift)/2.0;
			}
		}
		/*
		else
		{
		  if( !strcmp( q->atm_d, "HN" ) )
		  {
			flag = 0;
			for (i = 0; i <= rno; i++)
			{
				if (Rz[i].num == new->n)
				{
					Rz[i].hndist = q->dis;
					flag++;
				}
				else if (Rz[i].num == q->res_r)
				{
					flag++;
					Rz[i].rdist = q->dis;
				}
				if (flag == 2)
				{
					break;
				}
			}
			if( q->dis > 2.315912 )  r = 2.315912;
			if( q->dis < 1.8229   )  r = 1.8229;
			cs->hn = 12.580791/r + 0.030857/pow(r, 1.5) -0.000033/(r*r) + 
					  0.023198/pow(r, 2.5) - 6.080736;
		  }
		  else
		  {
			fprintf( stderr, "Unsupported atom found in hydrogen-bond calculation.\n" );
			fprintf( stderr, "Aborting...\n" );
			exit(1);
		  }
		}
		*/
		t = *q;
 
		/* Now we got the target hydrogen bond, let's reduce the list */

		*hb = RemoveHBond( *hb, q );
		p = *hb;
		while( p != NULL )
		{
			if( ((p->res_d == t.res_d) && !strcmp( p->atm_d, t.atm_d )) ||
			  ((p->res_r == t.res_r) && !strcmp( p->atm_r, t.atm_r ))    )
			{
				q = p->next;
				*hb = RemoveHBond( *hb, p );
				p = q;
				continue;
			}
			p = p->next;
		}
	}

	for (i = 0; i <= rno; i++)
	{
		if (Rz[i].hbonds[0].DA_FLAG == 1 || Rz[i].hbonds[1].DA_FLAG == 1)
		{
			if (Rz[i].hbonds[0].DA_FLAG == 1)
			{
				whichBond = 0;
			}
			else
			{
				whichBond = 1;
			}
#ifdef _DEBUG
			printf("V\t%d\t%d\t%s\t%s\t%f\n",Rz[i].num,Rz[Rz[i].hbonds[whichBond].partner].num,"HN","O",Rz[i].hbonds[whichBond].dist);
#endif
		    cs = FindCS( new, Rz[i].num );

			if( cs == NULL )
			{
				cs = new = CreateCS(new);
				new->type = iupac_code(Rz[i].type);
				new->n = Rz[i].num;
			}
			r = Rz[i].hbonds[whichBond].dist;
			Rz[i].hndist = r;
			Rz[Rz[i].hbonds[whichBond].partner].rdist = r;
			/*
			if( Rz[i].hbonds[whichBond].dist > 2.315912 )
			{
				r = 2.315912;
			}
			if(Rz[i].hbonds[whichBond].dist < 1.8229   )
			{
				r = 1.8229;
			}
			*/
			r = (r - 1.5486) / 0.02576;
			cs->hn = (-12.5199 - 2 * 15.1780 * cos(2 * M_PI * r / 70) - 2 * 6.2018 * sin(2 * M_PI * r / 70)) / 70;
			/*
			cs->hn = 12.580791/r + 0.030857/pow(r, 1.5) -0.000033/(r*r) + 
                  0.023198/pow(r, 2.5) - 6.080736;
				  */
		}
	}
	return(new);
}
