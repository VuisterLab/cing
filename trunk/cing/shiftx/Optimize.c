#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "psa.h"
#include "cs.h"
#include "residue.h"
#include "cspline.h"
#include "hydrogens.h"
#include "miner.h"
#include "minerha1.h"
#include "minerhn1.h"
#include "minern151.h"
#include "minercb1.h"
#include "minerca1.h"
#include "minerco1.h"
//#include "minerhb.h"
#include "minerhatoms.h"
/* ADDNEW */

#ifdef _WIN32
#include "crtdbg.h"
#else  // for GCC
#include "assert.h"
#define _isnan isnan
#define _ASSERT assert
#endif

#include <float.h>

#define FACTOR_AA		0 
#define FACTOR_PHI		1 
#define FACTOR_PSI		2 
#define FACTOR_CHI		3 
#define FACTOR_AAP1		4 
#define FACTOR_PHIP1	5 
#define FACTOR_PSIP1	6 
#define FACTOR_CHIP1	7 
#define FACTOR_AAM1		8 
#define FACTOR_PHIM1	9 
#define FACTOR_PSIM1	10
#define FACTOR_CHIM1	11
#define FACTOR_HBONDSTAT 12
#define FACTOR_INDEX	13	
#define FACTOR_SS		14
#define FACTOR_HA1BOND	15
#define FACTOR_HA2BOND	16
#define FACTOR_HNBOND	17
#define FACTOR_OBOND	18	
#define FACTOR_HA1LEN	19	
#define FACTOR_HA2LEN	20
#define FACTOR_HNLEN	21
#define FACTOR_OLEN		22
#define FACTOR_SSBOND   23
#define FACTOR_SSP1		24  // SJN SSP1
#define FACTOR_INDEXM1  25
#define FACTOR_SSBONDP1 26
#define FACTOR_INDEXP1  27
#define FACTOR_SSBONDM1 28
#define FACTOR_SSM1		29
#define FACTOR_OLENM1	30
#define FACTOR_OLENP1	31
#define FACTOR_CHI2	    32
#define FACTOR_ROW		33

#define FACTORTABLESIZE (sizeof(factors)/sizeof(struct factortable))

struct csarray
{
	int factorx,factory;
	double **grid,*rowAvgs,**grid2,**XAxisArray,XXavg,*colAvgs,*Xubounds,*Xlbounds,*Yubounds,*Ylbounds;
	void *xaxis,*yaxis;
	int xsize,ysize,xmax,ymax,*tcount,*rowMins,*rowMaxs,*rowZeros,*rowEntries,tripled;
	struct csarray *next;
} *ca_array=NULL, *cb_array=NULL, *co_array=NULL, *ha_array=NULL, *hn_array=NULL, *n15_array=NULL, 
  *hb_array=NULL,*hatom_array[NHATOMS];

void *MakeAxis(char *inline1,int size,char type,int maxlen,int wrap);
int CountEntries(char* inline1,int *maxlen);
int GetFactor(int factor,RESIDUE *r,RESIDUE *rp,RESIDUE *rm,char *hbondstate,int rmidx,int rpidx,int ridx,char *xchar,char **xstring,float *xfloat,int *xint);
float ArrayFactor(RESIDUE *r,RESIDUE *rp,RESIDUE *rm,char* hbondstate,struct csarray *array,int rmidx,int rpidx,int ridx);
int GetIntegerFactor(void *axis, int axisSize, int *xint);
static  void  splined( double x[], double y[], int n, double yp1, double ypn, double y2[] );
static  void splintd( double xa[], double ya[], double y2a[], int n, double x, double *y);
static  void nrerrord( char error_text[] );
static  double  *vectord( int nl, int nh );
static  void  free_vectord( double *v, int nl, int nh );
double SplineBinLookup(struct csarray *array,int row,double jdata);
double twoSplineLookup2(struct csarray *array,double idata,double jdata);
double BinBinLookup(struct csarray *array,int row,int column);
double SingleSplineLookup(struct csarray *array,double jdata);
void OutputDebugString(char *what);

#define GET_NEXT_LINE() if (filename != NULL) { fgets(inn,sizeof(inn),ff); } \
						else { strcpy(inn,inTextArray[++stringIndex]); }

#define END_OF_TEXT() ((filename != NULL && feof(ff)) || (filename == NULL && !strcmp(inTextArray[stringIndex],"END")))

#define WRAP_ARRAY_ROWS array->ysize
#define ARRAY_ROWS (array->ysize - 2)
#define WRAP_ARRAY_COLS array->xsize
#define ARRAY_COLS (array->xsize - 2)
#define VECTOR_OF_DOUBLE_MEMBER(X,Y)   *(((double *)X) + Y)
#define MINCOUNT 1
#define BADVAL 999.0 
#define USE_XX_AVERAGE 1
#define USE_YY_AVERAGE 1

struct factortable
{
	int index;
	char *name;
	char type; // Discrete, Spline, Bin, Character
	int wrap;  // Is this an angle that wraps from -180 to 180?
	int zero;  // Does this factor have a special zero bin?
} factors[34] = {	FACTOR_AA		 ,"aa",		'D', 0,0,
					FACTOR_PHI		 ,"phi",	'S', 1,0,
					FACTOR_PSI		 ,"psi",	'S', 1,0,
					FACTOR_CHI		 ,"chi",	'D', 0,0,
					FACTOR_AAP1		 ,"aa+1",	'D', 0,0,
					FACTOR_PHIP1	 ,"phi+1",	'S', 1,0,
					FACTOR_PSIP1	 ,"psi+1",	'S', 1,0,
					FACTOR_CHIP1	 ,"chi+1",	'D', 1,0,
					FACTOR_AAM1		 ,"aa-1",	'D', 0,0,
					FACTOR_PHIM1	 ,"phi-1",	'S', 1,0,
					FACTOR_PSIM1	,"psi-1",	'S', 1,0,
					FACTOR_CHIM1	,"chi-1",	'D', 0,0,
					FACTOR_HBONDSTAT,"hbondstat",'D',0,0,
					FACTOR_INDEX	,"index",	'I', 0,0,
					FACTOR_SS		,"ss",		'D', 0,0,
					FACTOR_HA1BOND	,"ha1bond",	'D', 0,0,
					FACTOR_HA2BOND	,"ha2bond",	'D', 0,0,
					FACTOR_HNBOND	,"hnbond",	'D', 0,0,
					FACTOR_OBOND	,"obond",	'D', 0,0,
					FACTOR_HA1LEN	,"ha1len",'B', 0,1, 
					FACTOR_HA2LEN	,"ha2len",'B', 0,1,
					FACTOR_HNLEN	,"hnlen",	'B', 0,1,
					FACTOR_OLEN		,"olen",	'B', 0,1,
					FACTOR_SSBOND	,"ssbond",  'I', 0,0,
					FACTOR_SSP1		,"ssp1",	'D', 0,0,
					FACTOR_INDEXM1	,"indexm1",	'I', 0,0,
					FACTOR_SSBONDP1	,"ssbondp1",  'I', 0,0,
					FACTOR_INDEXP1	,"indexp1",	'I', 0,0,
					FACTOR_SSBONDM1	,"ssbondm1",  'I', 0,0,
					FACTOR_SSM1		,"ssm1",	'D', 0,0,
					FACTOR_OLENM1	,"olenm1",	'B', 0,1,
					FACTOR_OLENP1	,"olenp1",	'B', 0,1,
					FACTOR_CHI2     ,"chi2",     'D',0,0,
					FACTOR_ROW		,"row",		'I', 0,0,
};



