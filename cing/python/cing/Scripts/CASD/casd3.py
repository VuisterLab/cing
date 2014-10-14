'''
CASD-NMR analysis 2013

Execute like:
python -u $CINGROOT/python/cing/Scripts/CASD/casd2.py --target CGR26A
'''

import cing
from cing import cingVersion
from cing.Libs.AwkLike import AwkLikeS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import NTpath
from cing.core.classes import ProjectTree

import numpy as np
import matplotlib.pyplot as plt

#cing.verbosity = 9

rootPath= NTpath('/Users/geerten/data/CASD-NMR-2013')
dataPath = rootPath / 'data'
analysisPath = rootPath / 'analysis'

collumns = ['group', 'method', 'entryName', 'peaklist', 'RDCdata', 'truncated', 'submitted', 'target', 'comment']
EntryInfo = """
Org	None	2l9r_Org	None	None	None	None	HR6470A	
Org	None	2la6_Org	None	None	None	None	HR6430A	
Org	None	2lah_Org	None	None	None	None	HR5460A	
Org	None	2lci_Org	None	None	None	None	OR36	
Org	None	2ln3_Org	None	None	None	None	OR135	
Org	None	2loj_Org	None	None	None	None	StT322	
Org	None	2ltl_Org	None	None	None	None	YR313A	
Org	None	2ltm_Org	None	None	None	None	HR2876B	
Org	None	2m2e_Org	None	None	None	None	HR8254A	UseOrigData_NO
Org	None	2m5o_Org	None	None	None	None	HR2876C	
AnnArbor	I-TASSER	2m2e_AnnArbor_271	Refined	False	False	2013-02-11	HR8254A	
AnnArbor	I-TASSER	2m2e_AnnArbor_272	Unrefined	False	False	2013-02-11	HR8254A	
AnnArbor	I-TASSER	2m5o_AnnArbor_298	Unrefined	False	False	2013-04-11	HR2876C	
AnnArbor	I-TASSER	2m5o_AnnArbor_305	Refined	False	False	2013-04-26	HR2876C	
Cheshire	Cheshire	2l9r_Cheshire_131	CS-only	False	False	2011-04-06	HR6470A	Restraints_NO
Cheshire	Cheshire	2la6_Cheshire_145	CS-only	False	False	2011-04-13	HR6430A	Restraints_NO
Cheshire	Cheshire	2lah_Cheshire_321	CS-only	False	False	2013-05-21	HR5460A	Ccpn_NO Restraints_NO
Cheshire	Cheshire	2lci_Cheshire_324	CS-only	False	False	2013-05-21	OR36	Ccpn_NO Restraints_NO
Cheshire	Cheshire	2ln3_Cheshire_210	CS-only	False	False	2012-01-30	OR135	Restraints_NO
Cheshire	Cheshire	2loj_Cheshire_231	CS-only	False	False	2012-06-19	StT322	Restraints_NO
Cheshire	Cheshire	2ltl_Cheshire_327	CS-only	False	False	2013-05-21	YR313A	Ccpn_NO Restraints_NO
Cheshire	Cheshire	2ltm_Cheshire_325	CS-only	False	False	2013-05-21	HR2876B	Ccpn_NO Restraints_NO
Cheshire	Cheshire	2m2e_Cheshire_329	CS-only	False	False	2013-05-21	HR8254A	Ccpn_NO Restraints_NO
Cheshire	Cheshire	2m5o_Cheshire_309	CS-only	False	False	2013-04-26	HR2876C	Restraints_NO
Cheshire	Cheshire-YAPP	2l9r_Cheshire_132	Unrefined	False	False	2011-04-06	HR6470A	Restraints_NO
Cheshire	Cheshire-YAPP	2l9r_Cheshire_153	Refined	False	False	2011-04-15	HR6470A	Restraints_NO
Cheshire	Cheshire-YAPP	2la6_Cheshire_146	Unrefined	False	False	2011-04-13	HR6430A	Restraints_NO
Cheshire	Cheshire-YAPP	2la6_Cheshire_169	Refined	False	False	2011-05-04	HR6430A	Restraints_NO
Cheshire	Cheshire-YAPP	2lah_Cheshire_322	Unrefined	False	False	2013-05-21	HR5460A	Ccpn_NO Restraints_NO
Cheshire	Cheshire-YAPP	2lah_Cheshire_323	Refined	False	False	2013-05-21	HR5460A	Ccpn_NO Restraints_NO
Cheshire	Cheshire-YAPP	2lci_Cheshire_188	Unrefined	False	False	2011-06-15	OR36	Restraints_NO
Cheshire	Cheshire-YAPP	2lci_Cheshire_194	Refined	False	False	2011-06-24	OR36	Restraints_NO
Cheshire	Cheshire-YAPP	2ln3_Cheshire_211	Unrefined	False	False	2012-01-30	OR135	Restraints_NO
Cheshire	Cheshire-YAPP	2ln3_Cheshire_216	Refined	False	False	2012-02-24	OR135	Restraints_NO
Cheshire	Cheshire-YAPP	2ltl_Cheshire_261	Unrefined	False	False	2012-08-10	YR313A	Restraints_NO
Cheshire	Cheshire-YAPP	2ltl_Cheshire_328	Refined	False	False	2013-05-21	YR313A	Ccpn_NO Restraints_NO
Cheshire	Cheshire-YAPP	2ltm_Cheshire_262	Unrefined	False	False	2012-08-10	HR2876B	Restraints_NO
Cheshire	Cheshire-YAPP	2ltm_Cheshire_326	Refined	False	False	2013-05-21	HR2876B	Ccpn_NO Restraints_NO
Cheshire	Cheshire-YAPP	2m5o_Cheshire_300	Unrefined	False	False	2013-04-16	HR2876C	Restraints_NO
Cheshire	Cheshire-YAPP	2m5o_Cheshire_308	Refined	False	False	2013-04-26	HR2876C	Restraints_NO
Frankfurt	CYANA	2l9r_Frankfurt_133	Unrefined	False	False	2011-04-06	HR6470A	
Frankfurt	CYANA	2l9r_Frankfurt_137	Refined	False	False	2011-04-07	HR6470A	
Frankfurt	CYANA	2la6_Frankfurt_134	Unrefined	False	False	2011-04-06	HR6430A	
Frankfurt	CYANA	2la6_Frankfurt_152	Refined	False	False	2011-04-15	HR6430A	
Frankfurt	CYANA	2lah_Frankfurt_171	Refined	False	False	2011-05-04	HR5460A	
Frankfurt	CYANA	2lci_Frankfurt_170	Unrefined	False	False	2011-05-04	OR36	
Frankfurt	CYANA	2lci_Frankfurt_187	Refined	False	False	2011-06-14	OR36	
Frankfurt	CYANA	2ln3_Frankfurt_198	Unrefined	False	False	2012-01-18	OR135	
Frankfurt	CYANA	2ln3_Frankfurt_212	Refined	False	False	2012-02-01	OR135	
Frankfurt	CYANA	2loj_Frankfurt_224	Refined	False	False	2012-03-16	StT322	
Frankfurt	CYANA	2ltl_Frankfurt_260	Refined	False	False	2012-08-10	YR313A	
Frankfurt	CYANA	2ltm_Frankfurt_259	Refined	False	False	2012-08-10	HR2876B	
Frankfurt	CYANA	2m2e_Frankfurt_299	Refined	False	False	2013-04-11	HR8254A	
Frankfurt	CYANA	2m5o_Frankfurt_297	Unrefined	False	False	2013-04-10	HR2876C	
Frankfurt	CYANA	2m5o_Frankfurt_302	Refined	False	False	2013-04-18	HR2876C	
Lyon	UNIO	2l9r_Lyon_122	RawSpectra	False	False	2011-04-05	HR6470A	
Lyon	UNIO	2l9r_Lyon_123	Unrefined	False	False	2011-04-05	HR6470A	
Lyon	UNIO	2la6_Lyon_141	RawSpectra	False	False	2011-04-12	HR6430A	
Lyon	UNIO	2la6_Lyon_142	Unrefined	False	False	2011-04-12	HR6430A	
Lyon	UNIO	2lah_Lyon_162	RawSpectra	False	False	2011-04-26	HR5460A	
Lyon	UNIO	2lah_Lyon_172	Refined	False	False	2011-05-05	HR5460A	UseOrigData_NO
Lyon	UNIO	2lah_Lyon_191	Refined	True	False	2011-05-05	HR5460A	
Lyon	UNIO	2lci_Lyon_180	RawSpectra	False	False	2011-06-06	OR36	
Lyon	UNIO	2lci_Lyon_181	Unrefined	False	False	2011-06-06	OR36	
Lyon	UNIO	2ln3_Lyon_203	Unrefined	False	False	2012-01-26	OR135	UseOrigData_NO
Lyon	UNIO	2ln3_Lyon_204	RawSpectra	False	False	2012-01-26	OR135	
Lyon	UNIO	2ltl_Lyon_237	RawSpectra	False	False	2012-06-25	YR313A	UseOrigData_NO
Lyon	UNIO	2ltm_Lyon_238	Unrefined	False	False	2012-06-25	HR2876B	
Lyon	UNIO	2ltm_Lyon_239	RawSpectra	False	False	2012-06-25	HR2876B	
Lyon	UNIO	2m2e_Lyon_263	Unrefined	False	False	2013-01-21	HR8254A	
Lyon	UNIO	2m5o_Lyon_293	RawSpectra	False	False	2013-04-10	HR2876C	
Lyon	UNIO	2m5o_Lyon_294	Unrefined	False	False	2013-04-10	HR2876C	
Madison	Ponderosa	2l9r_Madison_125	RawSpectra	False	False	2011-04-06	HR6470A	
Madison	Ponderosa	2la6_Madison_163	RawSpectra	False	False	2011-04-26	HR6430A	
Madison	Ponderosa	2lah_Madison_175	RawSpectra	False	False	2011-05-07	HR5460A	
Madison	Ponderosa	2lci_Madison_182	RawSpectra	False	False	2011-06-06	OR36	
Madison	Ponderosa	2ln3_Madison_226	RawSpectra	False	False	2012-04-10	OR135	
Madison	Ponderosa	2loj_Madison_221	RawSpectra	False	False	2012-03-07	StT322	
Madison	Ponderosa	2ltl_Madison_228	RawSpectra	False	False	2012-06-14	YR313A	UseOrigData_NO
Madison	Ponderosa	2ltm_Madison_227	RawSpectra	False	False	2012-06-13	HR2876B	UseOrigData_NO
Madison	Ponderosa	2m2e_Madison_268	RawSpectra	False	False	2013-01-28	HR8254A	
Madison	Ponderosa	2m5o_Madison_284	RawSpectra	False	False	2013-03-20	HR2876C	
Munich	autonoe-Rosetta-alpha	2l9r_Munich_185	Unrefined	False	True	2011-06-11	HR6470A	UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2l9r_Munich_186	Unrefined	True	False	2011-06-11	HR6470A	UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2la6_Munich_147	Unrefined	True	False	2011-04-13	HR6430A	
Munich	autonoe-Rosetta-alpha	2lah_Munich_165	Unrefined	True	False	2011-04-27	HR5460A	
Munich	autonoe-Rosetta-alpha	2lci_Munich_184	Unrefined	True	False	2011-06-10	OR36	Restraints_NO UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2ln3_Munich_209	Unrefined	True	False	2012-01-30	OR135	
Munich	autonoe-Rosetta-alpha	2loj_Munich_217	Unrefined	False	False	2012-03-05	StT322	
Munich	autonoe-Rosetta-alpha	2loj_Munich_218	Unrefined	False	False	2012-03-05	StT322	
Munich	autonoe-Rosetta-alpha	2loj_Munich_219	Unrefined	False	False	2012-03-05	StT322	Restraints_NO UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2loj_Munich_220	Unrefined	False	False	2012-03-05	StT322	
Munich	autonoe-Rosetta-alpha	2ltl_Munich_245	Unrefined	True	False	2012-07-10	YR313A	
Munich	autonoe-Rosetta-alpha	2ltm_Munich_244	Unrefined	True	False	2012-07-10	HR2876B	
Munich	autonoe-Rosetta-alpha	2m2e_Munich_264	Unrefined	False	False	2013-01-25	HR8254A	Restraints_NO UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2m2e_Munich_265	Refined	False	False	2013-01-25	HR8254A	Restraints_NO UseOrigData_NO
Munich	autonoe-Rosetta-alpha	2m5o_Munich_288	Unrefined	True	False	2013-04-08	HR2876C	
Paris	ARIA	2l9r_Paris_126	Unrefined	True	True	2011-04-06	HR6470A	
Paris	ARIA	2l9r_Paris_127	Unrefined	True	False	2011-04-06	HR6470A	
Paris	ARIA	2l9r_Paris_128	Unrefined	False	True	2011-04-06	HR6470A	
Paris	ARIA	2l9r_Paris_129	Unrefined	False	False	2011-04-06	HR6470A	
Paris	ARIA	2l9r_Paris_154	Refined	False	False	2011-04-18	HR6470A	
Paris	ARIA	2l9r_Paris_155	Refined	True	False	2011-04-18	HR6470A	
Paris	ARIA	2l9r_Paris_156	Refined	False	True	2011-04-18	HR6470A	
Paris	ARIA	2l9r_Paris_157	Refined	True	True	2011-04-18	HR6470A	
Paris	ARIA	2la6_Paris_144	Unrefined	False	False	2011-04-13	HR6430A	
Paris	ARIA	2la6_Paris_166	Refined	False	False	2011-04-28	HR6430A	
Paris	ARIA	2lah_Paris_176	Refined	False	False	2011-05-09	HR5460A	
Paris	ARIA	2lah_Paris_177	Refined	True	False	2011-05-16	HR5460A	
Paris	ARIA	2lci_Paris_189	Refined	False	False	2011-06-22	OR36	
Paris	ARIA	2lci_Paris_190	Refined	True	False	2011-06-22	OR36	
Paris	ARIA	2ln3_Paris_196	Unrefined	False	False	2012-01-13	OR135	
Paris	ARIA	2ln3_Paris_199	Unrefined	True	False	2012-01-26	OR135	
Paris	ARIA	2ln3_Paris_214	Refined	True	False	2012-02-03	OR135	
Paris	ARIA	2ln3_Paris_215	Refined	False	False	2012-02-03	OR135	
Paris	ARIA	2loj_Paris_225	Refined	False	False	2012-03-19	StT322	
Paris	ARIA	2ltl_Paris_253	Refined	False	False	2012-07-24	YR313A	
Paris	ARIA	2ltl_Paris_254	Refined	True	False	2012-07-24	YR313A	
Paris	ARIA	2ltm_Paris_240	Unrefined	False	False	2012-06-25	HR2876B	
Paris	ARIA	2ltm_Paris_241	Unrefined	True	False	2012-06-25	HR2876B	UseOrigData_NO
Paris	ARIA	2ltm_Paris_255	Refined	False	False	2012-07-24	HR2876B	
Paris	ARIA	2ltm_Paris_256	Refined	True	False	2012-07-24	HR2876B	
Paris	ARIA	2m2e_Paris_273	Refined	False	False	2013-02-11	HR8254A	
Paris	ARIA	2m5o_Paris_296	Unrefined	True	False	2013-04-10	HR2876C	
Paris	ARIA	2m5o_Paris_303	Refined	True	False	2013-04-25	HR2876C	
Paris	ARIA	2m5o_Paris_304	Refined	True	True	2013-04-25	HR2876C	
Piscataway	ASDP-CNS	2l9r_Piscataway_135	Unrefined	True	False	2011-04-07	HR6470A	UseOrigData_NO
Piscataway	ASDP-CNS	2l9r_Piscataway_136	Unrefined	False	False	2011-04-07	HR6470A	UseOrigData_NO
Piscataway	ASDP-CNS	2l9r_Piscataway_158	Refined	False	False	2011-04-19	HR6470A	
Piscataway	ASDP-CNS	2l9r_Piscataway_159	Refined	True	False	2011-04-19	HR6470A	
Piscataway	ASDP-CNS	2la6_Piscataway_148	Unrefined	False	False	2011-04-13	HR6430A	
Piscataway	ASDP-CNS	2la6_Piscataway_167	Refined	False	False	2011-04-29	HR6430A	
Piscataway	ASDP-CNS	2lah_Piscataway_164	Unrefined	False	False	2011-04-27	HR5460A	
Piscataway	ASDP-CNS	2lah_Piscataway_173	Refined	False	False	2011-05-06	HR5460A	
Piscataway	ASDP-CNS	2lah_Piscataway_174	Refined	True	False	2011-05-06	HR5460A	
Piscataway	ASDP-CNS	2lci_Piscataway_178	Unrefined	False	False	2011-05-20	OR36	
Piscataway	ASDP-CNS	2lci_Piscataway_179	Unrefined	True	False	2011-05-20	OR36	
Piscataway	ASDP-CNS	2lci_Piscataway_192	Refined	False	False	2011-06-24	OR36	
Piscataway	ASDP-CNS	2lci_Piscataway_193	Refined	True	False	2011-06-24	OR36	
Piscataway	ASDP-CNS	2ln3_Piscataway_207	Unrefined	False	False	2012-01-30	OR135	UseOrigData_NO
Piscataway	ASDP-CNS	2ln3_Piscataway_312	Refined	False	False	2013-05-09	OR135	UseOrigData_NO
Piscataway	ASDP-CNS	2loj_Piscataway_222	Unrefined	False	False	2012-03-08	StT322	
Piscataway	ASDP-CNS	2loj_Piscataway_229	Refined	False	False	2012-06-19	StT322	
Piscataway	ASDP-CNS	2ltl_Piscataway_276	Unrefined	False	False	2013-03-08	YR313A	
Piscataway	ASDP-CNS	2ltl_Piscataway_315	Refined	False	False	2013-05-09	YR313A	UseOrigData_NO
Piscataway	ASDP-CNS	2ltm_Piscataway_278	Unrefined	True	False	2013-03-08	HR2876B	
Piscataway	ASDP-CNS	2ltm_Piscataway_313	Refined	False	False	2013-05-09	HR2876B	UseOrigData_NO
Piscataway	ASDP-Rosetta	2ln3_Piscataway_208	Unrefined	False	False	2012-01-30	OR135	
Piscataway	ASDP-Rosetta	2ln3_Piscataway_311	Refined	False	False	2013-05-09	OR135	
Piscataway	ASDP-Rosetta	2loj_Piscataway_223	Unrefined	False	False	2012-03-08	StT322	
Piscataway	ASDP-Rosetta	2loj_Piscataway_230	Refined	False	False	2012-06-19	StT322	
Piscataway	ASDP-Rosetta	2ltl_Piscataway_277	Unrefined	False	False	2013-03-08	YR313A	UseOrigData_NO
Piscataway	ASDP-Rosetta	2ltl_Piscataway_316	Refined	False	False	2013-05-09	YR313A	UseOrigData_NO
Piscataway	ASDP-Rosetta	2ltm_Piscataway_279	Unrefined	True	False	2013-03-08	HR2876B	UseOrigData_NO
Piscataway	ASDP-Rosetta	2ltm_Piscataway_314	Refined	False	False	2013-05-09	HR2876B	UseOrigData_NO
Piscataway	ASDP-Rosetta	2m2e_Piscataway_274	Unrefined	False	False	2013-02-12	HR8254A	
Piscataway	ASDP-Rosetta	2m2e_Piscataway_275	Refined	False	False	2013-02-12	HR8254A	
Piscataway	ASDP-Rosetta	2m5o_Piscataway_301	Unrefined	True	False	2013-04-16	HR2876C	
Piscataway	ASDP-Rosetta	2m5o_Piscataway_307	Refined	True	False	2013-04-26	HR2876C	
Seattle	CS-HM-DP-Rosetta	2m5o_Seattle_291	Unrefined	True	False	2013-04-08	HR2876C	Restraints_NO
Seattle	CS-HM-Rosetta	2l9r_Seattle_143	CS-only	True	False	2011-04-13	HR6470A	Restraints_NO
Seattle	CS-HM-Rosetta	2la6_Seattle_149	CS-only	True	False	2011-04-14	HR6430A	Restraints_NO
Seattle	CS-HM-Rosetta	2lah_Seattle_138	CS-only	True	False	2011-04-08	HR5460A	Restraints_NO
Seattle	CS-HM-Rosetta	2ln3_Seattle_281	CS-only	True	False	2013-03-08	OR135	Restraints_NO UseOrigData_NO
Seattle	CS-HM-Rosetta	2ltl_Seattle_282	CS-only	True	False	2013-03-08	YR313A	Restraints_NO
Seattle	CS-HM-Rosetta	2ltm_Seattle_283	CS-only	True	False	2013-03-08	HR2876B	Restraints_NO
Seattle	CS-HM-Rosetta	2m2e_Seattle_270	CS-only	False	False	2013-02-05	HR8254A	Restraints_NO
Seattle	CS-HM-Rosetta	2m5o_Seattle_285	CS-only	True	False	2013-03-24	HR2876C	Restraints_NO
Trieste	BE-metadynamics		2m5o_Trieste_310	CS-only	False	False	2013-04-26	HR2876C	Restraints_NO
Utrecht	CS-DP-Rosetta	2la6_Utrecht_150	Unrefined	False	False	2011-04-14	HR6430A	Restraints_NO
Utrecht	CS-DP-Rosetta	2lci_Utrecht_183	Unrefined	False	False	2011-06-08	OR36	Restraints_NO
Utrecht	CS-Rosetta	2l9r_Utrecht_121	CS-only	False	False	2011-04-05	HR6470A	Restraints_NO
Utrecht	CS-Rosetta	2lah_Utrecht_168	CS-only	False	False	2011-05-04	HR5460A	Restraints_NO
Utrecht	CS-Rosetta	2ln3_Utrecht_205	CS-only	False	False	2012-01-26	OR135	Restraints_NO
Utrecht	CS-Rosetta	2m2e_Utrecht_269	CS-only	False	False	2013-01-29	HR8254A	Restraints_NO
Utrecht	CS-Rosetta	2m5o_Utrecht_286	CS-only	False	False	2013-04-07	HR2876C	
Utrecht	CS-Rosetta	2m5o_Utrecht_287	CS-only	False	False	2013-04-07	HR2876C	Restraints_NO
"""

