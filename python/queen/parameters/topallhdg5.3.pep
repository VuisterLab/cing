REMARKS  TOPH19.pep -MACRO for protein sequence
SET ECHO=FALSE END

! this is a macro to define standard protein peptide bonds
! and termini to generate a protein sequence.
! it should be added as @topallhdg5.3.pep in the SEGMent SEQUence
! level.
! 
! Author: Axel Brunger, 19-JAN-84
! modified for topallhdg5.3: Michael Nilges, 21-MAR-02

! replaced PEGP with PPGP to be consistent with topallhdg5.3.pro (JL):
link  PPGP head - GLY tail + PRO end

link  PPGG head - GLY tail + GLY end 
link  PEPP head - *   tail + PRO end
link  PPG2 head - GLY tail + *   end
link  PPG1 head - *   tail + GLY end
link  PEPT head - *   tail + *   end

first PROP            tail + PRO end
first NTER            tail + *   end

last  CTER head - *              end


SET ECHO=TRUE END