void ReadCSConfig(char *nucleus,char *filename)
{
	struct csarray *array,*inarray;
	FILE *ff;
	static char inn[1000],*tempaxis,**inTextArray;
	int maxlen,i,j,k,m,swapsize,swapmax,stringIndex,fTextWhere,*swaptcount,wrapx,wrapy;
	long fwhere;
	void *swapaxis;
	char **pt;
	double **swapgrid,spacing,*tempGrid;
	int YstartPt;  
	int YendPt;    
	int XstartPt;  
	int XendPt;    
	int xxcount;   
	int YbinNo;    
	int xcount;    
	int col,scol,ecol;

	if (!strcmp(nucleus,"CA"))
	{
		array = ca_array;
		inTextArray = minerca;
	}
	else if (!strcmp(nucleus,"CB"))
	{
		array = cb_array;
		inTextArray = minercb;
	}
	else if (!strcmp(nucleus,"CO"))
	{
		array = co_array;
		inTextArray = minerco;
	}
	else if (!strcmp(nucleus,"HA"))
	{
		array = ha_array;
		inTextArray = minerha;
	}
	else if (!strcmp(nucleus,"HN"))
	{
		array = hn_array;
		inTextArray = minerhn;
	}
	else if (!strcmp(nucleus,"N15"))
	{
		array = n15_array;
		inTextArray = minern15;
	}
	/*
	else if (!strcmp(nucleus,"HB"))
	{
		array = hb_array;
		inTextArray = minerhb;
		/* ADDNEW */
/*	}
*/
	else
	{  // TODO
		for (i = 0; i < NHATOMS; i++)
		{
			if (!strcmp(nucleus,hatoms[i].name))
			{
				break;
			}
		}
		if (i < NHATOMS)
		{
			j = 0;
			pt = minerhatoms;

			while (j < i)
			{
				if (!strcmp(*pt,"END"))
				{
					j++;
				}
				pt++;
			}
			array = hatom_array[i];
			inTextArray = pt;
		}
	}

	
	while (array != NULL)
	{
		inarray = array;
		array = inarray->next;
		if (array->grid != NULL)
		{
			free(array->grid);
		}
		if (array->xaxis != NULL)
		{
			free(array->xaxis);
		}
		if (array->yaxis != NULL)
		{
			free(array->yaxis);
		}
		if (array->tcount != NULL)
		{
			free(array->tcount);
		}
		free(array);
		array = inarray;
	}
	inarray = NULL;

	if (filename != NULL)
	{
		ff = fopen(filename,"rt");
		fgets(inn,sizeof(inn),ff);
	}
	else
	{
		stringIndex = 0;
		strcpy(inn,inTextArray[0]);
	}
	while (!END_OF_TEXT())
	{
//		check_co_array(array);
		if (!strncmp(inn,"Array #",7))
		{
			char *pt,*pt2;
			int f1=-1,f2=-1;
			int rowcount = 0,transpose = 0;
			
			pt = strtok(inn," ");  // Grab Array
			pt = strtok(NULL," "); // Grab #xx
			pt = strtok(NULL," "); // Grab f1/f2
			pt = strtok(NULL,"/"); // Grab name of factor1
			pt2 = strtok(NULL,"/\n"); // Grab name of factor2 

			for (i=0; i < FACTORTABLESIZE; i++)
			{
				if (!strcmp(pt,factors[i].name))
				{
					f1 = factors[i].index;
				}
				if (!strcmp(pt2,factors[i].name))
				{
					f2 = factors[i].index;
				}
			}

//			_ASSERT(f1 != -1 && f2 != -1);
			if (f1 != -1 && f2 != -1 /* && (f1 != 1 || f2 != 2)*/)
			{
				if ((factors[f1].type == 'S' || factors[f1].type == 'B') && factors[f2].type != 'S' && factors[f2].type != 'B')
				{
					// Tranpose array so that splining factor is in rows
					transpose = 1;
				}
				wrapx = factors[f2].wrap;
				wrapy = factors[f1].wrap;

				array = (struct csarray*)malloc(sizeof(struct csarray));
				memset(array,0,sizeof(struct csarray));
				array->factorx = f2;
				array->factory = f1;
				array->next = inarray;
				inarray = array;
				
//				GET_NEXT_LINE();

				if (filename != NULL)
				{
					fgets(inn,sizeof(inn),ff);
				}
				else
				{
					strcpy(inn,inTextArray[++stringIndex]);
				}
				array->xsize = CountEntries(inn,&maxlen) + 2;

				array->xaxis = MakeAxis(inn,array->xsize,factors[f2].type,maxlen,wrapx);
				if (transpose)
				{
					swapaxis = MakeAxis(inn,array->xsize,factors[f2].type,maxlen,wrapx);
				}
				array->xmax = maxlen;
				
				if (filename != NULL)
				{
					fwhere = ftell(ff);
				}
				else
				{
					fTextWhere = stringIndex;
				}

				maxlen = 0;
				GET_NEXT_LINE();

//				fgets(inn,sizeof(inn),ff);
				while (!END_OF_TEXT() && *inn != '\n')
				{
					int l;
					char *pt;
					if (factors[f1].type == 'I')
					{
						pt = strtok(inn,"|");
					}
					else
					{
						pt = strtok(inn," |");
					}
					if ((l=strlen(pt)) > maxlen)
					{
						maxlen = l;
					}
					rowcount++;
					GET_NEXT_LINE();
//					fgets(inn,sizeof(inn),ff);
				}

				rowcount += 2;  // Two extra rows for wrapping
				array->ysize = rowcount;  
				array->ymax = maxlen;
				array->grid = (double **)malloc(sizeof(double *) * rowcount);
				array->tcount = (int *)malloc(sizeof(int) * rowcount * array->xsize);
				tempaxis = (char *)malloc(rowcount * (maxlen+1) + 1);
				*tempaxis = 0;
				if (filename != NULL)
				{
					fseek(ff,fwhere,SEEK_SET);
				}
				else
				{
					stringIndex = fTextWhere;
				}
//				fgets(inn,sizeof(inn),ff);
				for (i = 1; i < rowcount - 1; i++)
				{
					char *pt;

					GET_NEXT_LINE();
//					fgets(inn,sizeof(inn),ff);
					if (factors[f1].type == 'I')
					{
						pt = strtok(inn,"|");
					}
					else
					{
						pt = strtok(inn,"| ");
					}
					strcat(tempaxis,pt);
					strcat(tempaxis," ");
					array->grid[i] = (double *)malloc(sizeof(double) * array->xsize);

					for (j = 1; j < array->xsize - 1; j++)
					{
						pt = strtok(NULL,"| (");
						array->grid[i][j] = atof(pt);
						pt = strtok(NULL,")");
						array->tcount[i * array->xsize + j] = atoi(pt);
					}
				}

				array->grid[0] = (double *)malloc(sizeof(double) * array->xsize);
				array->grid[rowcount - 1] = (double *)malloc(sizeof(double) * array->xsize);
/*
				for (k=0; k < array->xsize; k++)
				{
					array->grid[0][k] = array->grid[ARRAY_ROWS - 1][k];   // Copy from second last row to 0th row
					array->grid[(array->ysize - 2) + 1][k] = array->grid[2][k];
					array->tcount[k] = array->tcount[((array->ysize - 2) - 1) * array->xsize + k]; // Copy from last row to 0th row
					array->tcount[((array->ysize - 2) + 1) * array->xsize + k] = array->tcount[2 * array->xsize + k];
				}

				for (k=0; k < array->ysize; k++)
				{
					array->grid[k][0] = array->grid[k][(array->xsize - 2) - 1];
					array->grid[k][(array->xsize - 2) + 1] = array->grid[k][2];
					array->tcount[k * array->xsize] = array->tcount[k * array->xsize + (array->xsize - 2) - 1];
					array->tcount[k * array->xsize + (array->xsize - 2) + 1] = array->tcount[k * array->xsize + 2];
				}*/

				/* Wrap the array for splining purposes */

				for (k=0; k < WRAP_ARRAY_COLS; k++)
				{
					array->grid[0][k] = array->grid[ARRAY_ROWS - 1][k];   // Copy from second last row to 0th row
					array->grid[ARRAY_ROWS + 1][k] = array->grid[2][k];
					array->tcount[k] = array->tcount[(ARRAY_ROWS - 1) * WRAP_ARRAY_COLS + k]; // Copy from last row to 0th row
					array->tcount[(ARRAY_ROWS + 1) * WRAP_ARRAY_COLS + k] = array->tcount[2 * WRAP_ARRAY_COLS + k];
				}
				for (k=0; k < WRAP_ARRAY_ROWS; k++)
				{
					array->grid[k][0] = array->grid[k][ARRAY_COLS - 1];
					array->grid[k][ARRAY_COLS + 1] = array->grid[k][2];
					array->tcount[k * WRAP_ARRAY_COLS] = array->tcount[k * WRAP_ARRAY_COLS + ARRAY_COLS - 1];
					array->tcount[k * WRAP_ARRAY_COLS + ARRAY_COLS + 1] = array->tcount[k * WRAP_ARRAY_COLS + 2];
				}

				array->yaxis = MakeAxis(tempaxis,array->ysize,factors[f1].type,maxlen,wrapy);

				if (!factors[f1].wrap && (factors[f1].type == 'S' || factors[f1].type == 'B'))
				{
					array->Ylbounds = (double *)calloc(WRAP_ARRAY_ROWS,sizeof(double));
					array->Yubounds = (double *)calloc(WRAP_ARRAY_ROWS,sizeof(double));
					spacing = (VECTOR_OF_DOUBLE_MEMBER(array->yaxis,3) - VECTOR_OF_DOUBLE_MEMBER(array->yaxis,2)) / 2.0;

					for (i = 0; i < ARRAY_ROWS; i++)
					{
						array->Ylbounds[i] = VECTOR_OF_DOUBLE_MEMBER(array->yaxis,i + 1) - spacing;
						array->Yubounds[i] = VECTOR_OF_DOUBLE_MEMBER(array->yaxis,i + 1) + spacing;
					}
				}

				if (!factors[f2].wrap && (factors[f2].type == 'S' || factors[f2].type == 'B'))
				{
					array->Xlbounds = (double *)calloc(WRAP_ARRAY_COLS,sizeof(double));
					array->Xubounds = (double *)calloc(WRAP_ARRAY_COLS,sizeof(double));
					/* Using points 3 and 2 below because 0 is empty (no wrap) and 1 might have zero in it */
					spacing = (VECTOR_OF_DOUBLE_MEMBER(array->xaxis,3) - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,2)) / 2.0;
					for (i = 0; i < ARRAY_COLS; i++)
					{
						array->Xlbounds[i] = VECTOR_OF_DOUBLE_MEMBER(array->xaxis,i + 1) - spacing;
						array->Xubounds[i] = VECTOR_OF_DOUBLE_MEMBER(array->xaxis,i + 1) + spacing;
					}
				}

				free(tempaxis);
				if (transpose)
				{
					swapgrid = (double **)malloc(sizeof(double *)*array->xsize);
					swaptcount = (int *)malloc(sizeof(int) * array->xsize * rowcount);

					for (i=0; i < array->xsize; i++)
					{
						swapgrid[i] = (double *)malloc(sizeof(double)*array->ysize);
						for (j=0; j < array->ysize; j++)
						{
							swapgrid[i][j] = array->grid[j][i];
							swaptcount[i * array->ysize + j] = array->tcount[j * array->xsize + i];
						}
					}
					for (i=0; i < array->ysize; i++)
					{
						free(array->grid[i]);
					}
					free(array->grid);
					array->grid = swapgrid;
					free(array->tcount);
					array->tcount = swaptcount;
					swapsize = array->xsize;
					swapmax = array->xmax;
					free(array->xaxis);
					array->xaxis = array->yaxis;
					array->xsize = array->ysize;
					array->xmax = array->ymax;
					array->yaxis = swapaxis;
					array->ysize = swapsize;
					array->ymax = swapmax;
					swapmax = array->factorx;
					array->factorx = array->factory;
					array->factory = swapmax;
					i = wrapx;
					wrapx = wrapy;
					wrapy = i;
					swapaxis = array->Ylbounds;
					array->Ylbounds = array->Xlbounds;
					array->Xlbounds = swapaxis;
					swapaxis = array->Yubounds;
					array->Yubounds = array->Xubounds;
					array->Xubounds = swapaxis;

					i = f1;
					f1 = f2;
					f2 = i;
				}
				array->grid2 = (double **)calloc(array->ysize,sizeof(double **));
				for (i = 0; i < array->ysize; i++)
				{
					array->grid2[i] = (double *)calloc(array->xsize,sizeof(double));
				}

			}
			/* Step two: do all the auxillary calculations for this grid */
			if ((factors[f1].type == 'S' || factors[f1].type == 'B') 
			 && (factors[f2].type == 'S' || factors[f2].type == 'B'))
			{
				/* array->XAxisArray is the x value analog of array->tarray */
				array->XAxisArray = (double **)calloc(WRAP_ARRAY_ROWS,sizeof(double *));
//	UNWRAP			array->XAxisArray = (double **)calloc(WRAP_ARRAY_ROWS,sizeof(double *));
				/* array->rowEntries stores how many non-empty points are in each row */
				array->rowEntries = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // How many points are in each row
				/* array->rowMaxs is the index of the rightmost occupied column of a given row */
				array->rowMaxs = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // Max column number in each row
				/* array->rowMins is the index of the leftmost occupied column of a given row */
				/* (other than the zerobin column where it exists */
				array->rowMins = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // Min column number in each row
				/* array->rowAvgs holds the average y value for each row (for cases when we can't interpolate */
				array->rowAvgs = (double *)calloc(WRAP_ARRAY_ROWS,sizeof(double));
				/* array->rowZeros indicates whether or not a row has data in its zero bin */
				array->rowZeros = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int)); 

				for (k = 0; k < WRAP_ARRAY_ROWS; k++)
				{
					array->XAxisArray[k] = (double *)calloc(3 * WRAP_ARRAY_COLS,sizeof(double));
// UNWRAP			array->XAxisArray[k] = (double *)calloc(WRAP_ARRAY_COLS,sizeof(double));
				}

				/* The rows at which we want to start and stop looking at tarray data */
				if (!factors[f1].wrap)
				{
					YstartPt = 1;
					YendPt = ARRAY_ROWS + 1;
				}
				else 
				{
					YstartPt = 0;
					YendPt = WRAP_ARRAY_ROWS;
				}
				
				/* The columns at which we want to start and stop looking at tarray data */
				if (!factors[f2].wrap)
				{
					XstartPt = 1;
					XendPt = ARRAY_COLS + 1;
				}
				else
				{
					XstartPt = 0;
					XendPt = WRAP_ARRAY_COLS;
				}

				xxcount = 0;
				if (f1 == f2)
				{
					YbinNo = 0;
					array->rowMins[0] = -1;
					array->rowZeros[0] = 0;
					for (k = YstartPt; k < YendPt; k++)
					{
						if (array->tcount[k * WRAP_ARRAY_COLS + k] >= MINCOUNT)
						{
							if (factors[f2].zero && k == XstartPt)
							{
								array->rowZeros[0] = 1;
							}
							else // !cols[j].zerobin || k > XstartPt) 
							{
								if (array->rowMins[0] == -1)
								{
									array->rowMins[0] = k - 1;
								}
								if (k != 0 && k != WRAP_ARRAY_COLS - 1)
								{
									array->rowAvgs[0] += array->grid[k][k];
									xxcount++;
								}
							}
							array->rowMaxs[0] = k - 1;

							memmove(&array->grid[0][YbinNo],&array->grid[k][k],sizeof(double));
							/* And add the x axis points to the collection of x values */
							if (!k)  // One point before the beginning of the 'points' array
							{
								array->XAxisArray[0][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,1)
								 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,2);
							}
							else if (k == ARRAY_COLS + 1)
							{
								array->XAxisArray[0][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS) 
								 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS - 1);
							}
							else
							{
								array->XAxisArray[0][YbinNo++] = VECTOR_OF_DOUBLE_MEMBER(array->xaxis,k);
							}
						}
					}

					array->rowEntries[0] = YbinNo;

					if (xxcount)
					{
						array->rowAvgs[0] /= xxcount;
						array->XXavg = array->rowAvgs[0];
					}

					if (!factors[f1].zero || !array->rowZeros[0])
					{
						if (factors[f1].wrap && array->rowEntries[0] >= 3) // If so, make a trebly wrapped version of the grid 
						{
							/* Triple the X values, eliminating redundant points (i.e. -160 & 200) */
							ecol = -1;
							scol = -1;
							for (col = 0; col < array->rowEntries[0]; col++)
							{
								if (array->XAxisArray[0][col] - 360.0 < array->XAxisArray[0][0])
								{
									// ecol is the last non-redundant column of the leftmost rep 
									ecol = col;
								}
								if (scol == -1 && array->XAxisArray[0][col] + 360.0 > array->XAxisArray[0][array->rowEntries[0] - 1])
								{
									// scol is the first non-redundant column of the rightmost rep
									scol = col;
								}
							}
							memmove(&array->XAxisArray[0][ecol + 1 + array->rowEntries[0]], &array->XAxisArray[0][scol], (array->rowEntries[0] - scol) * sizeof(double));
							memmove(&array->XAxisArray[0][ecol + 1], array->XAxisArray[0], array->rowEntries[0] * sizeof(double));

							for (col = 0; col <= ecol; col++)
							{
								array->XAxisArray[0][col] -= 360.0;
							}
							for (col = ecol + 1 + array->rowEntries[0]; col < ecol + 1 + 2 * array->rowEntries[0] - scol; col++)
							{
								array->XAxisArray[0][col] += 360.0;
							}

							tempGrid = (double *)calloc(3 * array->rowEntries[0],sizeof(double));
							// Now create the same non-redundant structure with the Y values 
							memmove(tempGrid,array->grid[0],array->rowEntries[0] * sizeof(double));

							// These are analogs of the XAxisArray memmoves above
							memmove(&tempGrid[ecol + 1 + array->rowEntries[0]], &tempGrid[scol], (array->rowEntries[0] - scol) * sizeof(double));
							memmove(&tempGrid[ecol + 1], tempGrid, array->rowEntries[0] * sizeof(double));
							free(array->grid[0]);
							array->grid[0] = tempGrid;

							tempGrid = (double *)calloc(3 * array->rowEntries[0],sizeof(double));
							free(array->grid2[0]);
							array->grid2[0] = tempGrid;
							array->rowEntries[0] += ecol + 1 + (array->rowEntries[0] - scol);
							array->tripled = 1;
						}
						splined(array->XAxisArray[0] - 1,array->grid[0] - 1,YbinNo,1.0e30,1.0e30,array->grid2[0] - 1);
					}
					else
					{
						splined(array->XAxisArray[0],array->grid[0],YbinNo,1.0e30,1.0e30,array->grid2[0] - 1);
					}				
				}
				else
				{
					/* Find all the occupied bins on the Y axis */
					for (k = YstartPt; k < YendPt; k++)
					{
						YbinNo = 0;
						xcount = 0;
						array->rowMins[k] = -1;
						array->rowZeros[k] = 0;
						for (col = XstartPt; col < XendPt; col++)
						{
							if (array->tcount[k * WRAP_ARRAY_COLS + col] >= MINCOUNT)
							{
								array->rowEntries[k]++;  // Count number of occupied bins
								if (col == XstartPt && factors[f2].zero)
								{
									array->rowZeros[k] = 1;
								}
								else  // !cols[j].zerobin || col > XstartPt
								{
									if (array->rowMins[k] == -1)
									{
										array->rowMins[k] = col - 1; //... note lowest occupied non-zero column
									}
									if (col != 0 && col != WRAP_ARRAY_COLS - 1)
									{
										array->rowAvgs[k] += array->grid[k][col];
										xcount++;
									}
								}

								array->rowMaxs[k] = col - 1;     // ...and highest occupied column
								
								/* Add this point to the collection of y values */
								memmove(&array->grid[k][YbinNo],&array->grid[k][col],sizeof(double));

								/* And add the x axis points to the collection of x values */
								if (!col)  // One point before the beginning of the 'points' array
								{
									array->XAxisArray[k][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,1)
									 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,2);
								}
								else if (col == ARRAY_COLS + 1)
								{
									array->XAxisArray[k][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS) 
									 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS - 1);
								}
								else
								{
									array->XAxisArray[k][YbinNo++] = VECTOR_OF_DOUBLE_MEMBER(array->xaxis,col);
								}
							}
						}
						if (xcount)
						{
							array->rowAvgs[k] /= xcount;
							_ASSERT(!_isnan(array->rowAvgs[k]));
							array->XXavg += array->rowAvgs[k];
							xxcount++;
						}
					}
