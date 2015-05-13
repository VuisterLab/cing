#include <stdio.h>
#include <string.h>
#include <stdlib.h>  /* SJN */

/* this gets set in the installation script */ 
#define USER_LIB_PATH "/diadem/local/lib/VADAR"


#define DIVIDE(a,b) (b == 0? 0: (a/b))

/*.................... constants ......................*/

#define VERSION				"1.2, Sept 1996"
#define PARM_VERSION		"1.2.h"
#define VAD_MODULE			"VADAR_V1.2 0:9:96"
#define PARMS_SCH       	'>'
#define USER_PARMS			"vadar.parms"
#define PROMPT              "\n>> "
#define PARMS_FLAG          "-i"
#define FILE_FLAG           "-f"
#define RESULTS_FLAG        "-o"

#ifndef TRUE
#define TRUE				1
#endif
#ifndef FALSE
#define FALSE				0
#endif

#define MAX_LINE_LEN        256
#define MAX_FNAME_LEN       256
#define MAX_TITLE_LEN		256
#define MAX_NAME_LEN        5
#define MAX_RES_NUM			10000 
#define LINE_LEN            80
#define NUM_RAD_TYPES 		2
#define ALLCHAINS_POS		10		/* field in the parameter file */

/* values for vanderwaals radius */ 
#define CHOTH_RAD	0
#define EIS_RAD		1
#define RICH_RAD	2
#define SHRAKE_RAD	3

#define COIL 0
#define BETA 1
#define HELIX 2
#define TURN 3
#define ALSO_HELIX 4
#define ALSO_BETA 5

#define VOID -999

#define NUMAA_BASIC 20
#define NUMAA 25
#define ALA 0
#define ARG 1
#define ASN 2
#define ASP 3
#define CYS 4
#define GLN 5
#define GLU 6
#define GLY 7
#define HIS 8
#define ILE 9
#define NE2 10
#define LEU 11
#define LYS 12
#define MET 13
#define PHE 14
#define PRO 15
#define SER 16
#define THR 17
#define TRP 18
#define TYR 19
#define VAL 20
#define ACE 21
#define NH2_RES 22
#define DEU 23
#define NA 24


#define NUMATMS 40
#define BB 0
#define C 1
#define CA 2
#define CB 3
#define CD 4
#define CD1 5
#define CD2 6
#define CE 7
#define CE1 8
#define CE2 9
#define CE3 10
#define CG 11
#define CG1 12
#define CG2 13
#define CH 14
#define CH2 15
#define CZ 16
#define CZ1 17
#define CZ2 18
#define CZ3 19
#define N 20
#define ND1 21
#define ND2 22
#define NE 23
#define NE1 24
#define NH1 25
#define NH2 26
#define NZ 27
#define O 28
#define OD1 29
#define OD2 30
#define OE1 31
#define OE2 32
#define OG 33
#define OG1 34
#define OH 35
#define OXT 36
#define SC 37
#define SD 38
#define SG 39





/* describing the parameter file */
#define NUM_PROGS 	6

extern char	LIB_PATH[MAX_LINE_LEN];


/*.................... global vars ....................*/

/* from libc/util.c */
extern char		lastExtra;
extern int		resNumAdd;


/*.................... structures .....................*/
struct atomRec {
	char 	atomName[MAX_NAME_LEN];
	char 	resName[MAX_NAME_LEN];
	char	chain;
	int  	resNum;
	int  	origResNum;
	float 	x, y, z;
	float	contactArea, accessArea;
	float	volume;
	float	rad[NUM_RAD_TYPES];
};
typedef struct atomRec ATOM_REC;
