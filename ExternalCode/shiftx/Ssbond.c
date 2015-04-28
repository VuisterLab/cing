#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include "psa.h"
#include "vector.h"
#include "cs.h"
#include "ssbond.h"

static SSBOND   *CreateSSBond( SSBOND *ss )
{
  SSBOND     *new;

  new = (SSBOND *) malloc( (unsigned) sizeof(SSBOND) );
  if( new == NULL )
  {
    fprintf( stderr, "Memory allocation failure in creating SSBOND!\n" );
    fprintf( stderr, "Aborting...\n" );
    exit(1);
  }
  memset( new, 0, sizeof(SSBOND) );
  if( ss != NULL )
  {
    new->next = ss;
  }
  return(new);
}


void  ReadSSPairs( FILE *fpt, SSBOND **ss, char useChain )
{
	char    Line[500], *p, insCodeA, insCodeB, chain, chainA, chainB,atom[8],RES[5];
	int     A, B, status,atomflag=0,findssheader=0,resno, max,cyschain,i=0,j=0,m=0,n=0,pair[5][2];
	SSBOND  *q;
	long    fpos=0,atompos=0;
	CYSres  *Cys;
	float  x,y,z,distance;
	
	Cys=(CYSres *)malloc(10*sizeof(CYSres));
	max=10;
	fpos = ftell(fpt);
	while( fgets( Line, 500, fpt )!=NULL )
	{
		if( (p=strstr( Line, "ATOM" ))!=NULL && p==Line  )
		{
		   if(atomflag==0)
		     {
		       atompos=fpos;
		       atomflag=1;
		     }
		     
			if(findssheader==1)
			{
				fseek( fpt, fpos, SEEK_SET );
				break;
			}
                      	else{
			  
			/***haiyan zhang*****/	
                         	if((p=strstr(Line,"CYS"))!=NULL )
				{
				       
					status=sscanf(&Line[11],"%5s",atom);
					status=sscanf(&Line[21],"%c%5d%*c %f%f%f",&cyschain, &resno,&x, &y,&z);
					
					
					if(Cys[i].res !=resno)
					  { 
					   i++; Cys[i].res=resno;
					  
					  }
					if(i==max)
					{
					  Cys=(CYSres *)realloc((CYSres *)Cys,(max+10)*sizeof(CYSres));
					  max+=10;
					}
					if(strcmp(atom,"CA")==0)
					{
					     Cys[i].res=resno;
					     Cys[i].chain=cyschain;
					     Cys[i].CA[0]=x;
					     Cys[i].CA[1]=y;
					     Cys[i].CA[2]=z; 
					}
					if(strcmp(atom,"SG")==0)
					{
					     Cys[i].res=resno;
					     Cys[i].chain=cyschain;
					     Cys[i].SG[0]=x;
					     Cys[i].SG[1]=y;
					     Cys[i].SG[2]=z; 
					}
					
				}

			}
		}
		if( (p=strstr( Line, "SSBOND" ))!=NULL && p==Line )
		{
			if( (p=strstr( Line, "CYS" ))!=NULL )
			{
				findssheader=1;
				status = sscanf(Line, "SSBOND %*d CYS%*c%c%*c%d%c   CYS%*c%c%*c%d%c", &chainA, &A, &insCodeA, &chainB, &B, &insCodeB);
				if (insCodeB == 0x0D || insCodeB == 0x0A)
				{
					insCodeB = ' ';
				}
				if (status != 6)
				{
					fprintf( stderr, "SSBOND specification format error!\n" );
					fprintf( stderr, "Aborting...\n" );
					exit(1);
				}
				if (!useChain || (chainA == useChain && chainB == useChain))
				{
					q = *ss;
					status = 0;
					
					while( q != NULL )
					{
						if( A == q->resA || A == q->resB || B == q->resA || B == q->resB )
						{
							status = 1;
							break;
						}
						q = q->next;
					}
					
					if( !status )
					{
						*ss = CreateSSBond( *ss );
						(*ss)->resA = A;
						(*ss)->insCodeA = insCodeA;
						(*ss)->resB = B;
						(*ss)->insCodeB = insCodeB;
					}
				}
			}
		}
		fpos = ftell(fpt);
	}
	if(findssheader!=1)
	{
	 	if(i>1)
		{
			for(n=1;n<i;n++)
			{
			 	for(j=n+1;j<=i;j++)
				{
				 distance=sqrt(pow((Cys[n].SG[0]-Cys[j].SG[0]),2)
				              +pow((Cys[n].SG[1]-Cys[j].SG[1]),2)
					      +pow((Cys[n].SG[2]-Cys[j].SG[2]),2));
		                /*printf("distance=%f %d %d\n",distance,Cys[n].res,Cys[j].res);       */ 
					if(distance<2.5)
				 	{
						insCodeA =' ';
						insCodeB =' ';
						
				   		if (!useChain || (Cys[n].chain == useChain && Cys[j].chain == useChain))
						{
							q = *ss;
							status = 0;
							while( q != NULL )
							{
								if( Cys[n].res == q->resA || Cys[n].res == q->resB || Cys[j].res == q->resA || Cys[j].res == q->resB )
								{
								status = 1;
								break;
								}
								q = q->next;
							}
					
							if( !status )
							{
							
							*ss = CreateSSBond( *ss );
							(*ss)->resA = Cys[n].res;
							(*ss)->insCodeA = insCodeA;
							(*ss)->resB = Cys[j].res;
							(*ss)->insCodeB = insCodeB;
							}
						}
				 	}
				}	
			}
			
		}
	}
	
	fseek( fpt, atompos, SEEK_SET );
	free (Cys);
	return;
}

