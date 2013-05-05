
#ifndef  MAIN_H

#define MAX_RES_NUM 10000 /* SJN: max chain size we're prepared to handle */
#define MAX_HBONDS 2     /* Max # of hbonds per residue, for Vadar */

#define   TRUE      1
#define   FALSE     0
#define   NA        -666.0

#define CA_HA_FACTOR 0.2   // Scale factor for adding HA shifts to the corresponding CA shift
#define N15_HN_FACTOR 0.0  // Scale factor for adding HN shifts to the corresponding N15 shifts
/* Indices for coordinate set that Vadar needs */

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


struct recbond {
  int		partner;   // NOT a residue number, but an index into the residue array
  int		DA_FLAG;
  float	dist;
  float	angle;
  float	energy;
  int donor, dneighbour;
  int acceptor, aneighbour;
};
typedef struct recbond BOND_REC;


typedef struct
{
  float   x;
  float   y;
  float   z;
} VECTOR;

/* These are for reading in an entry from a PDB file */

typedef struct ATOM
{
  char          type[5];
  VECTOR        p;
  float         occupancy;
  float         BFactor;
  struct ATOM  *next, *last;
  int hIndex;		// Index into the array of sidechain hydrogens
} ATOM;


typedef struct
{
  char            type[5];
  int             num;
  
  /* Torison Angles */
  
  float           phi;
  float           psi;
  float           omega;
  float           chi;
  float			  chi2;
  float			  chi22;
  /* Orientation of ring w.r.t CA */
  
  float           theta;
  
  /* Locations of previous C and CA */
  
  VECTOR          lastc;
  VECTOR          lastca;
  VECTOR		  nextn;
  /* List of atoms */
  
  ATOM            *atom;

  char errflags;    // Causes of inaccuracies for this residue SJN
  char chain;       // Which chain this residue is part of SJN 
  int numLabel;     // Residue # as given in the PDB file 
  char insCode;     // Insertion code if one exists
  float x,y,z;      // Coordinates of backbone carbon SJN 
  char ss;					/* Secondary structure SJN */
  char ssbond;	  /* True if disulfide bond is present */
  VECTOR coords[NUM_COORDS]; /* Coordinates for use by Vadar */
  BOND_REC	hbonds[MAX_HBONDS];
  BOND_REC	sidebond[MAX_HBONDS];
  char    dstruct1[2];
  char    dstruct2[2];
  char	dstruct3[2];
  char	consens[2];
  char	bturn[5];
  float ha1dist,ha2dist,hndist,rdist; /* SJN */
  int hnPartner;			// res num of HN's bonding parnter
  char hnPartnerType[5];  // atom label of HN's bonding partner
  int ssPartner;			// res num of cysteine bonding partner
  char ssPartnerInsCode;  // Insertion code of ssbonding partner, if any
} RESIDUE;


/* Error codes for various residue problems; OR these into the errflags field of resiude */
#define RES_ERR_NO_CB 1 
#define RES_ERR_MISSING_ATOMS 2 
#define RES_ERR_MISSING_RES 4
#define RES_ERR_MISSING_RING_MEMBERS 8

/* These are the simplified version of the above but they are intended */
/* for coordinate calculations                                         */

typedef struct   ATM

{
  char           type[5];
  VECTOR         r;
  struct ATM     *next, *last;
  int hIndex;
} ATM;

typedef struct   RES
{
  char           type;
  int            num;
  ATM            *atom;
  struct RES     *next, *last;
} RES;


extern char UseChain;  /* SJN - label of chains to use for analysis */

RESIDUE *FindResidue(int resno);
int CheckHBond(RESIDUE *rrez,RESIDUE *drez,double *energy,int oindex,int cindex);
int CheckSolventHBond(RESIDUE *drez,double ox,double oy,double oz);
int CheckMultipleChains(FILE *ff,int cmdline);

#define HYDRO_H		0
#define HYDRO_HA	1
#define HYDRO_HA2	2
#define HYDRO_HA3	3
#define HYDRO_HB	4
#define HYDRO_HB1	5
#define HYDRO_HB2	6
#define HYDRO_HB3	7
#define HYDRO_HD1	8
#define HYDRO_HD11	9
#define HYDRO_HD12	10
#define HYDRO_HD13	11
#define HYDRO_HD2	12
#define HYDRO_HD21	13	
#define HYDRO_HD22	14
#define HYDRO_HD23	15
#define HYDRO_HD3	16
#define HYDRO_HE	17
#define HYDRO_HE1	18
#define HYDRO_HE2	19
#define HYDRO_HE21	20
#define HYDRO_HE22	21
#define HYDRO_HE3	22
#define HYDRO_HG	23
#define HYDRO_HG1	24
#define HYDRO_HG11	25
#define HYDRO_HG12	26
#define HYDRO_HG13	27
#define HYDRO_HG2	28
#define HYDRO_HG21	29
#define HYDRO_HG22	30
#define HYDRO_HG23	31
#define HYDRO_HG3	32
#define HYDRO_HH	33
#define HYDRO_HH11	34
#define HYDRO_HH12	35
#define HYDRO_HH2	36
#define HYDRO_HH21	37
#define HYDRO_HH22	38
#define HYDRO_HZ	39
#define HYDRO_HZ1	40
#define HYDRO_HZ2	41
#define HYDRO_HZ3	42
#define NHATOMS     43



extern struct hatoms
{
  char *name;
  int index;
} hatoms[NHATOMS];

#define  MAIN_H

#endif
