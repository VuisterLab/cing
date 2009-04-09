/*

 */

#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/*#include <linux/init.h>
*/
#include "nr/nrutil.h"

#define NO_DISTANCE     2048 // THIS CORRESPONDS TO ~550 RESIDUES (3.6 ANGSTROM PER RES)
#define ONEDIVLN2 	1.4426950409
#define LOG2(a) 	(log(a)*ONEDIVLN2)

extern int eflag;

// SOME DEFINITIONS
static float **dist_mtrx = 0;
static int     natoms = 0;
int	           eflag = 0;
static int     warningcount = 0;
static int     warninglimit = 50;


/* INITIALIZE THE DISTANCE MATRIX
   ############################## */
void initialize_matrix() 
{  
  int i, j;
  dist_mtrx = matrix(0, natoms-1, 0, natoms-1);
  // FILL THE DISTANCE MATRIX
  for (i=0; i!=natoms; i++) 
    { 
      for (j=0; j!=natoms; j++) 
	{
	  if (i==j)
	    dist_mtrx[i][j] = 0.0;
	  if (i > j) 
	    {
	      dist_mtrx[i][j] = 0.0;
	      dist_mtrx[j][i] = NO_DISTANCE;
	    }
	}
    }
}


/* FREE THE DISTANCE MATRIX
   ######################## */
void free_memory() 
{  
  free_matrix(dist_mtrx, 0, natoms-1, 0, natoms-1);
}


/* SET DISTANCE
   ############ */
void setdistance(int id1,
		 int id2,
		 float upper,
		 float lower) 
{
  int iatom, jatom;
  // CHECK IF THE ORDER IS RIGHT
  if (id1 > id2) 
    {
      iatom = id2; jatom = id1;
    }
  else 
    {
      iatom = id1; jatom = id2;
    }
  // ADD BOUNDS IF THEY ARE MORE TIGHT THEN EXISTING ONES
  if (dist_mtrx[iatom][jatom] == NO_DISTANCE || upper < dist_mtrx[iatom][jatom])
    {
      dist_mtrx[iatom][jatom] = upper; 
    }
  if (dist_mtrx[jatom][iatom] == NO_DISTANCE || lower > dist_mtrx[jatom][iatom])
    {
      dist_mtrx[jatom][iatom] = lower;
    }
}


/* GET LOWER BOUND
   ############### */
float lower_bound(int iatom, 
		  int jatom)
{
  if (iatom > jatom)
    return dist_mtrx[iatom][jatom];
  else if (iatom < jatom)
    return dist_mtrx[jatom][iatom];
  else
    return 0.0;
}


/* GET UPPER BOUND
   ############### */
float upper_bound(int iatom, 
		  int jatom)
{
  if (iatom < jatom)
    return dist_mtrx[iatom][jatom];
  else if (iatom > jatom)
    return dist_mtrx[jatom][iatom];
  else
    return 0.0;
}


/* CALCULATE UNCERTAINTY
   ##################### */
float uncertainty(int iatom, 
		  int jatom)
{
  float lower,upper;
  float score;
  lower = lower_bound(iatom, jatom);
  upper = upper_bound(iatom, jatom);
  if (lower > upper) 
    {
      if (warningcount < warninglimit) {
	printf("ALERT - LB > UB for atom pair (%d,%d): LB %.3f <-> UB %.3f \n",iatom+1, jatom+1, lower, upper);
	printf("        Atom numbers refer to the provided PDB file.\n");
      } else if (warningcount == warninglimit) {
	printf("ERROR - Warning limit has been reached.\n");
	printf("        Something seems to be wrong with your data.\n");
	printf("        To prevent endlessly scrolling terminals,\n");
	printf("        warnings beyond this point are not reported.\n");
      }
      score = 0.0;
      eflag = 1;
      warningcount ++;
    }
  else if (lower == upper)
    {
      if (warningcount < warninglimit) {
	printf("ALERT - UB = LB for atom pair (%d,%d): LB %.3f <-> UB %.3f \n",iatom+1, jatom+1, lower, upper);
	printf("        Atom numbers refer to the provided PDB file.\n");
      } else if (warningcount == warninglimit) {
	printf("ERROR - Warning limit has been reached.\n");
	printf("        Something seems to be wrong with your data.\n");
	printf("        To prevent endlessly scrolling terminals,\n");
	printf("        warnings beyond this point are not reported.\n");
      }
      score = 0.0;
      eflag = 1;
      warningcount ++;
    }
  else
    {
      score = LOG2(upper-lower);
    }
  return score;
}


