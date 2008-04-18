remark   file topallhdg.pro  version 5.3  date 23-Sept-02
remark      for file parallhdg.pro version 5.3 date 13-Feb-02 or later
remark   Geometric energy function parameters for distance geometry and
remark      simulated annealing.
remark   Author: Michael Nilges, EMBL Heidelberg; Institut Pasteur, Paris
remark   This file contains modifications from M. Williams, UCL London
remark   Last modification 16-Sept-02

set echo off message off end

!***********************************************************************!
! Copyright (C) 1995,1996 by Michael Nilges. All rights reserved.       !
! Copying and redistribution of this files is authorized only if etiher !
! (1) you make absolutely no changes to your copy, including name, or   !
! (2) if you do make changes, you name it something other than          !
! topallhdg.pro and topallhdg.x.xx.pro, and clearly mark the changes.   ! 
! The information in this software is subject to change without notice  !
! and should not be construed as a commitment by the EMBL or by the     !
! authors. Neither the EMBL, Yale University, nor the authors assume    !
! responsibility for the use or reliability of this software.           !
! We do hope, however, to get responses from users, especially when     !
! errors have been found.                                               !
!***********************************************************************!
! Description:                                                          !
! This parameter file was originally derived from the  CHARMM parameter !
! file PARMALLH6. It was designed specifically for the initial stages   ! 
! of calculating structures from NMR restraints.                           !
!***********************************************************************!
! History:
! version 5.3  (13-Feb-02) : merged UCL version with EMBL version
! version UCL  (07-JUL-01) : added new MULT disulphide/sidechain COO dihedral parameters
! version UCL  (03-JUL-01) : added new MULT phi/psi dihedral related parameters
! version UCL  (14-MAR-00) : modified peptide bond parameters for flexible omega
! version UCL  (12-MAR-00) : added C and N terminus and disulphide dihedrals
! version UCL  (09-MAR-00) : TYR O-H planarity & LYS NH3 stagger 
!                            & HIS dihedrals modified
! version 5.2  (18-Jun-99) : new cis peptide patch
! version 4.03 (04-APR-99) : THR CB atom type corrected
! version 4.02 (17-DEC-97) : Histidine hbond acceptor/donor corrected
! version 4.01 (29-Jul-96) : all covalent parameters
! version 4.00  (19-Jul-96) : all atom types from CSDX implemented
! version 3.00 (24-Oct-95) : mapped CSDX parmameters on parallhdg, 
!                            no changes in topallhdg
! previous modifications:
! proline residue modified, puckering enforced (MN)
! added hbond acceptor and donor definitions for analysis (MN)
! all references to internal coordinates (IC's) removed (MN) 
! added stereospecific impropers for all pro-chiral centers (ATB, JK)
! all dihedrals defining planarity converted to impropers (MN, PK)
! additional impropers at planar centers (MN)
!***********************************************************************!


set message off echo off end

autogenerate 
  angles=true
  dihedrals=false
end

mass H    1.008
mass HC   1.008
mass HA   1.008
mass C   12.011
mass CCIS  12.011
mass CH1E  12.011
mass CH2E  12.011
mass CH3E  12.011
mass CH2G  12.011
mass CH2P  12.011
mass C5W  12.011
mass CW  12.011

mass CR1E  12.011
mass C5  12.011
mass CRH  12.011
mass CR1H  12.011
mass CR1W  12.011
mass CRHH  12.011
mass CF  12.011
mass CY  12.011
mass CY2 12.011
mass N   14.007
mass NR  14.007
mass NH1 14.007
mass NH2 14.007
mass NH3 14.007
mass NC2 14.007
mass O   15.999
mass OC  15.999
mass OH1  15.999
mass SH1E   32.060
mass SM  32.060
mass S   32.060
 MASS OX1    15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS CX2    12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX3    12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS OX4    15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS PX5    30.97400 ! assuming P -> 30.97400 + 1.008 * 0 (Hs)
 MASS OX6    15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS PX7    30.97400 ! assuming P -> 30.97400 + 1.008 * 0 (Hs)
 MASS OX8    15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX9    15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX10   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS CX11   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX12   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX13   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX14   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX15   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX16   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS CX17   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX18   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX19   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX20   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS OX21   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS CX22   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX23   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX24   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS OX25   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX26   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX27   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX28   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX29   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS CX30   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX31   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX32   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX33   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS CX34   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX35   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS CX36   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS CX37   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX38   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS NX39   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS CX40   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS NX41   14.00700 ! assuming N -> 14.00700 + 1.008 * 0 (Hs)
 MASS CX42   12.01100 ! assuming C -> 12.01100 + 1.008 * 0 (Hs)
 MASS OX43   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS PX44   30.97400 ! assuming P -> 30.97400 + 1.008 * 0 (Hs)
 MASS OX45   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX46   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX47   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS OX48   15.99900 ! assuming O -> 15.99900 + 1.008 * 0 (Hs)
 MASS HX49    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX50    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX51    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX52    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX53    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX54    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX55    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX56    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX57    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX58    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX59    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX60    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX61    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX62    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX63    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX64    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX65    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX66    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX67    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX68    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX69    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX70    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX71    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX72    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX73    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)
 MASS HX74    1.00800 ! assuming H -> 1.00800 + 1.008 * 0 (Hs)

 autogenerate angles=true end

RESIdue NDP

GROUp
 ATOM  O1R  TYPE OX1   CHARge  0.0  END
 ATOM  C4R  TYPE CX2   CHARge  0.0  END
 ATOM  C5R  TYPE CX3   CHARge  0.0  END
 ATOM  O5R  TYPE OX4   CHARge  0.0  END
 ATOM  P1   TYPE PX5   CHARge  0.0  END
 ATOM  O10  TYPE OX6   CHARge  0.0  END
 ATOM  P2   TYPE PX7   CHARge  0.0  END
 ATOM  O21  TYPE OX8   CHARge  0.0  END
 ATOM  O11  TYPE OX9   CHARge  0.0  END
 ATOM O51R  TYPE OX10  CHARge  0.0  END
 ATOM C51R  TYPE CX11  CHARge  0.0  END
 ATOM C41R  TYPE CX12  CHARge  0.0  END
 ATOM C31R  TYPE CX13  CHARge  0.0  END
 ATOM C21R  TYPE CX14  CHARge  0.0  END
 ATOM C11R  TYPE CX15  CHARge  0.0  END
 ATOM  N11  TYPE NX16  CHARge  0.0  END
 ATOM  C61  TYPE CX17  CHARge  0.0  END
 ATOM  C51  TYPE CX18  CHARge  0.0  END
 ATOM  C71  TYPE CX19  CHARge  0.0  END
 ATOM  N71  TYPE NX20  CHARge  0.0  END
 ATOM  O71  TYPE OX21  CHARge  0.0  END
 ATOM  C41  TYPE CX22  CHARge  0.0  END
 ATOM  C31  TYPE CX23  CHARge  0.0  END
 ATOM  C21  TYPE CX24  CHARge  0.0  END
 ATOM O11R  TYPE OX25  CHARge  0.0  END
 ATOM O21R  TYPE OX26  CHARge  0.0  END
 ATOM O31R  TYPE OX27  CHARge  0.0  END
 ATOM  O2   TYPE OX28  CHARge  0.0  END
 ATOM  O1   TYPE OX29  CHARge  0.0  END
 ATOM  C3R  TYPE CX30  CHARge  0.0  END
 ATOM  C2R  TYPE CX31  CHARge  0.0  END
 ATOM  C1R  TYPE CX32  CHARge  0.0  END
 ATOM  N9   TYPE NX33  CHARge  0.0  END
 ATOM  C8   TYPE CX34  CHARge  0.0  END
 ATOM  N7   TYPE NX35  CHARge  0.0  END
 ATOM  C5   TYPE CX36  CHARge  0.0  END
 ATOM  C6   TYPE CX37  CHARge  0.0  END
 ATOM  N6   TYPE NX38  CHARge  0.0  END
 ATOM  N1   TYPE NX39  CHARge  0.0  END
 ATOM  C2   TYPE CX40  CHARge  0.0  END
 ATOM  N3   TYPE NX41  CHARge  0.0  END
 ATOM  C4   TYPE CX42  CHARge  0.0  END
 ATOM  O2R  TYPE OX43  CHARge  0.0  END
 ATOM  P3   TYPE PX44  CHARge  0.0  END
 ATOM  O5   TYPE OX45  CHARge  0.0  END
 ATOM  O4   TYPE OX46  CHARge  0.0  END
 ATOM  O3   TYPE OX47  CHARge  0.0  END
 ATOM  O3R  TYPE OX48  CHARge  0.0  END
 ATOM  H7   TYPE HX49  CHARge  0.0  END
 ATOM  H9   TYPE HX50  CHARge  0.0  END
 ATOM  H8   TYPE HX51  CHARge  0.0  END
 ATOM  H19  TYPE HX52  CHARge  0.0  END
 ATOM  H18  TYPE HX53  CHARge  0.0  END
 ATOM  H17  TYPE HX54  CHARge  0.0  END
 ATOM  H16  TYPE HX55  CHARge  0.0  END
 ATOM  H15  TYPE HX56  CHARge  0.0  END
 ATOM  H14  TYPE HX57  CHARge  0.0  END
 ATOM  H23  TYPE HX58  CHARge  0.0  END
 ATOM  H25  TYPE HX59  CHARge  0.0  END
 ATOM  H24  TYPE HX60  CHARge  0.0  END
 ATOM  H22  TYPE HX61  CHARge  0.0  END
 ATOM  H26  TYPE HX62  CHARge  0.0  END
 ATOM  H21  TYPE HX63  CHARge  0.0  END
 ATOM  H20  TYPE HX64  CHARge  0.0  END
 ATOM  H2   TYPE HX65  CHARge  0.0  END
 ATOM  H3   TYPE HX66  CHARge  0.0  END
 ATOM  H6   TYPE HX67  CHARge  0.0  END
 ATOM  H5   TYPE HX68  CHARge  0.0  END
 ATOM  H4   TYPE HX69  CHARge  0.0  END
 ATOM  H13  TYPE HX70  CHARge  0.0  END
 ATOM  H12  TYPE HX71  CHARge  0.0  END
 ATOM  H11  TYPE HX72  CHARge  0.0  END
 ATOM  H10  TYPE HX73  CHARge  0.0  END
 ATOM  H1   TYPE HX74  CHARge  0.0  END

 BOND  O1R  C4R      BOND  O1R  C1R      BOND  C4R  C5R      BOND  C4R  C3R
 BOND  C4R  H7       BOND  C5R  O5R      BOND  C5R  H9       BOND  C5R  H8
 BOND  O5R  P1       BOND  P1   O10      BOND  P1   O2       BOND  P1   O1
 BOND  O10  P2       BOND  P2   O21      BOND  P2   O11      BOND  P2  O51R
 BOND O51R C51R      BOND C51R C41R      BOND C51R  H19      BOND C51R  H18
 BOND C41R C31R      BOND C41R O11R      BOND C41R  H17      BOND C31R C21R
 BOND C31R O31R      BOND C31R  H16      BOND C21R C11R      BOND C21R O21R
 BOND C21R  H15      BOND C11R  N11      BOND C11R O11R      BOND C11R  H14
 BOND  N11  C61      BOND  N11  C21      BOND  C61  C51      BOND  C61  H23
 BOND  C51  C71      BOND  C51  C41      BOND  C71  N71      BOND  C71  O71
 BOND  N71  H25      BOND  N71  H24      BOND  C41  C31      BOND  C41  H22
 BOND  C41  H26      BOND  C31  C21      BOND  C31  H21      BOND  C21  H20
 BOND O21R  H2       BOND O31R  H3       BOND  C3R  C2R      BOND  C3R  O3R
 BOND  C3R  H6       BOND  C2R  C1R      BOND  C2R  O2R      BOND  C2R  H5
 BOND  C1R  N9       BOND  C1R  H4       BOND  N9   C8       BOND  N9   C4
 BOND  C8   N7       BOND  C8   H13      BOND  N7   C5       BOND  C5   C6
 BOND  C5   C4       BOND  C6   N6       BOND  C6   N1       BOND  N6   H12
 BOND  N6   H11      BOND  N1   C2       BOND  C2   N3       BOND  C2   H10
 BOND  N3   C4       BOND  O2R  P3       BOND  P3   O5       BOND  P3   O4
 BOND  P3   O3       BOND  O3R  H1

 { edit these DIHEdrals if necessary }
  DIHEdral  C1R  O1R  C4R  C3R ! flat ? (0 degrees = cis)     0.62
