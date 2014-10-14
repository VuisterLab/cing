#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "psa.h"
#include "main.h"
#include "states.h"
#include "cs.h"
#include "nn.h"
#include "ssbond.h"
#include "residue.h"
#include "hetatm.h"
#include "vector.h"
#include "phipsi.h"
#include "torison.h"
#include "hydrogens.h"
#include "rings.h"
#include "es.h"
#include "proline.h"
#include "hbond.h"
#include "optimize.h"										
#include "display.h"
#include "chi.h"
#include "atomnametable.h"

#define DUMPSHIFTS 

#ifdef _WIN32        /* SJN */
#include "direct.h" /* SJN */
#else                /* SJN */
#include <unistd.h> /* SJN */
#endif

#ifndef max
#define max(x,y) (x > y ? x : y)
#define min(x,y) (x < y ? x : y)
#endif // max

int HNFactor(RESIDUE r,CSHIFT *c);
int ChiFactor(RESIDUE r,CSHIFT *c);

/* Main menu states SJN */

#define MAIN 0
#define INFILE 1
#define OUTFILE 2
#define OPTION 3
#define GO 4

struct tratoms tratoms[] =
	
{
'A',"H","H","HN",-1,
'A',"HA","HA","HA",-1,
'A',"HB1","1HB","HB1",-1,
'A',"HB2","2HB","HB2",-1,
'A',"HB3","3HB","HB3",-1,
'A',"C","C","C",-1,
'A',"CA","CA","CA",-1,
'A',"CB","CB","CB",-1,
'A',"N","N","N",-1,
'A',"O","O","O",-1,
'R',"H","H","HN",-1,
'R',"HA","HA","HA",-1,
'R',"HB2","1HB","HB2",-1,
'R',"HB3","2HB","HB1",-1,
'R',"HG2","1HG","HG2",-1,
'R',"HG3","2HG","HG1",-1,
'R',"HD2","1HD","HD2",-1,
'R',"HD3","2HD","HD1",-1,
'R',"HE","HE","HE",-1,
'R',"HH11","1HH1","HH11",-1,
'R',"HH12","2HH1","HH12",-1,
'R',"HH21","1HH2","HH21",-1,
'R',"HH22","2HH2","HH22",-1,
'R',"C","C","C",-1,
'R',"CA","CA","CA",-1,
'R',"CB","CB","CB",-1,
'R',"CG","CG","CG",-1,
'R',"CD","CD","CD",-1,
'R',"CZ","CZ","CZ",-1,
'R',"N","N","N",-1,
'R',"NE","NE","NE",-1,
'R',"NH1","NH1","NH1",-1,
'R',"NH2","NH2","NH2",-1,
'R',"O","O","O",-1,
'D',"H","H","HN",-1,
'D',"HA","HA","HA",-1,
'D',"HB2","1HB","HB2",-1,
'D',"HB3","2HB","HB1",-1,
'D',"C", "C", "C",-1,
'D',"CA","CA","CA",-1,
'D',"CB","CB","CB",-1,
'D',"CG","CG","CG",-1,
'D',"N","N","N",-1,
'D',"O","O","O",-1,
'D',"OD1","OD1","OD1",-1,
'D',"OD2","OD2","OD2",-1,
'N',"H","H","HN",-1,
'N',"HA","HA","HA",-1,
'N',"HB2","1HB","HB2",-1,
'N',"HB3","2HB","HB1",-1,
'N',"HD21","2HD2","HD21",-1,
'N',"HD22","1HD2","HD22",-1,
'N',"C","C","C",-1,
'N',"CA","CA","CA",-1,
'N',"CB","CB","CB",-1,
'N',"CG","CG","CG",-1,
'N',"N","N","N",-1,
'N',"ND2","ND2","ND2",-1,
'N',"O","O","O",-1,
'N',"OD1","OD1","OD1",-1,
'C',"H","H","HN",-1,
'C',"HA","HA","HA",-1,
'C',"HB2","1HB","HB2",-1,
'C',"HB3","2HB","HB1",-1,
'C',"HG","HG","HG",-1,
'C',"C","C","C",-1,
'C',"CA","CA","CA",-1,
'C',"CB","CB","CB",-1,
'C',"N","N","N",-1,
'C',"O","O","O",-1,
'C',"SG","SG","SG",-1,
'E',"H","H","HN",-1,
'E',"HA","HA","HA",-1,
'E',"HB2","1HB","HB2",-1,
'E',"HB3","2HB","HB1",-1,
'E',"HG2","1HG","HG2",-1,
'E',"HG3","2HG","HG1",-1,
'E',"C","C","C",-1,
'E',"CA","CA","CA",-1,
'E',"CB","CB","CB",-1,
'E',"CG","CG","CG",-1,
'E',"CD","CD","CD",-1,
'E',"N","N","N",-1,
'E',"O","O","O",-1,
'E',"OE1","OE1","OE1",-1,
'E',"OE2","OE2","OE2",-1,
'Q',"H","H","HN",-1,
'Q',"HA","HA","HA",-1,
'Q',"HB2","1HB","HB2",-1,
'Q',"HB3","2HB","HB1",-1,
'Q',"HG2","1HG","HG2",-1,
'Q',"HG3","2HG","HG1",-1,
'Q',"HE21","2HE2","HE21",-1,
'Q',"HE22","1HE2","HE22",-1,
'Q',"C","C","C",-1,
'Q',"CA","CA","CA",-1,
'Q',"CB","CB","CB",-1,
'Q',"CG","CG","CG",-1,
'Q',"CD","CD","CD",-1,
'Q',"N","N","N",-1,
'Q',"NE2","NE2","NE2",-1,
'Q',"O","O","O",-1,
'Q',"OE1","OE1","OE1",-1,
'G',"H","H","HN",-1,
'G',"HA2","1HA","HA2",-1,
'G',"HA3","2HA","HA1",-1,
'G',"C","C","C",-1,
'G',"CA","CA","CA",-1,
'G',"N","N","N",-1,
'G',"O","O","O",-1,
'H',"H","H","HN",-1,
'H',"HA","HA","HA",-1,
'H',"HB2","1HB","HB2",-1,
'H',"HB3","2HB","HB1",-1,
'H',"HD1","HD1","HD1",-1,
'H',"HD2","HD2","HD2",-1,
'H',"HE1","HE1","HE1",-1,
'H',"C","C","C",-1,
'H',"CA","CA","CA",-1,
'H',"CB","CB","CB",-1,
'H',"CG","CG","CG",-1,
'H',"CD2","CD2","CD2",-1,
'H',"CE1","CE1","CE1",-1,
'H',"N","N","N",-1,
'H',"ND1","ND1","ND1",-1,
'H',"NE2","NE2","NE2",-1,
'H',"O","O","O",-1,
'I',"H","H","HN",-1,
'I',"HA","HA","HA",-1,
'I',"HB","HB","HB",-1,
'I',"HG12","1HG1","HG12",-1,
'I',"HG13","2HG1","HG11",-1,
'I',"HG21","1HG2","HG21",-1,
'I',"HG22","2HG2","HG22",-1,
'I',"HG23","3HG2","HG23",-1,
'I',"HD11","1HD1","HD11",-1,
'I',"HD12","2HD1","HD12",-1,
'I',"HD13","3HD1","HD13",-1,
'I',"C","C","C",-1,
'I',"CA","CA","CA",-1,
'I',"CB","CB","CB",-1,
'I',"CG1","CG1","CG1",-1,
'I',"CG2","CG2","CG2",-1,
'I',"CD1","CD1","CD1",-1,
'I',"N","N","N",-1,
'I',"O","O","O",-1,
'L',"H","H","HN",-1,
'L',"HA","HA","HA",-1,
'L',"HB2","1HB","HB2",-1,
'L',"HB3","2HB","HB1",-1,
'L',"HG","HG","HG",-1,
'L',"HD11","1HD1","HD11",-1,
'L',"HD12","2HD1","HD12",-1,
'L',"HD13","3HD1","HD13",-1,
'L',"HD21","1HD2","HD21",-1,
'L',"HD22","2HD2","HD22",-1,
'L',"HD23","3HD2","HD23",-1,
'L',"C","C","C",-1,
'L',"CA","CA","CA",-1,
'L',"CB","CB","CB",-1,
'L',"CG","CG","CG",-1,
'L',"CD1","CD1","CD1",-1,
'L',"CD2","CD2","CD2",-1,
'L',"N","N","N",-1,
'L',"O","O","O",-1,
'K',"H","H","HN",-1,
'K',"HA","HA","HA",-1,
'K',"HB2","1HB","HB2",-1,
'K',"HB3","2HB","HB1",-1,
'K',"HG2","1HG","HG2",-1,
'K',"HG3","2HG","HG1",-1,
'K',"HD2","1HD","HD2",-1,
'K',"HD3","2HD","HD1",-1,
'K',"HE2","1HE","HE2",-1,
'K',"HE3","2HE","HE1",-1,
'K',"HZ1","1HZ","HZ1",-1,
'K',"HZ2","2HZ","HZ2",-1,
'K',"HZ3","3HZ","HZ3",-1,
'K',"C","C","C",-1,
'K',"CA","CA","CA",-1,
'K',"CB","CB","CB",-1,
'K',"CG","CG","CG",-1,
'K',"CD","CD","CD",-1,
'K',"CE","CE","CE",-1,
'K',"N","N","N",-1,
'K',"NZ","NZ","NZ",-1,
'K',"O","O","O",-1,
'M',"H","H","HN",-1,
'M',"HA","HA","HA",-1,
'M',"HB2","1HB","HB2",-1,
'M',"HB3","2HB","HB1",-1,
'M',"HG2","1HG","HG2",-1,
'M',"HG3","2HG","HG1",-1,
'M',"HE1","1HE","HE1",-1,
'M',"HE2","2HE","HE2",-1,
'M',"HE3","3HE","HE3",-1,
'M',"C","C","C",-1,
'M',"CA","CA","CA",-1,
'M',"CB","CB","CB",-1,
'M',"CG","CG","CG",-1,
'M',"CE","CE","CE",-1,
'M',"N","N","N",-1,
'M',"O","O","O",-1,
'M',"SD","SD","SD",-1,
'F',"H","H","HN",-1,
'F',"HA","HA","HA",-1,
'F',"HB2","1HB","HB2",-1,
'F',"HB3","2HB","HB1",-1,
'F',"HD1","HD1","HD1",-1,
'F',"HD2","HD2","HD2",-1,
'F',"HE1","HE1","HE1",-1,
'F',"HE2","HE2","HE2",-1,
'F',"HZ","HZ","HZ",-1,
'F',"C","C","C",-1,
'F',"CA","CA","CA",-1,
'F',"CB","CB","CB",-1,
'F',"CG","CG","CG",-1,
'F',"CD1","CD1","CD1",-1,
'F',"CD2","CD2","CD2",-1,
'F',"CE1","CE1","CE1",-1,
'F',"CE2","CE2","CE2",-1,
'F',"CZ","CZ","CZ",-1,
'F',"N","N","N",-1,
'F',"O","O","O",-1,
'P',"H2","H2","HT2",-1,
'P',"H3","H1","HT1",-1,
'P',"HA","HA","HA",-1,
'P',"HB2","1HB","HB2",-1,
'P',"HB3","2HB","HB1",-1,
'P',"HG2","1HG","HG2",-1,
'P',"HG3","2HG","HG1",-1,
'P',"HD2","1HD","HD2",-1,
'P',"HD3","2HD","HD1",-1,
'P',"C","C","C",-1,
'P',"CA","CA","CA",-1,
'P',"CB","CB","CB",-1,
'P',"CG","CG","CG",-1,
'P',"CD","CD","CD",-1,
'P',"N","N","N",-1,
'P',"O","O","O",-1,
'S',"H","H","HN",-1,
'S',"HA","HA","HA",-1,
'S',"HB2","1HB","HB2",-1,
'S',"HB3","2HB","HB1",-1,
'S',"HG","HG","HG",-1,
'S',"C","C","C",-1,
'S',"CA","CA","CA",-1,
'S',"CB","CB","CB",-1,
'S',"N","N","N",-1,
'S',"O","O","O",-1,
'S',"OG","OG","OG",-1,
'T',"H","H","HN",-1,
'T',"HA","HA","HA",-1,
'T',"HB","HB","HB",-1,
'T',"HG1","HG1","HG1",-1,
'T',"HG21","1HG2","HG21",-1,
'T',"HG22","2HG2","HG22",-1,
'T',"HG23","3HG2","HG23",-1,
'T',"C","C","C",-1,
'T',"CA","CA","CA",-1,
'T',"CB","CB","CB",-1,
'T',"CG2","CG2","CG2",-1,
'T',"N","N","N",-1,
'T',"O","O","O",-1,
'T',"OG1","OG1","OG1",-1,
'W',"H","H","HN",-1,
'W',"HA","HA","HA",-1,
'W',"HB2","1HB","HB2",-1,
'W',"HB3","2HB","HB1",-1,
'W',"HD1","HD1","HD1",-1,
'W',"HE1","HE1","HE1",-1,
'W',"HE3","HE3","HE3",-1,
'W',"HZ2","HZ2","HZ2",-1,
'W',"HZ3","HZ3","HZ3",-1,
'W',"HH2","HH2","HH2",-1,
'W',"C","C","C",-1,
'W',"CA","CA","CA",-1,
'W',"CB","CB","CB",-1,
'W',"CG","CG","CG",-1,
'W',"CD1","CD1","CD1",-1,
'W',"CD2","CD2","CD2",-1,
'W',"CE2","CE2","CE2",-1,
'W',"CE3","CE3","CE3",-1,
'W',"CZ2","CZ2","CZ2",-1,
'W',"CZ3","CZ3","CZ3",-1,
'W',"CH2","CH2","CH2",-1,
'W',"N","N","N",-1,
'W',"NE1","NE1","NE1",-1,
'W',"O","O","O",-1,
'Y',"H","H","HN",-1,
'Y',"HA","HA","HA",-1,
'Y',"HB2","1HB","HB2",-1,
'Y',"HB3","2HB","HB1",-1,
'Y',"HD1","HD1","HD1",-1,
'Y',"HD2","HD2","HD2",-1,
'Y',"HE1","HE1","HE1",-1,
'Y',"HE2","HE2","HE2",-1,
'Y',"HH","HH","HH",-1,
'Y',"C","C","C",-1,
'Y',"CA","CA","CA",-1,
'Y',"CB","CB","CB",-1,
'Y',"CG","CG","CG",-1,
'Y',"CD1","CD1","CD1",-1,
'Y',"CD2","CD2","CD2",-1,
'Y',"CE1","CE1","CE1",-1,
'Y',"CE2","CE2","CE2",-1,
'Y',"CZ","CZ","CZ",-1,
'Y',"N","N","N",-1,
'Y',"O","O","O",-1,
'Y',"OH","OH","OH",-1,
'V',"H","H","HN",-1,
'V',"HA","HA","HA",-1,
'V',"HB","HB","HB",-1,
'V',"HG11","1HG1","HG11",-1,
'V',"HG12","2HG1","HG12",-1,
'V',"HG13","3HG1","HG13",-1,
'V',"HG21","1HG2","HG21",-1,
'V',"HG22","2HG2","HG22",-1,
'V',"HG23","3HG2","HG23",-1,
'V',"C","C","C",-1,
'V',"CA","CA","CA",-1,
'V',"CB","CB","CB",-1,
'V',"CG1","CG1","CG1",-1,
'V',"CG2","CG2","CG2",-1,
'V',"N","N","N",-1,
'V',"O","O","O",-1
};