//					check_co_array(inarray);

					array->XXavg /= xxcount;
					_ASSERT(!_isnan(array->rowAvgs[k]));
					/* Now we have a collection of x/y point sets; find the 2nd derivatives of each row */
					for (k = YstartPt; k < YendPt; k++)
					{
						if (array->rowEntries[k] - array->rowZeros[k] >= 3)
						{
							if (!factors[f2].zero || !array->rowZeros[k])
							{
								if (factors[f2].wrap && array->rowEntries[k] >= 3) // If so, make a trebly wrapped version of the grid 
								{
									/* Triple the X values, eliminating redundant points (i.e. -160 & 200) */
									ecol = -1;
									scol = -1;
									for (col = 0; col < array->rowEntries[k]; col++)
									{
										if (array->XAxisArray[k][col] - 360.0 < array->XAxisArray[k][0])
										{
											// ecol is the last non-redundant column of the leftmost rep 
											ecol = col;
										}
										if (scol == -1 && array->XAxisArray[k][col] + 360.0 > array->XAxisArray[k][array->rowEntries[k] - 1])
										{
											// scol is the first non-redundant column of the rightmost rep
											scol = col;
										}
									}
									memmove(&array->XAxisArray[k][ecol + 1 + array->rowEntries[k]], &array->XAxisArray[k][scol], (array->rowEntries[k] - scol) * sizeof(double));
									memmove(&array->XAxisArray[k][ecol + 1], array->XAxisArray[k], array->rowEntries[k] * sizeof(double));

									for (col = 0; col <= ecol; col++)
									{
										array->XAxisArray[k][col] -= 360.0;
									}
									for (col = ecol + 1 + array->rowEntries[k]; col < ecol + 1 + 2 * array->rowEntries[k] - scol; col++)
									{
										array->XAxisArray[k][col] += 360.0;
									}

									tempGrid = (double *)calloc(3 * array->rowEntries[k],sizeof(double));
									// Now create the same non-redundant structure with the Y values 
									memmove(tempGrid,array->grid[k],array->rowEntries[k] * sizeof(double));

									// These are analogs of the XAxisArray memmoves above
									memmove(&tempGrid[ecol + 1 + array->rowEntries[k]], &tempGrid[scol], (array->rowEntries[k] - scol) * sizeof(double));
									memmove(&tempGrid[ecol + 1], tempGrid, array->rowEntries[k] * sizeof(double));

/*
									memmove(&array->XAxisArray[k][array->rowEntries[k]], array->XAxisArray[k], array->rowEntries[k] * sizeof(double));
									memmove(&array->XAxisArray[k][2 * array->rowEntries[k]], array->XAxisArray[k], array->rowEntries[k] * sizeof(double));
									for (col = 0; col < array->rowEntries[k]; col++)
									{
										array->XAxisArray[k][col] -= 360.0;
										array->XAxisArray[k][2 * array->rowEntries[k] + col] += 360.0;
									}
									tempGrid = (double *)calloc(3 * array->rowEntries[k],sizeof(double));
									memmove(tempGrid,array->grid[k], sizeof(double) * array->rowEntries[k]);
									memmove(&tempGrid[array->rowEntries[k]], array->grid[k], sizeof(double) * array->rowEntries[k]);
									memmove(&tempGrid[array->rowEntries[k] * 2], array->grid[k], sizeof(double) * array->rowEntries[k]);
*/
									free(array->grid[k]);
									array->grid[k] = tempGrid;
									tempGrid = (double *)calloc(3 * array->rowEntries[k],sizeof(double));
									free(array->grid2[k]);
									array->grid2[k] = tempGrid;			
									array->rowEntries[k] += ecol + 1 + (array->rowEntries[k] - scol);
									array->tripled = 1;
								}

								splined(array->XAxisArray[k] - 1,array->grid[k] - 1,array->rowEntries[k],1.0e30,1.0e30,array->grid2[k] - 1);
							}
							else
							{
								/* Don't use the zero bin in the spline calculation */
								splined(array->XAxisArray[k],array->grid[k],array->rowEntries[k] - 1,1.0e30,1.0e30,array->grid2[k] - 1);
							}

						}
					}
				}

			}
			/* Only one axis is of the splining variety */
			else if (factors[f2].type == 'S' || factors[f2].type == 'B') 
			{
				xxcount = 0;
				array->XAxisArray = (double **)calloc(WRAP_ARRAY_ROWS,sizeof(double *));
				array->rowEntries = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // How many points are in each row
				array->rowMaxs = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // Max column number in each row
				/* array->rowMins is the index of the leftmost occupied column of a given row */
				/* (other than the zerobin column where it exists */
				array->rowMins = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // Min column number in each row
				/* array->rowAvgs holds the average y value for each row (for cases when we can't interpolate */
				array->rowAvgs = (double *)calloc(WRAP_ARRAY_ROWS,sizeof(double));
				/* array->rowZeros indicates whether or not a row has data in its zero bin */
				array->rowZeros = (int *)calloc(WRAP_ARRAY_ROWS,sizeof(int));  // How many points are in each row
				
				for (k = 0; k < WRAP_ARRAY_ROWS; k++)
				{
					array->XAxisArray[k] = (double *)calloc(3 * WRAP_ARRAY_COLS,sizeof(double));
				}

				if (!factors[f2].wrap)
				{
					XstartPt = 1;
					XendPt = ARRAY_COLS + 1;
				}
				else
				{
					XstartPt = 0;
					XendPt = WRAP_ARRAY_COLS;
				}

				/* Find all the sufficiently-occupied rows and set up the x and y vectors for 'em */
				for (k = 1; k < ARRAY_ROWS + 1; k++)
				{
					YbinNo = 0;
					xcount = 0;
					array->rowMins[k] = -1;
					array->rowZeros[k] = 0;

					for (col = XstartPt; col < XendPt; col++)
					{
						if (array->tcount[k * WRAP_ARRAY_COLS + col] >= MINCOUNT)
						{
							array->rowEntries[k]++;

							if (col == XstartPt && factors[f2].zero)
							{
								array->rowZeros[k] = 1;
							}
							else  // !cols[j].zerobin || col > XstartPt
							{
								if (array->rowMins[k] == -1)
								{
									array->rowMins[k] = col - 1; //... note lowest occupied non-zero column
								}
								if (col != 0 && col != WRAP_ARRAY_COLS - 1)
								{
									array->rowAvgs[k] += array->grid[k][col];
									xcount++;
								}
							}

							array->rowMaxs[k] = col - 1;     // ...and highest occupied column
							
							/* Add this point to the collection of y values */
							memmove(&array->grid[k][YbinNo],&array->grid[k][col],sizeof(double));

							if (!col)  // One point before the beginning of the 'points' array
							{
								array->XAxisArray[k][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,1)
								 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,2);
							}
							else if (col == ARRAY_COLS + 1)
							{
								array->XAxisArray[k][YbinNo++] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS) 
								 - VECTOR_OF_DOUBLE_MEMBER(array->xaxis,ARRAY_COLS - 1);
							}
							else // One point after the end of the points array
							{
								array->XAxisArray[k][YbinNo++] = VECTOR_OF_DOUBLE_MEMBER(array->xaxis,col);
							}
						}
					}
					if (xcount)
					{
						array->rowAvgs[k] /= xcount;
						_ASSERT(!_isnan(array->rowAvgs[k]));
						array->XXavg += array->rowAvgs[k];
						xxcount++;
					}

				}

				array->XXavg /= xxcount;
				for (k = 1; k < ARRAY_ROWS + 1; k++)
				{
					if (array->rowEntries[k] - array->rowZeros[k] >= 3)
					{
						if (!factors[f2].zero || !array->rowZeros[k])
						{
							if (factors[f2].wrap && array->rowEntries[k] >= 3) // If so, make a trebly wrapped version of the grid 
							{
								/* Triple the X values, eliminating redundant points (i.e. -160 & 200) */
								ecol = -1;
								scol = -1;
								for (col = 0; col < array->rowEntries[k]; col++)
								{
									if (array->XAxisArray[k][col] - 360.0 < array->XAxisArray[k][0])
									{
										// ecol is the last non-redundant column of the leftmost rep 
										ecol = col;
									}
									if (scol == -1 && array->XAxisArray[k][col] + 360.0 > array->XAxisArray[k][array->rowEntries[k] - 1])
									{
										// scol is the first non-redundant column of the rightmost rep
										scol = col;
									}
								}
								memmove(&array->XAxisArray[k][ecol + 1 + array->rowEntries[k]], &array->XAxisArray[k][scol], (array->rowEntries[k] - scol) * sizeof(double));
								memmove(&array->XAxisArray[k][ecol + 1], array->XAxisArray[k], array->rowEntries[k] * sizeof(double));

								for (col = 0; col <= ecol; col++)
								{
									array->XAxisArray[k][col] -= 360.0;
								}
								for (col = ecol + 1 + array->rowEntries[k]; col < ecol + 1 + 2 * array->rowEntries[k] - scol; col++)
								{
									array->XAxisArray[k][col] += 360.0;
								}

								tempGrid = (double *)calloc(3 * array->rowEntries[k],sizeof(double));
								// Now create the same non-redundant structure with the Y values 
								memmove(tempGrid,array->grid[k],array->rowEntries[k] * sizeof(double));

								// These are analogs of the XAxisArray memmoves above
								memmove(&tempGrid[ecol + 1 + array->rowEntries[k]], &tempGrid[scol], (array->rowEntries[k] - scol) * sizeof(double));
								memmove(&tempGrid[ecol + 1], tempGrid, array->rowEntries[k] * sizeof(double));

								free(array->grid[k]);
								array->grid[k] = tempGrid;
								tempGrid = (double *)calloc(3 * array->rowEntries[k],sizeof(double));
								free(array->grid2[k]);
								array->grid2[k] = tempGrid;
								
								array->rowEntries[k] += ecol + 1 + (array->rowEntries[k] - scol);
								array->tripled = 1;

								{
									char crud[100];
									int col;
									for (col = 0; col < array->rowEntries[k]; col++)
									{
										sprintf(crud,"%f\t",array->XAxisArray[k][col]);
										OutputDebugString(crud);
									}
									OutputDebugString("\n");
									for (col = 0; col < array->rowEntries[k]; col++)
									{
										sprintf(crud,"%f\t",array->grid[k][col]);
										OutputDebugString(crud);
									}
									OutputDebugString("\n");
								}
							}
							splined(array->XAxisArray[k] - 1,array->grid[k] - 1,array->rowEntries[k],1.0e30,1.0e30,array->grid2[k] - 1);
						}
						else
						{
							splined(array->XAxisArray[k],array->grid[k],array->rowEntries[k] - 1,1.0e30,1.0e30,array->grid2[k] - 1);
						}
					}
				}

			}
			else
			{
				array->colAvgs = (double *)calloc(WRAP_ARRAY_COLS,sizeof(double));
				array->rowAvgs = (double *)calloc(WRAP_ARRAY_ROWS,sizeof(double));
				array->rowEntries = (int *)calloc(WRAP_ARRAY_COLS,sizeof(int));

				array->XXavg = 0.0;
				xxcount = 0;

				/* What's going on here? We're computing the average value of each row and column, as
				   well as a global average of every occupied bin on the grid */

				for (k = 1; k < ARRAY_ROWS + 1; k++)
				{
					xcount = 0;
					array->rowAvgs[k] = 0.0;
					for (m = 1; m < ARRAY_COLS + 1; m++)
					{
						if (array->tcount[k * WRAP_ARRAY_COLS + m] >= MINCOUNT)
						{
							array->rowAvgs[k] += array->grid[k][m];
							xcount++;
							array->XXavg += array->grid[k][m];
							xxcount++;

							array->colAvgs[m] += array->grid[k][m];
							array->rowEntries[m]++;
						}
					}
					if (xcount)
					{
						array->rowAvgs[k] /= xcount; 
					}
					else
					{
						array->rowAvgs[k] = BADVAL;
					}
				}

				array->XXavg /= xxcount;   /* array->XXavg is the global average for the whole grid */

				for (m = 1; m < ARRAY_COLS + 1; m++)
				{
					if (array->rowEntries[m])
					{
						array->colAvgs[m] /= array->rowEntries[m];  /* array->colAvgs is the array of column averages */
					}
					else
					{
						array->colAvgs[m] = array->XXavg;  /* If there's no data in the column, use the global mean */
					}
				}
				
				for (k = 1; k < ARRAY_ROWS + 1; k++)
				{
					if (array->rowAvgs[k] == BADVAL)
					{
						array->rowAvgs[k] = array->XXavg;  /* If there's no data in the row, use the global average as the average for that row */
					}
				}
			}
		}
		GET_NEXT_LINE();
