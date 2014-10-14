#include <stdio.h>
#include <math.h>
#include <stdlib.h>

#define DSIZE 256

int xplor_read(char *filename)
/* 
  READ XPLOR DATA MATRIX
  
  GWV: April 2009; adjusted for funny Intel Mac problems
*/
{
  FILE *fp;

  typedef struct header {
    int      flag;
    int      dummy;
    long     nasq;
    char     dummy2[16];
  } HEADER;
  HEADER header;
  
  typedef struct footer {
    long long  data[2];
  } FOOTER;
  FOOTER footer;
  
  int i, j, n, natoms;
  float *values;
  
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
  // printf("header> %12d %12d\n", header.flag, header.nasq);
  
  if (header.nasq < 4){
    printf("Error xplor_read: too small value nasq (%d); probable error with file %s\n", header.nasq, filename);
    printf("... Bailing out ...\n");
    exit(1);
  }
  
  // SET THE NUMBER OF ATOMS
  natoms = (int) sqrt(header.nasq);
  // INITIALIZE MATRIX
  //initialize_matrix();

  
  //printf("natoms> %d\n", natoms);
  
  if ((values = (float *) malloc( sizeof(float)*natoms)) == NULL) {
    printf("Error xplor_read: allocating memory\n");
    printf("... Bailing out ...\n");
    exit(1);    
  }

  for (i=0; i<natoms; i++) {    
  
    n = (int) fread(values, (size_t) sizeof(float), (size_t) natoms, fp);
    //printf("> %d %d %d\n", i, n, natoms);

    if (n != natoms) {
        printf("Error xplor_read: only %d values while reading row %d\n", n, i);
        printf("... Bailing out ...\n");
        exit(1);    
    }
    for(j=0;j<10;j++)
        printf("%d %d> %10.3e\n", i, j, values[j]);
    for(j=natoms-10;j<natoms;j++)
        printf("%d %d> %10.3e\n", i, j, values[j]);
        
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
  printf ("vdw> %d\n", vdw);
  if (vdw != -1) {
    printf("Error: xplor_read: VDW flag is set to %d.\n",vdw);
    printf("... Bailing out ...\n");
    exit(1);    
  }
  // CLOSE THE FILE
  fclose(fp);
  
  return natoms;
}

main(argc,argv)
int argc; char *argv[];
{    
int n;

// printf("%d %s\n", argc, argv[0]);

xplor_read(argv[1]);

}