ranges = NTdict(
    HR6470A = '12-58',   # cv: 5-58; limited by: Utrecht_121
    HR6430A = '14-99',   # cv: 12-99; limited by: Utrecht_150
    HR5460A = '12-158',  # cv: 11-158; limited by: Utrecht_168
    OR36    = '2-128',   # cv: 2-128
    OR135   = '4-73',    # cv: 4-75; limited by Munich_209
    StT322  = '36-62',   # cv: 7-63; limited by: Cheshire_231: 38-63, Munich_218, Munich_220: 26-62
    YR313A  = '17-97',   # cv: 1-115; limited by: Cheshire_327: 17-115, Munich_245: 16-111, Seattle_282: 1-97
    HR2876B = '12-105',  # cv: 12-107; limited by: Munich_244
    HR8254A = '553-612', # cv: 551-621; limited by: Utrecht_269: 553-613, Munich_264, Munich_265: 551-612 
    HR2876C = '17-93',   # cv: 17-95; limited by: Utrecht_287
)
ranges.keysformat()

cingPars = 'cing_red cing_orange cing_green pc_core pc_allowed pc_disallowed pc_generous pc_gf WI_ramachandran WI_bbNormality WI_janin'.split()
entryPars = 'idx rmsd nmodels rmsdToTarget ranges'.split()