//		fgets(inn,sizeof(inn),ff);
	}
	if (filename != NULL)
	{
		fclose(ff);
	}
	
	if (!strcmp(nucleus,"CA"))
	{
		ca_array = inarray;
	}
	else if (!strcmp(nucleus,"CB"))
	{
		cb_array = inarray;
	}
	else if (!strcmp(nucleus,"CO"))
	{
		co_array = inarray;
	}
	else if (!strcmp(nucleus,"HA"))
	{
		ha_array = inarray; 
	}
	else if (!strcmp(nucleus,"HN"))
	{
		hn_array = inarray;
		/*
#ifdef _DEBUG		
		{
			struct csarray *a1,*a2;
			int i;

			a1 = hn_array;
			a2 = ha_array;

			while (a1 != NULL && a2 != NULL)
			{
				if (a1->factorx != a2->factorx
				 || a1->factory != a2->factory
				 || a1->xmax != a2->xmax
				 || a1->xsize != a2->xsize
				 || a1->ymax != a2->ymax
				 || a1->ysize != a2->ysize)
				{
					printf("!same\n");
				}


				for (i=0; i < a1->ysize; i++)
				{
					if (memcmp(a1->grid[i],a2->grid[i],sizeof(float)*a1->xsize))
					{
						printf("!same");
					}
				}
				a1 = a1->next;
				a2 = a2->next;
			}
		}
#endif
		*/
	}
	else if (!strcmp(nucleus,"N15"))
	{
		n15_array = inarray;
	}
	else if (!strcmp(nucleus,"HB"))
	{
		hb_array = inarray;
	}
	else
	{
		for (i = 0; i < NHATOMS; i++)
		{
			if (!strcmp(nucleus,hatoms[i].name))
			{
				hatom_array[i] = inarray;
				break;
			}
		}
	}
//	check_co_array(co_array); // SJN DEBUG
}

void OutputArray(char *fname,char *nucleus)
{
	FILE *ff;
	struct csarray *array;

	ff = fopen(fname,"wt");

	if (!strcmp(nucleus,"CA"))
	{
		array = ca_array;
	}
	else if (!strcmp(nucleus,"CB"))
	{
		array = cb_array;
	}
	else if (!strcmp(nucleus,"CO"))
	{
		array = co_array;
	}
	else if (!strcmp(nucleus,"HA"))
	{
		array = ha_array;
	}
	else if (!strcmp(nucleus,"HN"))
	{
		array = hn_array;
	}
	else if (!strcmp(nucleus,"N15"))
	{
		array = n15_array;
	}
	else if (!strcmp(nucleus,"HB"))
	{
		array = hb_array;
	}

	while (array != NULL)
	{
		int i,j;

		fprintf(ff,"Array #x %s/%s\n",factors[array->factory].name,factors[array->factorx].name);
		for (i=0; i < array->xsize; i++)
		{
			switch (factors[array->factorx].type)
			{
			case 'S':
			case 'B':
				fprintf(ff,"%f ",*((float *)array->xaxis+i));
				break;
			case 'C':
				fprintf(ff,"%c ",*((char *)array->xaxis+i));
				break;
			case 'D':
				fprintf(ff,"%s ",(char *)array->xaxis+i*(array->xmax+1));
				break;
			case 'I':
				fprintf(ff,"%d - %d ",*((int *)array->xaxis + i * 2),*((int *)array->xaxis + i * 2 + 1));
				break;
			}
		}
		fprintf(ff,"\n");
		
		for (i=0; i < array->ysize; i++)
		{
			switch (factors[array->factory].type)
			{
			case 'S':
			case 'B':
				fprintf(ff,"%f | ",((float *)array->yaxis)[i]);
				break;
			case 'C':
				fprintf(ff,"%c | ",*((char *)array->yaxis+i));
				break;
			case 'D':
				fprintf(ff,"%s | ",(char *)array->yaxis+i*(array->ymax+1));
				break;
			case 'I':
				fprintf(ff,"%d - %d | ",*((int *)array->yaxis + i * 2),*((int *)array->yaxis + i * 2 + 1));
				break;

			}
			for (j = 0; j < array->xsize; j++)
			{
				fprintf(ff,"%f ",array->grid[i][j]);
			}
			fprintf(ff,"\n");
		}
		fprintf(ff,"\n\n");
		array = array->next;
	}
	fclose(ff);
}


void *MakeAxis(char *inline1,int size,char type,int maxlen,int wrap)
{
	void *axis;
	char *what,*pt;
	int i;

	if (type == 'S' || type == 'B')
	{
		axis = malloc(sizeof(double) * size);
	}
	else if (type == 'D')
	{
		axis = malloc(sizeof(char) * (maxlen+1) * size);
	}
	else if (type == 'C')
	{
		axis = malloc(sizeof(char) * size);
	}
	else if (type == 'I')
	{
		axis = malloc(sizeof(int) * size * 2);
	}

        what = strdup(inline1);

	pt = strtok(what," \r\n"); 
	for (i = 1; i < size - 1; i++)  
	{
		if (type == 'S' || type == 'B')
		{
			*(((double *)axis)+i) = atof(pt);
		}
		else if (type == 'D')
		{
			strcpy((char *)axis+(i * (maxlen+1)),pt);
		}
		else if (type == 'C')
		{
			*((char *)axis+i) = *pt;
		}
		else if (type == 'I')
		{
			*((int *)axis + i * 2) = atoi(pt);
			pt = strtok(NULL," -\r\n");
			*((int *)axis + i * 2 + 1) = atoi(pt);
		}
		pt = strtok(NULL," \r\n");
	}

	if (wrap)
	{
		*(((double *)axis)) = 2 * VECTOR_OF_DOUBLE_MEMBER(axis,0) - VECTOR_OF_DOUBLE_MEMBER(axis,1);
		*(((double *)axis) + size - 1) = 2 * VECTOR_OF_DOUBLE_MEMBER(axis,size - 2) - VECTOR_OF_DOUBLE_MEMBER(axis,size - 3);
	}
	return(axis);
}

int CountEntries(char* inline1,int *maxlen)
{
        char *what = strdup(inline1),*pt;
	int count=0,entlen=0,l;

	pt = strtok(what," \r\n\t");
	while (pt != NULL)
	{
		count++;
		if ((l=strlen(pt)) > entlen)
		{
			entlen = l;
		}
		pt = strtok(NULL," \r\n\t");
	}
	free(what);
	
        if (strstr(inline1," - ") != NULL)
	{
//		count *= 2;
		count /= 3;
	}

	*maxlen = entlen;
	return(count);
}


float CAResponse( float x, char res )
{
  int   idx;

  /* Optimize so as to minimize the RMS deviations but to force the 
     least-square fit for GLY to be y=x 
  
  static  float A[]=
  {0.895898, 0.988883, 0.949192, 1.042914, 0.980558, 2.175914, 0.878000,
  1.015386, 0.919463, 0.973477, 0.913184, 0.955657, 0.782053, 1.041980,
  1.064484, 1.041828, 0.989738, 0.945177, 0.940342, 1.142027};

  static  float B[]=
  {5.529815, 0.669652, 2.735415, -2.491989, 0.823929, -53.884661, 6.667859,
  -0.881711, 4.708403, 1.528016, 5.012200, 2.405757, 13.776433, -2.426207,
  -3.620457, -2.354105, 0.890348, 3.162634, 3.440521, -7.991317};
  */
  

  /* Optimize so that the RMS deviation for individual residue is    */
  /* smallest                                                        */
  
  
  static  float A[]=
  {0.895898, 0.988883, 0.949192, 1.042914, 0.980558, 0.864110, 0.878000,
  1.015386, 0.919463, 0.973477, 0.913184, 0.955657, 0.782053, 1.041980,
  1.064484, 1.041828, 0.989738, 0.945177, 0.940342, 1.142027};

  static  float B[]=
  {5.529815, 0.669652, 2.735415, -2.491989, 0.823929, 6.120568, 6.667859,
  -0.881711, 4.708403, 1.528016, 5.012200, 2.405757, 13.776433, -2.426207,
  -3.620457, -2.354105, 0.890348, 3.162634, 3.440521, -7.991317};

  idx = rc_idx(res);
  return( A[idx]*x + B[idx] );
}

float HNResponse( float x, char res )
{
  int   idx;

  static  float A[]=
  {0.871508, 1.0, 0.712130, 0.670926, 0.886117, 1.0, 0.914512, 0.906781,
  0.938087, 0.812441, 0.904884, 0.714729, 1.0, 0.838542, 0.920680, 0.773050,
  0.801727, 0.853764, 0.897227, 0.843111};

  static  float B[]=
  {1.024197, 0.0, 2.379130, 2.682708, 0.920257, 0.0, 0.786595, 0.907054,
  0.415482, 1.543224, 0.735153, 2.308084, 0.0, 1.270296, 0.728950, 1.856916,
  1.717622, 1.309450, 0.780519, 1.376460};

  idx = rc_idx(res);
  return( A[idx]*x + B[idx] );
}

float HAResponse( float x, char res )
{
  int   idx;

  static  float A[]=
  {0.941089, 1.0, 0.754454, 1.011632, 0.970147, 1.0, 0.748769, 0.997637,
  0.896891, 0.949979, 0.853976, 0.751115, 0.620889, 0.968115, 0.880238,
  0.847684, 0.948614, 1.046074, 0.988165, 0.956718};

  static  float B[]=
  {0.248509, 0.0, 1.147550, -0.047162, 0.137542, 0.0, 1.187722, -0.008209,
  0.441835, 0.219843, 0.616542, 1.167506, 1.691411, 0.134961, 0.516342,
  0.686029, 0.220483, -0.207574, 0.037131, 0.209545};


  idx = rc_idx(res);
  return( A[idx]*x + B[idx] );
}


/*
void    Optimize( CSHIFT *cs )
{
  CSHIFT   *p;

  p = cs;
  while( p!=NULL )
  {
    if( p->ca != NA )  p->ca = CAResponse( p->ca, p->type );
    if( p->hn != NA )  p->hn = HNResponse( p->hn, p->type );
    if( p->ha != NA )  p->ha = HAResponse( p->ha, p->type );
    p = p->next;
  }
  return;
}
*/



