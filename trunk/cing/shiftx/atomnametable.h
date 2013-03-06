
#ifndef ATOMNAMETABLE_H 
#define ATOMNAMETABLE_H

extern struct tratoms
{
	char iupacCode;
	char *bmrb;
	char *pdb;
	char *xplor;
	int hatomsIndex;
}tratoms[];

//extern struct tratoms tratoms[];
//#define NTRATOMS (sizeof(tratoms) / sizeof(struct tratoms))
extern int NTRATOMS;

#endif 
