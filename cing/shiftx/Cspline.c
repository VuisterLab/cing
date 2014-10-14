/* Copyright (C) 1987,1988 Numerical Recipes Software */

#include <stdio.h>
#include <stdlib.h>
#if defined(HAVE_MALLOC_H) && !defined(STDC_HEADERS)
#include <malloc.h>
#endif
#include <math.h>
#include "psa.h"

static  void nrerror( char error_text[] )
{
  fprintf(stderr,"Numerical Recipes run-time error...\n");
  fprintf(stderr,"%s\n",error_text);
  fprintf(stderr,"...now exiting to system...\n");
  exit(1);
}

static  float  *vector( int nl, int nh )
{
  float   *v;
	
  v=(float *)malloc((unsigned) (nh-nl+1)*sizeof(float));
  if (!v)
  {
	  nrerror("allocation failure in vector()");
  }
  return(v-nl);
}

static  void  free_vector( float *v, int nl, int nh )
{
  free((char*) (v+nl));
}

static  void  spline( float x[], float y[], int n, float yp1, float ypn, float y2[] )
{
  int     i, k;
  float   p, qn, sig, un, *u;


  u=vector(1,n-1);
  if (yp1 > 0.99e30)
	{
          y2[1]=u[1]=0.0;
	}
  else
	{
          y2[1] = -0.5;
          u[1]=(3.0/(x[2]-x[1]))*((y[2]-y[1])/(x[2]-x[1])-yp1);
  }
  for (i=2;i<=n-1;i++)
	{
          sig=(x[i]-x[i-1])/(x[i+1]-x[i-1]);
          p=sig*y2[i-1]+2.0;
          y2[i]=(sig-1.0)/p;
          u[i]=(y[i+1]-y[i])/(x[i+1]-x[i]) - (y[i]-y[i-1])/(x[i]-x[i-1]);
          u[i]=(6.0*u[i]/(x[i+1]-x[i-1])-sig*u[i-1])/p;
  }
  if (ypn > 0.99e30)
	{
          qn=un=0.0;
	}
  else
	{
          qn=0.5;
          un=(3.0/(x[n]-x[n-1]))*(ypn-(y[n]-y[n-1])/(x[n]-x[n-1]));
  }
  y2[n]=(un-qn*u[n-1])/(qn*y2[n-1]+1.0);
  for (k=n-1;k>=1;k--)
	{
          y2[k]=y2[k]*y2[k+1]+u[k];
	}
  free_vector(u,1,n-1);
}

static  void splint( float xa[], float ya[], float y2a[], int n, float x, float *y)
{
  int     klo,khi,k;
  float   h,b,a;

  klo=1;
  khi=n;
  while (khi-klo > 1) {
          k=(khi+klo) >> 1;
          if (xa[k] > x) khi=k;
          else klo=k;
  }
  h=xa[khi]-xa[klo];
  if (h == 0.0) nrerror("Bad XA input to routine SPLINT");
  a=(xa[khi]-x)/h;
  b=(x-xa[klo])/h;
  *y=a*ya[klo]+b*ya[khi]+((a*a*a-a)*y2a[klo]+(b*b*b-b)*y2a[khi])*(h*h)/6.0;
}

void  splie2( float x1a[], float x2a[], float **ya, int m, int n, float **y2a)
{
  int     j;

  for (j=1;j<=m;j++)
	{
		spline(x2a,ya[j],n,1.0e30,1.0e30,y2a[j]);
	}
}

void  splin2( float x1a[], float x2a[], float **ya, float **y2a, int m, int n, 
              float x1, float x2, float *y)
{
  int     j;
  float  *ytmp,*yytmp;

  ytmp=vector(1,n);
  yytmp=vector(1,n);
  for (j=1;j<=m;j++)
          splint(x2a,ya[j],y2a[j],n,x2,&yytmp[j]);
  spline(x1a,yytmp,m,1.0e30,1.0e30,ytmp);
  splint(x1a,yytmp,ytmp,m,x1,y);
  free_vector(yytmp,1,n);
  free_vector(ytmp,1,n);
}


float quickSpline(float x[], float y[], int n,float xpt,int wrap)
{
	float *ytmp,*xtmp,answer;
	int i,flg;

	if (wrap)
	{
		xtmp = vector(1,n+2);
		for (i=2; i < n+2; i++)
		{
			xtmp[i] = y[i-2];
		}
		xtmp[1] = y[n-2];
		xtmp[n+2] = y[1];
		ytmp = vector(1,n+2);
	}
	else
	{
		xtmp = y - 1;
		ytmp = vector(1,n);
	}


	spline(x,xtmp,n+2*wrap,1.0e30,1.0e30,ytmp);
	splint(x,xtmp,ytmp,n+2*wrap,xpt,&answer);
	
	if (wrap)
	{
		free_vector(xtmp,1,n+2);
		free_vector(ytmp,1,n+2);
	}
	else
	{
		free_vector(ytmp,1,n);
	}
	return(answer);
}


