#ifndef  TORISON_H

float  dihedral_angle( VECTOR a, VECTOR b, VECTOR c, VECTOR d );
void   torison_angles( RESIDUE *r );
void   SideChainOrientation( RESIDUE *r, CSHIFT **cs );

#define  TORISON_H

#endif
