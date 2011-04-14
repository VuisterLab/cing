VASCO_STR       = "Vasco" # key to the entities (atoms, residues, etc under which the results will be stored

# Used in html
H_STR = 'H'
N_STR = 'N'
C_STR = 'C'
C_ALIPHATIC_STR = 'C_aliphatic'

vascoAtomTypeList = ( H_STR, N_STR, C_STR )

# Used in Vasco
vascoAtomIdLoL = (
            (H_STR, None),
            (N_STR, None),
            (C_STR, 3)
            )

# The certainty is estimated by comparing the shift to the uncertainty in the shift.
# E.g. if the shift is at least 4 times the uncertainty it is considered to useful.
VASCO_CERTAINTY_FACTOR_CUTOFF = 3.0
#VASCO_CERTAINTY_FACTOR_CUTOFF = -999.9 # always apply for debugging with 1brv
VASCO_APPLIED_STR = 'vascoApplied'
VASCO_RESULTS_STR = 'vascoResults'
VASCO_SUMMARY_STR = 'vascoSummary'

# Keys used in RDB and values used in html.
H_None_STR = 'H_None'
N_None_STR = 'N_None'
C_3_STR = 'C_3'
vascoMapAtomIdToHuman = {H_None_STR: H_STR, N_None_STR: N_STR, C_3_STR: 'Cali'}

# Used in RDB
atomclass_STR           = 'atomclass'
csd_STR                 = 'csd'
csd_err_STR             = 'csd_err'