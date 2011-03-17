VASCO_STR       = "Vasco" # key to the entities (atoms, residues, etc under which the results will be stored

H_STR = 'H'
N_STR = 'N'
C_STR = 'C'
C_ALIPHATIC_STR = 'C_aliphatic'

vascoAtomInfo = (
            (H_STR, (H_STR, None)),
            (N_STR, (N_STR, None)),
            (C_ALIPHATIC_STR, (C_STR, 3)))

vascoAtomTypeList = ( H_STR, N_STR, C_STR )

# The certainty is estimated by comparing the shift to the uncertainty in the shift.
# E.g. if the shift is at least 4 times the uncertainty it is considered to useful.
VASCO_CERTAINTY_FACTOR_CUTOFF = 3.0
VASCO_APPLIED_STR = 'vascoApplied'
VASCO_RESULTS_STR = 'vascoResults'
VASCO_SUMMARY_STR = 'vascoSummary'
