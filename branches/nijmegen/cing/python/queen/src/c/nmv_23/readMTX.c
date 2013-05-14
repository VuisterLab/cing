#include <stdio.h>
#include <math.h>

#define DSIZE 256

/* READ XPLOR DATA
   ############### */
int xplor_read(char *filename)
{
  FILE *fp;

  typedef union map4byte {
    char        c[4];
    int         i;
    long        l;
    float       f;
  } MAP4byte;
  MAP4byte value;

  typedef union array {
    char        c[DSIZE];
    int         i[DSIZE/sizeof(int)];
    long long   l[DSIZE/sizeof(long long)];
    float       f[DSIZE/sizeof(float)];
    double      d[DSIZE/sizeof(long double)];
  } ARRAY dummy;

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
  
  int i, natoms;

  
  printf("sizeof>%d %d %d %d\n", sizeof(int), sizeof(long), sizeof(long long), sizeof(HEADER));
  

  // OPEN BINARY FILE
  printf(">%s\n", filename);
  
  fp = fopen(filename, "rb");
  if (fp==NULL) {
   printf("Error: opening file %s\n", filename); 
  }

  // READ header
  i=fread(&header, (size_t) sizeof(HEADER), (size_t) 1, fp);
  printf("header> %12d %12d\n", header.flag, header.nasq);
  
  natoms = (int) sqrt(header.nasq);

  for (i=0; i<natoms; i++) {
    fread(&value, (size_t) sizeof(MAP4byte), (size_t) 1, fp);
    printf("%d> %12d %12d %10.3e\n", i, value.i, value.l, value.f);
  }
  
  fread(&footer, (size_t) sizeof(FOOTER), (size_t) 1, fp);
  
  for (i=0; i<16; i++) {
    fread(&value, (size_t) sizeof(MAP4byte), (size_t) 1, fp);
    printf("%d> %12d %12d %10.3e\n", i, value.i, value.l, value.f);
  }
  
 exit(0);

  
  // READ data
  i=fread(&dummy, (size_t) DSIZE, (size_t) 1, fp);
  dummy.c[DSIZE-1] = '\0';
  
  for (i=0; i<DSIZE/sizeof(double); i++)
    printf("%d> %12d %12d %10.3e %10.3e\n", i, dummy.i[i], dummy.l[i], dummy.f[i], dummy.d[i]);
     
  return 0;
}

main(argc,argv)
int argc; char *argv[];
{    
int n;

printf("%d %s\n", argc, argv[0]);

xplor_read(argv[1]);

}