class Entry( NTdict ):
    def __init__(self, dataPath, **kwds):
        NTdict.__init__(self)
        self.entryName   = 'undefined'
        self.dataPath    = NTpath(dataPath)
        self.comment     = ''
        self.cingSummary = None
        self.project     = None
        
        for key in entryPars + cingPars:
            self[key] = None
        self.idx = 0

        self.update(kwds)
    #end def
    
    def path(self, *args):
        p = self.dataPath / self.entryName[1:3] / self.entryName / self.entryName + '.cing'
        for a in args:
            p = p / a
        return p
    #end def
    
    def readProject(self):
        path = self.path()
        if not path.exists():
            print 'Error Entry.readProject: file %s does not exist' % path
            return None
        nTmessage( '==> reading project from %s', path )
        self.project = cing.Project.open(path,'old')
        return self.project
    #end def
        
    def readSummary(self, fix=False):
        path = self.path(self.entryName, 'Cing', 'CingSummaryDict.xml')
        if not path.exists():
            print 'Error Entry.readSummary: file %s does not exist' % path
            return None
        nTmessage( '==> reading summary from %s', path )
        self.cingSummary = xML2obj(path)
        
        if fix:
            rog = NTlist( 0, 0, 0 ) # Counts for red, orange, green.
            for resname, rogScore in self.cingSummary.CING_residueROG:
                print resname, rogScore
                if rogScore.isRed():
                    rog[0] += 1
                elif rogScore.isOrange():
                    rog[1] += 1
                else:
                    rog[2] += 1
            #end for
            total = reduce(lambda x, y: x+y+0.0, rog) # total expressed as a float because of 0.0
            print rog, total
            for i, _x in enumerate(rog): 
                rog[i] = rog[i]*100.0/total
            self.cingSummary.cing_red    = round(rog[0],1)
            self.cingSummary.cing_orange = round(rog[1],1)
            self.cingSummary.cing_green  = round(rog[2],1)   
        #end if
        #copy the data
        for par in cingPars:
            if par in self.cingSummary:
                self[par] = self.cingSummary[par]
        return self.cingSummary
    #end def
    
    def __str__(self):
        return '<Entry %s; Target: %s>' % (self.entryName, self.target)
    #end def
    
    def format(self):
        s = "----- " + str(self) + """ -----
group:           %(group)s
method:          %(method)s
submitted:       %(submitted)s
peaklist:        %(peaklist)s
RDCdata:         %(RDCdata)s
truncated:       %(truncated)s
comment:         %(comment)s
--- pairwise backbone rmsd ---
nmodels:         %(nmodels)s
ensemble:        %(rmsd)s
toTarget:        %(rmsdToTarget)s
ranges:          %(ranges)s
--- Cing ---
cing_red:        %(cing_red)s
cing_orange:     %(cing_orange)s
cing_green:      %(cing_green)s
--- Procheck ---
pc_core:         %(pc_core)s
pc_allowed:      %(pc_allowed)s
pc_generous:     %(pc_generous)s
pc_disallowed:   %(pc_disallowed)s
pc_gf:           %(pc_gf)s
--- Whatif ---
WI_ramachandran: %(WI_ramachandran)s
WI_bbNormality:  %(WI_bbNormality)s
WI_janin:        %(WI_janin)s
""" % self
        return s
    #end def
    
    def toJson(self, path):
        pass
    #end def
    
    def toXML(self, depth = 0, stream = sys.stdout, indent = '\t', lineEnd = '\n'):
        nTindent(depth, stream, indent)
        fprintf(stream, "<Entry>")
        fprintf(stream, lineEnd)

        for key in collumns + entryPars + cingPars:
            if self.has_key(key):
                value = self[key]
                nTindent(depth+1, stream, indent)
                fprintf(stream, "<key name=%s>", quote(key))
                fprintf(stream, lineEnd)
                nTtoXML(value, depth+2, stream, indent, lineEnd)
                nTindent(depth+1, stream, indent)
                fprintf(stream, "</key>")
                fprintf(stream, lineEnd)
            #end if    
        #end for
        nTindent(depth, stream, indent)
        fprintf(stream, "</Entry>")
        fprintf(stream, lineEnd)
    #end def