! DIHEdral  C4R  O1R  C1R  H4  ! flexible dihedral ???    96.59
! DIHEdral  O1R  C4R  C5R  O5R ! flexible dihedral ???   -69.84
  DIHEdral  O1R  C4R  C5R  H9  ! flat ? (180 degrees = trans)   170.10
! DIHEdral  O1R  C4R  C5R  H8  ! flexible dihedral ???    50.11
  DIHEdral  H7   C4R  C5R  O5R ! flat ? (180 degrees = trans)   170.73
! DIHEdral  H7   C4R  C5R  H9  ! flexible dihedral ???    50.67
! DIHEdral  H7   C4R  C5R  H8  ! flexible dihedral ???   -69.32
! DIHEdral  O1R  C4R  C3R  O3R ! flexible dihedral ???   -96.94
! DIHEdral  C5R  C4R  C3R  C2R ! flexible dihedral ???   -97.96
  DIHEdral  C5R  O5R  P1   O1  ! flat ? (0 degrees = cis)    -8.27
  DIHEdral  P1   O10  P2   O11 ! flat ? (180 degrees = trans)   188.26
  DIHEdral  P2  O51R C51R C41R ! flat ? (180 degrees = trans)   179.03
! DIHEdral  P2  O51R C51R  H19 ! flexible dihedral ???   -60.69
! DIHEdral  P2  O51R C51R  H18 ! flexible dihedral ???    58.81
! DIHEdral O51R C51R C41R O11R ! flexible dihedral ???   -62.54
  DIHEdral O51R C51R C41R  H17 ! flat ? (180 degrees = trans)   175.07
  DIHEdral  H19 C51R C41R O11R ! flat ? (180 degrees = trans)   177.16
! DIHEdral  H19 C51R C41R  H17 ! flexible dihedral ???    54.77
! DIHEdral  H18 C51R C41R O11R ! flexible dihedral ???    57.67
! DIHEdral  H18 C51R C41R  H17 ! flexible dihedral ???   -64.72
! DIHEdral C51R C41R C31R O31R ! flexible dihedral ???    87.87
! DIHEdral O11R C41R C31R  H16 ! flexible dihedral ???    80.23
! DIHEdral  H17 C41R C31R C21R ! flexible dihedral ???    80.10
! DIHEdral  H17 C41R O11R C11R ! flexible dihedral ???   -97.47
! DIHEdral O31R C31R C21R  H15 ! flexible dihedral ???   -86.12
  DIHEdral C41R C31R O31R  H3  ! flat ? (180 degrees = trans)   179.94
! DIHEdral C21R C31R O31R  H3  ! flexible dihedral ???    66.79
! DIHEdral  H16 C31R O31R  H3  ! flexible dihedral ???   -58.80
! DIHEdral C31R C21R C11R  N11 ! flexible dihedral ???    93.06
! DIHEdral O21R C21R C11R O11R ! flexible dihedral ???    88.21
! DIHEdral  H15 C21R C11R  H14 ! flexible dihedral ???    94.84
  DIHEdral C31R C21R O21R  H2  ! flat ? (180 degrees = trans)   180.05
! DIHEdral  H15 C21R O21R  H2  ! flexible dihedral ???   -54.49
  DIHEdral C21R C11R O11R C41R ! flat ? (0 degrees = cis)     7.05
  DIHEdral C11R  N11  C61  C51 ! flat ? (180 degrees = trans)   182.58
  DIHEdral C11R  N11  C61  H23 ! flat ? (0 degrees = cis)     2.54
  DIHEdral  C21  N11  C61  C51 ! flat ? (0 degrees = cis)     2.32
  DIHEdral  C21  N11  C61  H23 ! flat ? (180 degrees = trans)   182.27
  DIHEdral C11R  N11  C21  C31 ! flat ? (180 degrees = trans)   180.25
  DIHEdral C11R  N11  C21  H20 ! flat ? (0 degrees = cis)     0.20
  DIHEdral  C61  N11  C21  C31 ! flat ? (0 degrees = cis)     0.53
  DIHEdral  C61  N11  C21  H20 ! flat ? (180 degrees = trans)   180.48
  DIHEdral  N11  C61  C51  C71 ! flat ? (180 degrees = trans)   179.46
  DIHEdral  N11  C61  C51  C41 ! flat ? (0 degrees = cis)    -3.69
  DIHEdral  H23  C61  C51  C71 ! flat ? (0 degrees = cis)    -0.50
  DIHEdral  H23  C61  C51  C41 ! flat ? (180 degrees = trans)   176.35
  DIHEdral  C61  C51  C71  O71 ! flat ? (0 degrees = cis)    -9.28
  DIHEdral  C41  C51  C71  O71 ! flat ? (180 degrees = trans)   173.66
  DIHEdral  C61  C51  C41  C31 ! flat ? (0 degrees = cis)     2.00
  DIHEdral  C71  C51  C41  C31 ! flat ? (180 degrees = trans)   178.50
! DIHEdral  C71  C51  C41  H22 ! flexible dihedral ???    58.48
! DIHEdral  C71  C51  C41  H26 ! flexible dihedral ???   -61.51
  DIHEdral  O71  C71  N71  H25 ! flat ? (0 degrees = cis)     0.08
  DIHEdral  O71  C71  N71  H24 ! flat ? (180 degrees = trans)   180.03
  DIHEdral  C51  C41  C31  C21 ! flat ? (0 degrees = cis)     1.31
  DIHEdral  C51  C41  C31  H21 ! flat ? (180 degrees = trans)   181.31
! DIHEdral  H22  C41  C31  H21 ! flexible dihedral ???   -54.78
! DIHEdral  H26  C41  C31  H21 ! flexible dihedral ???    57.42
  DIHEdral  C41  C31  C21  N11 ! flat ? (0 degrees = cis)    -2.48
  DIHEdral  C41  C31  C21  H20 ! flat ? (180 degrees = trans)   177.57
  DIHEdral  H21  C31  C21  N11 ! flat ? (180 degrees = trans)   177.52
  DIHEdral  H21  C31  C21  H20 ! flat ? (0 degrees = cis)    -2.43
! DIHEdral  O3R  C3R  C2R  C1R ! flexible dihedral ???    82.29
! DIHEdral  H6   C3R  C2R  O2R ! flexible dihedral ???    81.24
  DIHEdral  C4R  C3R  O3R  H1  ! flat ? (180 degrees = trans)   180.02
! DIHEdral  C2R  C3R  O3R  H1  ! flexible dihedral ???    63.22
! DIHEdral  H6   C3R  O3R  H1  ! flexible dihedral ???   -59.22
! DIHEdral  C3R  C2R  C1R  H4  ! flexible dihedral ???   -84.36
! DIHEdral  O2R  C2R  C1R  N9  ! flexible dihedral ???   -80.90
  DIHEdral  C3R  C2R  O2R  P3  ! flat ? (180 degrees = trans)   179.96