void  FreeSSBond( SSBOND  *ss )
{
  SSBOND    *p;

  while( ss != NULL )
  {
    p = ss->next;
    free(ss);
    ss = p;
  }
  return;
}

void    ReadSSCoordinates( RESIDUE *r, SSBOND *bonds )
{
  SSBOND    *p;


  p = bonds;
  while( p != NULL )
  {
    if( r->numLabel == p->resA )
    {
	  r->ssbond = 1;
      /* Not doing calculations with these coods anymore
      if( atm_vector( r, "CA", &(p->CA_A) ) )
      {
        fprintf( stderr, "Missing atom CA in residue %d\n", r->numLabel );
        exit(1);
      }
      if( atm_vector( r, "SG", &(p->SG_A) ) )
      {
        fprintf( stderr, "Missing atom SG in residue %d\n", r->numLabel );
        exit(1);
      }
	*/
      return;
    }
    if( r->numLabel == p->resB )
    {
	  r->ssbond = 1;
	/* Not doing calculations with these coods anymore
      if( atm_vector( r, "CA", &(p->CA_B) ) )
      {
		  fprintf( stderr, "Missing atom CA in residue %d\n", r->numLabel );
        exit(1);
      }
      if( atm_vector( r, "SG", &(p->SG_B) ) )
      {
        fprintf( stderr, "Missing atom SG in residue %d\n", r->numLabel );
        exit(1);
      }
	*/
      return;
    }
    p = p->next;
  }
  return;
}

CSHIFT   *DiSulfideBonds( SSBOND *bonds )
{
  CSHIFT    *cs=NULL;
  SSBOND    *p;
  VECTOR    u, v, w, s;
  float     theta_A, theta_B;

  p = bonds;
  while( p != NULL )
  {
    v = normalize( diff( p->SG_A, p->SG_B ) );
    w = normalize( diff( p->SG_A, p->CA_A ) );
    theta_A = dot( v, w );
    cs = CreateCS( cs );
    cs->n = p->resA;
    cs->type = 'C';
    cs->ca = 5.0*sin(8.0*theta_A + 3.3) - 2.0 + 57.7917;

    u = multiply( v, -1 );
    s = normalize( diff( p->SG_B, p->CA_B ) );
    theta_B = dot( u, s );
    cs = CreateCS( cs );
    cs->n = p->resB;
    cs->type = 'C';
    cs->ca = 5.0*sin(8.0*theta_B + 3.3) - 2.0 + 57.7917;
  
    p = p->next;
  }

  return(cs);
}