void Optimize(RESIDUE *Rz,CSHIFT *cs,long int lastresidx)
{
	CSHIFT *p;
	int ridx,i,resindex,rpidx,rmidx;
	RESIDUE *r=NULL,*rm,*rp;
	float x[] = {0.0,-200.00000, -180.000000, -160.000000, -140.000000, -120.000000, -100.000000, -80.000000, -60.000000,  -40.000000, -20.000000, 0.000000, 20.000000, 40.000000, 60.000000, 80.000000, 100.000000, 120.000000, 140.000000, 160.000000, 180.000000, 200.00000};
	float bigx[28] = {0.0,-260.0,-240.0, -220.0, -200.00000, -180.000000, -160.000000, -140.000000, -120.000000, -100.000000, -80.000000, -60.000000,  -40.000000, -20.000000, 0.000000, 20.000000, 40.000000, 60.000000, 80.000000, 100.000000, 120.000000, 140.000000, 160.000000, 180.000000, 200.00000, 220.0, 240.0, 260.0};
	char hbondstate[5] = {0,0,0,0,0};
	int rno;

	p = cs;

	rno = Rz[lastresidx].num;

	while (p != NULL)
	{
		for (i=0; i <= rno; i++)
		{
			if (Rz[i].num == p->n)
			{
				r = &Rz[i];
				resindex = i;
				break;
			}
		}

		if (r != NULL)
		{
			rp = &Rz[resindex+1];
			rm = &Rz[resindex-1];
			if (resindex != 0)
			{
				rmidx = rc_idx(iupac_code(rm->type));
			}
			else 
			{
				rmidx = -1;
			}

			if (r->num != rno)
			{
				rpidx = rc_idx(iupac_code(rp->type));
			}
			else
			{
				rpidx = -1;
			}

			hbondstate[0] = Rz[i].ha1dist == 0.0 ? 'N' : 'Y';
			hbondstate[1] = Rz[i].ha2dist == 0.0 ? 'N' : 'Y';
			hbondstate[2] = Rz[i].hndist == 0.0 ? 'N' : 'Y';
			hbondstate[3] = Rz[i].rdist == 0.0 ? 'N' : 'Y';

//			hbondstate[0] = Rz[i].hbonds[0].DA_FLAG == 2 || Rz[i].hbonds[1].DA_FLAG == 2 ? 'A' : 'N';
//			hbondstate[1] = Rz[i].hbonds[0].DA_FLAG == 1 || Rz[i].hbonds[1].DA_FLAG == 1 ? 'D' : 'N';
										
			if (r->ssbond)  /* Cysteine/Cystine Random Coil Correction */
			{
				if (p->ha != NA)
				{
					p->ha += 0.16;
				}
				if (p->ca != NA)
				{
					p->ca += -2.8;
				}
				if (p->cb != NA)
				{
					p->cb += 13.1;
				}
				if (p->n15 != NA)
				{
					p->n15 += -0.2;
				}
				if (p->hn != NA)
				{
					p->hn += 0.11;
				}
				if (p->hside[HYDRO_HB2] != NA)
				{
					p->hside[HYDRO_HB2] += 0.32;
				}
				if (p->hside[HYDRO_HB3] != NA)
				{
					p->hside[HYDRO_HB3] += 0.06;
				}
			}

			ridx = rc_idx(iupac_code(r->type));

	/* Alpha Hydrogen */
			if (p->ha != NA) 
			{
				/* AA/PHI */
				if (r->phi < 360.0)
				{
					p->ha += quickSpline(x,ha_aaphi[ridx],19,r->phi,1);
				}
				if (rmidx != -1)
				{
					/* AA/AA-1 */
					p->ha += ha_aaaam1[ridx][rmidx];
					
					/* AA-1/PHI */
					if (r->phi < 360.0)
					{
						p->ha += quickSpline(x,ha_aam1phi[rmidx],19,r->phi,1);
					}

					/* AA-1/PHI-1 */
					if (rm->phi < 360.0)
					{
						p->ha += quickSpline(x,ha_aam1phim1[rmidx],19,rm->phi,1);
					}
					if (rpidx != -1)
					{
						/* AA-1/AA+1 */
						p->ha += ha_aam1aap1[rmidx][rpidx];
					
						/* PSI-1/PHI+1 */
						if (rm->psi < 360.0 && rp->phi < 360.0)
						{
							p->ha += quickSpline2(bigx,bigx,rm->psi,rp->phi,ha_psim1phip1);
						}			
					}
				}
				if (rpidx != -1)
				{
					/* AA/PSI+1 */
					if (rp->psi < 360.0)
					{
						p->ha += quickSpline(x,ha_aapsip1[ridx],19,rp->psi,1);			
					}

					/* AA/AA+1 */
					p->ha += ha_aaaap1[ridx][rpidx];

					
					/* AA+1/PSI */
					if (r->psi < 360.0)
					{
						p->ha += quickSpline(x,ha_aap1psi[rpidx],19,r->psi,1);
					}
					/* AA+1/PSI+1 */
					if (rp->psi < 360.0)
					{
						p->ha += quickSpline(x,ha_aap1psip1[rpidx],19,rp->psi,1);
					}
				}
			}

/* Alpha Carbon */
			if (p->ca != NA)
			{
				/* AA/PSI */
				if (r->psi < 360.0)
				{
					p->ca += quickSpline(x,ca_aapsi[ridx],19,r->psi,1);
				}
				/* AA/CHI */
				if (r->chi > -666.0)
				{
					if (r->chi < 0.0)
					{
						r->chi += 360.0;
					}
					if (r->chi >= 0.0 && r->chi < 120.0)
					{
						p->ca += ca_aachi[ridx][0];
					}
					else if (r->chi >= 120.0 && r->chi < 240.0)
					{
						p->ca += ca_aachi[ridx][1];
					}
					else if (r->chi >= 240.0 && r->chi < 360.0)
					{
						p->ca += ca_aachi[ridx][2];
					}
				}


				/* AA-1/AA+1 */
				if (rmidx != -1 && rpidx != -1)
				{
					p->ca += ca_aam1aap1[rmidx][rpidx];
				}
				/* AA-1/PSI+1 */
				if (rmidx != -1 && rpidx != -1 && rp->psi < 360.0)
				{
					p->ca += quickSpline(x,ca_aam1psip1[rmidx],19,rp->psi,1);
				}
				
				/* AA+1/PSI */
				if (rpidx != -1 && r->psi < 360.0) 
				{
					p->ca += quickSpline(x,ca_aap1psi[rpidx],19,r->psi,1);
				}
				/* AA/AA-1 */
				if (rmidx != -1)
				{
					p->ca += ca_aaaam1[ridx][rmidx];
				}
				/* AA/PSI-1 */
				if (rmidx != -1 && rm->psi < 360.0)
				{
					p->ca += quickSpline(x,ca_aapsim1[ridx],19,rm->psi,1);
				}
				/* AA/AA+1 */
				if (rpidx != -1)
				{
					p->ca += ca_aaaap1[ridx][rpidx];
				}
				/* AA/PHI */
				if (r->phi < 360.0)
				{
					p->ca += quickSpline(x,ca_aaphi[ridx],19,r->phi,1);
				}
				/* AA/PHI+1 */
				if (rpidx != -1 && rp->phi < 360.0)
				{
					p->ca += quickSpline(x,ca_aaphip1[ridx],19,rp->phi,1);
				}	
			}

			if (p->cb != NA)
			{
				/* AA/SSBOND */
				if (r->ssbond == 0)
				{
					p->cb += cb_aassbond[ridx][0];
				}
				else 
				{
					p->cb += cb_aassbond[ridx][1];
				}
				/* AA-1/AA+1 */
				if (rmidx != -1 && rpidx != -1)
				{
					p->cb += cb_aam1aap1[rmidx][rpidx];
				}
				/* AA/AA-1 */
				if (rmidx != -1)
				{
					p->cb += cb_aaaam1[ridx][rmidx];
				}
				/* AA/AA+1 */
				if (rpidx != -1)
				{
					p->cb += cb_aaaap1[ridx][rpidx];
				}
				/* AA+1/PSI */
				if (rpidx != -1 && r->psi < 360.0)
				{
					p->cb += quickSpline(x,cb_aap1psi[rpidx],19,r->psi,1);
				}
				/* AA/PHI+1 */
				if (rpidx != -1 && rp->phi < 360.0)
				{
					p->cb += quickSpline(x,cb_aaphip1[ridx],19,rp->phi,1);
				}
				/* AA/PSI */
				if (r->psi < 360.0)
				{
					p->cb += quickSpline(x,cb_aapsi[ridx],19,r->psi,1);
				}
				/* PSI/PSI+1 */
				if (r->psi < 360.0 && rpidx != -1 && rp->psi < 360.0)
				{
					p->cb += quickSpline2(bigx,bigx,r->psi,rp->psi,cb_psipsip1);
				}
				/* AA-1/PSI-1 */
				if (rmidx != -1 && rm->psi < 360.0)
				{
					p->cb += quickSpline(x,cb_aam1psim1[rmidx],19,rm->psi,1);
				}
				/* AA/PHI */
				if (r->phi < 360.0)
				{
					p->cb += quickSpline(x,cb_aaphi[ridx],19,r->phi,1);
				}	
			}				

			if (p->co != NA)
			{
				/* AA/PHI+1 */
				if (rpidx != -1 && rp->phi < 360.0)
				{
					p->co += quickSpline(x,co_aaphip1[ridx],19,rp->phi,1);
				}
				/* AA+1/PSI+1 */
				if (rpidx != -1 && rp->psi < 360.0)
				{
					p->co += quickSpline(x,co_aap1psip1[rpidx],19,rp->psi,1);
				}	
				/* AA/AA-1 */
				if (rmidx != -1)
				{
					p->co += co_aaaam1[ridx][rmidx];
				}
				/* AA/AA+1 */
				if (rpidx != -1)
				{
					p->co += co_aaaap1[ridx][rpidx];
				}
				/* AA-1/AA+1 */
				if (rpidx != -1 && rmidx != -1)
				{
					p->co += co_aam1aap1[rmidx][rpidx];
				}
				/* AA/PSI */
				if (r->psi < 360.0)
				{
					p->co += quickSpline(x,co_aapsi[ridx],19,r->psi,1);
				}
				/* AA-1/PSI-1 */
				if (rmidx != -1 && rm->psi < 360.0)
				{
					p->co += quickSpline(x,co_aam1psim1[rmidx],19,rm->psi,1);
				}
				/* PHI+1/PSI+1 */
				if (rpidx != -1 && rp->phi < 360.0 && rp->psi < 360.0)
				{
					p->co += quickSpline2(bigx,bigx,rp->phi,rp->psi,co_phip1psip1);
				}
				/* AA/PSI+1 */
				if (rpidx != -1 && rp->psi < 360.0)
				{
					p->co += quickSpline(x,co_aapsip1[ridx],19,rp->psi,1);
				}
				/* PSI-1/PSI+1 */
				if (rpidx != -1 && rmidx != -1 && rm->psi < 360.0 && rp->psi < 360.0)
				{
					p->co += quickSpline2(bigx,bigx,rm->psi,rp->psi,co_psim1psip1);
				}
			}

			if (p->n15 != NA)
			{
				/* AA-1/PSI-1 */
				if (rmidx != -1 && rm->psi < 360.0)
				{
					p->n15 += quickSpline(x,n15_aam1psim1[rmidx],19,rm->psi,1);
				}
				
				/* AA/CHI */
				if (r->chi > -666.0)
				{
					if (r->chi >= 0.0 && r->chi < 120.0)
					{
						p->n15 += n15_aachi[ridx][0];
					}
					else if (r->chi >= 120.0 && r->chi < 240.0)
					{
						p->n15 += n15_aachi[ridx][1];
					}
					else if (r->chi >= 240.0 && r->chi < 360.0)
					{
						p->n15 += n15_aachi[ridx][2];
					}
				}

				/* PSI/PSI-1 */
				if (rmidx != -1 && r->psi < 360.0 && rm->psi < 360.0)
				{
					p->n15 += quickSpline2(bigx,bigx,r->psi,rm->psi,n15_psipsim1);
				}
				/* AA/AA-1 */
				if (rmidx != -1) 
				{
					p->n15 += n15_aaaam1[ridx][rmidx];
				}

				/* AA/AA+1 */
				if (rpidx != -1)
				{
					p->n15 += n15_aaaap1[ridx][rpidx];
				}
				/* AA-1/AA+1 */
				if (rmidx != -1 && rpidx != -1)
				{
					p->n15 += n15_aam1aap1[rmidx][rpidx];
				}
				/* AA+1/PSI */
				if (rpidx != -1 && r->psi < 360.0)
				{
					p->n15 += quickSpline(x,n15_aap1psi[rpidx],19,r->psi,1);
				}
				/* AA/PSI-1 */
				if (rmidx != -1 && rm->psi < 360.0)
				{
					p->n15 += quickSpline(x,n15_aapsim1[ridx],19,rm->psi,1);
				}
				/* AA/PSI+1 */
				if (rpidx != -1 && rp->psi < 360.0)
				{
					p->n15 += quickSpline(x,n15_aapsip1[ridx],19,rp->psi,1);
				}
				/* AA-1/PSI */
				if (rmidx != -1 && r->psi < 360.0)
				{
					p->n15 += quickSpline(x,n15_aam1psi[rmidx],19,r->psi,1);
				}
			}

			if (p->hn != NA)
			{
				/* PSI-1/PSI+1 */
				if (rmidx != -1 && rpidx != -1 && rm->psi < 360.0 && rp->psi < 360.0)
				{
					p->hn += quickSpline2(bigx,bigx,rm->psi,rp->psi,hn_psim1psip1);
				}
				/* AA+1/PHI-1 */
				if (rmidx != -1 && rpidx != -1 && rm->phi < 360.0)
				{
					p->hn += quickSpline(x,hn_aap1phim1[rpidx],19,rm->phi,1);
				}
				/* AA/HBONDSTATE */
				if (!strcmp(hbondstate,"NN"))
				{
					p->hn += hn_aahbondstate[ridx][0];
				}
				else if (!strcmp(hbondstate,"ND"))
				{
					p->hn += hn_aahbondstate[ridx][1];
				}
				else if (!strcmp(hbondstate,"AN"))
				{
					p->hn += hn_aahbondstate[ridx][2];
				}
				else if (!strcmp(hbondstate,"AD"))
				{
					p->hn += hn_aahbondstate[ridx][3];
				}	
				/* AA+1/PSI+1 */
				if (rpidx != -1 && rp->psi < 360.0)
				{
					p->hn += quickSpline(x,hn_aap1psip1[rpidx],19,rp->psi,1);
				}
				/* AA-1/HBONDSTATE */
				if (rmidx != -1)
				{
					if (!strcmp(hbondstate,"NN"))
					{
						p->hn += hn_aam1hbondstate[rmidx][0];
					}
					else if (!strcmp(hbondstate,"ND"))
					{
						p->hn += hn_aam1hbondstate[rmidx][1];
					}
					else if (!strcmp(hbondstate,"AN"))
					{
						p->hn += hn_aam1hbondstate[rmidx][2];
					}
					else if (!strcmp(hbondstate,"AD"))
					{
						p->hn += hn_aam1hbondstate[rmidx][3];
					}
				}
				/* AA-1/AA+1 */
				if (rmidx != -1 && rpidx != -1)
				{
					p->hn += hn_aam1aap1[rmidx][rpidx];
				}
				/* AA+1/PSI */
				if (rpidx != -1 && r->psi < 360.0)
				{
					p->hn += quickSpline(x,hn_aap1psi[rpidx],19,r->psi,1);
				}
				/* AA-1/PSI */
				if (rmidx != -1 && r->psi < 360.0)
				{
					p->hn += quickSpline(x,hn_aam1psi[rmidx],19,r->psi,1);
				}
				/* AA/PSI */
				if (r->psi < 360.0)
				{
					p->hn += quickSpline(x,hn_aapsi[ridx],19,r->psi,1);
				}
				/* AA-1/PSI+1 */
				if (rmidx != -1 && rpidx != -1 && rp->psi < 360.0)
				{
					p->hn += quickSpline(x,hn_aam1psip1[rmidx],19,rp->psi,1);
				}
			}
		}
		p = p->next;
	}
	return;
}