! DIHEdral  C1R  C2R  O2R  P3  ! flexible dihedral ???    65.42
! DIHEdral  H5   C2R  O2R  P3  ! flexible dihedral ???   -56.52
! DIHEdral  O1R  C1R  N9   C8  ! flexible dihedral ???    52.32
! DIHEdral  C2R  C1R  N9   C8  ! flexible dihedral ???   -65.69
  DIHEdral  H4   C1R  N9   C8  ! flat ? (180 degrees = trans)   172.09
  DIHEdral  H4   C1R  N9   C4  ! flat ? (0 degrees = cis)    -1.58
  DIHEdral  C1R  N9   C8   N7  ! flat ? (180 degrees = trans)   187.10
  DIHEdral  C1R  N9   C8   H13 ! flat ? (0 degrees = cis)     7.14
  DIHEdral  C4   N9   C8   N7  ! flat ? (0 degrees = cis)     1.99
  DIHEdral  C4   N9   C8   H13 ! flat ? (180 degrees = trans)   182.03
  DIHEdral  C1R  N9   C4   C5  ! flat ? (180 degrees = trans)   174.46
  DIHEdral  C1R  N9   C4   N3  ! flat ? (0 degrees = cis)    -5.28
  DIHEdral  C8   N9   C4   C5  ! flat ? (0 degrees = cis)    -0.62
  DIHEdral  C8   N9   C4   N3  ! flat ? (180 degrees = trans)   179.64
  DIHEdral  N9   C8   N7   C5  ! flat ? (0 degrees = cis)    -2.57
  DIHEdral  H13  C8   N7   C5  ! flat ? (180 degrees = trans)   177.39
  DIHEdral  C8   N7   C5   C6  ! flat ? (180 degrees = trans)   175.56
  DIHEdral  C8   N7   C5   C4  ! flat ? (0 degrees = cis)     1.97
  DIHEdral  N7   C5   C6   N6  ! flat ? (0 degrees = cis)     6.01
  DIHEdral  N7   C5   C6   N1  ! flat ? (180 degrees = trans)   184.02
  DIHEdral  C4   C5   C6   N6  ! flat ? (180 degrees = trans)   178.96
  DIHEdral  C4   C5   C6   N1  ! flat ? (0 degrees = cis)    -3.03
  DIHEdral  N7   C5   C4   N9  ! flat ? (0 degrees = cis)    -0.82
  DIHEdral  N7   C5   C4   N3  ! flat ? (180 degrees = trans)   178.94
  DIHEdral  C6   C5   C4   N9  ! flat ? (180 degrees = trans)   184.87
  DIHEdral  C6   C5   C4   N3  ! flat ? (0 degrees = cis)     4.63
  DIHEdral  C5   C6   N6   H12 ! flat ? (180 degrees = trans)   177.86
  DIHEdral  C5   C6   N6   H11 ! flat ? (0 degrees = cis)    -2.23
  DIHEdral  N1   C6   N6   H12 ! flat ? (0 degrees = cis)     0.03
  DIHEdral  N1   C6   N6   H11 ! flat ? (180 degrees = trans)   179.94
  DIHEdral  C5   C6   N1   C2  ! flat ? (0 degrees = cis)     1.11
  DIHEdral  N6   C6   N1   C2  ! flat ? (180 degrees = trans)   179.23
  DIHEdral  C6   N1   C2   N3  ! flat ? (0 degrees = cis)    -0.52
  DIHEdral  C6   N1   C2   H10 ! flat ? (180 degrees = trans)   179.46
  DIHEdral  N1   C2   N3   C4  ! flat ? (0 degrees = cis)     1.73
  DIHEdral  H10  C2   N3   C4  ! flat ? (180 degrees = trans)   181.74
  DIHEdral  C2   N3   C4   N9  ! flat ? (180 degrees = trans)   175.93
  DIHEdral  C2   N3   C4   C5  ! flat ? (0 degrees = cis)    -3.77
! DIHEdral  C2R  O2R  P3   O5  ! flexible dihedral ???   -60.01
! DIHEdral  C2R  O2R  P3   O4  ! flexible dihedral ???    59.97
  DIHEdral  C2R  O2R  P3   O3  ! flat ? (180 degrees = trans)   179.95

 { edit these IMPRopers if necessary }
 IMPRoper  C4R  O1R  C5R  C3R ! chirality or flatness improper    33.80
 IMPRoper  C5R  C4R  O5R  H9  ! chirality or flatness improper    31.11
 IMPRoper  P1   O5R  O10  O2  ! chirality or flatness improper    36.46
 IMPRoper  P2   O10  O21  O11 ! chirality or flatness improper    27.05
 IMPRoper C51R O51R C41R  H19 ! chirality or flatness improper   -31.56
 IMPRoper C41R C51R C31R O11R ! chirality or flatness improper    45.26
 IMPRoper C31R C41R C21R O31R ! chirality or flatness improper    34.15
 IMPRoper C21R C31R C11R O21R ! chirality or flatness improper    31.05
 IMPRoper C11R C21R  N11 O11R ! chirality or flatness improper    33.28
 IMPRoper  N11 C11R  C61  C21 ! chirality or flatness improper     0.14
 IMPRoper  C61  N11  C51  H23 ! chirality or flatness improper    -0.02
 IMPRoper  C51  C61  C71  C41 ! chirality or flatness improper    -1.55
 IMPRoper  C71  C51  N71  O71 ! chirality or flatness improper     5.34
 IMPRoper  N71  C71  H25  H24 ! chirality or flatness improper    -0.03
 IMPRoper  C41  C51  C31  H22 ! chirality or flatness improper    31.27
 IMPRoper  C31  C41  C21  H21 ! chirality or flatness improper     0.00
 IMPRoper  C21  N11  C31  H20 ! chirality or flatness improper    -0.03
 IMPRoper  C3R  C4R  C2R  O3R ! chirality or flatness improper    34.63
 IMPRoper  C2R  C3R  C1R  O2R ! chirality or flatness improper    27.29
 IMPRoper  C1R  O1R  C2R  N9  ! chirality or flatness improper    36.59
 IMPRoper  N9   C1R  C8   C4  ! chirality or flatness improper     3.60
 IMPRoper  C8   N9   N7   H13 ! chirality or flatness improper     0.02
 IMPRoper  C5   N7   C6   C4  ! chirality or flatness improper     4.31
 IMPRoper  C6   C5   N6   N1  ! chirality or flatness improper    -1.27
 IMPRoper  N6   C6   H12  H11 ! chirality or flatness improper    -0.05
 IMPRoper  C2   N1   N3   H10 ! chirality or flatness improper    -0.01
 IMPRoper  C4   N9   C5   N3  ! chirality or flatness improper     0.13
 IMPRoper  P3   O2R  O5   O4  ! chirality or flatness improper   -34.81

 { edit any DONOrs and ACCEptors if necessary }
 ACCEptor  O1R  C4R
 ACCEptor  O5R  C5R
 ACCEptor  O10  P1
! DONOr H?  O21 ! only true if -OHx (x>0)
 ACCEptor  O21  P2
! DONOr H?  O11 ! only true if -OHx (x>0)
 ACCEptor  O11  P2
 ACCEptor O51R  P2
! DONOr H?  O71 ! only true if -OHx (x>0)
 ACCEptor  O71  C71
 ACCEptor O11R C41R
 ACCEptor O21R C21R
 ACCEptor O31R C31R
! DONOr H?  O2  ! only true if -OHx (x>0)
 ACCEptor  O2   P1
! DONOr H?  O1  ! only true if -OHx (x>0)
 ACCEptor  O1   P1
! DONOr H?  N7  ! only true if -NHx (x>0)
! DONOr H?  N1  ! only true if -NHx (x>0)
! DONOr H?  N3  ! only true if -NHx (x>0)
 ACCEptor  O2R  C2R
! DONOr H?  O5  ! only true if -OHx (x>0)
 ACCEptor  O5   P3
! DONOr H?  O4  ! only true if -OHx (x>0)
 ACCEptor  O4   P3
! DONOr H?  O3  ! only true if -OHx (x>0)
 ACCEptor  O3   P3
 ACCEptor  O3R  C3R

END

residue ALA
  group
    atom N   type=NH1     charge=-0.570 end
    atom HN  type=H       charge= 0.370 end
    atom CA  type=CH1E    charge= 0.200 end
    atom HA  type=HA      charge= 0.000 end
    atom CB  type=CH3E    charge= 0.000 end
    atom HB1 type=HA      charge= 0.000 end
    atom HB2 type=HA      charge= 0.000 end
    atom HB3 type=HA      charge= 0.000 end
    atom C   type=C       charge= 0.500 end
    atom O   type=O       charge=-0.500 end

  bond N  HN       
  bond N  CA    bond CA  HA   
  bond CA  CB   bond CB  HB1   bond CB  HB2     bond CB  HB3
  bond CA  C       
  bond C   O

  improper HA  N   C   CB  ! chirality CA
  improper HB1 HB2 CA HB3  ! methyl CB

  dihedral HB1 CB  CA  C   ! methyl stagger UCL 12-MAR-00 

  DONO HN   N
  ACCE O    C
end
 

