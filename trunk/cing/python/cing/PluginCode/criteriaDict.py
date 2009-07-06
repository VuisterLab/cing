from cing import programName
from cing.Libs.NTutils import NTdict
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.core.constants import ANY_ENTITY_LEVEL
from cing.core.constants import BAD_PROP
from cing.core.constants import CHAIN_LEVEL
from cing.core.constants import OPERATION_GREATER_THAN
from cing.core.constants import OPERATION_LESS_THAN_OR_EQUALS
from cing.core.constants import POOR_PROP
from cing.core.constants import RES_LEVEL

criteriaDict= NTdict()
criteriaDict = {
  WHATIF_STR: {
    RES_LEVEL: {
     'RAMCHK': { POOR_PROP:  ( OPERATION_LESS_THAN_OR_EQUALS, -0.5 ),
                 BAD_PROP:   ( OPERATION_LESS_THAN_OR_EQUALS, -1.0 )
                 },
     'BNDCHK': { POOR_PROP:  ( OPERATION_GREATER_THAN, 3.0 ),
                 BAD_PROP:   ( OPERATION_GREATER_THAN, 5.0 )
                 },
    }
  },
  programName: {
    ANY_ENTITY_LEVEL: {
    # See Fig2. in
     'dr_maxall': { POOR_PROP:  ( OPERATION_GREATER_THAN, 0.5 ),
                    BAD_PROP:   ( OPERATION_GREATER_THAN, 1.0 )
                 },
    },
    CHAIN_LEVEL: {
     'dr_rms': { POOR_PROP:  ( OPERATION_GREATER_THAN, 0.05 ),
                 BAD_PROP:   ( OPERATION_GREATER_THAN, 0.1 )
                 },
     'dr_avall': {
                 POOR_PROP:  ( OPERATION_GREATER_THAN, 0.01 ),
                 BAD_PROP:   ( OPERATION_GREATER_THAN, 0.02 )
                 },
     'dr_avviol': {
                 POOR_PROP:  ( OPERATION_GREATER_THAN, 0.1 ),
                 BAD_PROP:   ( OPERATION_GREATER_THAN, 0.2 )
                 },
    }
  }
}

cingCriticismDict = criteriaDict[ programName ]

#NTmessage( `criteriaDict` )
#NTdebug( "Read criteriDict.py version 0.0.0" )