int NTRATOMS = (sizeof(tratoms) / sizeof(struct tratoms));

typedef struct OPTIONS
{
  int   phipsi;
  int   es;
  int   rc;
  int   hb;
  int   proline;
  int   sidechain;
  int   ss;
  int   nn;
  int   optimize;
  int   nucleus;
  int   chi;   /* SJN */ 
  int   hnbond; /* SJN */
  int   deuteration; /*dong xiaoli*/
} OPTIONS;

struct shiftlimit
{
  char res;
  char iupac_code;
  char nuc[5];
  char atom;
  int n;
  float min,max,avg,std,upper,lower;
};
double outOfBounds(char type,char *nucl,double shift);

char UseChain; 

void    usage_exit(int c)
{
  //do_ss();  /* SJN DEBUG */
  fprintf( stderr, "PSA v1.1 - A System for Protein Structure Analysis\n" );
  fprintf( stderr, "Written by Alexander Nip\n" );
  fprintf( stderr, "University of Alberta\n" );
  fprintf( stderr, "Feb. 1999\n\n" );
  fprintf( stderr, "Usage: psa [-help] [-cs] [-torison] [-IUPAC] [-phipsi] [-es] [-rc] [-hb]\n" );
  fprintf( stderr, "           [-proline] [-sidechain] [-ss] [-neighbors] [-optimize]\n" );
  fprintf( stderr, "           [-nn] [-radius] [-center] [-sort] [-HA] [-HN]\n" );
  fprintf( stderr, "           [-N15] [-CA] [-CB] [-CO] <pdb-file>\n" );
  fprintf( stderr, "-help     = display usage and exit\n" );
  fprintf( stderr, "-cs       = predict chemical shifts (default)\n" );
  fprintf( stderr, "-torison  = calcuate phi, psi and omega dihedral angles.\n" );
  fprintf( stderr, "-IUPAC    = produce 1-letter IUPAC codes (applicable only to \n" );
  fprintf( stderr, "            calculations of torison angles).\n" );
  fprintf( stderr, "-phipsi   = include phipsi dependency (always enabled).\n" );
  fprintf( stderr, "-es       = include electrostatics.\n" );
  fprintf( stderr, "-rc       = include ring-current effects.\n" );
  fprintf( stderr, "-hb       = include hydrogen-bonding effects.\n" );
  fprintf( stderr, "-proline  = include effects of proline's.\n" );
  fprintf( stderr, "-sidechain= include effects of orientations of sidechains.\n" );
  fprintf( stderr, "-ss       = include effects of di-sulfide bonds.\n" );
  fprintf( stderr, "-neighbors= include nearest-neighbor effect for N15.\n" );
  fprintf( stderr, "-optimize = include final optimization step.\n" );
  fprintf( stderr, "-nn       = list all neighboring atoms.\n" );
  fprintf( stderr, "-radius   = radius measured in A used in the nearest-neighbor calculation.\n" );
  fprintf( stderr, "-center   = atom of interest in the nearest-neighbor calculation.\n" );
  fprintf( stderr, "-sort     = sort the list of nearest-neighbors in ascending order.\n" );
  fprintf( stderr, "-HA       = display chemical shift predictiond for alpha-hydrogens only.\n" );
  fprintf( stderr, "-HN       = display chemical shift predictiond for amide-hydrogens only.\n" );
  fprintf( stderr, "-N15      = display chemical shift predictiond for amide-nitrogens only.\n" );
  fprintf( stderr, "-CA       = display chemical shift predictiond for alpha-carbons only.\n" );
  fprintf( stderr, "-CB       = display chemical shift predictiond for beta-carbons only.\n" );
  fprintf( stderr, "-CO       = display chemical shift predictiond for carbons only.\n" );
  if( c == 1 )  exit(1);
  return;
}

static RESIDUE      Rz[MAX_RES_NUM];  /* SJN */
static long rno = 0;  /* number of residues in Rz */
RES *receptor=NULL;  // SJN DEBUG