residue ARG
  group
    atom N    type=NH1    charge=-0.570 end
    atom HN   type=H      charge= 0.370 end
    atom CA   type=CH1E   charge= 0.200 end
    atom HA   type=HA     charge= 0.000 end
    atom CB   type=CH2E   charge= 0.000 end
    atom HB1  type=HA     charge= 0.000 end
    atom HB2  type=HA     charge= 0.000 end
    atom CG   type=CH2E   charge= 0.070 end
    atom HG1  type=HA     charge= 0.000 end
    atom HG2  type=HA     charge= 0.000 end
    atom CD   type=CH2E   charge= 0.310 end
    atom HD1  type=HA     charge= 0.000 end
    atom HD2  type=HA     charge= 0.000 end
    atom NE   type=NH1    charge=-0.700 end
    atom HE   type=H      charge= 0.440 end
    atom CZ   type=C      charge= 0.640 end
    atom NH1  type=NC2    charge=-0.800 end
    atom HH11 type=HC     charge= 0.460 end
    atom HH12 type=HC     charge= 0.460 end
    atom NH2   type=NC2   charge=-0.800 end
    atom HH21  type=HC    charge= 0.460 end
    atom HH22  type=HC    charge= 0.460 end
    atom C     type=C     charge= 0.500 end
    atom O     type=O     charge=-0.500 end
 
  bond N  HN
  bond N  CA     bond CA  HA
  bond CA CB     bond CB  HB1     bond CB  HB2
  bond CB CG     bond CG  HG1     bond CG  HG2
  bond CG CD     bond CD  HD1     bond CD  HD2
  bond CD NE     bond NE  HE
  bond NE CZ
  bond CZ NH1    bond NH1 HH11    bond NH1 HH12
  bond CZ NH2    bond NH2 HH21    bond NH2 HH22
  bond CA C
  bond C  O

  improper HA  N  C    CB  !chirality CA
  improper NE  CD CZ   HE  
  improper CZ  NE NH1  NH2
  improper NH1 CZ HH11 HH12
  improper NH2 CZ HH21 HH22
  improper NE  CZ NH1  HH11
  improper NE  CZ NH2  HH21
  improper CZ  NH2 HE NE  ! planar HE, CZ
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB CD  !stereo CG
  improper HD1 HD2 CG NE  !stereo CD
  
  dihedral CG  CB  CA  N
  dihedral CD  CG  CB  CA
  dihedral NE  CD  CG  CB
  dihedral CZ  NE  CD  CG
  
  DONO HN   N
  DONO HE   NE
  DONO HH11 NH1
  DONO HH12 NH1
  DONO HH21 NH2
  DONO HH22 NH2
  ACCE O    C
end

residue ASN
  group
    atom N    type=NH1    charge=-0.570 end
    atom HN   type=H      charge= 0.370 end
    atom CA   type=CH1E   charge= 0.200 end
    atom HA   type=HA     charge= 0.000 end
    atom CB   type=CH2E   charge=-0.000 end
    atom HB1  type=HA     charge= 0.000 end
    atom HB2  type=HA     charge= 0.000 end
    atom CG   type=C      charge= 0.500 end
    atom OD1  type=O      charge=-0.500 end
    atom ND2  type=NH2    charge=-0.850 end
    atom HD21 type=H      charge= 0.425 end
    atom HD22 type=H      charge= 0.425 end
    atom C    type=C      charge= 0.500 end
    atom O    type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA  HA
  bond CA CB     bond CB  HB1     bond CB  HB2
  bond CB CG
  bond CG OD1
  bond CG ND2    bond ND2 HD21    bond ND2 HD22
  bond CA C
  bond C  O

  improper HA  N  C    CB  ! chirality CA
  improper CG  CB OD1  ND2
  improper ND2 CG HD21 HD22
  improper CB  CG ND2  HD21
  improper HB1 HB2 CA CG  ! stereo CB

  dihedral CG  CB  CA  N
  dihedral OD1 CG  CB  CA ! mult 2 ! UCL

  DONO HN   N
  DONO HD21 ND2
  DONO HD22 ND2
  ACCE OD1  CG
  ACCE O    C
end


residue ASP
  group
    atom N   type=NH1   charge=-0.570 end
    atom HN  type=H     charge= 0.370 end
    atom CA  type=CH1E  charge= 0.200 end
    atom HA  type=HA    charge= 0.000 end
    atom CB  type=CH2E  charge=-0.100 end
    atom HB1 type=HA    charge= 0.000 end
    atom HB2 type=HA    charge= 0.000 end
    atom CG  type=C     charge= 0.700 end
    atom OD1 type=OC    charge=-0.800 end
    atom OD2 type=OC    charge=-0.800 end
    atom C   type=C     charge= 0.500 end
    atom O   type=O     charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG
  bond CG OD1
  bond CG OD2
  bond CA C
  bond C  O

  improper HA N  C   CB   !chirality CA
  improper CG CB OD1 OD2
  improper HB1 HB2 CA CG  !stereo CB

  dihedral CG  CB  CA  N

  dihedral OD1 CG  CB  CA

  DONO HN   N
  ACCE OD1  CG
  ACCE OD2  CG
  ACCE O    C
end


residue CYS
  group
    atom N   type=NH1    charge=-0.570 end
    atom HN  type=H      charge= 0.370 end
    atom CA  type=CH1E   charge= 0.200 end
    atom HA  type=HA     charge= 0.000 end
    atom CB  type=CH2E   charge= 0.180 end
    atom HB1 type=HA     charge= 0.000 end
    atom HB2 type=HA     charge= 0.000 end
    atom SG  type=SH1E   charge=-0.450 end
    atom HG  type=H      charge= 0.270 end
    atom C   type=C      charge= 0.500 end
    atom O   type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB SG     bond SG HG 
  bond CA C
  bond C  O

  improper HA N C CB   !chirality CA
  improper HB1 HB2 CA SG  !stereo CB

  dihedral SG  CB  CA  N

  DONO HN   N
  DONO HG  SG
  !!! ACCE SG    !REMOVED, ATB
  ACCE O    C
end


residue GLN
  group
    atom N    type=NH1     charge=-0.570 end
    atom HN   type=H       charge= 0.370 end
    atom CA   type=CH1E    charge= 0.200 end
    atom HA   type=HA      charge= 0.000 end
    atom CB   type=CH2E    charge= 0.000 end
    atom HB1  type=HA      charge= 0.000 end
    atom HB2  type=HA      charge= 0.000 end
    atom CG   type=CH2E    charge= 0.000 end
    atom HG1  type=HA      charge= 0.000 end
    atom HG2  type=HA      charge= 0.000 end
    atom CD   type=C       charge= 0.500 end
    atom OE1  type=O       charge=-0.500 end
    atom NE2  type=NH2     charge=-0.850 end
    atom HE21 type=H       charge= 0.425 end
    atom HE22 type=H       charge= 0.425 end
    atom C    type=C       charge= 0.500 end
    atom O    type=O       charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA  HA
  bond CA CB     bond CB  HB1     bond CB  HB2
  bond CB CG     bond CG  HG1     bond CG  HG2
  bond CG CD
  bond CD OE1
  bond CD NE2    bond NE2 HE21    bond NE2 HE22
  bond CA C
  bond C  O

  improper HA  N  C    CB  !chirality CA
  improper CD  CG OE1  NE2
  improper NE2 CD HE21 HE22
  improper CG  CD NE2  HE21
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB CD  !stereo CG

  dihedral CG  CB  CA  N
  dihedral CD  CG  CB  CA
  dihedral OE1 CD  CG  CB 

  DONO HN   N
  DONO HE21 NE2
  DONO HE22 NE2
  ACCE OE1  CD
  ACCE O    C
end


residue GLU
  group
    atom N   type=NH1    charge=-0.570 end
    atom HN  type=H      charge= 0.370 end
    atom CA  type=CH1E   charge= 0.200 end
    atom HA  type=HA     charge= 0.000 end
    atom CB  type=CH2E   charge= 0.000 end
    atom HB1 type=HA     charge= 0.000 end
    atom HB2 type=HA     charge= 0.000 end
    atom CG  type=CH2E   charge=-0.100 end
    atom HG1 type=HA     charge= 0.000 end
    atom HG2 type=HA     charge= 0.000 end
    atom CD  type=C      charge= 0.700 end
    atom OE1 type=OC     charge=-0.800 end
    atom OE2 type=OC     charge=-0.800 end
    atom C   type=C      charge= 0.500 end
    atom O   type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG     bond CG HG1     bond CG HG2
  bond CG CD
  bond CD OE1
  bond CD OE2
  bond CA C
  bond C  O

  improper HA N  C   CB    !chirality CA
  improper CD CG OE1 OE2
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB CD  !stereo CG

  dihedral CG  CB  CA  N
  dihedral CD  CG  CB  CA
  dihedral OE1 CD  CG  CB ! mult 2 ! UCL

  DONO HN   N
  ACCE OE1  CD
  ACCE OE2  CD
  ACCE O    C
end


residue GLY
  group
    atom N   type=NH1    charge=-0.570 end
    atom HN  type=H      charge= 0.370 end
    atom CA  type=CH2G   charge= 0.200 end
    atom HA1 type=HA     charge= 0.000 end
    atom HA2 type=HA     charge= 0.000 end
    atom C   type=C      charge= 0.500 end
    atom O   type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA1     bond CA HA2
  bond CA C
  bond C  O

  DONO HN   N
  ACCE O    C

  improper HA1 HA2 N C  !stereo CA
end


residue HISH
  group
    atom N   type=NH1     charge=-0.570 end
    atom HN  type=H       charge= 0.370 end
    atom CA  type=CH1E    charge= 0.200 end
    atom HA  type=HA      charge= 0.000 end
    atom CB  type=CH2E    charge= 0.000 end
    atom HB1 type=HA      charge= 0.000 end
    atom HB2 type=HA      charge= 0.000 end
    atom CG  type=C5      charge= 0.330 end
    atom ND1 type=NH1     charge=-0.540 end
    atom HD1 type=H       charge= 0.460 end
    atom CD2 type=CR1H    charge= 0.330 end
    atom HD2 type=HA      charge= 0.000 end
    atom CE1 type=CRHH    charge= 0.500 end
    atom HE1 type=HA      charge= 0.000 end
    atom NE2 type=NH1     charge=-0.540 end
    atom HE2 TYPE=H       charge= 0.460   END  !#
    atom C   type=C       charge= 0.500 end
    atom O   type=O       charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG
  bond CG  ND1    bond ND1 HD1
  bond ND1 CE1    bond CE1 HE1
  bond CG  CD2    bond CD2 HD2
  bond CD2 NE2    bond NE2 HE2
  bond CE1 NE2
  bond CA  C
  bond C   O

  improper HA  N   C   CB  !chirality CA
  improper CG  CB  ND1 CD2
  improper ND1 CE1 CG  HD1
  improper CD2 NE2 CG  HD2
  improper CE1 ND1 NE2 HE1
  improper CG  ND1 CE1 NE2
  improper ND1 CE1 NE2 CD2
  improper CE1 NE2 CD2 CG
  improper NE2 CD2 CG  ND1
  improper CD2 CG  ND1 CE1
  improper HB1 HB2 CA CG  ! stereo CB

  dihedral CG  CB  CA  N
  dihedral ND1 CG  CB  CA
  dihedral CD2 CG  CB  CA ! UCL added 09-MAR-00

  DONO HN   N
  DONO HD1  ND1
  DONO HE2  NE2
  ACCE O    C