/* CALCULATE UNCERTAINTY OF AN ATOM
   ################################ */
float atom_uncertainty(int iatom) 
{
  int jatom;
  float unc;
  unc = 0.0;
  for (jatom=0; jatom!=natoms; jatom++)
    {
      if (iatom != jatom) 
	{  
	  unc += uncertainty(iatom,jatom);
	}
    }
  return unc/(natoms-1);
}


/* CALCULATE UNCERTAINTY
   ##################### */
float total_uncertainty() 
{
  int i, j;
  float unc;
  // SET INITIAL UNCERTAINTY TO ZERO
  unc = 0.0;
  for (i=0; i!=natoms; i++)
    {
      unc += atom_uncertainty(i);
    }
  return unc/natoms;
}


/* CLEAR THE DISTANCE MATRIX
   ######################### */
void clear_matrix() 
{
  int i, j;
  // CLEAR THE DISTANCE MATRIX
  for (i=0; i!=natoms; i++) 
    {
      for (j=0; j!=natoms; j++) 
	{
	  if (i==j)
	    dist_mtrx[i][j] = 0.0;
	  if (i > j) {
	    dist_mtrx[i][j] = 0.0;
	    dist_mtrx[j][i] = NO_DISTANCE;
	  }
	}
    }
}


int xplor_read(char *filename)
/* 
  READ XPLOR DATA MATRIX
  
  GWV: April 2009; adjusted for funny Intel Mac problems; adjust HEADER and FOOTER defs for other platforms
*/
{
  FILE *fp;

  typedef struct header {
    int      flag;
    int      dummy;         /* delete on  LINUX 32 bit */
    long     nasq;
    char     dummy2[16];   /* dummy2[8] on LINUX 32 bit */
  } HEADER;
  HEADER header;
  
  typedef struct footer {
    char     dummy[16];    /* dummy[8] on LINUX 32 bit */
  } FOOTER;
  FOOTER footer;
  
  int i, j, n;  
  int vdw;

  // OPEN BINARY FILE
  //printf(">%s\n", filename);  
  fp = fopen(filename, "rb");
  if (fp==NULL) {
    printf("Error: opening file %s\n", filename); 
    printf("... Bailing out ...\n");
    exit(1);
  }

  // READ header
  n=fread(&header, (size_t) sizeof(HEADER), (size_t) 1, fp);
  //printf("header> %12d %12d\n", header.flag, header.nasq);
  
  if (header.nasq < 4){
    printf("Error xplor_read: too small value nasq (%d); probable error with file %s\n", header.nasq, filename);
    printf("... Bailing out ...\n");
    exit(1);
  }
  
  // SET THE NUMBER OF ATOMS
  natoms = (int) sqrt(header.nasq);
  //printf("natoms> %d\n", natoms);

  // INITIALIZE MATRIX
  initialize_matrix();

  // Read the matrix
  for (i=0; i<natoms; i++) {    
  
    n = (int) fread(dist_mtrx[i], (size_t) sizeof(float), (size_t) natoms, fp);
    //printf("> %d %d %d\n", i, n, natoms);

    if (n != natoms) {
        printf("Error xplor_read: only %d values while reading row %d\n", n, i);
        printf("... Bailing out ...\n");
        exit(1);    
    }

    /*
    for(j=0;j<10;j++)
        printf("%d %d> %10.3e\n", i, j, dist_mtrx[i][j]);
    for(j=natoms-10;j<natoms;j++)
        printf("%d %d> %10.3e\n", i, j, dist_mtrx[i][j]);
    */    
    // Read a footer after every row
    n = fread(&footer, (size_t) sizeof(FOOTER), (size_t) 1, fp);
    if (n != 1) {
        printf("Error xplor_read: while reading footer row %d\n", n, i);
        printf("... Bailing out ...\n");
        exit(1);    
    }    
  }
  
  // read final completion code indicator of XPLOR
  n = fread(&vdw, (size_t) sizeof(int), (size_t) 1, fp);
  //printf ("vdw> %d\n", vdw);
  if (vdw != -1) {
    printf("Error: xplor_read: VDW flag is set to %d.\n",vdw);
    printf("... Bailing out ...\n");
    exit(1);    
  }
  // CLOSE THE FILE
  fclose(fp);
  
  return natoms;
}