#end class

class XMLEntryHandler( XMLhandler ):
    """Entry handler class"""
    def __init__(self):
        XMLhandler.__init__(self, name='Entry')
    #end def

    def handle(self, node):
        attrs = self.handleDictElements(node)
        if attrs == None: 
            return None
        result = Entry(dataPath=dataPath)
        result.update(attrs)
        return result
    #end def
#end class
xmlentryhandler = XMLEntryHandler()

#--------------------------------------------------------------------------------------------------------------
class ResultsList(NTlist):

    def __init__(self, dataPath):
        NTlist.__init__(self)
        self.dataPath = dataPath
        self.byTarget = NTdict()
        self.byGroup  = NTdict()
        self.byKey    = NTdict()
        self.byMethod = NTdict()
        self.groups   = NTlist()
        self.targets  = NTlist()
        self.methods  = NTlist()
        self.ranges   = ranges
    #end def
    
    def append( self, entry ):
        NTlist.append(self, entry)
        # make some mappings to find them back
        self.byKey[entry.idx] = entry
        self.byKey[(entry.target,entry.group)] = entry
        self.byKey[entry.entryName] = entry
        
        self.byTarget.setdefault(entry.target, NTlist())
        self.byTarget[entry.target].append(entry)
        
        self.byGroup.setdefault(entry.group, NTlist())
        self.byGroup[entry.group].append(entry)
                
        self.byMethod.setdefault(entry.method, NTlist())
        self.byMethod[entry.method].append(entry)

        if entry.target not in self.targets:
            self.targets.append(entry.target)
        if entry.group not in self.groups:
            self.groups.append(entry.group)
        if entry.method not in self.methods:
            self.methods.append(entry.method)
    #end def
    
    def allEntries(self, byTarget=False, byGroup=False):
        if byTarget:
            for target in self.byTarget.values():
                for entry in target:
                    yield entry
        elif byGroup:
            for group in self.byGroup.values():
                for entry in group:
                    yield entry
        else:
            for entry in self:
                yield entry
    #end def
    
    def readCingSummaries(self):
        for entry in self:
            entry.readSummary()
    #end def
    
    def save(self, path=None):
        if path == None:
            path = self.dataPath / 'results.xml'
        tmp = []
        for entry in self:
            tmp.append(entry)
        print '==> Saving %d entries to %s' % (len(tmp), path)
        obj2XML(tmp, path=path)
    #end def
    
    @staticmethod
    def restore(path=None):
        if path == None:
            path = analysisPath / 'results.xml'
        tmp = xML2obj(path)
        if not tmp:
            return 1
        
        results = ResultsList(dataPath=path[:-1])       
        for entry in tmp:
            # replace keyword
            if entry.has_key('programType'):
                entry['method'] = entry['programType']
                del entry['programType']
            if entry['method'] == 'None' and entry['group'] == 'Org':
                entry['method'] = 'Original'
                
            results.append(entry)       
        return results
    #end def
    
    def __str__(self):
        return '<ResultsList (N:%d,groups:%d,targets:%d)>' % (len(self),len(self.groups),len(self.targets))
    #end def
    
    def format(self):
        s = """=============== ResultsList ===============
dataPath:   %s
entryCount: %d
groups:     %s
targets:    %s
methods:    %s
""" % (self.dataPath, len(self), self.groups.format(), self.targets.format(), self.methods.format())
        return s
    #end def
    
    def printAll(self, target=None):
        print self.format()
        if target == None:
            targets = self.targets
        else:
            targets = [target]
        for t in targets:
            print "===============", t, "==============="
            for entry in self.byTarget[t]:
                print entry.format()
    #end def
    
    def calculatePairWiseRmsd( self, entry1, entry2, ranges ):
        """Calculate pairwise rmsd between mol1 and mol2
           Optionally use ranges for the fitting
        """
        if not entry1 or not entry1.project:
            nTerror('ResultsList.calculatePairWiseRmsd: undefined entry1')
            return None, None, None, None
        else:
            mol1 = entry1.project.molecule
        
        if not entry2 or not entry2.project:
            nTerror('ResultsList.calculatePairWiseRmsd: undefined entry2')
            return None, None, None, None
        else:
            mol2 = entry2.project.molecule
 
        #Use ranges routines to define fitAtoms ed
        fitResidues1 = mol1.setResiduesFromRanges(ranges)
        fitAtoms1 = mol1.selectFitAtoms( fitResidues1, backboneOnly=True, includeProtons = False )
        mol1.ensemble.setFitCoordinates( fitAtoms1 )
        fitResidues2 = mol2.setResiduesFromRanges(ranges)        
        fitAtoms2 = mol2.selectFitAtoms( fitResidues2, backboneOnly=True, includeProtons = False )
        mol2.ensemble.setFitCoordinates( fitAtoms2 )
    #    mol2.superpose( ranges )

        l1 = len(mol1.ensemble)
        l2 = len(mol2.ensemble)

        if (   l1 == 0 or len(mol1.ensemble[0].fitCoordinates) == 0
            or l2 == 0 or len(mol2.ensemble[0].fitCoordinates) == 0
            or len(mol1.ensemble[0].fitCoordinates) != len(mol2.ensemble[0].fitCoordinates)
        ):
            nTerror( "ResultsList.calculatePairWiseRmsd: mol1: %s %s, mol2: %s %s, ranges: %s",
                      l1, len(mol1.ensemble[0].fitCoordinates),
                      l2, len(mol2.ensemble[0].fitCoordinates),
                      ranges)
            return None, None, None, None
        #end if

        models = mol1.ensemble + mol2.ensemble

        result = NTlistOfLists(len(models), len(models), 0.0)

        nTmessage('==> Calculating pairwise rmsds %s %s', mol1, mol2)

        for i in range(len(models)):
            for j in range(i+1, len(models)):
                result[i][j] = models[i].superpose( models[j] )
                result[j][i] = result[i][j]
            #end for
        #end for

        pairwise1 = NTlist()
        for i in range(l1):
            for j in range(i+1, l1):
                pairwise1.append(result[i][j])
    #            print '1>', i,j

        pairwise2 = NTlist()
        for i in range(l1, l1+l2):
            for j in range(i+1, l1+l2):
                pairwise2.append(result[i][j])
    #            print '2>', i,j

        pairwise12 = NTlist()
        for i in range(l1):
            for j in range(l1, l1+l2):
                pairwise12.append(result[i][j])

    #            print '12>', i,j
    #    print len(pairwise1), len(pairwise2), len(pairwise12)
        return (result, pairwise1.average2( fmt='%.2f +- %.2f'),
                        pairwise2.average2( fmt='%.2f +- %.2f'),
                        pairwise12.average2(fmt='%.2f +- %.2f') )
    #end def
    
    def processTarget( self, target):
        "Calculate rmsd's for target"
        if target not in self.targets:
            nTerror('ResultsList.processTarget: invalid target')
            return True        
        for e2 in results.byTarget[target]:
            self.calcRmsdToTarget(e2)
        #end for
    #end def

    def getRanges(self, target):
        e1 = self.byTarget[target][0]
        if e1.project == None:
            e1.readProject()
        ranges = e1.project.molecule.rangesByCv()
        print '%s: %s' % (e1, ranges)
        
        for e in self.byTarget[target][1:]:
            mol,res,atms = getFitted(e,ranges)
            print  '%s: %d-%d' % (e, atms[0].residue.resNum, atms[-1].residue.resNum)
    #end def
    
    def getValues(self, target, par):
        """get values of par for target
        return numpy array
        """
        l = len(self.byTarget[target])
        x = np.zeros(l)
        values = np.zeros(l)
        
        methodDict = {}
        for i,g in enumerate(self.methods):
            methodDict[g] = float(i+1)
        
        for i,e in enumerate(self.byTarget[target]):
            # map group onto index
            x[i] = methodDict[e.method]
            methodDict[e.method]+= 0.1
            
            _tmp = NTvalue(0.0, 0.0)
            #print par, type(e[par]), type(_tmp)
            if par in e:
                if type(e[par]) == type(_tmp):
                    values[i] = float(e[par].value)
                else:
                    values[i] = float(e[par])
        #end for
        return x,values
    #end def    
    
    def calcRmsdToTarget( self, entry):
        "Calculate rmsd of entry to target"
        target = entry.target
        if target not in self.targets:
            nTerror('ResultsList.CalcRmsdToTarget: invalid target')
            return True        
        if (target,'Org') not in self.byKey:
            nTerror('ResultsList.CalcRmsdToTarget: cannot find original')
            return True
        e1 = self.byKey[(target,'Org')]
        if e1 == entry:
            entry.rmsdToTarget = NTvalue(0.0,0.0,fmt='%.2f +- %.2f')
        else:        
            if e1.project == None:
                e1.readProject()
            if target in self.ranges:
                e1.ranges = self.ranges[target]
            else:
                e1.ranges = e1.project.molecule.rangesByCv()
            e1.nmodels = len(e1.project.molecule.ensemble)
            
            if entry.project == None:
                entry.readProject()
            entry.ranges = e1.ranges        
            entry.nmodels = len(entry.project.molecule.ensemble)
            
            _tmp,e1.rmsd,entry.rmsd,entry.rmsdToTarget = self.calculatePairWiseRmsd(e1, entry, e1.ranges)
        #endif
        print '==> %s rmsdToTarget: %s ranges: %s' % (entry, entry.rmsdToTarget, entry.ranges)
        return False
    #end def