end

residue HIS
  group
    atom N   type=NH1     charge=-0.570 end
    atom HN  type=H       charge= 0.370 end
    atom CA  type=CH1E    charge= 0.200 end
    atom HA  type=HA      charge= 0.000 end
    atom CB  type=CH2E    charge= 0.000 end
    atom HB1 type=HA      charge= 0.000 end
    atom HB2 type=HA      charge= 0.000 end
    atom CG  type=C5      charge= 0.330 end
    atom ND1 type=NH1     charge=-0.540 end
    atom HD1 type=H       charge= 0.460 end
    atom CD2 type=CR1H    charge= 0.330 end
    atom HD2 type=HA      charge= 0.000 end
    atom CE1 type=CRHH    charge= 0.500 end
    atom HE1 type=HA      charge= 0.000 end
    atom NE2 type=NH1     charge=-0.540 end
    atom HE2 TYPE=H       charge= 0.460 end
    atom C   type=C       charge= 0.500 end
    atom O   type=O       charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG
  bond CG  ND1    bond ND1 HD1
  bond ND1 CE1    bond CE1 HE1
  bond CG  CD2    bond CD2 HD2
  bond CD2 NE2    bond NE2 HE2
  bond CE1 NE2
  bond CA  C
  bond C   O

  improper HA  N   C   CB  !chirality CA
  improper CG  CB  ND1 CD2
  improper ND1 CE1 CG  HD1
  improper CD2 NE2 CG  HD2
  improper CE1 ND1 NE2 HE1
  improper CG  ND1 CE1 NE2
  improper ND1 CE1 NE2 CD2
  improper CE1 NE2 CD2 CG
  improper NE2 CD2 CG  ND1
  improper CD2 CG  ND1 CE1
  improper HB1 HB2 CA CG  !stereo CB

  dihedral CG  CB  CA  N
  dihedral ND1 CG  CB  CA
  dihedral CD2 CG  CB  CA ! UCL added 09-MAR-00

  DONO HN   N
  DONO HD1  ND1
  DONO HE2  NE2
  ACCE O    C
end

residue ILE
  group
    atom N    type=NH1     charge=-0.570 end
    atom HN   type=H       charge= 0.370 end
    atom CA   type=CH1E    charge= 0.200 end
    atom HA   type=HA      charge= 0.000 end
    atom CB   type=CH1E    charge= 0.000 end
    atom HB   type=HA      charge= 0.000 end
    atom CG1  type=CH2E    charge= 0.000 end
    atom HG11 type=HA      charge= 0.000 excl = (HG21 HG22 HG23 HD11 HD12 HD13) end
    atom HG12 type=HA      charge= 0.000 excl = (HG21 HG22 HG23 HD11 HD12 HD13) end
    atom CG2  type=CH3E    charge= 0.000 end
    atom HG21 type=HA      charge= 0.000 excl = (HG11 HG12 HD11 HD12 HD13) end
    atom HG22 type=HA      charge= 0.000 excl = (HG11 HG12 HD11 HD12 HD13) end
    atom HG23 type=HA      charge= 0.000 excl = (HG11 HG12 HD11 HD12 HD13) end
    atom CD1  type=CH3E    charge= 0.000 end
    atom HD11 type=HA      charge= 0.000 excl = (HG21 HG22 HG23 HG11 HG12) end
    atom HD12 type=HA      charge= 0.000 excl = (HG21 HG22 HG23 HG11 HG12) end
    atom HD13 type=HA      charge= 0.000 excl = (HG21 HG22 HG23 HG11 HG12) end
    atom C    type=C       charge= 0.500 end
    atom O    type=O       charge=-0.500 end
  
  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB
  bond CB  CG1    bond CG1 HG11    bond CG1 HG12
  bond CB  CG2    bond CG2 HG21    bond CG2 HG22    bond CG2 HG23
  bond CG1 CD1    bond CD1 HD11    bond CD1 HD12    bond CD1 HD13
  bond CA  C
  bond C   O

  improper HA N  C   CB   !chirality CA
  improper HB CA CG2 CG1  !chirality CB
  
  improper HG11 HG12 CB CD1  !stereo CG1
  improper HG21 HG22 CB HG23   !methyl CG2
  improper HD11 HD12 CG1 HD13  !methyl CD1

  dihedral CG1 CB  CA  N
  dihedral CD1 CG1 CB  CA
  dihedral HD11 CD1 CG1 CB   ! UCL methyl stagger 12-MAR-00 
  dihedral HG21 CG2 CB  CA   ! UCL methyl stagger 12-MAR-00 

  DONO HN   N
  ACCE O    C
end


residue LEU
  group
    atom N    type=NH1    charge=-0.570 end
    atom HN   type=H      charge= 0.370 end
    atom CA   type=CH1E   charge= 0.200 end
    atom HA   type=HA     charge= 0.000 end
    atom CB   type=CH2E   charge= 0.000 end
    atom HB1  type=HA     charge= 0.000 end
    atom HB2  type=HA     charge= 0.000 end
    atom CG   type=CH1E   charge= 0.000 end
    atom HG   type=HA     charge= 0.000 end
    atom CD1  type=CH3E   charge= 0.000 end
    atom HD11 type=HA     charge= 0.000 excl = (HD21 HD22 HD23 HG) end
    atom HD12 type=HA     charge= 0.000 excl = (HD21 HD22 HD23 HG) end
    atom HD13 type=HA     charge= 0.000 excl = (HD21 HD22 HD23 HG) end
    atom CD2  type=CH3E   charge= 0.000 end
    atom HD21 type=HA     charge= 0.000 excl = (HD11 HD12 HD13 HG) end
    atom HD22 type=HA     charge= 0.000 excl = (HD11 HD12 HD13 HG) end
    atom HD23 type=HA     charge= 0.000 excl = (HD11 HD12 HD13 HG) end
    atom C    type=C      charge= 0.500 end
    atom O    type=O      charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG     bond CG  HG
  bond CG  CD1    bond CD1 HD11    bond CD1 HD12    bond CD1 HD13
  bond CG  CD2    bond CD2 HD21    bond CD2 HD22    bond CD2 HD23
  bond CA  C
  bond C   O

  improper HA   N    C   CB    !chirality CA
  improper HG   CB   CD1 CD2   !stereo CG
  improper HB1 HB2 CA CG       !stereo CB
  improper HD11 HD12 CG HD13   !methyl CD1
  improper HD21 HD22 CG HD23   !methyl CD2
    
  dihedral CG  CB  CA  N
  dihedral CD1 CG  CB  CA
  dihedral HD11 CD1 CG  CB   ! UCL methyl stagger 12-MAR-00 
  dihedral HD21 CD2 CG  CB   ! UCL methyl stagger 12-MAR-00 

  DONO HN   N
  ACCE O    C
end


residue LYS
  group
    atom N   type=NH1    charge=-0.570 end
    atom HN  type=H      charge= 0.370 end
    atom CA  type=CH1E   charge= 0.200 end
    atom HA  type=HA     charge= 0.000 end
    atom CB  type=CH2E   charge= 0.000 end
    atom HB1 type=HA     charge= 0.000 end
    atom HB2 type=HA     charge= 0.000 end
    atom CG  type=CH2E   charge= 0.000 end
    atom HG1 type=HA     charge= 0.000 end
    atom HG2 type=HA     charge= 0.000 end
    atom CD  type=CH2E   charge= 0.000 end
    atom HD1 type=HA     charge= 0.000 end
    atom HD2 type=HA     charge= 0.000 end
    atom CE  type=CH2E   charge= 0.310 end
    atom HE1 type=HA     charge= 0.000 end
    atom HE2 type=HA     charge= 0.000 end
    atom NZ  type=NH3    charge=-0.300 end
    atom HZ1 type=HC     charge= 0.330 end
    atom HZ2 type=HC     charge= 0.330 end
    atom HZ3 type=HC     charge= 0.330 end
    atom C   type=C      charge= 0.500 end
    atom O   type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG     bond CG HG1     bond CG HG2
  bond CG CD     bond CD HD1     bond CD HD2
  bond CD CE     bond CE HE1     bond CE HE2
  bond CE NZ     bond NZ HZ1     bond NZ HZ2     bond NZ HZ3
  bond CA C
  bond C  O

  improper HA N C CB      !chirality CA
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB CD  !stereo CG
  improper HD1 HD2 CG CE  !stereo CD
  improper HE1 HE2 CD NZ  !stereo CE
  improper HZ1 HZ2 CE HZ3 !methyl NZ

  dihedral CG  CB  CA  N
  dihedral CD  CG  CB  CA
  dihedral CE  CD  CG  CB
  dihedral NZ  CE  CD  CG
  dihedral HZ1 NZ  CE  CD ! UCL stagger NH3 group 12-MAR-00

  DONO HN   N
  DONO HZ1  NZ
  DONO HZ2  NZ
  DONO HZ3  NZ
  ACCE O    C
