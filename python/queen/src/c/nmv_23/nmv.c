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
  printf("DEBUG: FILL THE DISTANCE MATRIX\n");
  for (i=0; i!=natoms; i++)
    {
      for (j=0; j!=natoms; j++)
    {
          // diagonal
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
  int i;
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

//void NTprintf(char *msg){
//    printf(msg);
//    fflush(stdout);
//}


int xplor_read(char *filename)
/*
  READ XPLOR DATA MATRIX

  GWV: April 2009; adjusted for funny Intel Mac problems; adjust HEADER and FOOTER defs for other platforms
*/
{
  FILE *fp;

  int i, n;
  long pos;
  int vdw, flag, junk1, junk2;
  int nasq; // MIND THAT THIS IS A FORTRAN INTEGER IN xplor-nih/source/mmdisg.f on line 51:
//  INTEGER VALPTR, NSLCT, NMETR, BUNIT, LENGTH

  printf ("DEBUG: nmv.xplor_read %s\n", filename);

  // OPEN BINARY FILE
  fp = fopen(filename, "rb");
  if (fp==NULL) {
    printf("Error: opening file %s\n", filename);
    printf("... Bailing out ...\n");
    exit(1);
  }

  printf("Reading at pos: %ld\n", ftell(fp));
  fread(&flag, (size_t) sizeof(int), (size_t) 1, fp);
  // READ NATOMS SQUARED
  printf("Reading at pos: %ld\n", ftell(fp));
//  fread(&nasq, (size_t) sizeof(nasq), (size_t) 1, fp); # sanders latest code
  fread(&nasq, (size_t) sizeof(int), (size_t) 1, fp);
  // READ JUNK
  fread(&junk1, (size_t) sizeof(int), (size_t) 1, fp);
  fread(&junk2, (size_t) sizeof(int), (size_t) 1, fp);

  printf("DEBUG: int  flag: %d\n", flag);
  printf("DEBUG: int  nasq: %d\n", nasq);
  printf("DEBUG: int  junk1: %d\n", junk1);
  printf("DEBUG: int  junk2: %d\n", junk2);

  if (nasq < 4){
    printf("Error xplor_read: too small value nasq (%d); probable error with file %s\n", nasq, filename);
    printf("... Bailing out ...\n");
    exit(1);
  }

  natoms = (int) sqrt(nasq);
  printf("natoms> %d\n", natoms);

  /** Inserted extra check when having problems reading the file and this code found a million+ atoms that were then allocated in a squared matrix ;-)*/
  if (natoms > 999999){
    printf("Error xplor_read: too large number of atoms %d\n", natoms);
    exit(1);
  }

  printf("DEBUG: INITIALIZE MATRIX\n");
  initialize_matrix();

  printf("DEBUG: Read the matrix\n");
  for (i=0; i<natoms; i++) {

    // Read n atom floats
//    printf("Starting at pos: %ld\n", ftell(fp));

    n = (int) fread(dist_mtrx[i], (size_t) sizeof(float), (size_t) natoms, fp);
//    printf("Ending at pos: %ld\n", ftell(fp));
//    printf(">i,n %d %d\n", i, n);
    if (n != natoms) {
        if (feof(fp)) {
            fprintf(stderr, "End of file found\n");
        } else {
            fprintf(stderr, "Read error\n");
        }
        printf(">i,n %d %d\n", i, n);
        printf("Error xplor_read: only %d values while reading row %d\n", n, i);
        printf("... Bailing out ...\n");
        exit(1);
    }

//    for(j=0;j<10;j++)
//        printf("i,j,d %d %d> %10.3e\n", i, j, dist_mtrx[i][j]);
//    for(j=natoms-10;j<natoms;j++)
//        printf("%d %d> %10.3e\n", i, j, dist_mtrx[i][j]);

    // Read a footer after every row
    fread(&junk1, (size_t) sizeof(int), (size_t) 1, fp);
    fread(&junk2, (size_t) sizeof(int), (size_t) 1, fp);
  }

  printf("DEBUG: read final completion code indicator of XPLOR\n");
  n = fread(&vdw, (size_t) sizeof(int), (size_t) 1, fp);
  printf ("vdw> %d\n", vdw);
  if (vdw != -1) {
    printf("Error: xplor_read: VDW flag is set to %d.\n",vdw);
    printf("... Bailing out ...\n");
    exit(1);
  }
  printf("DEBUG: CLOSE THE FILE\n");
  fclose(fp);

  return natoms;
}