#end class
#--------------------------------------------------------------------------------------------------------------

def parseEntryInfo():
    #initiate a results dictionary
    results = ResultsList(dataPath)
    
    # fill the results dictionary
    entryIdx = 1
    for line in AwkLikeS(EntryInfo, commentString='#', minNF=5):
        entry = Entry(dataPath=resultsPath, comment=None)
        #extract the field
        for idx,field in enumerate(collumns):
            #print idx,field, line.NF
            if idx < line.NF:
                entry[field] = line.dollar[idx+1]
        # extract idx from entryName
        _tmp = entry.entryName.split('_')
        if len(_tmp) == 3:
            entry.idx = int(_tmp[2])
        else:
            entry.idx = entryIdx
            entryIdx += 1
            nTwarning('parseEntryInfo: assigned idx %d to entry "%s"', entry.idx, entry.entryName)
        #end if
        
        results.append(entry)
    #end for
    return results
#end def

def getFitted( entry, ranges ):
    if entry.project == None:
        entry.readProject()
    mol = entry.project.molecule
    res = mol.setResiduesFromRanges(ranges)
    atms = mol.selectFitAtoms( res, backboneOnly=True, includeProtons = False )
    return mol, res, atms
#end def

    
def reorder( results ):
    "Reorder the entry to follow new order based on methods"
    methods = 'Original CYANA UNIO ARIA ASDP-CNS Ponderosa I-TASSER Cheshire Cheshire-YAPP autonoe-Rosetta-alpha ASDP-Rosetta CS-HM-DP-Rosetta CS-HM-Rosetta CS-DP-Rosetta CS-Rosetta BE-metadynamics'.split()
    methodDict = {}
    for i,g in enumerate(methods):
            methodDict[g] = i
    for e in results:
        e.im = methodDict[e.method]
    NTsort(results,'im',inplace=True)
    # now copy and build a new list
    res = ResultsList(dataPath)
    for e in results:
        res.append(e)
    return res