end

residue MET
  group
    atom N   type=NH1     charge=-0.570 end
    atom HN  type=H       charge= 0.370 end
    atom CA  type=CH1E    charge= 0.200 end
    atom HA  type=HA      charge= 0.000 end
    atom CB  type=CH2E    charge=-0.000 end
    atom HB1 type=HA      charge= 0.000 end
    atom HB2 type=HA      charge= 0.000 end
    atom CG  type=CH2E    charge= 0.235 end
    atom HG1 type=HA      charge= 0.000 end
    atom HG2 type=HA      charge= 0.000 end
    atom SD  type=SM      charge=-0.470 end
    atom CE  type=CH3E    charge= 0.235 end
    atom HE1 type=HA      charge= 0.000 end
    atom HE2 type=HA      charge= 0.000 end
    atom HE3 type=HA      charge= 0.000 end
    atom C   type=C       charge= 0.500 end
    atom O   type=O       charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG     bond CG HG1     bond CG HG2
  bond CG SD
  bond SD CE     bond CE HE1     bond CE HE2     bond CE HE3
  bond CA C
  bond C  O

  improper HA N C CB      !chirality CA
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB SD  !stereo CG
  improper HE1 HE2 SD HE3 !methyl CE

  dihedral CG  CB  CA  N
  dihedral SD  CG  CB  CA
  dihedral CE  SD  CG  CB
  dihedral HE1 CE  SD  CG ! UCL methyl stagger 12-MAR-00

  DONO HN   N
  ACCE O    C
end


residue PHE
  group
    atom N   type=NH1     charge=-0.570 end
    atom HN  type=H       charge= 0.370 end
    atom CA  type=CH1E    charge= 0.200 end
    atom HA  type=HA      charge= 0.000 end
    atom CB  type=CH2E    charge= 0.000 end
    atom HB1 type=HA      charge= 0.000 end
    atom HB2 type=HA      charge= 0.000 end
    atom CG  type=CF      charge= 0.000 exclude=(CZ) end
    atom CD1 type=CR1E    charge= 0.000 exclude=(CE2) end
    atom HD1 type=HA      charge= 0.000 end
    atom CD2 type=CR1E    charge= 0.000 exclude=(CE1) end
    atom HD2 type=HA      charge= 0.000 end
    atom CE1 type=CR1E    charge= 0.000 exclude=(CD2) end
    atom HE1 type=HA      charge= 0.000 end
    atom CE2 type=CR1E    charge= 0.000 exclude=(CD1) end
    atom HE2 type=HA      charge= 0.000 end
    atom CZ  type=CR1E    charge= 0.000 exclude=(CG) end
    atom HZ  type=HA      charge= 0.000 end
    atom C   type=C       charge= 0.500 end
    atom O   type=O       charge=-0.500 end
  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG
  bond CG  CD1    bond CD1 HD1
  bond CG  CD2    bond CD2 HD2
  bond CD1 CE1    bond CE1 HE1
  bond CD2 CE2    bond CE2 HE2
  bond CE1 CZ     bond CZ  HZ
  bond CE2 CZ
  bond CA  C
  bond C   O

  improper HA  N   C   CB !chirality CA
  improper HB1 HB2 CA CG  !stereo CB

! Hs and CB around the ring
  improper HD2 CD2 CE2 CZ
  improper HE2 CE2 CZ  CE1
  improper HZ  CZ  CE1 CD1
  improper HE1 CE1 CD1 CG
  improper HD1 CD1 CG  CD2
  improper CB  CG  CD2 CE2

! around the ring
  improper CG  CD1 CE1 CZ 
  improper CD1 CE1 CZ  CE2
  improper CE1 CZ  CE2 CD2
  improper CZ  CE2 CD2 CG
  improper CE2 CD2 CG  CD1
  improper CD2 CG  CD1 CE1

  dihedral CG  CB  CA  N
  dihedral CD1 CG  CB  CA

  DONO HN   N
  ACCE O    C
end


residue PRO
  group
    atom N   type=N     charge=-0.570 end
    atom CA  type=CH1E  charge= 0.285 end
    atom HA  type=HA    charge= 0.000 end
    atom CB  type=CH2E  charge= 0.000 end
    atom HB1 type=HA    charge= 0.000 end
    atom HB2 type=HA    charge= 0.000 end
    atom CG  type=CH2P  charge= 0.000 end
    atom HG1 type=HA    charge= 0.000 end
    atom HG2 type=HA    charge= 0.000 end
    atom CD  type=CH2P  charge= 0.285 end
    atom HD1 type=HA    charge= 0.000 end   
    atom HD2 type=HA    charge= 0.000 end   
    atom C   type=C     charge= 0.500 end   
    atom O   type=O     charge=-0.500 end

  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG     bond CG HG1     bond CG HG2
  bond CG CD     bond CD HD1     bond CD HD2
  bond CD N
  bond CA C
  bond C  O

  improper HA N C CB      !chirality CA
  improper HB1 HB2 CA CG  !stereo CB
  improper HG1 HG2 CB CD  !stereo CG
  improper HD1 HD2 CG N   !stereo CD

  ACCE O    C
end


residue SER
  group
    atom N   type=NH1    charge=-0.570 end
    atom HN  type=H      charge= 0.370 end
    atom CA  type=CH1E   charge= 0.200 end
    atom HA  type=HA     charge= 0.000 end
    atom CB  type=CH2E   charge= 0.265 end
    atom HB1 type=HA     charge= 0.000 end
    atom HB2 type=HA     charge= 0.000 end
    atom OG  type=OH1    charge=-0.700 end
    atom HG  type=H      charge= 0.435 end
    atom C   type=C      charge= 0.500 end
    atom O   type=O      charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB OG     bond OG HG
  bond O  C
  bond C  CA

  improper HA N C CB      !chirality CA
  improper HB1 HB2 CA OG  !stereo CB

  dihedral OG  CB  CA  N

  DONO HN   N
  DONO HG   OG
  ACCE OG  " "
  ACCE O    C
end


residue THR
  group
    atom N    type=NH1 charge=-0.570 end
    atom HN   type=H   charge= 0.370 end
    atom CA   type=CH1E  charge= 0.200 end
    atom HA   type=HA  charge= 0.000 end
    atom CB   type=CH1E  charge= 0.265 end
    atom HB   type=HA  charge= 0.000 end
    atom OG1  type=OH1  charge=-0.700 end
    atom HG1  type=H   charge= 0.435 end
    atom CG2  type=CH3E  charge=-0.000 end
    atom HG21 type=HA  charge= 0.000 end
    atom HG22 type=HA  charge= 0.000 end
    atom HG23 type=HA  charge= 0.000 end
    atom C    type=C   charge= 0.500 end
    atom O    type=O   charge=-0.500 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB
  bond CB OG1    bond OG1 HG1
  bond CB CG2    bond CG2 HG21    bond CG2 HG22    bond CG2 HG23
  bond CA C
  bond C  O

  improper HA N  C   CB        !chirality CA
  improper HB CA OG1 CG2       !stereo CB
  improper HG21 HG22 CB HG23   !methyl CG2

  dihedral OG1 CB  CA  N
  dihedral HG21 CG2 CB  CA   ! UCL methyl stagger 12-MAR-00 

  DONO HN   N
  DONO HG1  OG1
  ACCE OG1 " "
  ACCE O    C
end


residue TRP
  group
    atom N   type=NH1 charge=-0.570 end
    atom HN  type=H   charge= 0.370 end
    atom CA  type=CH1E  charge= 0.200 end
    atom HA  type=HA  charge= 0.000 end
    atom CB  type=CH2E  charge= 0.000 end
    atom HB1 type=HA  charge= 0.000 end
    atom HB2 type=HA  charge= 0.000 end
    atom CG  type=C5W  charge=-0.055 end
    atom CD1 type=CR1E  charge= 0.130 end
    atom HD1 type=HA  charge= 0.000 end
    atom CD2 type=CW  charge=-0.055 exclude=(CH2) end
    atom NE1 type=NH1 charge=-0.570 end
    atom HE1 type=H   charge= 0.420 end
    atom CE2 type=CW  charge= 0.130 exclude=(CZ3) end
    atom CE3 type=CR1E  charge= 0.000 exclude=(CZ2) end
    atom HE3 type=HA  charge= 0.000 end
    atom CZ2 type=CR1W charge= 0.000 exclude=(CE3) end
    atom HZ2 type=HA  charge= 0.000 end
    atom CZ3 type=CR1E  charge= 0.000 exclude=(CE2) end
    atom HZ3 type=HA  charge= 0.000 end
    atom CH2 type=CR1W charge= 0.000 exclude=(CD2) end
    atom HH2 type=HA  charge= 0.000 end
    atom C   type=C   charge= 0.500 end
    atom O   type=O   charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG
  bond CG  CD1    bond CD1 HD1
  bond CG  CD2
  bond CD1 NE1    bond NE1 HE1
  bond NE1 CE2
  bond CD2 CE2
  bond CD2 CE3    bond CE3 HE3
  bond CE2 CZ2    bond CZ2 HZ2
  bond CE3 CZ3    bond CZ3 HZ3
  bond CZ2 CH2    bond CH2 HH2
  bond CZ3 CH2
  bond CA  C
  bond C   O

! chirality
  improper HA  N   C   CB !chirality CA
  improper HB1 HB2 CA CG  !stereo CB

! around the 6-ring
  improper CD2 CE2 CZ2 CH2
  improper CE2 CZ2 CH2 CZ3
  improper CZ2 CH2 CZ3 CE3
  improper CH2 CZ3 CE3 CD2
  improper CZ3 CE3 CD2 CE2
  improper CE3 CD2 CE2 CZ2