float quickSpline2(float xs1[],float xs2[],float x1,float x2,float p[19][19])
{
	float result,**pp,**ppa;
	int i,j;

	pp = (float **)calloc(sizeof(float *),27);
	for (i = 0; i < 27; i++)
	{
		pp[i] = (float *)calloc(sizeof(float),27);
		pp[i]--;
	}

	ppa = (float **)calloc(sizeof(float *),27);
	for (i = 0; i < 27; i++)
	{
		ppa[i] = (float *)calloc(sizeof(float),27);
		ppa[i]--;
	}
	
	for (i=1; i < 20; i++)
	{
		for (j=1; j < 20; j++)
		{
			pp[i+3][j+1+3] = p[i-1][j-1];
		}
	}
	for (i=0; i < 27; i++)
	{
		pp[0][i+1] = pp[18][i+1];
		pp[1][i+1] = pp[19][i+1];
		pp[2][i+1] = pp[20][i+1];
		pp[3][i+1] = pp[21][i+1];
		
		pp[23][i+1] = pp[2+3][i+1];
		pp[24][i+1] = pp[3+3][i+1];
		pp[25][i+1] = pp[4+3][i+1];
		pp[26][i+1] = pp[5+3][i+1];
	}

	for (i=0; i < 27; i++)
	{
		pp[i][1] = pp[i][15+1+3];
		pp[i][2] = pp[i][16+1+3];
		pp[i][3] = pp[i][17+1+3];
		pp[i][4] = pp[i][18+1+3];

		pp[i][23+1] = pp[i][2+1+3];
		pp[i][24+1] = pp[i][3+1+3];
		pp[i][25+1] = pp[i][4+1+3];
		pp[i][26+1] = pp[i][5+1+3];
	}					
	
	splie2(xs1,xs2,&pp[-1],27,27,&ppa[-1]);
//	splin2(x,x,&pp[-1],&ppa[-1],21,21,Rz[resindex+1].phi,Rz[resindex+1].psi,&result);
	splin2(xs1,xs2,&pp[-1],&ppa[-1],27,27,x1,x2,&result);
	
	for (i=0; i < 27; i++)
	{
		free(pp[i]+1);
		free(ppa[i]+1);
	}
	free(pp);
	free(ppa);
	return(result);
}


float quickSpline3(float xs1[],float xs2[],float x1,float x2,float **p)
{
	float result,**pp,**ppa;
	int i,j;

	pp = (float **)calloc(sizeof(float *),27);
	for (i = 0; i < 27; i++)
	{
		pp[i] = (float *)calloc(sizeof(float),27);
		pp[i]--;
	}

	ppa = (float **)calloc(sizeof(float *),27);
	for (i = 0; i < 27; i++)
	{
		ppa[i] = (float *)calloc(sizeof(float),27);
		ppa[i]--;
	}
	
	for (i=1; i < 20; i++)
	{
		for (j=1; j < 20; j++)
		{
			pp[i+3][j+1+3] = p[i-1][j-1];
		}
	}
	for (i=0; i < 27; i++)
	{
		pp[0][i+1] = pp[18][i+1];
		pp[1][i+1] = pp[19][i+1];
		pp[2][i+1] = pp[20][i+1];
		pp[3][i+1] = pp[21][i+1];
		
		pp[23][i+1] = pp[2+3][i+1];
		pp[24][i+1] = pp[3+3][i+1];
		pp[25][i+1] = pp[4+3][i+1];
		pp[26][i+1] = pp[5+3][i+1];
	}

	for (i=0; i < 27; i++)
	{
		pp[i][1] = pp[i][15+1+3];
		pp[i][2] = pp[i][16+1+3];
		pp[i][3] = pp[i][17+1+3];
		pp[i][4] = pp[i][18+1+3];

		pp[i][23+1] = pp[i][2+1+3];
		pp[i][24+1] = pp[i][3+1+3];
		pp[i][25+1] = pp[i][4+1+3];
		pp[i][26+1] = pp[i][5+1+3];
	}					
	
	splie2(xs1,xs2,&pp[-1],27,27,&ppa[-1]);
//	splin2(x,x,&pp[-1],&ppa[-1],21,21,Rz[resindex+1].phi,Rz[resindex+1].psi,&result);
	splin2(xs1,xs2,&pp[-1],&ppa[-1],27,27,x1,x2,&result);
	
	for (i=0; i < 27; i++)
	{
		free(pp[i]+1);
		free(ppa[i]+1);
	}
	free(pp);
	free(ppa);
	return(result);
}