int DumpGrid(float **pp,int size)
{
	static FILE *ff;
	static int count1,count2;
	int i,j;

	if (ff == NULL)
	{
		ff = fopen("c:\\nmrshifts\\dgrid.txt","wt");
	}

	if ((size == 27 && count1 == 4) || (size == 21 && count2 == 2))
	{
		return(1);
	}
	if (size == 27)
	{
		count1++;
	}
	else if (size == 21)
	{
		count2++;
	}

	if (ff != NULL)
	{
		for (i=0; i < size; i++)
		{
			for (j=0; j < size; j++)
			{
				fprintf(ff,"%f ",pp[i+1][j+1]);
			}
			fprintf(ff,"\n");
		}
		fprintf(ff,"\n");
	}
	return(1);
}


void Optimize2(RESIDUE *Rz,CSHIFT *cs,long int lastresidx)
{
	CSHIFT *p;
	int ridx,i,resindex,rpidx,rmidx;
	RESIDUE *r=NULL,*rm,*rp;
	float x[] = {0.0,-200.00000, -180.000000, -160.000000, -140.000000,
                     -120.000000, -100.000000, -80.000000, -60.000000,
                     -40.000000, -20.000000, 0.000000, 20.000000, 40.000000,
                      60.000000, 80.000000, 100.000000, 120.000000,
                      140.000000, 160.000000, 180.000000, 200.00000};
	float bigx[28] = {0.0,-260.0,-240.0, -220.0, -200.00000, -180.000000,
                       -160.000000, -140.000000, -120.000000, -100.000000,
                        -80.000000, -60.000000,  -40.000000, -20.000000,
                          0.000000, 20.000000, 40.000000, 60.000000,
                         80.000000, 100.000000, 120.000000, 140.000000,
                        160.000000, 180.000000, 200.00000, 220.0, 240.0, 260.0};

	char hbondstate[5] = {0,0,0,0,0};
	int rno;
	struct csarray* array;

#ifdef SURFACING
	static int surfaced;  // SJN SURFACE
#endif

#ifdef _DEBUG1
	FILE *ff;

	ff = fopen("shiftx.log","wt");
#endif
	p = cs;

	rno = /* Rz[lastresidx].num; SJN */ lastresidx;

	while (p != NULL)
	{
		for (i=0; i <= rno; i++)
		{
			if (Rz[i].num == p->n)
			{
				r = &Rz[i];
				resindex = i;
				break;
			}
		}

		if (r != NULL)
		{
			rp = &Rz[resindex+1];
			rm = &Rz[resindex-1];
			if (resindex != 0)
			{
				rmidx = rc_idx(iupac_code(rm->type));
			}
			else 
			{
				rmidx = -1;
			}

			if (/* SJN r->num */ resindex != rno)
			{
				rpidx = rc_idx(iupac_code(rp->type));
			}
			else
			{
				rpidx = -1;
			}

			hbondstate[0] = Rz[i].ha1dist == 0.0 ? 'N' : 'Y';
			hbondstate[1] = Rz[i].ha2dist == 0.0 ? 'N' : 'Y';
			hbondstate[2] = Rz[i].hndist == 0.0 ? 'N' : 'Y';
			hbondstate[3] = Rz[i].rdist == 0.0 ? 'N' : 'Y';
										
			if (r->ssbond)  /* Cysteine/Cystine Random Coil Correction */
			{
				if (p->ha != NA)
				{
					p->ha += 0.16;
				}
				if (p->ca != NA)
				{
					p->ca += -2.8;
				}
				if (p->cb != NA)
				{
					p->cb += 13.1;
				}
				if (p->n15 != NA)
				{
					p->n15 += -0.2;
				}
				if (p->hn != NA)
				{
					p->hn += 0.11;
				}
				if (p->hn != NA)
				{
					p->hb += 0.0;  // TODO
				}
			}

			ridx = rc_idx(iupac_code(r->type));

#ifdef _DEBUG1
			fprintf(ff,"%d\t%s\nHA\t",r->num,r->type);
#endif
			if (p->ha != NA)
			{
				array = ha_array;

				while (array != NULL)
				{
#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&1))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 1;
						fq = fopen("surfaceha.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif
					p->ha += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					array = array->next;
				}
			}

#ifdef _DEBUG1
			fprintf(ff,"\nHN\t");
#endif
			if (p->hn != NA)
			{
				array = hn_array;
				while (array != NULL)
				{
#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&2))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 2;
						fq = fopen("surfacehn.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif
					p->hn += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					array = array->next;
				}
			}
#ifdef _DEBUG1
			fprintf(ff,"\nCA\t");
#endif
			if (p->ca != NA)
			{
				array = ca_array;
				while (array != NULL)
				{
#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&4))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 4;
						fq = fopen("surfaceca.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif

					p->ca += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					array = array->next;
				}
			}
#ifdef _DEBUG1
			fprintf(ff,"\nCB\t");
#endif
			if (p->cb != NA)
			{
				array = cb_array;
				while (array != NULL)
				{
#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&8))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 8;
						fq = fopen("surfacecb.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif

					p->cb += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					array = array->next;
				}
			}
#ifdef _DEBUG1
			fprintf(ff,"\nCO\t");
#endif
			if (p->co != NA)
			{
				array = co_array;
				while (array != NULL)
				{
					#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&16))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 16;
						fq = fopen("surfaceco.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif

					p->co += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					array = array->next;
				}
			}
#ifdef _DEBUG1
			fprintf(ff,"\nN15\t");
#endif
			if (p->n15 != NA)
			{
				array = n15_array;
				while (array != NULL)
				{
#ifdef SURFACING
					if (array->factorx==2 && array->factory==1 && !(surfaced&32))
					{
						int x,y;
						double z,ophi,opsi;
						FILE *fq;
						ophi = r->phi;
						opsi = r->psi;
						surfaced |= 32;
						fq = fopen("surfacen15.txt","wq");
						for (x = -180; x <= 180; x++)
						{
							for (y = -180; y <= 180; y++)
							{
								r->phi = (double)x;
								r->psi = (double)y;
								z = ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
								fprintf(fq,"%f ",z);
							}
							fprintf(fq,"\n");
						}
						r->phi = ophi;
						r->psi = opsi;
						fclose(fq);
					}
#endif

					p->n15 += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					_ASSERT(!_isnan(p->n15));
					array = array->next;
				}
			}
#ifdef _DEBUG1
			fprintf(ff,"\nHB\t");
#endif
			for (i = 0; i < NHATOMS; i++)
			{
				if (p->hside[i] != NA)
				{
					array = hatom_array[i];

					while (array != NULL)
					{
						p->hside[i] += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
						array = array->next;
					}
				}
			}
			if (p->hb != NA)
			{
				array = hb_array;
				while (array != NULL)
				{
					p->hb += ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx);
#ifdef _DEBUG1
					fprintf(ff,"%f\t",ArrayFactor(r,rp,rm,hbondstate,array,rmidx,rpidx,ridx));
#endif
					_ASSERT(!_isnan(p->hb));
					array = array->next;
				}
			}

#ifdef _DEBUG1
			fprintf(ff,"\n");
#endif
		}
		p = p->next;
	}
#ifdef _DEBUG1
	fclose(ff);
#endif
	return;
}


float ArrayFactor(RESIDUE *r,RESIDUE *rp,RESIDUE *rm,char* hbondstate,struct csarray *array,int rmidx,int rpidx,int ridx)
{
	char xchar,ychar;
	char *xstring,*ystring;
	float xfloat,yfloat,result=0.0;
	int xint,yint,*iaxis;
	float x[] = {0.0,-200.00000, -180.000000, -160.000000, -140.000000,
         -120.000000, -100.000000, -80.000000, -60.000000,  -40.000000,
          -20.000000, 0.000000, 20.000000, 40.000000, 60.000000, 80.000000,
           100.000000, 120.000000, 140.000000, 160.000000, 180.000000, 200.00000};
	float bigx[28] = {0.0,-260.0,-240.0, -220.0, -200.00000, -180.000000,
         -160.000000, -140.000000, -120.000000, -100.000000, -80.000000,
          -60.000000,  -40.000000, -20.000000, 0.000000, 20.000000, 40.000000,
           60.000000, 80.000000, 100.000000, 120.000000, 140.000000, 160.000000,
            180.000000, 200.00000, 220.0, 240.0, 260.0};

	if (!GetFactor(array->factorx,r,rp,rm,hbondstate,rmidx,rpidx,ridx,&xchar,&xstring,&xfloat,&xint)
	 || !GetFactor(array->factory,r,rp,rm,hbondstate,rmidx,rpidx,ridx,&ychar,&ystring,&yfloat,&yint))
	{
		return(array->XXavg);
	}

	/* Transform these one step further by getting the associated bin index instead of */
	/* the value itself */

	/*
	{
		int i,j;
		FILE *ff;
		
		ff = fopen("ppgrid.txt","wt");

		for (i = 0; i < 22; i++)
		{
			fprintf(ff,"%f\t",-180.0 + i * 20.0);
		}
		fprintf(ff,"\n");

		for (i = 0; i < 22; i++)
		{
			fprintf(ff,"%f\t",-180.0 + i * 20.0);
			for (j = 0; j < 22; j++)
			{
				fprintf(ff,"%f\t",twoSplineLookup2(array,-180.0 + i * 20.0, -180.0 + j * 20.0));
			}
			fprintf(ff,"\n");
		}
		fclose(ff);
	}
    */
	if (factors[array->factorx].type == 'I')
	{
		if (GetIntegerFactor(array->xaxis,array->xsize,&xint) == -1)
		{
			return(0.0);
		}
	}

	if (factors[array->factory].type == 'I')
	{
		if (GetIntegerFactor(array->yaxis,array->ysize,&yint) == -1)
		{
			return(0.0);
		}
	}


	if (factors[array->factorx].type == 'S' || factors[array->factorx].type == 'B')
	{
		switch (factors[array->factory].type)
		{
			case 'S':
			case 'B':
				if (array->factorx == array->factory)
				{
					return(SingleSplineLookup(array,xfloat));
				}
				else
				{
					return(twoSplineLookup2(array,yfloat,xfloat));
				}
				break;

			case 'D':
			case 'I': 
				return(SplineBinLookup(array,yint + 1,xfloat));
				break;
		}
	}
	else
	{
		return(BinBinLookup(array,yint,xint));
	}

/*
	if (factors[array->factorx].type == 'S')
	{
		switch (factors[array->factory].type)
		{
		case 'S':
			result = quickSpline3(bigx,bigx,yfloat,xfloat,array->grid);
			break;
		
		case 'D':
		case 'I':
			result = quickSpline(x,array->grid[yint],array->xsize,xfloat,1);
			break;

		case 'B':
			break;
		}
	}
	else if (factors[array->factorx].type == 'D')
	{
		switch (factors[array->factory].type)
		{
		case 'S':
			break; // shouldn't ever happen; should be transposed at the factory 
		
		case 'D':
		case 'I':
			result = array->grid[yint][xint];
			break;

		case 'B':
			break;
		}
	}
	else if (factors[array->factorx].type == 'B')
	{
		result = 0.0;
	}
*/
	return(result);
}


int GetIntegerFactor(void *axis, int axisSize, int *xint)
{
	int i, *iaxis;

	iaxis = (int *)axis;
	for (i=2; i < axisSize * 2 - 2; i += 2)
	{
		if (*xint >= iaxis[i] && *xint <= iaxis[i + 1])
		{
			*xint = (i - 2) / 2;
			return(*xint);
		}
	}
	return(-1);
}

int GetFactor(int factor,RESIDUE *r,RESIDUE *rp,RESIDUE *rm,char *hbondstate,int rmidx,int rpidx,int ridx,char *xchar,char **xstring,float *xfloat,int *xint)
{
	int success = 1;

	switch (factor)
	{
	case FACTOR_AA:
		*xint = ridx;
		break;

	case FACTOR_PHI:
		if (r->phi < 360.0)
		{
			*xfloat = r->phi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_PSI:
		if (r->psi < 360.0)
		{
			*xfloat = r->psi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_CHI:
		if (ridx == 0)  /* = ALA */
		{
			*xint = 4;
		}
		else if (ridx == 5)  /* = GLY */
		{
			*xint = 5;
		}
		else if (r->chi == NA)
		{
			*xint = 3;
		}
		else
		{
			if (r->chi < 0.0)
			{
				r->chi += 360.0;
			}

			if (r->chi >= 0.0 && r->chi < 120.0)
			{
				*xint = 0;
			}
			else if (r->chi >= 120.0 && r->chi < 240.0)
			{
				*xint = 1;
			}
			else if (r->chi >= 240.0 && r->chi < 360.0)
			{
				*xint = 2;
			}
		}
		*xfloat = r->chi;
		break;

	case FACTOR_CHI2:
		if (r->chi2 == NA)
		{
			*xint = 3;
		}
		else if (r->chi2 == -777.0)
		{
			*xint = 4;
		}
		else
		{
			if (r->chi2 < 0.0)
			{
				r->chi2 += 360.0;
			}

			if (r->chi2 >= 0.0 && r->chi2 < 120.0)
			{
				*xint = 0;
			}
			else if (r->chi2 >= 120.0 && r->chi2 < 240.0)
			{
				*xint = 1;
			}
			else if (r->chi2 >= 240.0 && r->chi2 < 360.0)
			{
				*xint = 2;
			}
		}
		*xfloat = r->chi2;
		break;

	case FACTOR_AAP1:
		if (rpidx != -1)
		{
			*xint = rpidx;
		}
		else
		{
			*xint = -1;
			success = 0;
		}
		break;

	case FACTOR_PHIP1:
		if (rpidx != -1 && rp->phi < 360.0)
		{
			*xfloat = rp->phi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_PSIP1:
		if (rpidx != -1 && rp->psi < 360.0)
		{
			*xfloat = rp->psi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_CHIP1:
		if (rpidx == 0)  /* = ALA */
		{
			*xint = 4;
		}
		else if (rpidx == 5)  /* = GLY */
		{
			*xint = 5;
		}
		else if (rpidx == -1 || rp->chi == NA)
		{
			*xint = 3;
		}
		else
		{
			if (rp->chi < 0.0)
			{
				rp->chi += 360.0;
			}

			if (rp->chi >= 0.0 && rp->chi < 120.0)
			{
				*xint = 0;
			}
			else if (rp->chi >= 120.0 && rp->chi < 240.0)
			{
				*xint = 1;
			}
			else if (rp->chi >= 240.0 && rp->chi < 360.0)
			{
				*xint = 2;
			}
		}
		*xfloat = rp->chi;
		break;


	case FACTOR_AAM1:
		if (rmidx != -1)
		{
			*xint = rmidx;
		}
		else
		{
			*xint = -1;
			success = 0;
		}
		break;

	case FACTOR_PHIM1:
		if (rmidx != -1 && rm->phi < 360.0)
		{
			*xfloat = rm->phi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_PSIM1:
		if (rmidx != -1 && rm->psi < 360.0)
		{
			*xfloat = rm->psi;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_CHIM1:
		if (rmidx == 0)  /* = ALA */
		{
			*xint = 4;
		}
		else if (rmidx == 5)  /* = GLY */
		{
			*xint = 5;
		}
		else if (rmidx == -1 || rm->chi == NA)
		{
			*xint = 3;
		}
		else
		{
			if (rm->chi < 0.0)
			{
				rm->chi += 360.0;
			}

			if (rm->chi >= 0.0 && rm->chi < 120.0)
			{
				*xint = 0;
			}
			else if (rm->chi >= 120.0 && rm->chi < 240.0)
			{
				*xint = 1;
			}
			else if (rm->chi >= 240.0 && rm->chi < 360.0)
			{
				*xint = 2;
			}
		}
		*xfloat = rm->chi;
		break;


	case FACTOR_HBONDSTAT:
		*xstring = hbondstate;
		*xint = 0;
		if (hbondstate[0] == 'Y')
		{
			*xint += 8;
		}
		if (hbondstate[1] == 'Y')
		{
			*xint += 4;
		}
		if (hbondstate[2] == 'Y')
		{
			*xint += 2;
		}
		if (hbondstate[3] == 'Y')
		{
			*xint += 1;
		}
		break;

	case FACTOR_INDEX:
		/*
		if (r->num == 1)
		{
			*xint = 0;
		}
		else
		{
			*xint = 1;
		}
		*/
		*xint = r->num;
		break;

	case FACTOR_INDEXM1:
		if (rmidx == -1)
		{
			success = 0;
		}
		else
		{
			*xint = rm->num;
		}
		break;

	case FACTOR_INDEXP1:
		if (rpidx == -1)
		{
			success = 0;
		}
		else
		{
			*xint = rp->num;
		}
		break;

	case FACTOR_ROW:
		*xint = 2;
		break;

	case FACTOR_SS:
		if (r->consens[0] == 'C')
		{
			*xint = 0;
		}
		else if (r->consens[0] == 'H')
		{
			*xint = 1;
		}
		else if (r->consens[0] == 'B')
		{
			*xint = 2;
		}
		else
		{
			success = 0;
		}
		*xchar = r->consens[0];
		break;

	case FACTOR_HA1BOND:
		if (hbondstate[0] == 'Y')
		{
			*xint = 0;
		}
		else if (hbondstate[0] == 'N')
		{
			*xint = 1;
		}
		break;

	case FACTOR_HA2BOND:
		if (hbondstate[1] == 'Y')
		{
			*xint = 0;
		}
		else if (hbondstate[1] == 'N')
		{
			*xint = 1;
		}
		break;

	case FACTOR_HNBOND:
		if (hbondstate[2] == 'Y')
		{
			*xint = 0;
		}
		else if (hbondstate[2] == 'N')
		{
			*xint = 1;
		}
		break;

	case FACTOR_OBOND:
		if (hbondstate[3] == 'Y')
		{
			*xint = 0;
		}
		else if (hbondstate[3] == 'N')
		{
			*xint = 1;
		}
		break;

	case FACTOR_HA1LEN:
		*xfloat = r->ha1dist;
		break;

	case FACTOR_HA2LEN:
		*xfloat = r->ha2dist;
		break;

	case FACTOR_HNLEN:
		*xfloat = r->hndist;
		break;

	case FACTOR_OLEN:
		*xfloat = r->rdist;
		break;

	case FACTOR_OLENM1:
		if (rmidx != -1)
		{
			*xfloat = rm->rdist;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_OLENP1:
		if (rpidx != -1)
		{
			*xfloat = rp->rdist;
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_SSBOND:
		*xint = r->ssbond;
		/*
		if (r->ssbond == 0)
		{
			*xint = 0;
		}
		else {
			*xint = 1;
		}*/
		break;

	case FACTOR_SSBONDP1:
		if (rpidx == -1)
		{
			success = 0;
		}
		else
		{
			*xint = rp->ssbond;
		}
		break;

	case FACTOR_SSBONDM1:
		if (rmidx == -1)
		{
			success = 0;
		}
		else
		{
			*xint = rm->ssbond;
		}
		break;

	case FACTOR_SSP1:
		if (rpidx != -1)
		{
			if (rp->consens[0] == 'C')
			{
				*xint = 0;
			}
			else if (rp->consens[0] == 'H')
			{
				*xint = 1;
			}
			else if (rp->consens[0] == 'B')
			{
				*xint = 2;
			}
			else
			{
				success = 0;
			}
			*xchar = rp->consens[0];
		}
		else
		{
			success = 0;
		}
		break;

	case FACTOR_SSM1:
		if (rmidx != -1)
		{
			if (rm->consens[0] == 'C')
			{
				*xint = 0;
			}
			else if (rm->consens[0] == 'H')
			{
				*xint = 1;
			}
			else if (rm->consens[0] == 'B')
			{
				*xint = 2;
			}
			else
			{
				success = 0;
			}
			*xchar = rm->consens[0];
		}
		else
		{
			success = 0;
		}
		break;

	}
	return(success);
}




static  void  splined( double x[], double y[], int n, double yp1, double ypn, double y2[] )
{
  int     i, k;
  double   p, qn, sig, un, *u;

  u=vectord(1,n-1);
  if (yp1 > 0.99e30)
  {
      y2[1]=u[1]=0.0;
  }
  else
  {
          y2[1] = -0.5;
          u[1]=(3.0/(x[2]-x[1]))*((y[2]-y[1])/(x[2]-x[1])-yp1);
  }
  //if (dcol == 8 && ecol == 29) printf("spl1 %x\n",*dpt);

  for (i=2;i<=n-1;i++)
  {
          sig=(x[i]-x[i-1])/(x[i+1]-x[i-1]);
          p=sig*y2[i-1]+2.0;
          y2[i]=(sig-1.0)/p;
          u[i]=(y[i+1]-y[i])/(x[i+1]-x[i]) - (y[i]-y[i-1])/(x[i]-x[i-1]);
          u[i]=(6.0*u[i]/(x[i+1]-x[i-1])-sig*u[i-1])/p;
  }
  
  //if (dcol == 8 && ecol == 29) printf("spl2 %x\n",*dpt);

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
  //if (dcol == 8 && ecol == 29) printf("spl0 %x\n",*dpt);
  
  for (k=n-1;k>=1;k--)
  {
		y2[k]=y2[k]*y2[k+1]+u[k];
  }
  free_vectord(u,1,n-1);
  //if (dcol == 8 && ecol == 29) printf("spl %x\n",*dpt);

}

static  void splintd( double xa[], double ya[], double y2a[], int n, double x, double *y)
{
  int     klo,khi,k;
  double   h,b,a;


  klo=1;
  khi=n;
  while (khi-klo > 1) {
          k=(khi+klo) >> 1;
		  
  //if (dcol == 8 && ecol == 29) printf("s2 %x\n",*dpt);
          if (xa[k] > x)
		  {
			  khi=k;
		  }
          else
		  {
			  klo=k;
		  }
  }
  h=xa[khi]-xa[klo];
  if (h == 0.0) nrerrord("Bad XA input to routine SPLINT");
  a=(xa[khi]-x)/h;
  b=(x-xa[klo])/h;
  // if (dcol == 8 && ecol == 29) printf("s3a %x\n",*dpt);
 *y=a*ya[klo]+b*ya[khi]+((a*a*a-a)*y2a[klo]+(b*b*b-b)*y2a[khi])*(h*h)/6.0;
  // if (dcol == 8 && ecol == 29) printf("s3 %x\n",*dpt);

}


static  void nrerrord( char error_text[] )
{
  fprintf(stderr,"Numerical Recipes run-time error...\n");
  fprintf(stderr,"%s\n",error_text);
  fprintf(stderr,"...now exiting to system...\n");
  exit(1);
}

static  double  *vectord( int nl, int nh )
{
  double   *v;

  v=(double *)malloc((unsigned) (nh-nl+1)*sizeof(double));
  if (!v) nrerrord("allocation failure in vector()");
  return(v-nl);
}

static  void  free_vectord( double *v, int nl, int nh )
{
  free((char*) (v+nl));
}



double twoSplineLookup2(struct csarray *array,double idata,double jdata)
{
	double result;
	int YbinNo,yymin,yymax,row,yycount = 0,yyzero = 0,col;
	double *xarray,*yarray,*yarray2,YYavg = 0.0;
	int YstartPt;  
	int YendPt;    
	int XstartPt;  
	int XendPt;    
	int ecol;
	int scol;

	xarray = (double *)calloc(3 * WRAP_ARRAY_ROWS,sizeof(double));
	yarray = (double *)calloc(3 * WRAP_ARRAY_ROWS,sizeof(double));
	yarray2 = (double *)calloc(3 * WRAP_ARRAY_ROWS,sizeof(double));

	if (!factors[array->factory].wrap)
	{
		YstartPt = 1;
		YendPt = ARRAY_ROWS + 1;
	}
	else 
	{
		YstartPt = 0;
		YendPt = WRAP_ARRAY_ROWS;
	}
	
	if (!factors[array->factorx].wrap)
	{
		XstartPt = 1;
		XendPt = ARRAY_COLS + 1;
	}
	else
	{
		XstartPt = 0;
		XendPt = WRAP_ARRAY_COLS;
	}

	YbinNo = 0;
	yymin = -1;

	for (row = YstartPt; row < YendPt; row++)
	{
		if (array->rowEntries[row] - array->rowZeros[row] >= 3)  // Need enough points to spline (or average) from...
		{
			if (factors[array->factory].zero && row == YstartPt)
			{
				yyzero = 1;
			}
			else if (yymin == -1)
			{
				yymin = row - 1;
			}

			yymax = row - 1;

			if (!row)  // One point before the beginning of the 'points' array
			{
				xarray[YbinNo] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->yaxis,1)
				 - VECTOR_OF_DOUBLE_MEMBER(array->yaxis,2);
			}
			else if (row == ARRAY_ROWS + 1)
			{
				xarray[YbinNo] = 2 * VECTOR_OF_DOUBLE_MEMBER(array->yaxis,ARRAY_ROWS) 
				 - VECTOR_OF_DOUBLE_MEMBER(array->yaxis,ARRAY_ROWS - 1);
			}
			else
			{
				xarray[YbinNo] = VECTOR_OF_DOUBLE_MEMBER(array->yaxis,row);
			}

			if (factors[array->factorx].wrap // ... and to ensure against extrapolation, either a wrapped row...
		     || (jdata == 0.0 && factors[array->factorx].zero && array->rowZeros[row]) // ... or a point in the zero bin
		     || (jdata >= VECTOR_OF_DOUBLE_MEMBER(array->Xlbounds,array->rowMins[row]) // or a point within the known limits of the row
		      && jdata <= VECTOR_OF_DOUBLE_MEMBER(array->Xubounds,array->rowMaxs[row])))
			{
				if (!factors[array->factorx].zero)
				{
					splintd(array->XAxisArray[row] - 1,array->grid[row] - 1,array->grid2[row] - 1,array->rowEntries[row],jdata,&yarray[YbinNo++]);
				}
				else
				{
					if (jdata == 0.0)
					{
						yarray[YbinNo++] = array->grid[row][0];
					}
					else if (array->rowZeros[row])
					{
						splintd(array->XAxisArray[row],array->grid[row],array->grid2[row] - 1,array->rowEntries[row] - 1,jdata,&yarray[YbinNo++]);
					}
					else
					{
						splintd(array->XAxisArray[row] - 1,array->grid[row] - 1,array->grid2[row] - 1,array->rowEntries[row],jdata,&yarray[YbinNo++]);
					}
				}
			}
			else
			{
				yarray[YbinNo++] = array->rowAvgs[row];
			}

			if (row != 0 && row != WRAP_ARRAY_ROWS - 1 && (!factors[array->factory].zero || row > YstartPt))
			{
				YYavg += yarray[YbinNo - 1];
				yycount++;
			}
		}
	}

	if (yycount)
	{
		YYavg /= yycount;
	}
	else
	{
		for (row = 1; row < ARRAY_ROWS + 1; row++)
		{
			if (!yyzero || row > YstartPt)
			{
				for (col = array->rowZeros[row] ? 1 : 0; col <= array->rowEntries[row]; col++)
				{
					YYavg += array->grid[row][col];
					yycount++;
				}
			}
		}
		YYavg /= yycount;
	}


	if (YbinNo - yyzero >= 3)
	{
		if (!factors[array->factory].zero)
		{
			if (factors[array->factory].wrap
			 || (idata >= VECTOR_OF_DOUBLE_MEMBER(array->Ylbounds,yymin)
			  && idata <= VECTOR_OF_DOUBLE_MEMBER(array->Yubounds,yymax)))
			{
				if (factors[array->factory].wrap)
				{
					ecol = -1;
					scol = -1;
					for (col = 0; col < YbinNo; col++)
					{
						if (xarray[col] - 360.0 < xarray[0])
						{
							// ecol is the last non-redundant column of the leftmost rep 
							ecol = col;
						}
						if (scol == -1 && xarray[col] + 360.0 > xarray[YbinNo - 1])
						{
							// scol is the first non-redundant column of the rightmost rep
							scol = col;
						}
					}
					memmove(&xarray[ecol + 1 + YbinNo], &xarray[scol], (YbinNo - scol) * sizeof(double));
					memmove(&xarray[ecol + 1], xarray, YbinNo * sizeof(double));

					for (col = 0; col <= ecol; col++)
					{
						xarray[col] -= 360.0;
					}
					for (col = ecol + 1 + YbinNo; col < ecol + 1 + 2 * YbinNo - scol; col++)
					{
						xarray[col] += 360.0;
					}
						
//					memmove(xarray,xarray + YbinNo, YbinNo * sizeof(double));
//					memmove(xarray,xarray + 2 * YbinNo, YbinNo * sizeof(double));
//					for (row = 0; row < YbinNo; row++)
//					{
//						xarray[row] -= 360.0;
//						xarray[row + 2 * YbinNo] += 360.0;
//					}
//					memmove(yarray,yarray + YbinNo, YbinNo * sizeof(double));
//					memmove(yarray,yarray + 2 * YbinNo, YbinNo * sizeof(double));
					memmove(&yarray[ecol + 1 + YbinNo], &yarray[scol], (YbinNo - scol) * sizeof(double));
					memmove(&yarray[ecol + 1], yarray, YbinNo * sizeof(double));
					
					{
						int col;
						OutputDebugString("Lookup Spline\n");
						for (col = 0; col < 2 * YbinNo + ecol + 1 - scol; col++)
						{
							char crud[100];

							sprintf(crud,"%f\t",xarray[col]);
							OutputDebugString(crud);
						}
						OutputDebugString("\n");
						for (col = 0; col < 2 * YbinNo + ecol + 1 - scol; col++)
						{
							char crud[100];

							sprintf(crud,"%f\t",yarray[col]);
							OutputDebugString(crud);
						}
						OutputDebugString("\n");
					}
					splined(xarray - 1,yarray - 1,2 * YbinNo + ecol + 1 - scol,1.0e30,1.0e30,yarray2 - 1);
					splintd(xarray - 1,yarray - 1,yarray2 - 1,2 * YbinNo + ecol + 1 - scol,idata,&result);
				}
				else
				{
					splined(xarray - 1,yarray - 1,YbinNo,1.0e30,1.0e30,yarray2 - 1);
					splintd(xarray - 1,yarray - 1,yarray2 - 1,YbinNo,idata,&result);
				}
			}
			else
			{
				result = USE_YY_AVERAGE ? YYavg : BADVAL;
			}
		}
		else
		{
			if (idata == 0.0)
			{
				if (xarray[0] == 0.0)
				{
					result = yarray[0];
				}
				else
				{
					result = USE_YY_AVERAGE ? YYavg : BADVAL;
				}
				
			}
			else if (idata >= VECTOR_OF_DOUBLE_MEMBER(array->Ylbounds,yymin)
			  && idata <= VECTOR_OF_DOUBLE_MEMBER(array->Yubounds,yymax))
			{
				splined(xarray,yarray,YbinNo - 1,1.0e30,1.0e30,yarray2 - 1);
				splintd(xarray,yarray,yarray2 - 1,YbinNo - 1,idata,&result);
			}
			else
			{
				result = USE_YY_AVERAGE ? YYavg : BADVAL;
			}
		}

	}
	else
	{
		result = USE_YY_AVERAGE ? YYavg : BADVAL;
	}
	free(xarray);
	free(yarray);
	free(yarray2);
	_ASSERT(!_isnan(result));
	return(result);
}


double SplineBinLookup(struct csarray *array,int row,double jdata)
{
	double result;

	if (!factors[array->factorx].zero)
	{
		if (array->rowEntries[row] >= 3
		 && (factors[array->factorx].wrap 
		 || (jdata >= VECTOR_OF_DOUBLE_MEMBER(array->Xlbounds,array->rowMins[row])
		 && jdata <= VECTOR_OF_DOUBLE_MEMBER(array->Xubounds,array->rowMaxs[row]))))
		{
			splintd(array->XAxisArray[row] - 1,array->grid[row] - 1,array->grid2[row] - 1,array->rowEntries[row],jdata,&result);
		}
		else
		{
			result = USE_XX_AVERAGE ? array->rowAvgs[row] : BADVAL;
		}
	}
	else  // The horizontal axis has a zero bin
	{
		if (jdata == 0.0)  // Take it from the zero bin
		{
			if (array->rowZeros[row])
			{
				result = array->grid[row][0];
			}
			else
			{
				result = USE_XX_AVERAGE ? array->rowAvgs[row] : BADVAL;
			}
		}
		else if (array->rowEntries[row] - array->rowZeros[row] >= 3 
		 && jdata >= VECTOR_OF_DOUBLE_MEMBER(array->Xlbounds,array->rowMins[row])
		 && jdata <= VECTOR_OF_DOUBLE_MEMBER(array->Xubounds,array->rowMaxs[row]))
		{
			if (array->rowZeros[row])
			{
				splintd(array->XAxisArray[row],array->grid[row],array->grid2[row] - 1,array->rowEntries[row],jdata,&result);
			}
			else
			{
				splintd(array->XAxisArray[row] - 1,array->grid[row] - 1,array->grid2[row] - 1,array->rowEntries[row],jdata,&result);
			}
		}
		else
		{
			result = USE_XX_AVERAGE ? array->rowAvgs[row] : BADVAL;
		}
	}
	_ASSERT(!_isnan(result));
	return(result);
}


double BinBinLookup(struct csarray *array,int xbin,int ybin)
{
	double result;
	int m;

	if (xbin != -1 && ybin != -1)
	{
		if (array->tcount[(xbin + 1) * WRAP_ARRAY_COLS + ybin + 1] >= MINCOUNT)
		{
			result = array->grid[xbin + 1][ybin + 1];
		}
		else  /* There's no data in that bin, so use the average of the row and column averages */
		{
			result = (array->rowAvgs[xbin + 1] + array->colAvgs[ybin + 1])/2.0;
		}
	}
	else
		{
			result = BADVAL;
#ifdef USE_XX_AVERAGE

			for (m = 0; m < ARRAY_ROWS; m++)
			{
				if (xbin == m)
				{
					result = array->rowAvgs[xbin + 1];
					break;
				}
			}
			if (result == BADVAL)
			{
				for (m = 0; m < ARRAY_COLS; m++)
				{
					if (ybin == m)
					{
						result = array->colAvgs[ybin + 1];
						break;
					}
				}
			}
			if (result == BADVAL)
			{
				result = array->XXavg;
			}
#endif

	}
	_ASSERT(!_isnan(result));
	return(result);

}


double SingleSplineLookup(struct csarray *array,double jdata)
{
	double result;
	int XstartPt,XendPt;

	if (!factors[array->factorx].wrap)
	{
		XstartPt = 1;
		XendPt = ARRAY_COLS + 1;
	}
	else
	{
		XstartPt = 0;
		XendPt = WRAP_ARRAY_COLS;
	}

	if (factors[array->factorx].zero)
	{
		if (jdata == 0.0)
		{
			if (array->rowZeros[0])
			{
				result = array->grid[0][XstartPt];
			}
			else
			{
				result = array->rowAvgs[0];
			}
		}
		else if (factors[array->factorx].wrap || (jdata >= VECTOR_OF_DOUBLE_MEMBER(array->Xlbounds,array->rowMins[0])
		 && jdata <= VECTOR_OF_DOUBLE_MEMBER(array->Xubounds,array->rowMaxs[0])))
		{
			if (array->rowZeros[0])
			{
				splintd(array->XAxisArray[0],array->grid[0],array->grid2[0] - 1,array->rowEntries[0],jdata,&result);
			}
			else
			{
				splintd(array->XAxisArray[0] - 1, array->grid[0] - 1, array->grid2[0] - 1,array->rowEntries[0],jdata,&result);
			}
		}
		else
		{
			result = (USE_XX_AVERAGE ? array->rowAvgs[0] : BADVAL);
		}
	}
	else if (factors[array->factorx].wrap || (jdata >= VECTOR_OF_DOUBLE_MEMBER(array->Xlbounds,array->rowMins[0])
		 && jdata <= VECTOR_OF_DOUBLE_MEMBER(array->Xubounds,array->rowMaxs[0])))
	{
		splintd(array->XAxisArray[0] - 1, array->grid[0] - 1, array->grid2[0] - 1,array->rowEntries[0],jdata,&result);
	}
	else
	{
		result = (USE_XX_AVERAGE ? array->rowAvgs[0] : BADVAL);
	}
	_ASSERT(!_isnan(result));
	return(result);
}



void OutputDebugString(char *what)
{
	static int first;
	FILE *ff;

	return; 

	if (!first)
	{
		ff = fopen("shiftx.log","wt");
		first = 1;
	}
	else
	{
		ff = fopen("shiftx.log","at");
	}
	if (ff != NULL)
	{
		fprintf(ff,"%s",what);
		fclose(ff);
	}
}


/*
int check_co_array(struct csarray *co_array)
{
	struct csarray *co = co_array;
	static int rowEntries = -1;

	while (co != NULL)
	{
		if (co->factorx == 5 && co->factory == 4)
		{
			break;
		}
		co = co->next;
	}

	if (co == NULL || co->factorx != 5 || co->factory != 4)
	{
		return(0);
	}

	if (rowEntries == -1)
	{
		rowEntries = co->rowEntries[9];
	}
	else
	{
		_ASSERT(rowEntries == co->rowEntries[9]);
	}
	return(1);
}
*/