#end def



header = """
#======================================================================================================
#    CASD-NMR -2013      version %s
#======================================================================================================
""" % (cingVersion)

print header

init = False
if init:
    results=parseEntryInfo()
    results.readCingSummaries()
    results.save()
else:
    print '==> Restoring results'
    results = ResultsList.restore()

print results.format()

t=-1
if t>=0:
    target = results.targets[t]
    results.processTarget(target)
    results.save()

#
#
#parser = OptionParser(usage="casd.py [options] Use -h or --help for full options.")
#
#parser.add_option("--target",
#                  dest="target",
#                  help="Define CASD-NMR target.",
#                  metavar="TARGET"
#                 )
#parser.add_option("--out",
#                  dest="outFile",
#                  help="Define result output file.",
#                  metavar="OUTFILE"
#                 )
#
#parser.add_option("-v", "--verbosity", type='int',
#                  default=cing.verbosityDefault,
#                  dest="verbosity", action='store',
#                  help="verbosity: [0(nothing)-9(debug)] no/less messages to stdout/stderr (default: 3)"
#                 )
#
#(options, args) = parser.parse_args()
#
#if options.verbosity >= 0 and options.verbosity <= 9:
##        print "In main, setting verbosity to:", options.verbosity
#    cing.verbosity = options.verbosity
#else:
#    nTerror("set verbosity is outside range [0-9] at: " + options.verbosity)
#    nTerror("Ignoring setting")
##end if
#
##options.target = 'CGR26A'
#options.target = '1brv'
#
## Check the targets
#if not options.target:
#    nTerror('No target defined, aborting')
#    sys.exit(1)
#if not options.target in targets:
#    nTerror('Target "%s" not in %s, aborting', options.target, targets)
#    sys.exit(1)
#
#target = options.target
#groupsForTarget = getGroupsForTarget(target, groups)[0:2]
#nTmessage( "Target:          " + target )
#nTmessage( "Ranges target:   " + ranges[target] )
#nTmessage( "Groups target:   " + str( groupsForTarget ))
##sys.exit(1)
#
## Open the project instances.
#pTree = ProjectTree( target, groups=groupsForTarget, ranges=ranges[target], groupDefs=groupDefs )
#pTree.openCompleteTree()
#p0 = pTree.entries[0] # shortcut
#
#fp = sys.stdout
#if options.outFile:
#    fp = open(pTree.path(options.outFile), 'w')
#    nTmessage('\n==> Starting analysis: Output to %s', pTree.path(options.outFile))
#
#fprintf( fp, '%s\n\n', pTree.format() )
#
#if False:
#    # Superpose (also defines fitAtoms)
#    for p in pTree:
#        p.superpose(ranges=pTree.ranges)
#        fprintf( fp, '%s\n%s\n', p.molecule, p.molecule.rmsd.format() )
#
#    # Get the closestToMean models, superpose, export to PDB file
#    closestToMean = NTlist()
#    for p in pTree:
#        cl = p.molecule.rmsd.closestToMean
#        closestToMean.append( p.molecule.ensemble[cl] )
#    fitted = closestToMean.zap('fitCoordinates')
#    for m in closestToMean[1:]:
#        r = m.superpose(closestToMean[0])
#        #print '>', r
#    # Export'
#    for p in pTree:
#        p.molecule.toPDBfile( pTree.path(p.name+'.pdb'), model=p.molecule.rmsd.closestToMean)
#
##sys.exit(1)
#
## Positional global RMSDs
#rmsds = pTree.calcRmsds( ranges=pTree.ranges )
#pTree.printRmsds('  Pairwise positional RMSDs residues '+pTree.ranges, rmsds, fp )
#
## Pih-Psi global RMSDs
#rmsds2 = pTree.calcPhiPsiRmsds( ranges=pTree.ranges )
#pTree.printRmsds('  Relative pairwise Phi-Psi RMSDs residues '+pTree.ranges, rmsds2, fp )
#
#pTree.printOverallScores( fp )
#pTree.printRestraintScores( fp )
#
##cp.test( pTree, fp )
#
## yasara macros
#pTree.loadPDBmacro(  )
#pTree.colorPDBmacro(  )
#pTree.rogMacro(  )
#pTree.qShiftMacro()
##pTree.colorPhiPsiMacro(  )
#
#if options.outFile:
#    fp.close()
#
#pTree.copyFiles2Project(  )