int    main( int argc, char *argv[] )
{			
  OPTIONS      opt={FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, -1, FALSE, FALSE};
  int          i,j,k, mode=CS, iupac=FALSE, sort=FALSE, last_num, nuclei=0,
    properties=0, seq_length=0,state=MAIN;
  float        radius, last_phi, last_psi=NA, last_chi;
  char         *file=NULL, center[20], res_label[4], last_res_label[4],last_res_type,label[8],label2[6]; /* SJN */
  FILE         *in=NULL,*out=NULL;  /* SJN */
  NN_ATOM      target_atom;
  SSBOND       *ssbonds=NULL, *sspt;
  HETATM       *water=NULL;
  CSHIFT       *phipsi=NULL, *ring_current=NULL, *es=NULL, *ss=NULL, *hb=NULL,
    *sidechain=NULL,*oldphipsi=NULL;
  PHIPSI       *mat=NULL, *mat2=NULL;
  long int     seed=-1; /*,rno=0; */
  RES          *protein=NULL, *rc_atom=NULL, *proline=NULL, *donor=NULL;
               
  NEIGHBOR     *neighbor=NULL;
  RING         *ring=NULL;
  HBOND        *hbond=NULL;
  DISPLAY_DATA *display_data=NULL;
  char *fileout = NULL,instring[512],*nonestring="<none>";   /* SJN */
  char  *pt,infile[512],outfile[512]; /* SJN */
  int errset;
  CSHIFT      *q;

  char xiaoliiupacCode;
  
  int xiaolihIndex;
  void ReadCSConfig(char *nucleus,char *filename);
  ReadCSConfig("N15",NULL);
  ReadCSConfig("CA",NULL);
  ReadCSConfig("CB",NULL);
  ReadCSConfig("CO",NULL);
  ReadCSConfig("HA",NULL);
  ReadCSConfig("HN",NULL);
  
  
  for (i = 2; i < NHATOMS; i++)  // Start at 2, skipping over H and HA 
    {
      ReadCSConfig(hatoms[i].name,NULL);
    }
  initShiftLimits();
  while (1) {
    if (/*argc == 1 */ 1)  /* SJN - patch to restore some command line functionality */
      {
	mode = CS;
	opt.phipsi    = TRUE;
	opt.rc        = TRUE;
	opt.ss        = TRUE;
	opt.optimize  = TRUE;
	opt.hb        = TRUE;
	opt.proline   = TRUE;
	opt.es        = TRUE;
	opt.sidechain = TRUE;
	opt.nn        = TRUE;
	opt.chi       = TRUE; /* SJN */
	opt.hnbond    = TRUE; /* SJN */
	
	properties = 11;
	file = nonestring;
	fileout = nonestring;
		
	if (argc == 4)
	  {
	    mode = CS;
	    opt.phipsi    = TRUE;
	    opt.rc        = TRUE;
	    opt.ss        = TRUE;
	    opt.optimize  = TRUE;
	    opt.hb        = TRUE;
	    opt.proline   = TRUE;
	    opt.es        = TRUE;
	    opt.sidechain = TRUE;
	    opt.nn        = TRUE;
	    opt.chi       = TRUE; /* SJN */
	    opt.hnbond	  = TRUE; /* SJN */
	    properties = 11;
	    file = argv[2];
	    fileout = argv[3];

	    switch (*(argv[1]))
	      {
	      case '2':
		opt.nucleus = N_CA;
		nuclei = 1;
		break;

	      case '3':
		opt.nucleus = N_CO;
		nuclei = 1;
		break;

	      case '4':
		opt.nucleus = N_CB;
		nuclei = 1;
		break;

	      case '5':
		opt.nucleus = N_HA;
		nuclei = 1;
		break;

	      case '6':
		opt.nucleus = N_HN;
		nuclei = 1;
		break;

	      case '7':
		opt.nucleus = N_N15;
		nuclei = 1;
		break;
	      }

	    strcpy(infile,argv[2]);
	    if (in != NULL) {
	      fclose(in);
	      in = NULL;
	    }
	    in = fopen(infile,"rb");
					
	    if (in == NULL) {
	      printf("\nFile \"%s\" not found.\n\n"
		     "Press RETURN to continue...",argv[2]);
					
	      exit(0);
	    }
	    else
	      {
		/* SJN - check for multiple chains if one isn't specified on the cmdline */
		if (*(argv[1] + 1) != '\0' && isalpha(*(argv[1] + 1)))  
		  {
		    UseChain = *(argv[1] + 1);
		  }
		else if (!CheckMultipleChains(in,1)) 
		  {
		    fclose(in);
		    exit(0);
		  }

		file = strdup(argv[2]);
	      }


	    strcpy(outfile,argv[3]);
	    out = fopen(outfile,"at");
        
	    if (out == NULL)
	      {
		printf("Unable to open \"%s\" for write.\n\n"
		       "Press RETURN to continue...",outfile);
		exit(0);
	      }
	    else 
	      {
		fclose(out);
		fileout = strdup(argv[3]);
	      }
	  }


	while (1 && argc != 4) {  /* SJN - still sneaking cmdline stuff in */
	  switch (state) {

	  case MAIN:
	    printf("%c\n",12);
	    printf("************************************************\n");
	    printf("*                                              *\n");
	    printf("*  ShiftX (Version 1.1.0)                        *\n");
	    printf("*    July 26,2004                                *\n");
	    printf("*                                              *\n");
	    printf("* A program to predict protein chemical shifts *\n");
	    printf("* from 3D coordinate (PDB format) data         *\n");
	    printf("*                                              *\n");
	    printf("* By Alex Nip                                  *\n");
	    printf("*    David Wishart                             *\n");
	    printf("*    Steve Neal                                *\n");
	    printf("*                                              *\n");
	    printf("* Contact: dsw@redpoll.pharmacy.ualberta.ca    *\n");
	    printf("*                                              *\n");
	    printf("************************************************\n\n");
#ifdef _DEBUG
	    printf("Time: %d\n",time(NULL));
#endif
	    printf("1) Predict All Shifts (1H, 13C, 15N)\n");
	    printf("2) Predict Alpha 13C Shifts Only\n");
	    printf("3) Predict Carbonyl 13C Shifts Only\n");
	    printf("4) Predict Beta 13C Shifts Only\n");
	    printf("5) Predict Alpha 1H Shifts Only\n");
	    printf("6) Predict Amide 1H Shifts Only\n");
	    printf("7) Predict Amide 15N Shifts Only\n");
	    printf("\n");
	    printf("8) Options\n\n");
	    printf("H) Help\n");
	    printf("X) Exit\n");
	    printf("\n");
	    printf("Enter your choice below: \n>>");
	    fgets(instring,sizeof(instring), stdin);
	    instring[strlen(instring)-1]='\0';
	    if (!isdigit(instring[0])) {
	      if (toupper(instring[0]) == 'H') {
		printf("<insert helpful information here>\n");
		/*system("more shiftx.help"); */
		fgets(instring,sizeof(instring), stdin);
		instring[strlen(instring)-1]='\0';
	      }
	      else if (toupper(instring[0]) == 'X') {
		printf("\nBye!\n");
		exit(0);
	      }
	      else {
		printf("Invalid choice.  Press RETURN to continue...");
		fgets(instring,sizeof(instring), stdin);	
		instring[strlen(instring)-1]='\0';
	      }
	    }
	    else if (isdigit(instring[0]) && instring[0] != '0') {
	      switch (instring[0]) {

	      case '1':
		opt.nucleus = -1;
		state = INFILE;
		break;
 
	      case '2':
		opt.nucleus = N_CA;
		state = INFILE;
		nuclei = 1;
		break;

	      case '3':
		opt.nucleus = N_CO;
		state = INFILE;
		nuclei = 1;
		break;

	      case '4':
		opt.nucleus = N_CB;
		state = INFILE;
		nuclei = 1;
		break;

	      case '5':
		opt.nucleus = N_HA;
		state = INFILE;
		nuclei = 1;
		break;

	      case '6':
		opt.nucleus = N_HN;
		state = INFILE;
		nuclei = 1;
		break;

	      case '7':
		opt.nucleus = N_N15;
		state = INFILE;
		nuclei = 1;
		break;

	      case '8':
		state = OPTION;
		break;

	      default:
		printf("Invalid choice.  Press RETURN to continue...");
		fgets(instring,sizeof(instring), stdin);	
		instring[strlen(instring)-1]='\0';
		break;
	      }
	    }
	    else {
	      printf("Invalid choice.  Press RETURN to continue...");
	      fgets(instring,sizeof(instring), stdin);	
	      instring[strlen(instring)-1]='\0';
	    }
	    break;

	  case OPTION:
	    printf("%c\n",12);  /* Clear screen */
	    printf("1) Toggle phipsi effects [%s]\n",opt.phipsi == TRUE ? "ON" : "OFF");
	    printf("2) Toggle electrostatic effects [%s]\n",opt.es == TRUE ? "ON" : "OFF");
	    printf("3) Toggle sidechain orientation effects [%s]\n",opt.sidechain == TRUE ? "ON" : "OFF");
	    printf("4) Toggle disulfide effects [%s]\n",opt.ss == TRUE ? "ON" : "OFF");
	    printf("5) Toggle hydrogen bond effects [%s]\n",opt.hb == TRUE ? "ON" : "OFF");
	    printf("6) Toggle proline effects [%s]\n",opt.proline == TRUE ? "ON" : "OFF");
	    printf("7) Toggle nearest neighbour effects (affects N15 only) [%s]\n",opt.nn == TRUE ? "ON" : "OFF");
	    printf("8) Toggle ring current effects [%s]\n",opt.rc == TRUE ? "ON" : "OFF");
	    printf("9) Toggle optimization [%s]\n",opt.optimize == TRUE ? "ON" : "OFF");
	    printf("10) Toggle N15 chi factor [%s]\n",opt.chi == TRUE ? "ON" : "OFF");
	    printf("11) Toggle N15 hydrogen bond factor [%s]\n",opt.hnbond == TRUE ? "ON" : "OFF");
	    printf("12) Toggle deuteration[%s]\n",opt.deuteration == TRUE ? "ON" : "OFF");
	    printf("\n");
	    printf("H) Help\n");
	    printf("X) Return to main menu\n");
	    printf("\n");
	    printf("Enter choice: ");
	    fgets(instring,sizeof(instring), stdin);	
	    instring[strlen(instring)-1]='\0';

	    if (!isdigit(instring[0])) {
	      if (toupper(instring[0]) == 'H') {
		printf("<insert helpful information here>\n");
		/*system("more shiftx.help"); */
		fgets(instring,sizeof(instring), stdin);	
		instring[strlen(instring)-1]='\0';
	      }
	      else {
		state = MAIN;
	      }
	    }
	    else if (isdigit(instring[0]) && instring[0] != '0') {

	      switch (instring[0]) {

	      case '1':
		if (instring[1] == '0') {
		  if (opt.chi = opt.chi ^ 1) {
		    properties++;
		  }
		  else {
		    properties--;
		  }
		}
		else if (instring[1] == '1') {
		  if (opt.hnbond = opt.hnbond ^ 1) {
		    properties++;
		  }
		  else {
		    properties--;
		  }
		}
		else if (instring[1] == '2') {
		  if (opt.deuteration = opt.deuteration ^ 1) {
		    ;
		  }
		  
		}
		else {
		  if (opt.phipsi = opt.phipsi ^ 1) {
		    properties++;
		  }
		  else {
		    properties--;
		  }
		}
		break;

	      case '2':
		if (opt.es = opt.es ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;

	      case '3':
		if (opt.sidechain = opt.sidechain ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;


	      case '4':
		if (opt.ss = opt.ss ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;

	      case '5':
		if (opt.hb = opt.hb ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;


	      case '6':
		if (opt.proline = opt.proline ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;


	      case '7':
		if (opt.nn = opt.nn ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;

	      case '8':
		if (opt.rc = opt.rc ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;


	      case '9':
		if (opt.optimize = opt.optimize ^ 1) {
		  properties++;
		}
		else {
		  properties--;
		}
		break;

	      }
	    }
	    else {
	      printf("Invalid choice.  Press RETURN to continue...");
	      fgets(instring,sizeof(instring), stdin);	
	      instring[strlen(instring)-1]='\0';
	    }
	    break;

	  case INFILE:
	    printf("Enter input PDB file name (RETURN to cancel): \n>>");
	    fgets(instring,sizeof(instring), stdin);	
	    instring[strlen(instring)-1]='\0';
	    if (strlen(instring) == 0) {
	      state = MAIN;
	      break;
	    }

	    strcpy(infile,instring);
	    if (in != NULL) {
	      fclose(in);
	      in = NULL;
	    }
	    in = fopen(infile,"rb");
	    if (in == NULL) {
	      file = nonestring;
	      printf("\nFile \"%s\" not found.\n\n"
		     "Press RETURN to continue...",instring);
	      fgets(instring,sizeof(instring), stdin);	
	      instring[strlen(instring)-1]='\0';
	    }
	    else {
	      /* SJN - check for multiple chains */
	      if (!CheckMultipleChains(in,0)) 
		{
		  fclose(in);
		}
	      else 
		{
		  file = strdup(instring);
		  state = OUTFILE;
		}
	    }
	    break;

	  case OUTFILE:
	    strcpy(instring,file);
	    pt = strtok(instring,".");
	    strcpy(infile,pt);  /* Use infile to hold suggested name */
	    strcat(infile,".out");
	    printf("Enter output file name (RETURN to use \"%s\"): \n>>",infile);
	    fgets(instring,sizeof(instring), stdin);	
	    instring[strlen(instring)-1]='\0';
	    if (strlen(instring) == 0) {
	      strcpy(outfile,infile);
	    }
	    else {
	      strcpy(outfile,instring);
	    }
	    out = fopen(outfile,"at");
        
	    if (out == NULL) {
	      printf("Unable to open \"%s\" for write.\n\n"
		     "Press RETURN to continue...",outfile);
	      fgets(instring,sizeof(instring), stdin);	
	      instring[strlen(instring)-1]='\0';
	    }
	    else {
	      fclose(out);
	      if (!strlen(instring)) {
		fileout = strdup(infile);
	      }
	      else {
		fileout = strdup(instring);
	      }
	      state = GO;
	    }
	    break;
	  }

	  if (state == GO) {
	    break;
	  }
	}
	strcpy(outfile,fileout);
	out=fopen(outfile,"wt");
	/* Run the program */
      }
    else {

      for( i=1; i<argc; i++ )
	{
	  if( *argv[i] == '-' )
	    {
	      argv[i]++;
	      if( !strcmp( argv[i], "help"  ) )  usage_exit(1);
	      if( !strcmp( argv[i], "torison" ) )
		{
		  mode = TORISON;
		  continue;
		}
	      if( !strcmp( argv[i], "IUPAC" ) )
		{
		  iupac = TRUE;
		  continue;
		}
	      if( !strcmp( argv[i], "nn" ) )
		{
		  mode = NN;
		  continue;
		}
	      if( !strcmp( argv[i], "cs" ) )
		{
		  mode = CS;
		  continue;
		}
	      if( !strcmp( argv[i], "radius" ) )
		{
		  i++;
		  if( sscanf( argv[i], "%f", &radius )!=1 )
		    {
		      fprintf( stderr, "A numerical value is expected immediately following"
			       " the -radius flag!\n\n" );
		      usage_exit(1);
		    }
		  continue;
		}
	      if( !strcmp( argv[i], "center" ) )
		{
		  i++;
		  if( sscanf( argv[i], "%s", center )!=1 )
		    {
		      fprintf( stderr, "An atom of interest must be specified immediately "
			       "after the -center flag!\n" );
		      usage_exit(1);
		    }
		  target_atom = resolve_atom( center );
		  continue;
		}
	      if( !strcmp( argv[i], "sort" ) )
		{
		  sort = TRUE;
		  continue;
		}
	      if( !strcmp( argv[i], "deuteration" ) )
		{
		  opt.deuteration = TRUE;
		  continue;
		}
	      /* Chemical Shift Prediction Options */

	      if( !strcmp( argv[i], "phipsi" ) )
		{
		  opt.phipsi = TRUE;
		  continue;
		}

	      if( !strcmp( argv[i], "rc" ) )
		{
		  opt.rc = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "ss" ) )
		{
		  opt.ss = TRUE;
		  properties++;
		  continue;
		}

	      if( !strcmp( argv[i], "neighbors" ) )
		{
		  opt.nn = TRUE;
		  properties++;
		  continue;
		}

	      if( !strcmp( argv[i], "optimize" ) )
		{
		  opt.optimize = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "hb" ) )
		{
		  opt.hb = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "proline" ) )
		{
		  opt.proline = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "es" ) )
		{
		  opt.es = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "sidechain" ) )
		{
		  opt.sidechain = TRUE;
		  properties++;
		  continue;
		}
	      if( !strcmp( argv[i], "HA" ) )
		{
		  opt.nucleus = N_HA;
		  nuclei++;
		  continue;
		}
	      if( !strcmp( argv[i], "HN" ) )
		{
		  opt.nucleus = N_HN;
		  nuclei++;
		  continue;
		}
	      if( !strcmp( argv[i], "N15" ) )
		{
		  opt.nucleus = N_N15;
		  nuclei++;
		  continue;
		}
	      if( !strcmp( argv[i], "CA" ) )
		{
		  opt.nucleus = N_CA;
		  nuclei++;
		  continue;
		}
	      if( !strcmp( argv[i], "CB" ) )
		{
		  opt.nucleus = N_CB;
		  nuclei++;
		  continue;
		}
	      if( !strcmp( argv[i], "CO" ) )
		{
		  opt.nucleus = N_CO;
		  nuclei++;
		  continue;
		}

	      

	      fprintf( stderr, "Unknown option - %s\n", argv[i] );
	      usage_exit(1);
	    }
	  else
	    {
	      file = strdup( argv[i] );
	      if( (in=fopen( file, "rb" ))==NULL )
		{
		  fprintf( stderr, "Cannot open file %s.\n", file );
		  exit(1);
		}
	    }
	}
      if( nuclei > 1 )
	{
	  fprintf( stderr, "More than one nucleus is selected for chemical shift predictions!\n" );
	  fprintf( stderr, "Please note that the -HA, -HN, -N15, -CA, -CB and -CO flags\n" );
	  fprintf( stderr, "are mutually exclusive.\n\n" );
	  exit(1);
	}
    }

    if( in == NULL ) {
      in = stdin;
    }

    /* Sort out the options first and then Read di-sulfide bonds from header */
#ifdef _DEBUG
    //	printf("Time: %d\n",time(NULL));
#endif
    if( mode == CS )
      {
	if( properties==0 && opt.phipsi==FALSE )
	  {
	    opt.phipsi    = TRUE;
	    opt.rc        = TRUE;
	    opt.ss        = TRUE;
	    opt.optimize  = TRUE;
	    opt.hb        = TRUE;
	    opt.proline   = TRUE;
	    opt.es        = TRUE;
	    opt.sidechain = TRUE;
	    opt.nn        = TRUE;
	    opt.chi       = TRUE;  /* SJN */
	    opt.hnbond    = TRUE;  /* SJN */
	    properties = 11;
	  }
	else
	  {
	    properties++;
	  }

	if( opt.ss == TRUE ) 
	  {
	    ReadSSPairs( in, &ssbonds,UseChain );
	  }

      }

    /* Initialize RESIDUE */

    memset( &Rz, 0,MAX_RES_NUM * sizeof(RESIDUE) );
    for (i=0; i < MAX_RES_NUM; i++)
      {
	for (j=0; j < NUM_COORDS; j++) 
	  {
	    Rz[i].coords[j].x = NA;
	    Rz[i].coords[j].y = NA;
	    Rz[i].coords[j].z = NA;
	  }
	for (k=0; k < MAX_HBONDS; k++) 
	  {
	    Rz[i].hbonds[k].partner = NA;
	    Rz[i].sidebond[k].partner = NA;
	  }
      }
	
    /*
      R.lastc.x = 0.0;
      R.lastc.y = 0.0;
      R.lastc.z = 0.0;
    */

    /* Print header for torison angles */
  
    if( mode == TORISON )
      {
	if( iupac == TRUE )
	  {
	    fprintf( out, "%-3s %3s %6s %12s %13s %12s\n",
		     "NUM", "RES", "PHI", "PSI", "OMEGA", "CHI1" );
	    fprintf( out, "%-3s %3s %11s %12s %12s %12s\n", "---", "---", 
		     "---------", "---------", "---------", "---------" );
	  }
	else
	  {
	    fprintf( out, "%-5s %4s %9s %12s %13s %12s\n",
		     "NUM", "RES", "PHI", "PSI", "OMEGA", "CHI1" );
	    fprintf( out, "%-5s %4s %12s %12s %12s %12s\n", "----", "---", 
		     "---------", "---------", "---------", "---------" );
	  }
      }
  
    /* Initialize pointers to various phi-psi matrices and their second */
    /* derivatives for CS prediction                                    */
  
    if( mode == CS )
      {
	mat  = PhiPsiContours();
	mat2 = SecondDerivatives( mat );
      }

    rno = ReadPDB(in,Rz,&water);


    for (i=0; i <= rno; i++)   // SJN added = 
      {
	if (i > 0) 
	  {
	    if (Rz[i-1].num == Rz[i].num - 1) 
	      {
		atm_vector(&Rz[i-1],"C",&(Rz[i].lastc));
		atm_vector(&Rz[i-1],"CA",&(Rz[i].lastca));
	      }																	
	    else 
	      {

		Rz[i].errflags |= RES_ERR_MISSING_RES;
	      }
	  }
	torison_angles(&Rz[i]);
      }

    for (i = 0; i <= rno; i++)
      {
	add_hydrogens(&Rz[i],&seed);
		

      }
	      

    

    for (i = 0; i <= rno; i++)
      {
	if (!strcmp(Rz[i].type,"CYS"))
	  {
	    for (sspt = ssbonds; sspt != NULL; sspt = sspt->next)
	      {
		if (sspt->resA == Rz[i].numLabel && sspt->insCodeA == Rz[i].insCode)
		  {
		    Rz[i].ssPartner = sspt->resB;
		    Rz[i].ssPartnerInsCode = sspt->insCodeB;
		  }
		else if (sspt->resB == Rz[i].numLabel && sspt->insCodeB == Rz[i].insCode)
		  {
		    Rz[i].ssPartner = sspt->resA;
		    Rz[i].ssPartnerInsCode = sspt->insCodeA;
		  }
	      }
	  }
      }



    do_ss(Rz,rno); /* SJN - calculate secondary structure */

    errset = 0;

    for (i=0; i <= rno; i++)
      {

	switch(mode)
	  {
	  case CS:					// torison_angles( &Rz[i] );
	    if( Rz[i].phi == NA )
	      {
		Rz[i].phi = 360.0;  /* SJN - used to be 0.0 for some reason */
	      }
											
	    if (Rz[i].psi == NA )
	      {											
		Rz[i].psi = 360.0;
	      }
	    if( opt.sidechain==TRUE )
	      {
		SideChainOrientation( &Rz[i], &sidechain );
	      }
                    
	    /* Phi-Psi dependency */
                    
	    phipsi = PhiPsiMatrices( &Rz[i], mat, mat2, phipsi, last_psi );
	    ProcessCShifts(phipsi);
	    /* Hydrogens are needed for further computations */

	    // add_hydrogens( &Rz[i], &seed ); moved up a little
                    
	    /* Ring-current effects */
                    
	    if( opt.rc==TRUE )
	      {
		aromatic_ring( &Rz[i], &ring );
		RingShiftedAtoms( &Rz[i], &rc_atom );
	      }

	    /* Chi angle effects on N15 */
	    /* SJN Jul 2000
	       if (opt.chi == TRUE) {
	       ChiFactor(Rz[i],phipsi);
	       }
	    */
	    /* Hydrogen bonding effects on H15 */

	    /* SJN Jul 2000
	       if (opt.hnbond == TRUE) {
	       HNFactor(Rz[i],phipsi);
	       }
	    */											
	    /* Store atomic position for electrostatic calculation */
                    
	    if( opt.es==TRUE ) {
	      protein = AddResidue( &Rz[i], protein, NULL );
	    }
                    
	    /* Extract coordinates for di-sulfide bonds */
                    
	    if( opt.ss==TRUE && !strcmp( Rz[i].type, "CYS" ) )
	      {
		ReadSSCoordinates( &Rz[i], ssbonds );
	      }
                    
	    /* Keep track of proline's positions */
                    
	    if( opt.proline==TRUE && !strcmp( Rz[i].type, "PRO" ) )
	      {
		proline = CreatePRO( &Rz[i], proline);
	      }
                    
	    /* Extract donors and receptors for hydrogen-bond */
	    /* calculation.                                   */
                    
	    if( opt.hb == TRUE )
	      {
		Donor( &Rz[i], &donor );
		Receptor( &Rz[i], &receptor );
	      }
                    
	    last_psi = Rz[i].psi;
	    break;

	  case TORISON: torison_angles( &Rz[i] );
	    if( Rz[i].phi == NA   )  Rz[i].phi=360.0;
	    if( Rz[i].psi == NA   )  Rz[i].psi=360.0;
	    if( Rz[i].chi == NA   )  Rz[i].chi=360.0;
	    if( Rz[i].theta == NA )  Rz[i].theta=360.0;
	    if( Rz[i].omega == NA )  Rz[i].omega=360.0;
	    else
	      {
		fprintf( out, "%-5d %4s %12.4f %12.4f %12.4f %12.4f\n",
			 last_num, last_res_label, last_phi,
			 last_psi, Rz[i].omega, last_chi );
	      }
	    strcpy( last_res_label, res_label );
	    last_phi = Rz[i].phi;
	    last_psi = Rz[i].psi;
	    last_chi = Rz[i].chi;
	    last_num = Rz[i].num;
	    break;

	  case NN:      protein = AddResidue( &Rz[i], protein, &target_atom );
	    break;
                    
	  default:      fprintf( stderr, "Unknown mode of operation...\n" );
	    exit(1);
	  }
      }

    /* Clean up */

    FreePhiPsiMatrices( mat2 );
    mat2 = NULL;
    if( mat != NULL )
      {
	free( (char *) ++(mat->ca) );
	free( (char *) ++(mat->ca_dev) );
	free( (char *) ++(mat->cb) );
	free( (char *) ++(mat->co) );
	free( (char *) ++(mat->ha) );
	free( (char *) ++(mat->ha_dev) );
	free( (char *) ++(mat->hn) );
	free( (char *) ++(mat->hn_dev) );
	free( (char *) ++(mat->n15) );
	free( (char *) mat );
	mat = NULL;
      }

    if( file != NULL )
      {
	fclose(in);
	free( file );
      }
    /* Post Processing */
  
    switch(mode)
      {
      case CS:						if( opt.rc == TRUE )
	{
	  ring_current = RingCurrent( ring, rc_atom );
	  FreeRings( ring );
	  ring = NULL;
	  FreeRES( rc_atom );
	  rc_atom = NULL;
	}
                    
	if( opt.es == TRUE )
	  {
	    es = Electrostatics( protein );
	    FreeRES( protein );
	    protein = NULL;
	  }
	/* SJN Jul 2000
	   if( opt.ss == TRUE )
	   {
	   /*												ss = DiSulfideBonds( ssbonds ); */
	/*												FreeSSBond( ssbonds );
													ssbonds = NULL;
													}
	*/                    
	if( opt.hb == TRUE )
	  {
	    AddToReceptor( &receptor, water );
	    FreeWaterOxy( water );
	    water = NULL;
                    
	    hbond = HydrogenBonds( donor, receptor );
	    FreeRES( donor );
	    FreeRES( receptor );
	    donor = NULL;
	    receptor = NULL;

	    hb = HBondShifts( &hbond,Rz,rno );
	    //												hb = HBondShifts2(&hbond,Rz,rno);  // SJN
	  }

	if( opt.nucleus != -1 )
	  {
	    display_data = CreateDisplayData( rno+1, properties, opt.nucleus );
	    InitializeDisplayData( display_data, phipsi, "PHIPSI" );
	  }

	if( opt.rc == TRUE )
	  {
#ifdef DUMPSHIFTS
	    //DumpHShifts(phipsi,out);
	    //DumpHShifts(ring_current,out);
#endif
	    ProcessCShifts(ring_current);
	    AddCShifts( phipsi, ring_current );
	    if( opt.nucleus != -1 )
	      {
		FillDisplayData( display_data, ring_current, "RC", 1 );
	      }
	    FreeCShifts( ring_current );
	    ring_current = NULL;
	  }

	if( opt.es == TRUE )
	  {
#ifdef DUMPSHIFTS
	    //DumpHShifts(es,out); // SJN DEBUG
#endif
	    ProcessCShifts(es);
	    AddCShifts( phipsi, es );
	    if( opt.nucleus != -1 )
	      {
		FillDisplayData( display_data, es, "ES", 1 );
	      }
	    FreeCShifts( es );
	    es = NULL;
	  }
                    
	if( opt.hb == TRUE )
	  {
#ifdef DUMPSHIFTS
	    //DumpHShifts(hb,out); // SJN DEBUG
#endif
	    ProcessCShifts(hb);
	    AddCShiftsHB( phipsi, hb );
	    if( opt.nucleus==N_HN || opt.nucleus==N_HA || opt.nucleus==N_N15 )
	      {
		FillDisplayDataHB( display_data, hb );
	      }
	    FreeCShifts( hb );
	    hb = NULL;
	  }
	/* SJN Jul 2000                  
	   if( opt.proline == TRUE )
	   {
	   ProlineEffect( phipsi, proline );
	   if( opt.nucleus == N_CA )
	   {
	   FillDisplayDataPRO( display_data, proline );
	   }
	   FreeRES( proline );
	   proline = NULL;
	   }
	*/                     
	if( opt.sidechain == TRUE )
	  {
	    ProcessCShifts(sidechain);
	    AddCShifts( phipsi, sidechain );
	    if( opt.nucleus == N_CA )
	      {
		FillDisplayData( display_data, sidechain, "S.CHN", 1 );
	      }
	    FreeCShifts( sidechain );
	    sidechain = NULL;
	  }

	/* These should probably be the last step before mapping */
	/* SJN Jul 2000                  
	   if( opt.ss == TRUE )
	   {
	   if( opt.nucleus == N_CA )
	   {
	   FillDisplayDataCYS( display_data, phipsi, ss );
	   }
	   AdjustCYS( phipsi, ss );
	   FreeCShifts( ss );
	   ss = NULL;
	   }
	*/                    
	/* Contribution from previous residue (affects N15 only) */
	/* SJN Jul 2000                   
	   if( opt.nn == TRUE )
	   {
	   NearestNeighborEffect( phipsi );
	   if( opt.nucleus == N_N15 )
	   {
	   FillDisplayDataNN( display_data );
	   }
	   }
	*/                   
	/* Optimization step based on a nuclear-specific linear transformation */
 
	if (opt.optimize == TRUE)
	  {
	    oldphipsi = CopyCS(phipsi);
	    Optimize2(Rz,phipsi,rno );

	    if (opt.nucleus != -1)
	      {
		FillDisplayDataOPT( display_data, phipsi,oldphipsi );
	      }
	    FreeCShifts(oldphipsi);
	  }
	
	if(opt.deuteration == TRUE)
	  AdjustDeuteration(phipsi);
	
	/* Display Results */
                    
	if( opt.nucleus == -1 )
	  {
	   /* GV 11 September 2007: adjusted from original */
	   
		fprintf(out,"# Entries marked with a * may have inaccurate shift predictions.\n");
		fprintf(out,"# Entries marked with a value -666 should be igonored\n");
		fprintf(out,"# Output format adjusted by GV 11 September 2007\n");

	    q = phipsi;
	    while( q->next != NULL ) {q = q->next;}
	    
	    while( q!=NULL )
	    {  										
		  q->ca  = outOfBounds(q->type,"CA",q->ca);
		  q->cb  = outOfBounds(q->type,"CB",q->cb);
		  q->ha  = outOfBounds(q->type,"HA",q->ha);
		  q->co  = outOfBounds(q->type,"CO",q->co);
		  q->hn  = outOfBounds(q->type,"H",q->hn);
		  q->n15 = outOfBounds(q->type,"N",q->n15);

	
		  { int j;
		    for (j = 2; j < NHATOMS; j++)
		      {q->hside[j] = outOfBounds(q->type,hatoms[j].name,q->hside[j]);
		      }
		  }

		  if (FindResidue(q->n)->errflags) {errset = 1;}
		
		  for (i=0; i <= rno; i++) // SJN added = 
		      {if (Rz[i].num == q->n)
		          {break;}
		      }
		  sprintf(label,"%c%d%c",Rz[i].errflags ? '*' : ' ',Rz[i].numLabel, Rz[i].insCode);

		  if (q->n15 != 0.0) {fprintf( out, " %-5s %2c  N    %10.4f\n", label, q->type, q->n15);}
		  if (q->ca  != 0.0) {fprintf( out, " %-5s %2c  CA   %10.4f\n", label, q->type, q->ca);}
		  if (q->cb  != 0.0) {fprintf( out, " %-5s %2c  CB   %10.4f\n", label, q->type, q->cb);}
		  if (q->co  != 0.0) {fprintf( out, " %-5s %2c  C    %10.4f\n", label, q->type, q->co);}
		  
		  /* protons */
		q->hside[0]=q->hn;
		if (q->type != 'G') {q->hside[1]=q->ha;}
		
		/* GV: no averaging
		if(q->hside[5]!=0 && q->hside[6]!=0 &&q->hside[7]!=0)
		  {       q->hside[4]=(q->hside[5]+q->hside[6]+q->hside[7])/3;
		  q->hside[5]=q->hside[6]=q->hside[7]=0;
		  }
		if(q->hside[9]!=0 && q->hside[10]!=0 &&q->hside[11]!=0)
		  {       q->hside[8]=(q->hside[9]+q->hside[10]+q->hside[11])/3;
		  q->hside[9]=q->hside[10]=q->hside[11]=0;
		  }
		if(q->hside[13]!=0 && q->hside[14]!=0 &&q->hside[15]!=0)
		  {       q->hside[12]=(q->hside[13]+q->hside[14]+q->hside[15])/3;
		  q->hside[13]=q->hside[14]=q->hside[15]=0;
		  }
		if(q->hside[9]!=0 && q->hside[10]!=0 &&q->hside[11]!=0)
		  {       q->hside[8]=(q->hside[9]+q->hside[10]+q->hside[11])/3;
		  q->hside[9]=q->hside[10]=q->hside[11]=0;
		  }
		if(q->type=='M')
		  {       q->hside[17]=q->hside[22];
		  q->hside[18]=q->hside[19]=q->hside[22]=0;
		  }
		if(q->type == 'K')
		  {       q->hside[39]=q->hside[40];
		  q->hside[40]=q->hside[41]=q->hside[42]=0;
		  }
		if(q->hside[29]!=0 && q->hside[30]!=0 &&q->hside[31]!=0)
		  {      q->hside[28]=(q->hside[29]+q->hside[30]+q->hside[31])/3;
		  q->hside[29]=q->hside[30]=q->hside[31]=0;
		  }
		if(q->hside[25]!=0 && q->hside[26]!=0 &&q->hside[27]!=0)
		  {       q->hside[24]=(q->hside[25]+q->hside[26]+q->hside[27])/3;
		  q->hside[25]=q->hside[26]=q->hside[27]=0;
		  }
		  */

          for (i=0; i< NHATOMS; i++) {
            if (q->hside[i] != 0.0)
                {fprintf(out, " %-5s %2c  %-4s %10.4f\n", label, q->type, hatoms[i].name, q->hside[i]);}
          }
          		  		
		  q = q->last;
	    }

	    FreeCShifts( phipsi );
	    phipsi = NULL;
	  }
	else
	  {
	    FillDisplayData( display_data, phipsi, "ALL", 0 );
	    FreeCShifts( phipsi );
	    phipsi = NULL;
	    display_selected_nucleus( display_data);
	    FreeDisplayData( display_data );
	    display_data = NULL;
	  }
	break;

      case TORISON:   fprintf( out, "%-5d %4s %12.4f %12.4f %12.4f %12.4f\n", 
			       last_num, last_res_label, last_phi, 360.0, 360.0, 
			       last_chi );
	break;

      case NN:        if( target_atom.p.x == 0.0 && target_atom.p.y == 0.0 &&
			  target_atom.p.z == 0.0 )
	{
	  fprintf( stderr, "Center atom not found in PDB file!\n" );
	  fprintf( stderr, "Aborting...\n" );
	  exit(1);
	}
	neighbor = search_neighbors( protein, target_atom, radius );
	display_neighbors( neighbor, sort );
	protein  = NULL;
	neighbor = NULL;
	break;
      }
    if (argc != 1) {
      fclose(out);
      break;
    }
    else {
      fclose(out);
      state = MAIN;
    }
  }
  return(0);
}



int ChiFactor(RESIDUE r,CSHIFT *c)
{
  float chi;
  int idx;

  if (r.chi < 0.0) 
    {
      chi = r.chi + 360.0;
    }
  else
    {
      chi = r.chi;
    }
  if (chi <= 120)
    {
      idx = 0;
    }
  else if (chi <= 240)
    {
      idx = 1;
    }
  else if (chi < 360)
    {
      idx = 2;
    }
  else
    {
      idx = 3;
    }

  switch (r.consens[0]) 
    {
    case 'C':  /* Coil */
      c->n15 -= N15chiC[idx][rc_idx(c->type)];
      break;
    case 'H':  /* Helix */
      c->n15 -= N15chiH[idx][rc_idx(c->type)];
      break;
    case 'S':  /* Sheet */
      c->n15 -= N15chiS[idx][rc_idx(c->type)];
      break;
    }
  return(1);
}

int HNFactor(RESIDUE r,CSHIFT *c)
{
  double resfactor[20] = {1.5, -0.2, 1.4, 1.2, 0.3, 1.6, 0.9, 0.9, 0.9, 1.1,
			  2.3, -0.1, 0  , 1  , 2  , 2.8, 1.6, 2.1, 0.2, 2.1};

  c->n15 += resfactor[rc_idx(c->type)] * (c->hn-8.3);
  return(1);
}

/* cmdline should be true when we're running from the command line and just want to use the */
/* first chain found */
int CheckMultipleChains(FILE *ff,int cmdline)
{
#define MAXCHAINS 20
  char inn[1000],x1[20],x2[20],x3[20],x4[20],x5[20],x6[20],x7[20],chainlabel[MAXCHAINS],label;
  long atoms=0L,rez[MAXCHAINS],rezlow[MAXCHAINS],resno;
  int chains=0,i;

  UseChain = 0;
  for (i=0; i < MAXCHAINS; i++)
    {
      rez[i] = 0;
      rezlow[i] = 0x0FFFFFFF;
    }
  fgets(inn,sizeof(inn),ff);
  while (!feof(ff)) 
    {
      if (!strncmp(inn,"ATOM  ",6))
	{
	  /* According to offical PDB format, column 22 is the chain identifier */
	  if (isalpha(inn[21]))
	    {
	      sscanf(inn,"%6[a-zA-Z ]%5[0-9 ]%*c%4[0-9a-zA-Z* ]%1c%3s%*c%1c%4[0-9 ]",x1,x2,x3,x4,x5,x6,x7);
	      resno = atoi(x7);
	      label = inn[21];

	      for (i=0; i < chains; i++)
		{
		  if (chainlabel[i] == label) 
		    {
		      rez[i] = max(rez[i],resno);
		      rezlow[i] = min(rezlow[i],resno);
		      break;
		    }
		}

	      if (i == chains) 
		{
		  chainlabel[chains++] = label;
		  rez[chains - 1] = resno;
		  rezlow[chains - 1] = resno;
		}
	      if (chains == 20) 
		{
		  fprintf(stderr,"This file contains more than %d chains.  Please edit it to eliminate\n"
			  "some of the chains and try again.\n",MAXCHAINS);
		  return(0);
		}
	    }
	  else
	    {
	      rewind(ff);
	      return(1);
	    }
	}
      fgets(inn,sizeof(inn),ff);
    }
  rewind(ff);

  i = -1;
  if (chains > 1) 
    {
      if (cmdline)
	{
	  UseChain = chainlabel[0];
	  return(1);
	}

      while (i < 0) 
	{
	  fprintf(stderr,"This file contains multiple chains.  Please choose one from the following list:\n\n");
	  for (i=0; i < chains; i++)
	    {
	      fprintf(stderr,"%d) Chain %c (%d residues)\n",i+1,chainlabel[i],rez[i] - rezlow[i] + 1);
	    }
	  fprintf(stderr,"X) Exit without processing this file.\n\n");
	  fprintf(stderr,"Enter your choice below: \n>>");
	  fgets(inn,sizeof(inn),stdin);
	  if (tolower(inn[0]) == 'x') 
	    {
	      return(0);
	    }
	  i = atoi(inn);
	  if (i < 1 || i > chains) 
	    {
	      i = -1;
	      continue;
	    }
	}
      UseChain = chainlabel[i-1];
    }
  return(1);
}


int ReadPDB(FILE *in,RESIDUE rez[],HETATM **h)
{
  char inn[1000],iupacCode,insCode;
  int args,rs=-1,i, j;
  char atom[15], res[15],resndx[5],label[2],sublabel,atom2[15],*pt; 
  int atom_num, res_num,idx,num = -1;
  float x, y, z, a, b;
  ATOM *q;
  int ignore = 0;  // Flag: the PDB has more than one structure, ignore all but the first
  int xplorIndex, bmrbIndex, hIndex;

  for (i = 0; i < NTRATOMS; i++)		// Set up cross-indexes between the atom name table (tratoms) 
    {									// and the hydrogen atom index (hatoms)
      if (tratoms[i].bmrb[0] == 'H')
	{
	  for (j = 0; j < NHATOMS; j++)
	    {
	      if (!strcmp(tratoms[i].bmrb,hatoms[j].name))
		{
		  tratoms[i].hatomsIndex = j;
		  break;
		}
	    }
	}
    }

  fgets(inn,sizeof(inn),in);
  while (!feof(in)) 
    {
      if (!strncmp(inn,"HETATM",6))
	{
	  if (UseChain == 0 || (inn[21] == UseChain || inn[21] == ' '))
	    {
	      *h = AddWaterOxy(inn,*h);
	    }
	}
      else if (!strncmp(inn,"ATOM",4) && !ignore) 
	{
	  args = sscanf(inn + 6,"%5d%*c%4[A-Za-z0-9* ]%*c%3s%*c%c%4d%c%8f%8f%8f%6f%6f",
			&atom_num, atom2, res,&label,&res_num, &insCode,&x, &y, &z, &a, &b);

	  /*
	    args = sscanf( inn+6, "%5d%6[A-Z 0-9]%3s%4d %f %f %f %f %f",
	    &atom_num, atom2, res,&res_num, &x, &y, &z, &a, &b );
	    /*    ATOM atom_num atom residue res_num x y z junk junk */
	  /* ie ATOM 1 N SER 145 1.00 1.00 1.00 etc */
	  /*
	    if (args != 9) {
	    args=-sscanf( inn+6, "%5d%6[A-Z 0-9]%3s%2s%4s %f %f %f %f %f", 
	    &atom_num, atom2, res, label,resndx, &x, &y, &z, &a, &b );
	  */
	  /*    ATOM atom_num atom residue chain res_num x y z junk junk */
	  /* ie ATOM 1 N SER A 145 1.00 1.00 1.00 etc */
	  /*
	    }
	  */
	  //if (args != 9 && args != -10) 
	  if (args != 11)
	    {
	      fprintf( stderr, "File format error...\n" );				
	      fprintf( stderr, "%s\n", inn );
	      exit(1);
	    }

	  if (UseChain != 0 && label[0] != UseChain)
	    {
	      fgets(inn,sizeof(inn),in);
	      continue;
	    }

	  /*
	    if (insCode != ' ')
	    {
	    fgets(inn,sizeof(inn),in);
	    continue;
	    }
	  */
	  /*
	    if (args == -10) 
	    {
	    sublabel = resndx[strlen(resndx)-1];
	    if (!isdigit(sublabel))
	    {
	    fgets(inn,sizeof(inn),in);
	    continue;
	    }
	    res_num = atoi(resndx);  
			
	    if (UseChain != 0 && label[0] != UseChain) 
	    {
	    fgets(inn,sizeof(inn),in);
	    continue;
	    }
	  */
		
	  /*
	    if (strlen(res) > 3) 
	    {
	    memmove(&res[0],&res[strlen(res)-3],4);
	    }
	  */
	  if (iupac_code_safe(res) == 'X')   // skip over weird residues
	    {
	      fgets(inn,sizeof(inn),in);
	      continue;
	    }

	  if (rs == -1 || rez[rs].numLabel != res_num || rez[rs].insCode != insCode)
	    {
	      if (rs != -1 && res_num < rez[rs].numLabel)  // likely indicating that there's more than one structure here
		{
#ifdef _DEBUG
		  printf("Ha!\n");
#endif
		  ignore = 1;
		  fgets(inn,sizeof(inn),in);
		  continue;
		}
	      else if (rs != -1 && res_num > rez[rs].numLabel + 1)  // Deal with gaps in the PDB data
		{
		  num += (res_num - rez[rs].num - 1);
		}
	      rs++;
	      num++;
	      rez[rs].numLabel = res_num;
	      rez[rs].insCode = insCode;
	      rez[rs].num = num;
	      strcpy( rez[rs].type, res );
	    }
	  else if (strcmp(rez[rs].type, res ))
	    {
	      fprintf( stderr, "Unexpected change in residue type!\n" );
	      fprintf( stderr, "%s\n", inn );
	      fprintf( stderr, "Aborting...\n" );
	      exit(1);
	    }


	  atom[0] = '\0';
	  
	  //SJN original code 	
	  //pt = strtok(atom2," ");
	  //strcat(atom,pt);
	  
	  
	  // Haiyan modified to not read in the Hydrogen coordinates  all Hydrogen 
	    // coordinated treat as atom 'H', Later filter the atom H at line 2001, May 2004
	     
	  if(atom2[1]!='H'){
	     pt = strtok(atom2," ");
	     strcat(atom,pt);
	  }else{
	    
	    
	    pt = strtok(atom2," ");
	    if(!strcmp(pt,"H")){
	      strcat(atom,"HN");
	      
	    }
	    else
	      strcat(atom,"H");	
	  }
	  
	     // Haiyan modified  May 2004		
	  
	  iupacCode = iupac_code(res);
	  xplorIndex = -1;
	  bmrbIndex = -1;
	  hIndex = -1;

	  for (i = 0; i < NTRATOMS; i++)
	    {
	      if (tratoms[i].iupacCode == iupacCode)
		{
		  if (!strcmp(atom,tratoms[i].pdb))
		    {
		      hIndex = tratoms[i].hatomsIndex;
		      break;
		    }
		  else if (!strcmp(atom,tratoms[i].xplor))
		    {
		      xplorIndex = i;
		    }
		  else if (!strcmp(atom,tratoms[i].bmrb))
		    {
		      bmrbIndex = i;
		    }
		}
				
	    }


	  if (i == NTRATOMS)
	    {
	      if (xplorIndex != -1)
		{
		  strcpy(atom,tratoms[xplorIndex].pdb);
		  hIndex = tratoms[xplorIndex].hatomsIndex;
		}
	      else if (bmrbIndex != -1)
		{
		  strcpy(atom,tratoms[bmrbIndex].pdb);
		  hIndex = tratoms[bmrbIndex].hatomsIndex;
		}
	    }

	  /*
	    while (pt != NULL) {
	    strcat(atom,pt);
	    pt = strtok(NULL," ");
	    if (pt != NULL) {

	    strcat(atom," ");
	    }
	    }
	  */
	  if (!strcmp(atom,"CA")) /* Separate record of backbone coords, for convenience */
	    { 
	      rez[rs].x = x;
	      rez[rs].y = y;
	      rez[rs].z = z;
	    }

	  idx = -1;
	  if (!strcmp(atom, "H") || !strcmp(atom, "HN"))
	    {
	      idx = H_COORD;
	    }
	  else if (0 == strcmp(atom, "N"))
	    {
	      idx = N_COORD;
	      if (rs != 0)
		{
		  rez[rs-1].nextn.x = x;
		  rez[rs-1].nextn.y = y;
		  rez[rs-1].nextn.z = z;
		}
	    }
	  else if (0 == strcmp(atom, "C"))
	    idx = C_COORD;
	  else if (0 == strcmp(atom, "O"))
	    idx = O_COORD;
	  else if (0 == strcmp(atom, "NH1"))
	    idx = NH1_COORD;
	  else if (0 == strcmp(atom, "NH2"))
	    idx = NH2_COORD;
	  else if (0 == strcmp(atom, "NZ"))
	    idx = NZ_COORD;
	  else if (0 == strcmp(atom, "NE"))
	    idx = NE_COORD;
	  else if (0 == strcmp(atom, "NE1"))
	    idx = NE1_COORD;
	  else if (0 == strcmp(atom, "NE2"))
	    idx = NE2_COORD;
	  else if (0 == strcmp(atom, "ND1"))
	    idx = ND1_COORD;
	  else if (0 == strcmp(atom, "ND2"))
	    idx = ND2_COORD;
	  else if (0 == strcmp(atom, "OD1"))
	    idx = OD1_COORD;
	  else if (0 == strcmp(atom, "OD2"))
	    idx = OD2_COORD;
	  else if (0 == strcmp(atom, "OE1"))
	    idx = OE1_COORD;
	  else if (0 == strcmp(atom, "OE2"))
	    idx = OE2_COORD;
	  else if (0 == strcmp(atom, "OG"))
	    idx = OG_COORD;
	  else if (0 == strcmp(atom, "OG1"))
	    idx = OG1_COORD;
	  else if (0 == strcmp(atom, "OH"))
	    idx = OH_COORD;
	  else if (0 == strcmp(atom, "CG"))
	    idx = CG_COORD;
	  else if (0 == strcmp(atom, "CD"))
	    idx = CD_COORD;
	  else if (0 == strcmp(atom, "SG"))
	    idx = SG_COORD;
	  else if (0 == strcmp(atom, "CZ"))
	    idx = CZ_COORD;
	  else if (0 == strcmp(atom, "CE"))
	    idx = CE_COORD;
	  else if (0 == strcmp(atom, "CB"))
	    idx = CB_COORD;
			
	  if (idx != -1) {
	    rez[rs].coords[idx].x = x;
	    rez[rs].coords[idx].y = y;
	    rez[rs].coords[idx].z = z;
	  }

	  if ((q=FindAtom(rez[rs].atom,atom)) == NULL)
	    {
	      if(atom[0]!='H'){// add by Haiyan May 2004 to filtered the hydrogen atoms	
		CreateAtom(&rez[rs] );
		strcpy(rez[rs].atom->type, atom );
		rez[rs].atom->p.x = x;
		rez[rs].atom->p.y = y;
		rez[rs].atom->p.z = z;
		rez[rs].atom->occupancy = a;
		rez[rs].atom->BFactor = b;
		rez[rs].atom->hIndex = hIndex;
	      } // add by Haiyan May 2004
	    }

	}
      fgets(inn,sizeof(inn),in);
    }
  return(rs);
}


RESIDUE *FindResidue(int resno)
{
  int i;

  for (i = 0; i <= rno; i++)
    {
      if (Rz[i].num == resno)
	{
	  return(&Rz[i]);
	}
    }
  return(NULL);
}

int DumpHShifts(CSHIFT *p, FILE *out)
{
  CSHIFT *pp;
  int i, j, hit;

  for (i = 0; i <= rno; i++)
    {
      pp = p;
      hit = 0;

      while (pp != NULL)
	{
	  if (pp->n == Rz[i].num)
	    {
	      hit = 1;
	      //fprintf(stdout,"%f %f\n",pp->ha,pp->hside[1]);
				
	      for (j = 0; j < NHATOMS; j++)
		{
		  fprintf(out,"%f ",pp->hside[j]);
		}
	      fprintf(out,"\n");
				
	      break;
	    }
	  else 
	    {
	      pp = pp->next;
	    }
	}

      if (pp == NULL)
	{
	  //fprintf(stdout,"0.0 0.0");
			
	  for (j = 0; j < NHATOMS; j++)
	    {
	      fprintf(out,"0 ");
	    }
			
	  fprintf(out,"\n");
	  continue;
	}
    }
  fprintf(out,"\n");
}

char *shiftlimits[] =
  {
    "ALA     H        H        4338        3.97       11.58       8.20       0.60",
    "ALA     HA       H        3997        1.92        6.16       4.26       0.42",
    "ALA     HB       H        3691       -0.62        2.63       1.38       0.25",
    "ALA     C        C        1446      168.80      183.70     177.80       2.18",
    "ALA     CA       C        2502       43.00       63.50      53.16       2.06",
    "ALA     CB       C        2172        0.00       26.30      18.90       1.85",
    "ALA     N        N        2985       99.44      137.20     123.23       3.70",

    "ARG     H        H        2864        5.02       11.38       8.24       0.60",
    "ARG     HA       H        2609        2.12        5.94       4.27       0.44",
    "ARG     HB2      H        2287       -0.38        3.29       1.79       0.28",
    "ARG     HB3      H        2166        0.00        3.29       1.78       0.28",
    "ARG     HG2      H        1932       -0.64        3.12       1.58       0.27",
    "ARG     HG3      H        1815       -0.23        3.12       1.58       0.27",
    "ARG     HD2      H        1893        1.43        4.28       3.13       0.23",
    "ARG     HD3      H        1764        1.22        4.28       3.13       0.22",
    "ARG     HE       H        1090        3.25       11.82       7.32       0.52",
    "ARG     HH11     H        130         5.82        8.76       6.74       0.31",
    "ARG     HH12     H        116         5.82        8.76       6.75       0.32",
    "ARG     HH21     H        119         4.59        7.62       6.72       0.32",
    "ARG     HH22     H        112         4.59        7.62       6.72       0.33",
    "ARG     C        C        915       168.67      181.50     176.49       2.16",
    "ARG     CA       C        1589       46.10       65.13      56.95       2.41",
    "ARG     CB       C        1324       24.50       38.27      30.66       1.77",
    "ARG     CG       C        831        18.22       49.39      27.31       1.65",
    "ARG     CD       C        874        29.71       45.60      43.10       1.10",
    "ARG     CZ       C        44        157.52      160.60     159.01       0.87",
    "ARG     N        N        1815      103.60      137.60     120.61       3.90",
    "ARG     NE       N        342         7.28      128.90      89.80      12.83",
    "ARG     NH1      N        13         70.10      112.50      74.78      11.38",
    "ARG     NH2      N        13         70.10      111.90      75.84      11.44",

    "ASP     H        H        3351        6.12       11.54       8.33       0.57",
    "ASP     HA       H        3070        2.59        6.33       4.61       0.31",
    "ASP     HB2      H        2715        1.25        6.60       2.74       0.29",
    "ASP     HB3      H        2624        0.65        4.58       2.70       0.29",
    "ASP     C        C        1276      166.80      181.65     176.41       1.77",
    "ASP     CA       C        1991       39.80       60.37      54.52       2.10",
    "ASP     CB       C        1702       29.51       48.30      40.70       1.67",
    "ASP     CG       C        61        173.49      181.31     178.41       1.84",
    "ASP     N        N        2405      105.50      136.80     120.73       4.20",

    "ASN     H        H        2669        3.61       12.40       8.37       0.65",
    "ASN     HA       H        2427        2.92        6.32       4.70       0.39",
    "ASN     HB2      H        2188        0.10        4.47       2.80       0.34",
    "ASN     HB3      H        2133        0.26        4.47       2.78       0.34",
    "ASN     HD21     H        1502        3.33        9.30       7.27       0.52",
    "ASN     HD22     H        1497        3.14       10.33       7.20       0.52",
    "ASN     C        C        845       168.60      180.20     175.16       1.76",
    "ASN     CA       C        1453       43.30       62.30      53.43       1.94",
    "ASN     CB       C        1230       29.20       45.81      38.66       1.78",
    "ASN     CG       C        131       173.50      179.43     176.61       1.33",
    "ASN     N        N        1719      105.00      132.70     119.13       4.42",
    "ASN     ND2      N        804       104.00      124.77     112.83       2.60",

    "CYS     H        H        2001        5.05       10.74       8.42       0.66",
    "CYS     HA       H        1955        1.70        6.19       4.73       0.57",
    "CYS     HB2      H        1847        0.29        4.65       2.95       0.43",
    "CYS     HB3      H        1832       -0.28        4.65       2.98       0.45",
    "CYS     HG       H        3           1.38        2.22       1.66       0.48",
    "CYS     C        C        322       168.50      180.71     174.78       1.99",
    "CYS     CA       C        519        49.74       66.25      57.43       3.41",
    "CYS     CB       C        421        22.30       57.00      34.15       6.77",
    "CYS     N        N        676       106.60      135.89     119.95       4.79",

    "GLU     H        H        4117        4.98       11.72       8.34       0.61",
    "GLU     HA       H        3742        1.77        6.29       4.26       0.43",
    "GLU     HB2      H        3211        0.12        3.21       2.04       0.22",
    "GLU     HB3      H        3075        0.06        3.13       2.04       0.23",
    "GLU     HG2      H        2746        0.85        3.68       2.31       0.21",
    "GLU     HG3      H        2603        1.06        3.68       2.31       0.21",
    "GLU     C        C        1559      167.90      181.70     176.93       2.11",
    "GLU     CA       C        2532       46.80       66.60      57.42       2.19",
    "GLU     CB       C        2131       21.70       44.18      30.07       1.84",
    "GLU     CG       C        1498       25.10       51.92      36.01       1.51",
    "GLU     CD       C        61        177.76      184.74     181.94       1.85",
    "GLU     N        N        2994      109.80      137.30     120.68       3.68",

    "GLN     H        H        2388        5.93       11.94       8.22       0.62",
    "GLN     HA       H        2162        2.39        6.18       4.28       0.44",
    "GLN     HB2      H        1845       -0.22        4.00       2.05       0.28",
    "GLN     HB3      H        1777       -0.22        4.04       2.04       0.29",
    "GLN     HG2      H        1634        0.06        3.66       2.32       0.29",
    "GLN     HG3      H        1537        0.26        3.66       2.32       0.29",
    "GLN     HE21     H        1224        5.21        9.14       7.17       0.46",
    "GLN     HE22     H        1220        4.30        9.02       7.07       0.49",
    "GLN     C        C        807       170.37      182.22     176.39       1.96",
    "GLN     CA       C        1401       47.70       61.42      56.62       2.19",
    "GLN     CB       C        1177       21.70       41.54      29.10       1.97",
    "GLN     CG       C        815        26.10       39.44      33.72       1.10",
    "GLN     CD       C        97        172.80      181.25     179.68       1.17",
    "GLN     N        N        1656      105.10      136.00     119.92       4.01",
    "GLN     NE2      N        765        92.49      122.30     111.81       2.20",

    "GLY     H        H        4437        3.15       12.22       8.34       0.74",
    "GLY     HA2      H        3986        0.34        6.17       3.95       0.40",
    "GLY     HA3      H        3875        1.27        6.01       3.93       0.40",
    "GLY     C        C        1385      165.80      182.40     174.04       1.94",
    "GLY     CA       C        2464       35.50       56.69      45.33       1.42",
    "GLY     N        N        2903       88.30      135.66     109.91       4.29",

    "HIS     H        H        1179        4.60       10.80       8.25       0.74",
    "HIS     HA       H        1092        1.95        8.90       4.62       0.51",
    "HIS     HB2      H        977         0.37        8.70       3.12       0.43",
    "HIS     HB3      H        958         0.70        8.70       3.11       0.45",
    "HIS     HD1      H        86          6.29       17.20      10.14       3.50",
    "HIS     HD2      H        925         3.46        8.82       7.08       0.50",
    "HIS     HE1      H        913         3.21        9.60       8.08       0.57",
    "HIS     HE2      H        48          6.87       16.53      10.43       3.11",
    "HIS     C        C        331       167.60      179.90     175.19       2.14",
    "HIS     CA       C        665        45.80       65.40      56.37       2.40",
    "HIS     CB       C        567        23.70       40.86      29.95       2.15",
    "HIS     CG       C        39        122.67      136.80     130.59       3.41",
    "HIS     CD2      C        180       112.80      138.85     119.84       3.30",
    "HIS     CE1      C        133       115.52      140.50     136.05       3.58",
    "HIS     N        N        758       105.00      133.70     119.44       4.52",
    "HIS     ND1      N        30        106.60      248.00     190.74      22.84",
    "HIS     NE2      N        30        161.70      231.50     179.81      13.86",

    "ILE     H        H        2829        3.75       10.91       8.26       0.71",
    "ILE     HA       H        2630        1.03        6.30       4.20       0.56",
    "ILE     HB       H        2402       -0.57        2.79       1.80       0.31",
    "ILE     HG12     H        2014       -2.02        2.57       1.30       0.40",
    "ILE     HG13     H        1944       -2.04        2.88       1.24       0.40",
    "ILE     HG2      H        2210       -2.07        1.77       0.80       0.29",
    "ILE     HD1      H        2124       -1.06        1.94       0.70       0.30",
    "ILE     C        C        1025      167.50      182.70     175.82       1.95",
    "ILE     CA       C        1688       51.50       69.14      61.59       2.78",
    "ILE     CB       C        1455       20.94       44.58      38.58       2.09",
    "ILE     CG1      C        990         9.80       58.63      27.65       2.32",
    "ILE     CG2      C        1116        7.30       24.40      17.36       1.60",
    "ILE     CD1      C        1036        3.20       27.00      13.41       1.91",
    "ILE     N        N        1998       99.00      135.00     121.60       4.72",

    "LEU     H        H        4775        5.38       11.75       8.22       0.65",
    "LEU     HA       H        4361        2.31        6.15       4.32       0.47",
    "LEU     HB2      H        3763       -1.31        3.02       1.63       0.34",
    "LEU     HB3      H        3605       -1.21        3.11       1.57       0.36",
    "LEU     HG       H        3330       -1.06        3.90       1.54       0.33",
    "LEU     HD1      H        3608       -1.23        2.36       0.77       0.27",
    "LEU     HD2      H        3547       -1.45        2.78       0.76       0.28",
    "LEU     C        C        1692      168.90      189.78     176.97       2.09",
    "LEU     CA       C        2796       44.60       65.10      55.65       2.21",
    "LEU     CB       C        2373       32.60       53.70      42.37       1.86",
    "LEU     CG       C        1566       20.53       37.80      26.77       1.25",
    "LEU     CD1      C        1812       11.70       29.60      24.73       1.71",
    "LEU     CD2      C        1744       12.50       28.60      24.10       1.78",
    "LEU     N        N        3351      109.76      136.00     121.98       4.07",

    "LYS     H        H        4577        5.36       11.53       8.22       0.64",
    "LYS     HA       H        4120        0.68        7.96       4.28       0.45",
    "LYS     HB2      H        3560       -0.15        3.94       1.79       0.25",
    "LYS     HB3      H        3362       -0.37        3.94       1.78       0.26",
    "LYS     HG2      H        2844       -0.69        3.01       1.38       0.27",
    "LYS     HG3      H        2646       -0.77        2.99       1.37       0.29",
    "LYS     HD2      H        2437        0.32        3.61       1.61       0.25",
    "LYS     HD3      H        2254        0.28        3.61       1.61       0.25",
    "LYS     HE2      H        2395        1.25        4.32       2.93       0.20",
    "LYS     HE3      H        2190        1.49        4.32       2.93       0.20",
    "LYS     HZ       H        332         2.85        9.90       7.52       0.36",
    "LYS     C        C        1537      170.15      181.50     176.46       2.05",
    "LYS     CA       C        2556       46.10       62.71      56.84       2.25",
    "LYS     CB       C        2161       22.90       46.60      32.83       1.88",
    "LYS     CG       C        1312       17.30       31.28      24.91       1.31",
    "LYS     CD       C        1213       21.30       42.60      28.78       1.39",
    "LYS     CE       C        1197       34.20       56.00      41.78       0.98",
    "LYS     N        N        3085      105.45      136.10     121.16       4.11",
    "LYS     NZ       N        5          33.00      131.04      71.86      52.41",

    "MET     H        H        1127        5.80       10.36       8.26       0.60",
    "MET     HA       H        1088        2.80        6.22       4.39       0.46",
    "MET     HB2      H        894        -0.99        4.07       2.03       0.38",
    "MET     HB3      H        855        -0.97        3.15       2.01       0.36",
    "MET     HG2      H        763        -0.36        3.80       2.44       0.36",
    "MET     HG3      H        736         0.18        3.80       2.41       0.40",
    "MET     HE       H        573        -0.19        3.30       1.86       0.47",
    "MET     C        C        428       169.13      181.20     176.30       2.13",
    "MET     CA       C        746        47.70       62.24      56.16       2.34",
    "MET     CB       C        629        24.86       40.75      32.90       2.23",
    "MET     CG       C        397        20.83       37.31      32.07       1.45",
    "MET     CE       C        307         9.50       48.46      17.21       3.42",
    "MET     N        N        845       107.82      131.60     120.10       3.88",

    "PHE     H        H        2127        5.72       11.46       8.42       0.74",
    "PHE     HA       H        1969        2.72        6.56       4.62       0.58",
    "PHE     HB2      H        1772        0.43        4.32       2.99       0.37",
    "PHE     HB3      H        1726        0.59        3.99       2.97       0.38",
    "PHE     HD1      H        1774        2.02        7.94       6.91       0.82",
    "PHE     HD2      H        1575        2.02        8.08       6.89       0.86",
    "PHE     HE1      H        1663        2.95        8.80       6.95       0.82",
    "PHE     HE2      H        1504        2.95        8.80       6.94       0.86",
    "PHE     HZ       H        1322        3.04        9.50       6.92       0.80",
    "PHE     C        C        790       169.00      181.00     175.49       2.13",
    "PHE     CA       C        1260       48.30       67.10      58.25       2.73",
    "PHE     CB       C        1063       32.00       50.40      39.95       2.04",
    "PHE     CG       C        21        136.20      140.40     138.35       1.12",
    "PHE     CD1      C        407       118.50      134.00     131.38       1.38",
    "PHE     CD2      C        265       119.10      137.20     131.33       1.48",
    "PHE     CE1      C        345       117.50      133.30     130.48       1.29",
    "PHE     CE2      C        228       126.40      133.30     130.60       0.97",
    "PHE     CZ       C        273       118.70      138.60     129.11       1.68",
    "PHE     N        N        1503      104.78      134.60     120.69       4.18",

    "PRO     HA       H        2114        1.63        6.05       4.41       0.36",
    "PRO     HB2      H        1870       -0.78        3.98       2.05       0.39",
    "PRO     HB3      H        1813       -0.15        3.98       2.05       0.39",
    "PRO     HG2      H        1643       -0.93        4.92       1.93       0.36",
    "PRO     HG3      H        1540       -0.90        4.92       1.92       0.37",
    "PRO     HD2      H        1738        1.01        4.62       3.64       0.36",
    "PRO     HD3      H        1688        0.99        5.16       3.63       0.40",
    "PRO     C        C        708       170.95      182.30     176.70       1.69",
    "PRO     CA       C        1297       50.12       68.10      63.30       1.64",
    "PRO     CB       C        1083       26.32       56.76      31.81       1.54",
    "PRO     CG       C        681        19.31       33.39      27.14       1.18",
    "PRO     CD       C        742        40.44       56.00      50.28       1.04",
    "PRO     N        N        38        106.00      144.29     127.40      10.05",

    "SER     H        H        3661        2.96       11.68       8.29       0.62",
    "SER     HA       H        3342        1.43        6.37       4.51       0.43",
    "SER     HB2      H        2922        1.48        4.99       3.88       0.29",
    "SER     HB3      H        2775        1.51        4.96       3.87       0.31",
    "SER     HG       H        53          1.10        8.97       5.33       1.16",
    "SER     C        C        1229      166.90      181.40     174.53       1.73",
    "SER     CA       C        2080       48.90       66.91      58.57       2.12",
    "SER     CB       C        1718       55.50       70.80      63.80       1.57",
    "SER     N        N        2375      102.60      133.10     116.30       3.95",

    "THR     H        H        3358        5.93       11.01       8.27       0.62",
    "THR     HA       H        3050        0.87        6.35       4.48       0.50",
    "THR     HB       H        2704        0.92        5.90       4.17       0.37",
    "THR     HG1      H        140         0.32        8.21       4.40       1.92",
    "THR     HG2      H        2651       -0.83        4.35       1.16       0.28",
    "THR     C        C        1084      165.50      181.39     174.60       1.80",
    "THR     CA       C        1891       52.00       69.18      62.15       2.72",
    "THR     CB       C        1570       58.60       78.30      69.64       1.70",
    "THR     CG2      C        1083       13.20       38.90      21.44       1.39",
    "THR     N        N        2276       97.70      132.80     115.70       5.05",

    "TRP     H        H        730         5.73       10.76       8.35       0.84",
    "TRP     HA       H        652         2.28        6.75       4.74       0.55",
    "TRP     HB2      H        594         0.42        4.54       3.22       0.36",
    "TRP     HB3      H        575         1.02        4.49       3.18       0.36",
    "TRP     HD1      H        617         5.81        8.93       7.16       0.34",
    "TRP     HE1      H        596         6.79       11.90      10.13       0.53",
    "TRP     HE3      H        610         1.85        8.98       7.17       1.03",
    "TRP     HZ2      H        633         2.63        8.60       7.14       0.89",
    "TRP     HZ3      H        605         0.76        8.20       6.68       1.02",
    "TRP     HH2      H        610         2.84       10.17       6.82       0.94",
    "TRP     C        C        203       170.70      180.82     176.10       1.89",
    "TRP     CA       C        358        47.70       65.12      57.71       2.65",
    "TRP     CB       C        307        24.10       43.02      30.16       2.19",
    "TRP     CG       C        82        107.50      114.60     110.37       1.55",
    "TRP     CD1      C        147       119.50      129.80     126.16       1.76",
    "TRP     CD2      C        68        120.20      130.10     127.40       1.33",
    "TRP     CE2      C        52        118.37      139.20     137.38       2.86",
    "TRP     CE3      C        113       116.50      127.30     120.38       1.50",
    "TRP     CZ2      C        118       111.18      118.90     114.19       1.09",
    "TRP     CZ3      C        111       116.46      129.70     121.57       1.76",
    "TRP     CH2      C        115       119.60      128.73     123.75       1.34",
    "TRP     N        N        446       101.75      134.59     121.87       4.58",
    "TRP     NE1      N        247       106.75      136.30     129.48       2.56",

    "TYR     H        H        2003        5.64       11.92       8.37       0.75",
    "TYR     HA       H        1883        1.20        6.65       4.63       0.56",
    "TYR     HB2      H        1722        0.31        4.70       2.91       0.37",
    "TYR     HB3      H        1676        0.34        4.70       2.91       0.37",
    "TYR     HD1      H        1861        2.77        8.00       6.87       0.65",
    "TYR     HD2      H        1681        2.77        8.50       6.86       0.68",
    "TYR     HE1      H        1843        2.61        7.86       6.64       0.58",
    "TYR     HE2      H        1669        2.61        8.50       6.63       0.61",
    "TYR     HH       H        40          5.96       13.03       9.25       1.34",
    "TYR     C        C        562       169.20      180.34     175.39       1.89",
    "TYR     CA       C        1046       45.20       65.80      58.02       2.64",
    "TYR     CB       C        866        29.20       46.06      39.16       2.23",
    "TYR     CG       C        52        125.70      131.10     129.29       1.21",
    "TYR     CD1      C        397       122.10      136.70     132.54       1.35",
    "TYR     CD2      C        218       118.15      136.70     132.26       1.99",
    "TYR     CE1      C        401       110.70      133.31     117.81       2.09",
    "TYR     CE2      C        222       115.00      133.31     117.91       2.60",
    "TYR     CZ       C        50        153.54      162.70     156.37       2.50",
    "TYR     N        N        1216      104.60      134.53     120.79       4.69",

    "VAL     H        H        3757        3.98       11.03       8.29       0.71",
    "VAL     HA       H        3421        1.73        6.13       4.16       0.57",
    "VAL     HB       H        3094       -0.56        3.42       1.99       0.33",
    "VAL     HG1      H        2981       -1.09        2.31       0.84       0.27",
    "VAL     HG2      H        2884       -2.32        3.32       0.83       0.29",
    "VAL     C        C        1249      168.50      181.44     175.69       2.03",
    "VAL     CA       C        2180       51.10       69.74      62.48       3.04",
    "VAL     CB       C        1820       22.04       40.75      32.66       1.91",
    "VAL     CG1      C        1362       11.60       26.90      21.38       1.53",
    "VAL     CG2      C        1281       11.30       28.74      21.31       1.76",
    "VAL     N        N        2637       96.29      136.80     121.02       4.96"

  };

struct shiftlimit shiftlimit[sizeof(shiftlimits)/sizeof(char *)];

int initShiftLimits(void)
{
  int i;
  char res[4], *pt;

  for (i = 0; i < sizeof(shiftlimits)/sizeof(char *); i++)
    {
      sscanf(shiftlimits[i],"%3c %4c %c %d %f %f %f %f",res,shiftlimit[i].nuc,&shiftlimit[i].atom,
	     &shiftlimit[i].n,&shiftlimit[i].min,&shiftlimit[i].max,&shiftlimit[i].avg,&shiftlimit[i].std);
      res[3] = '\0';
      shiftlimit[i].res = rc_idx(iupac_code(res));
      shiftlimit[i].iupac_code = iupac_code(res);
      if ((pt = strchr(shiftlimit[i].nuc,' ')) != NULL)
	{
	  *pt = '\0';
	}
      shiftlimit[i].upper = shiftlimit[i].avg + 4 * shiftlimit[i].std;
      shiftlimit[i].lower = shiftlimit[i].avg - 4 * shiftlimit[i].std;
      //	printf("%d %d %s %c %d %f %f %f %f\n",i,shiftlimit[i].res,shiftlimit[i].nuc,shiftlimit[i].atom,
      //		shiftlimit[i].n,shiftlimit[i].min,shiftlimit[i].max,shiftlimit[i].avg,shiftlimit[i].std);
    }
#ifdef _DEBUG
  {
    FILE *ff;
    int j;

    ff = fopen("c:\\psa\\limits.txt","wt");
    for (j = 0; j < i; j++)
      {
	fprintf(ff,"%c %s %f %f\n",shiftlimit[j].iupac_code,shiftlimit[j].nuc,shiftlimit[j].lower,shiftlimit[j].upper);
      }
    fclose(ff);
  }
#endif // _DEBUG

  return(1);
}

double outOfBounds(char type,char *nucl,double shift)
{
  int i, idx;
	
  if (shift == NA)
    {
      return(0.0);
    }

  if (type == 'F')
    {
      if (!strncmp(nucl,"HD",2) || !strncmp(nucl,"HE",2) || !strncmp(nucl,"HZ",2))
	{
	  return(0.0);
	}
    }
  else if (type == 'Y')
    {
      if (!strncmp(nucl,"HD",2) || !strncmp(nucl,"HE",2))
	{
	  return(0.0);
	}
    }
  else if (type == 'W')
    {
      if (!strncmp(nucl,"HD",2) || !strncmp(nucl,"HE",2) || !strncmp(nucl,"HZ",2) || !strncmp(nucl,"HH",2))
	{
	  return(0.0);
	}
    }
  idx = rc_idx(type);

  if (!strcmp(nucl,"HA"))
    {
      if (shift < 2.0)
	{
	  return(2.0);
	}
      if (shift > 6.3)
	{
	  return(6.3);
	}
    }

  if (!strcmp(nucl,"CA"))
    {
      if (shift < 41.0)
	{
	  return(41.0);
	}
      if (shift > 72.0)
	{
	  return(72.0);
	}
    }

  if (!strcmp(nucl,"CO"))
    {
      if (shift < 165.0)
	{
	  return(165.0);
	}
      if (shift > 185.0)
	{
	  return(185.0);
	}
    }

  if (!strcmp(nucl,"N"))
    {
      if (shift < 95.0)
	{
	  return(95.0);
	}
      if (shift > 135.0)
	{
	  return(135.0);
	}
    }

  if (!strcmp(nucl,"H"))
    {
      if (shift < 4.0)
	{
	  return(4.0);
	}
      if (shift > 12.0)
	{
	  return(12.0);
	}
    }

  for (i = 0; i < sizeof(shiftlimits)/sizeof(char *); i++)
    {
      if (shiftlimit[i].res == idx && !strcmp(nucl,shiftlimit[i].nuc))
	{
	  if (shift > shiftlimit[i].upper)
	    {
	      return(shiftlimit[i].upper);
	    }
	  else if (shift < shiftlimit[i].lower)
	    {
	      return(shiftlimit[i].lower);
	    }
	}
    }
  return(shift);
}
