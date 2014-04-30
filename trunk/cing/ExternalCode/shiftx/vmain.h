
/*
	vadar driver header file
*/

#include "stdvadar.h"

#define CH2INT(x) ( x - '0' )
#define INT2CH(x) ( x + '0' )

#define PI				3.1415927


/* individual progs called */
#define VOLUME			2
#define PHIPSI			3
#define DEFINE1			4
#define AREA			5
#define DEFINE2			6

/* main menu options */
#define VHELP			1
#define EDPARMS			2
#define VADAR			3
#define LOG				4
#define	EXIT			0

/* def of polar, nonpolar, and charged */
#define CHOTH_DEF	0
#define EIS_DEF		1
#define SHRAKE_DEF	2

/* values for volume calculations */
#define VOR_VOL		0
#define RICH_VOL	1
#define RAD_VOL		2

/* hbonds */
#define MAX_HBONDS	2
#define DONOR 1
#define ACCEPTOR 2

/* types of extra output */
#define MOLSCRIPT	1
#define RIBBONS		2

#define NUMSTRUC	5
#define BTURN_BOUND	20
#define RAMA_LEN	36

/* output file pointers */
#define FPMAIN	0
#define FPSIDE	1
#define FPSTATS	2
#define FPBOND	3
#define FPMOL 	4

/* for define1 */
#define NUM_SKIP        5
#define LEN_HELIX_MASK  5
#define LEN_BETA_MASK 3

#define EMPTY -1.0

/* environment class types */
#define NUM_ENV     18
#define B1H			0
#define B1B			1
#define B1C			2
#define B2H			3
#define B2B			4
#define B2C			5
#define B3H			6
#define B3B			7
#define B3C			8
#define P1H			9
#define P1B			10
#define P1C			11
#define P2H			12
#define P2B			13
#define P2C			14
#define E0H			15
#define E0B			16
#define E0C			17


/*..........................................................................*/
/* coordinates that are saved from pdb file
*/
#define		NUM_COORDS 25
#define	 	H_COORD	0

#define		N_COORD 1
#define		NH1_COORD 2
#define		NH2_COORD 3
#define		NZ_COORD 4
#define		NE_COORD 5
#define     NE1_COORD 6
#define		NE2_COORD 7
#define     ND1_COORD 8 
#define		ND2_COORD 9

#define		O_COORD 10 
#define		OD1_COORD 11 
#define		OD2_COORD 12 
#define		OE1_COORD 13
#define		OE2_COORD 14
#define		OG_COORD 15
#define		OG1_COORD 16
#define		OH_COORD 17

#define		C_COORD 18
#define		CG_COORD 19
#define		CD_COORD 20
#define		SG_COORD 21
#define		CZ_COORD 22
#define		CE_COORD 23
#define 	CB_COORD 24

/*..........................................................................*/
/* macros
*/

#define DSTR(x)( strcmp(x.dstruct3, "H") == 0 ? HELIX : ( strcmp(x.dstruct3, "B") == 0 ? BETA : COIL) )

#define ABS(x)( (x)<0 ? -(x) : (x))

/*..........................................................................*/
/* define structures 
*/

struct qi {
	int vol;
	int tors;
	int tors2;
	int sfe;
	int eis;
	int env;
	int total;
	int profile;
};
typedef struct qi QI_REC;

struct rec3d {
	float x, y, z;
};
typedef struct rec3d COORD3D;

struct recbond {
	int		partner;
	int		DA_FLAG;
	float	dist;
	float	angle;
	float	energy;
	int donor, dneighbour;
	int acceptor, aneighbour;
};
typedef struct recbond BOND_REC;

struct resRec {
	char	name[MAX_NAME_LEN];
	int     resNum;
	int     origResNum;
	char	chain;
	char    dstruct1[2];
	char    dstruct2[2];
	char	dstruct3[2];
	char	consens[2];
	char	bturn[4];
	BOND_REC	hbonds[MAX_HBONDS];
	BOND_REC	sidebond[MAX_HBONDS];
	int		ssbond;
	float	ssdist;
	COORD3D	coords[NUM_COORDS];
	float	asa;
	float	fracasa;
	float	sideasa;
	float	sidefracasa;
	float	sidesfe;
	char	eclass[4];
	float	vol;
	float	fracvol;
	float	phi, psi, omega, chi;
	QI_REC	quality;
};
typedef struct resRec RESIDUE;


/* for define1 */
struct define_struct {
        int     num;
        char    name[5];
		char	chain;
        int     type;
        double  x, y, z;
};
typedef struct define_struct DEF_REC;


/* for water hbonds */
struct water_bond {
	int	wnum;
	int residx;
	char atomname[10];
	float dist;
};
typedef struct water_bond WATER_REC;


/*..........................................................................*/
/* globals 
*/


/* from tables.c */
extern float	aaAve[NUMAA][NUMATMS];
extern float    sidestandAsa[NUMAA];

/* from main.c */
extern char		parmsFname[MAX_FNAME_LEN];
extern char		outFname[MAX_FNAME_LEN];

/* from calc.c */
extern char 	resultsFname[MAX_FNAME_LEN];
extern char		tmp_out[MAX_FNAME_LEN];
extern char		area_in[MAX_FNAME_LEN], vol_in[MAX_FNAME_LEN];
extern char		def2_in[MAX_FNAME_LEN], def1_in[MAX_FNAME_LEN];
extern char		phipsi_in[MAX_FNAME_LEN];
extern char		pdbFname[MAX_FNAME_LEN];
extern int		aaCount[NUMAA];
extern float	phiheld;

/* from init.c */
extern int		interactive;
extern int		statsType, radType;
extern int		hDisplay, mainDisplay, sideDisplay, statsDisplay, graphDisplay;
extern int		qualityDisplay, atomDisplay, allChains, bigfile, hbondsH2O;
extern double 	hbond_dist, hbond_dist2, sidebond_dist, ssbond_dist;
extern int		hbond_angle;

/* from print.c */
extern float	resolution, rfactor;
extern char		protName[MAX_LINE_LEN];

/* from side.c */
extern int 		buriedCharges;

/* from util.c */
extern int	 	first;
extern RESIDUE	resArray[MAX_RES_NUM];
extern float	rvalue;

/* from stats.c */
extern int		lastResNum;
extern int 		structCount[NUMSTRUC];
extern int		begin;
extern int		lastType, lastNumSequence; 
extern int		lastResNum;
extern int		numburied, numpacking;
extern char		logFname[MAX_FNAME_LEN];
extern float	standardAsa[NUMAA];
extern float	standardVol[NUMAA];
extern float	molWeightTable[NUMAA];
extern float	fef, expfef;


/* from define1.c */
extern char     maskFname[MAX_FNAME_LEN];
extern DEF_REC  struc[MAX_RES_NUM];
extern FILE     *infp, *outfp[5];
extern int      num_res;
extern double   beta_rmsd, helix_rmsd;
extern double   hmask[LEN_HELIX_MASK];
extern double   bmask[LEN_BETA_MASK];

/* from quality.c */
extern int 		ramaTable[RAMA_LEN][RAMA_LEN]; 
extern float    molWeight;
extern int      ramaCore, ramaAllow, ramaGenerous, ramaOutside;

/* from bonds.c */
extern COORD3D *watertab;
extern int watercnt;
extern WATER_REC *waterOut;
extern int woutcnt;