! link 5-ring to 6-ring
  improper CD1 NE1 CE2 CZ2
  improper CD1 CG  CD2 CE3
  improper NE1 CE2 CZ2 CH2
  improper NE1 CE2 CD2 CE3
  improper CG  CD2 CE3 CZ3
  improper CG  CD2 CE2 CZ2

! 6-ring hydrogens
  improper HZ2 CZ2 CH2 CZ3
  improper HH2 CH2 CZ3 CE3
  improper HZ3 CZ3 CH2 CZ2
  improper HE3 CE3 CZ3 CH2

! 5-ring hydrogens and CB
  improper HE1 NE1 CE2 CD2
  improper HD1 CD1 NE1 CE2
  improper CB  CG  CD2 CE2

  dihedral CG  CB  CA  N
  dihedral CD1 CG  CB  CA

  DONO HN   N
  DONO HE1  NE1
  ACCE O    C
end

residue TYR
  group
    atom N   type=NH1 charge=-0.570 end
    atom HN  type=H   charge= 0.370 end
    atom CA  type=CH1E  charge= 0.200 end
    atom HA  type=HA  charge= 0.000 end
    atom CB  type=CH2E  charge= 0.000 end
    atom HB1 type=HA  charge= 0.000 end
    atom HB2 type=HA  charge= 0.000 end
    atom CG  type=CY  charge= 0.000 exclude=(CZ) end
    atom CD1 type=CR1E  charge= 0.000 exclude=(CE2) end
    atom HD1 type=HA  charge= 0.000 end
    atom CD2 type=CR1E  charge= 0.000 exclude=(CE1) end
    atom HD2 type=HA  charge= 0.000 end
    atom CE1 type=CR1E  charge= 0.000 exclude=(CD2) end
    atom HE1 type=HA  charge= 0.000 end
    atom CE2 type=CR1E  charge= 0.000 exclude=(CD1) end
    atom HE2 type=HA  charge= 0.000 end
    atom CZ  type=CY2   charge= 0.265 exclude=(CG) end
    atom OH  type=OH1  charge=-0.700 end
    atom HH  type=H   charge= 0.435 end
    atom C   type=C   charge= 0.500 end
    atom O   type=O   charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB1     bond CB  HB2
  bond CB  CG
  bond CG  CD1    bond CD1 HD1
  bond CG  CD2    bond CD2 HD2
  bond CD1 CE1    bond CE1 HE1
  bond CD2 CE2    bond CE2 HE2
  bond CE1 CZ
  bond CE2 CZ
  bond CZ  OH     bond OH  HH
  bond CA  C
  bond C   O

! chirality
  improper HA  N   C   CB !chirality CA
  improper HB1 HB2 CA CG  !stereo CB

! Hs, OH, and CB around the ring
  improper HD2 CD2 CE2 CZ
  improper HE2 CE2 CZ  CE1
  improper OH  CZ  CE1 CD1
  improper HE1 CE1 CD1 CG
  improper HD1 CD1 CG  CD2
  improper CB  CG  CD2 CE2

! around the ring
  improper CG  CD1 CE1 CZ 
  improper CD1 CE1 CZ  CE2
  improper CE1 CZ  CE2 CD2
  improper CZ  CE2 CD2 CG
  improper CE2 CD2 CG  CD1
  improper CD2 CG  CD1 CE1

  dihedral CG  CB  CA  N
  dihedral CD1 CG  CB  CA
  dihedral CE2 CZ  OH  HH   ! UCL Added 12-MAR-00

  DONO HN   N
  DONO HH   OH
  ACCE OH  " "
  ACCE O    C
end


residue VAL
  group
    atom N    type=NH1 charge=-0.570 end
    atom HN   type=H   charge= 0.370 end
    atom CA   type=CH1E  charge= 0.200 end
    atom HA   type=HA  charge= 0.000 end
    atom CB   type=CH1E  charge= 0.000 end
    atom HB   type=HA  charge= 0.000 end
    atom CG1  type=CH3E  charge= 0.000 end
    atom HG11 type=HA  charge= 0.000 excl = (HG21 HG22 HG23) end
    atom HG12 type=HA  charge= 0.000 excl = (HG21 HG22 HG23) end
    atom HG13 type=HA  charge= 0.000 excl = (HG21 HG22 HG23) end
    atom CG2  type=CH3E  charge=-0.000 end
    atom HG21 type=HA  charge= 0.000 excl = (HG11 HG12 HG13) end
    atom HG22 type=HA  charge= 0.000 excl = (HG11 HG12 HG13) end
    atom HG23 type=HA  charge= 0.000 excl = (HG11 HG12 HG13) end
    atom C    type=C   charge= 0.500 end
    atom O    type=O   charge=-0.500 end

  bond N   HN
  bond N   CA     bond CA  HA
  bond CA  CB     bond CB  HB
  bond CB  CG1    bond CG1 HG11    bond CG1 HG12    bond CG1 HG13
  bond CB  CG2    bond CG2 HG21    bond CG2 HG22    bond CG2 HG23
  bond CA  C
  bond C   O

  improper HA N C CB         !chirality CA
  improper HB   CA   CG1 CG2 !stereo CB
  improper HG11 HG12 CB HG13    !methyl G1
  improper HG21 HG22 CB HG23    !methyl G2

  dihedral CG1 CB  CA  N
  dihedral HG11 CG1 CB  CA   ! UCL methyl stagger 12-MAR-00 
  dihedral HG21 CG2 CB  CA   ! UCL methyl stagger 12-MAR-00 

  DONO HN   N
  ACCE O    C
end




residue CHEX  !! ADDED BY MN
  group
    atom N   type=NH1 charge=-0.360 end
    atom HN  type=H   charge= 0.260 end
    atom CA  type=CH1E  charge= 0.000 end
    atom HA  type=HA  charge= 0.100 end
    atom CB  type=CH2E  charge=-0.200 end
    atom HB1 type=HA  charge= 0.100 end
    atom HB2 type=HA  charge= 0.100 end
    atom CG  type=CH1E  charge=-0.200 end
    atom HG  type=HA  charge= 0.100 end
    atom CD1  type=CH2E  charge=-0.200 end
    atom HD11 type=HA  charge= 0.100 end
    atom HD12 type=HA  charge= 0.100 end
    atom CD2  type=CH2E  charge=-0.200 end
    atom HD21 type=HA  charge= 0.100 end
    atom HD22 type=HA  charge= 0.100 end
    atom CE1  type=CH2E  charge=-0.200 end
    atom HE11 type=HA  charge= 0.100 end
    atom HE12 type=HA  charge= 0.100 end
    atom CE2  type=CH2E  charge=-0.200 end
    atom HE21 type=HA  charge= 0.100 end
    atom HE22 type=HA  charge= 0.100 end
    atom CZ  type=CH2E  charge=-0.200 end
    atom HZ1 type=HA  charge= 0.100 end
    atom HZ2 type=HA  charge= 0.100 end
    atom C   type=C   charge= 0.480 end
    atom O   type=O   charge=-0.480 end

  bond N  HN
  bond N  CA     bond CA HA
  bond CA CB     bond CB HB1     bond CB HB2
  bond CB CG     bond CG CD1     bond CG CD2     bond CG HG    
  bond CD1 CE1   bond CD1 HD11    bond CD1 HD12   
  bond CD2 CE2   bond CD2 HD21    bond CD2 HD22
  bond CE1 CZ    bond CE1 HE11    bond CE1 HE12
  bond CE2 CZ    bond CE2 HE21    bond CE2 HE22
  bond CZ HZ1    bond CZ  HZ2
  bond CA C
  bond C  O

  improper HA N C CB          !chirality CA
  improper HB1 HB2 CA CG  !stereo CB
  improper HG CB CD1 CD2      !stereo CG
  improper HD11 HD12 CG CE1      !stereo CD1
  improper HD21 HD22 CG CE2      !stereo CD2
  improper HE11 HE12 CE1 CZ      !stereo CE1
  improper HE11 HE22 CE2 CZ      !stereo CE2
  improper HZ1 HZ2 CE1 CE2  !stereo CZ

  dihedral CG  CB  CA  N
  dihedral CD1  CG  CB  CA

  DONO HN   N
  ACCE O    C
end





residue ACE
  group
    atom CA  type=CH3E charge= 0.000 end
    atom HA1 type=HA charge= 0.000 end
    atom HA2 type=HA charge= 0.000 end
    atom HA3 type=HA charge= 0.000 end
    atom C   type=C  charge= 0.500 end
    atom O   type=O  charge=-0.500 end

  bond C  CA     bond CA HA1     bond CA HA2     bond CA HA3
  bond C  O

  improper HA1 HA2 C HA3  !methyl CA

  ACCE O    C
end




presidue NTER                      ! patch as "NTER - *" to any except PRO
  group
    modify    atom +N   type=NH3 charge=-0.300 end
    delete    atom +HN                        end
    add       atom +HT1 type=HC  charge= 0.330 end
    add       atom +HT2 type=HC  charge= 0.330 end
    add       atom +HT3 type=HC  charge= 0.330 end
    modify    atom +CA           charge= 0.310 end

  add bond +HT1 +N
  add bond +HT2 +N
  add bond +HT3 +N

  add angle +HT1 +N +HT2
  add angle +HT2 +N +HT3
  add angle +HT2 +N +CA
  add angle +HT1 +N +HT3
  add angle +HT1 +N +CA
  add angle +HT3 +N +CA
  add improper +HT1 +HT2 +CA +HT3  !methyl N ???

  add dihedral +C  +CA  +N  +HT1      ! UCL (12-MAR-00)

  ADD DONOr +HT1  +N
  ADD DONOr +HT2  +N
  ADD DONOr +HT3  +N
end


