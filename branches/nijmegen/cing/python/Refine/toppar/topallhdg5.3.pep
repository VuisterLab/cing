REMARKS  TOPH19.pep -MACRO for protein sequence
SET ECHO=FALSE END

! this is a macro to define standard protein peptide bonds
! and termini to generate a protein sequence.
! it should be added as @topallhdg5.3.pep in the SEGMent SEQUence
! level.
! 
! Author: Axel Brunger, 19-JAN-84
! modified for topallhdg5.3: Michael Nilges, 21-MAR-02

! Edited GV 22 May: removed NTER CTER statements
! Edited GV 22 May because of errors:
! %SEGMENT-ERR: max. number of FIRST exceeded
! %SEGMENT-ERR: max. number of FIRST exceeded
! %SEGMENT-ERR: max. number of FIRST exceeded
! %SEGMENT-ERR: max. number of FIRST exceeded
! %SEGMENT-ERR: max. number of FIRST exceeded
! %SEGMENT-ERR: max. number of LAST exceeded
! %SEGMENT-ERR: max. number of LAST exceeded
! %SEGMENT-ERR: max. number of LAST exceeded

! Edited JFD 2011-05-06 adjusted for working with NRG-CING setup.
!   Reenabled the proper NTER patches.


link  PPGP head - GLY tail + PRO end
link  PPGG head - GLY tail + GLY end 
link  PEPP head - *   tail + PRO end
link  PPG2 head - GLY tail + *   end
link  PPG1 head - *   tail + GLY end
link  PEPT head - *   tail + *   end

!first IONS            tail + NA1 end
!first IONS            tail + CL1 end
first IONS            tail + CA2 end
first IONS            tail + CU2 end
first IONS            tail + CU3 end
first IONS            tail + MG2 end
first IONS            tail + FE2 end
first IONS            tail + ZN2 end
!first IONS            tail + SO4 end
!first IONS            tail + PO4 end
!first IONS            tail + HEB end
!first IONS            tail + HEC end
first PROP            tail + PRO end
first NTER            tail + *   end
first ACET            tail + ACE end

!last  IONS head - NA1            end
!last  IONS head - CL1            end
last  IONS head - CA2            end
last  IONS head - CU2            end
last  IONS head - CU3            end
last  IONS head - MG2            end
last  IONS head - FE2            end
last  IONS head - ZN2            end
!last  IONS head - SO4            end
!last  IONS head - PO4            end
!last  IONS head - HEB            end
!last  IONS head - HEC            end
last  CTER head - *              end


SET ECHO=TRUE END