presidue PROP                        ! N-terminal for PRO: "PROP - PRO"
! the charges are guessed from making the residue have charge +1
! and keeping the same charge on N as in NTER (Michael Nilges)
  modify    atom +CD           charge= 0.320 end
  modify    atom +CA           charge= 0.320 end
  modify    atom +N   type=NH3 charge=-0.300 end
  add       atom +HT1 type=HC  charge= 0.330 end
  add       atom +HT2 type=HC  charge= 0.330 end

  add bond +HT1 +N
  add bond +HT2 +N

  add angle +HT1 +N +HT2
  add angle +HT2 +N +CA
  add angle +HT1 +N +CD
  add angle +HT1 +N +CA
  add angle +CD  +N +HT2
  add improper +HT1 +HT2 +CA +CD  !stereo N 
 
  ADD DONOr +HT1  +N
  ADD DONOr +HT2  +N
end
 

presidue CTER               ! C-terminal for all amino acids "* - CTER"
! charge on -C changed from 0.700 to make group -1, Michael Nilges
  group
    modify    atom -CA            charge= 0.100  end
    modify    atom -C             charge= 0.700  end
    delete    atom -O                            end
    add       atom -OT1 type=OC   charge=-0.800  end
    add       atom -OT2 type=OC   charge=-0.800  end

  add bond -C -OT1
  add bond -C -OT2

  add angle -CA  -C -OT1
  add angle -CA  -C -OT2
  add angle -OT1 -C -OT2

  add improper -C -CA -OT2 -OT1
 
  add dihedral -N -CA -C -OT1      ! UCL (12-MAR-00)

  ADD ACCEptor -OT1 -C
  ADD ACCEptor -OT2 -C
end


presidue CTN                  ! C-terminal for all, CONH2 at end "* - CTN"
! charges not consistent with rest, Michael Nilges
  group
    modify    atom -C           charge= 0.48 end
    modify    atom -O           charge=-0.48 end
    add       atom -NT type=NH2 charge=-0.52 end
    add       atom -H1 type=H   charge= 0.26 end
    add       atom -H2 type=H   charge= 0.26 end

  add bond -C  -NT
  add bond -NT -H1
  add bond -NT -H2

  add angle -CA -C  -NT
  add angle -O  -C  -NT
  add angle -CA -C  -O
  add angle -C  -NT -H1
  add angle -C  -NT -H2
  add angle -H1 -NT -H2

  add improper -C  -CA -NT -O
  add improper -C  -NT -O  -H1
  add improper -NT -H1 -H2 -C

  add dihedral -N -CA -C -NT      ! UCL (12-MAR-00)

  ADD DONOR  -H1 -NT
  ADD DONOR  -H2 -NT
end


presidue PEPT     ! PEPTide bond link, for all except the  *(-) - (+)PRO link
                  ! "*(-) - PEPT - (+)*:
  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +HN

  add improper  -C -CA +N -O                 ! planar -C
  add improper  +N -C +CA +HN                ! planar +N
  add improper -CA -C  +N  +CA               ! angle across peptide plane

! phi/psi related topology UCL 05-JUL-01

  add dihedral  -C +N +CA +C  mult 6
  add dihedral  -C +N +CA +CB mult 6
  add dihedral  -CB -CA -C +N mult 6
  add dihedral  -CB -CA -C -O mult 6         ! corrected from +O 16-Sept-02
end
 

presidue PEPP     ! for  ...*(-) - (+)PRO  link, same as PEPT except
                  ! replacement H by CD and improper +N +CA +CD -C
  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +CD

!  ADD DIHEdral  -C +N +CA +C  ! taken out since related to phi MN 18-MAR-02
!  ADD DIHEdral  -N -CA -C +N  ! taken out since equivalent below MN 18-MAR-02
!  ADD DIHEdral  -CA -C +N +CA ! taken out since improper below MN 18-MAR-02

  add improper  -C  -CA +N  -O               ! planar -C
  add improper  +N  -C +CA +CD               ! planar +N
  add improper -CA  -C  +N  +CA              ! angle across peptide plane

! psi related topology N.B. phi is fixed by ring bonding 05-JUL-01

  add dihedral  -CB -CA -C +N mult 6
  add dihedral  -CB -CA -C -O mult 6         ! corrected from +O 16-Sept-02
end


presidue PPGP     ! for  GLY(-) - (+)PRO  link, same as PEPT except
                  ! replacement H by CD and improper +N +CA +CD -C
  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +CD

!  ADD DIHEdral  -C +N +CA +C  ! taken out since related to phi MN 18-MAR-02
!  ADD DIHEdral  -N -CA -C +N  ! taken out since equivalent below MN 18-MAR-02
!  ADD DIHEdral  -CA -C +N +CA ! taken out since improper below MN 18-MAR-02

  add improper  -C  -CA +N  -O               ! planar -C
  add improper  +N  -C +CA +CD               ! planar +N
  add improper -CA  -C  +N  +CA              ! angle across peptide plane

end


PRESidue PPGG { for GLY (-) - (+) GLY LINK }

  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +HN

  add improper  -C -CA +N -O                 ! planar -C
  add improper  +N -C +CA +HN                ! planar +N
  add improper -CA -C  +N  +CA               ! angle across peptide plane

! phi/psi related topology UCL 05-JUL-01

  add dihedral  -C +N +CA +C  mult 6
end

PRESidue PPG1 { for ...*(-) - (+) GLY LINK }

  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +HN

  add improper  -C -CA +N -O                 ! planar -C
  add improper  +N -C +CA +HN                ! planar +N
  add improper -CA -C  +N  +CA               ! angle across peptide plane

! phi/psi related topology UCL 05-JUL-01

  add dihedral  -C +N +CA +C  mult 6
  add dihedral  -CB -CA -C +N mult 6
  add dihedral  -CB -CA -C -O mult 6          ! corrected from +O 16-Sept-02

end


PRESidue PPG2 { for ... GLY(-) - (+) * LINK }
  add bond -C +N

  add angle -CA -C +N
  add angle -O  -C +N
  add angle -C  +N +CA
  add angle -C  +N +HN

  add improper  -C -CA +N -O                  ! planar -C
  add improper  +N -C +CA +HN                 ! planar +N
  add improper -CA -C  +N  +CA                ! angle across peptide plane

! phi/psi related topology UCL 05-JUL-01

  add dihedral  -C +N +CA +C  mult 6
  add dihedral  -C +N +CA +CB mult 6
end



presidue DISU                ! disulfide bridge  ...CYS - DISU - CYS...
  group
    delete    atom 1HG               end
    modify    atom 1CB              charge= 0.300 end
    MODIfy    ATOM 1SG  TYPE=S      charge=-0.300 end
  group
    delete    atom 2HG               end
    modify    atom 2CB              charge= 0.300 end
    MODIfy    ATOM 2SG  TYPE=S      charge=-0.300 end

  add bond 1SG 2SG

  add angle 1CB 1SG 2SG
  add angle 1SG 2SG 2CB

  add dihedral 1CB 1SG 2SG 2CB mult 6   ! UCL modified 12-MAR-00 & 07-JUL-01
end


presidue DISN                ! disulfide bridge  ...CYS - DISU - CYS...
                             ! w/o the actual bond
  group
    delete    atom 1HG               end
    modify    atom 1CB              charge= 0.300 end
    MODIfy    ATOM 1SG  TYPE=S      charge=-0.300 end
  group
    delete    atom 2HG               end
    modify    atom 2CB              charge= 0.300 end
    MODIfy    ATOM 2SG  TYPE=S      charge=-0.300 end
end


presidue LTOD                        ! change from L to D amino acid
  delete improper HA N C CB
  add    improper HA C N CB
end

presidue CISP                        ! change from trans to cis peptide bond
  modify atom C type=CCIS end
end
presidue CIPP                        ! change from trans to cis peptide bond. not necessary to have separate patch
  modify atom C type=CCIS end
end


!--------------------------------------------------------------------------

PRESidue HISE   ! Patch to change doubly protonated HIS to singly
                ! protonated histidine (HE2)
                ! has to be patched as REFErence=NIL=<selection>

  !DELETE DONOR  ND1 HD1
  MODIFY ATOM  CB   TYPE=CH2E    CHARge= 0.000  END
  MODIFY ATOM  CG   TYPE=C5      CHARge= 0.130  END !#
  MODIFY ATOM  ND1  TYPE=NR      CHARge=-0.570  END !#
  MODIFY ATOM  CE1  TYPE=CRH     CHARge= 0.410  END !#
  MODIFY ATOM  CD2  TYPE=CR1E    CHARge= 0.100  END
  MODIFY ATOM  NE2  TYPE=NH1     CHARge=-0.570  END !#
  MODIFY ATOM  HE2  TYPE=H       CHARge= 0.420  END !#
  DELETE ATOM  HD1                              END

  ADD ACCEPTOR  ND1 " "
END {HISE}

!--------------------------------------------------------------------------

PRES HISD   ! Patch to change doubly protonated HIS to singly
            ! protonated histidine (HD1)
            ! has to be patched as REFErence=NIL=<selection>
  !DELETE DONOR HE2 NE2
  MODIFY ATOM  CB   TYPE=CH2E    CHARge= 0.000  END
  MODIFY ATOM  CG   TYPE=C5      CHARge= 0.130  END !#
  MODIFY ATOM  ND1  TYPE=NH1     CHARge=-0.570  END  !#
  MODIFY ATOM  HD1  TYPE=H       CHARge= 0.420  END  !#
  MODIFY ATOM  CD2  TYPE=CR1E    CHARge= 0.100  END  !#
  MODIFY ATOM  NE2  TYPE=NR      CHARge=-0.490  END  !#
  MODIFY ATOM  CE1  TYPE=CRH     CHARge= 0.410  END  !#
  DELETE ATOM  HE2                              END

  ADD ACCEPTOR NE2 " "

END {HISD}




set echo=true end
