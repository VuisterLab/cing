'''
Created on Aug 30, 2010

@author: jd
'''
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.nrgCingRdb import * #@UnusedWildImport

dictDivideByResidueCount = {DIVIDE_BY_RESIDUE_COUNT:1}
dictDivideByResidueCount_OnlyProtein = {DIVIDE_BY_RESIDUE_COUNT:1, ONLY_PROTEIN:1}
dictDivideByResidueCount_OnlyProtein_OnlySelection = {DIVIDE_BY_RESIDUE_COUNT:1, ONLY_PROTEIN:1, ONLY_SELECTION:1}
dictDivideByResidueCount_OnlySelection_OnlyNonZero = {DIVIDE_BY_RESIDUE_COUNT:1, ONLY_PROTEIN:1, ONLY_SELECTION:1, ONLY_NON_ZERO:1}
dict_OnlyNonZero = {ONLY_NON_ZERO:1}
dict1 = dictDivideByResidueCount #@UnusedVariable
dict2 = dictDivideByResidueCount_OnlyProtein #@UnusedVariable
dict3 = dictDivideByResidueCount_OnlyProtein_OnlySelection #@UnusedVariable
dict4 = dictDivideByResidueCount_OnlySelection_OnlyNonZero #@UnusedVariable
d5 = dict_OnlyNonZero #@UnusedVariable

uR = updateAndReturnDict
MI = USE_MIN_VALUE_STR
MA = USE_MAX_VALUE_STR

plotList = [
            [ PROJECT_LEVEL, CING_STR, DISTANCE_COUNT_STR,uR(dict4,{MI: 0, MA: 40}) ], # 1
            [ PROJECT_LEVEL, CING_STR, DIHEDRAL_COUNT_STR,uR(dict4,{MI: 0, MA: 4}) ],
            [ PROJECT_LEVEL, CING_STR, RDC_COUNT_STR,     uR(dict4,{MI: 0, MA: 5}) ],
#            [ PROJECT_LEVEL, CING_STR, PEAK_COUNT_STR,dict4 ],                          # These will come later.
            [ PROJECT_LEVEL, CING_STR, CS_COUNT_STR,      uR(dict4,{MI: 0, MA: 15}) ],
            [ PROJECT_LEVEL, CING_STR, CS1H_COUNT_STR,    uR(dict4,{MI: 0, MA: 10}) ],
            [ PROJECT_LEVEL, CING_STR, CS13C_COUNT_STR,   uR(dict4,{MI: 0, MA: 6}) ],
            [ PROJECT_LEVEL, CING_STR, CS15N_COUNT_STR,   uR(dict4,{MI: 0, MA: 2}) ],
            [ PROJECT_LEVEL, CING_STR, RES_COUNT_STR,     uR({},   {MI: 0, MA: 500}) ],
            [ PROJECT_LEVEL, CING_STR, MODEL_COUNT_STR,   uR({},   {MI: 0, MA: 100}) ],
            [ PROJECT_LEVEL, CING_STR, ROG_STR,{} ],                #11
            [ PROJECT_LEVEL, CING_STR, DIS_MAX_ALL_STR, uR(d5,{MI: 0, MA: 4}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_RMS_ALL_STR, uR(d5,{MI: 0, MA: 1}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_AV_ALL_STR , uR(d5,{MI: 0, MA: 1}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_AV_VIOL_STR, uR(d5,{MI: 0, MA: 1}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_C1_VIOL_STR, uR(d5,{MI: 0, MA: 20000}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_C3_VIOL_STR, uR(d5,{MI: 0, MA: 20000}) ],
            [ PROJECT_LEVEL, CING_STR, DIS_C5_VIOL_STR, uR(d5,{MI: 0, MA: 20000}) ],
            [ PROJECT_LEVEL, CING_STR, DIH_MAX_ALL_STR, uR(d5,{MI: 0 }) ],
            [ PROJECT_LEVEL, CING_STR, DIH_RMS_ALL_STR, uR(d5,{MI: 0, MA: 60}) ],
            [ PROJECT_LEVEL, CING_STR, DIH_AV_ALL_STR , uR(d5,{MI: 0, MA: 60}) ],       #21
            [ PROJECT_LEVEL, CING_STR, DIH_AV_VIOL_STR, uR(d5,{MI: 0, MA: 120}) ],
            [ PROJECT_LEVEL, CING_STR, DIH_C1_VIOL_STR, uR(d5,{MI: 0, MA: 4000}) ],
            [ PROJECT_LEVEL, CING_STR, DIH_C3_VIOL_STR, uR(d5,{MI: 0, MA: 4000}) ],
            [ PROJECT_LEVEL, CING_STR, DIH_C5_VIOL_STR, uR(d5,{MI: 0, MA: 4000}) ],
            [ PROJECT_LEVEL, WHATIF_STR, BBCCHK_STR,    uR(d5,{MI:-8, MA: 8}) ],
            [ PROJECT_LEVEL, WHATIF_STR, BNDCHK_STR,    uR(d5,{MI: 0, MA: 8}) ],
            [ PROJECT_LEVEL, WHATIF_STR, HNDCHK_STR,    uR(d5,{MI: 0, MA: 4}) ],
            [ PROJECT_LEVEL, WHATIF_STR, INOCHK_STR,    uR(d5,{MI: 0, MA: 2}) ],
            [ PROJECT_LEVEL, WHATIF_STR, NQACHK_STR,    uR(d5,{MI:-10,MA: 15}) ], # 29
            [ PROJECT_LEVEL, WHATIF_STR, OMECHK_STR,    uR(d5,{MI: 0, MA: 4}) ],           #31
            [ PROJECT_LEVEL, WHATIF_STR, PLNCHK_STR,    uR(d5,{MI: 0, MA: 4}) ],
            [ PROJECT_LEVEL, WHATIF_STR, QUACHK_STR,    uR(d5,{MI:-8, MA: 8}) ],
            [ PROJECT_LEVEL, WHATIF_STR, RAMCHK_STR,    uR(d5,{MI:-10,MA: 5}) ],
#            [ PROJECT_LEVEL, WHATIF_STR, ROTCHK_STR,    uR(d5,{MI: 0, MA: 4000}) ], # not done
            [ PROJECT_LEVEL, PC_STR, pc_gf_STR       ,  uR({},   {MI:-3, MA: 1}) ],
            [ PROJECT_LEVEL, PC_STR, pc_gf_PHIPSI_STR,  uR({},   {MI:-3, MA: 1}) ],
            [ PROJECT_LEVEL, PC_STR, pc_gf_CHI12_STR ,  uR({},   {MI:-3, MA: 1}) ],
            [ PROJECT_LEVEL, PC_STR, pc_gf_CHI1_STR  ,  uR({},   {MI:-1, MA: 1}) ],
            [ PROJECT_LEVEL, PC_STR, pc_rama_core_STR  ,uR({},   {MI: 0, MA: 100}) ],
            [ PROJECT_LEVEL, PC_STR, pc_rama_allow_STR ,uR({},   {MI: 0, MA: 100}) ],
            [ PROJECT_LEVEL, PC_STR, pc_rama_gener_STR ,uR({},   {MI: 0, MA: 20}) ],
            [ PROJECT_LEVEL, PC_STR, pc_rama_disall_STR,uR({},   {MI: 0, MA: 20}) ],
            [ PROJECT_LEVEL, WATTOS_STR, NOE_COMPL4_STR,uR(d5,   {MI: 0, MA: 100}) ], # 43
            [ RES_LEVEL, CING_STR, ROG_STR,             {} ], # idx is 44
            [ RES_LEVEL, CING_STR, DISTANCE_COUNT_STR,  uR(d5,{MI: 0, MA: 400})  ],
            [ RES_LEVEL, CING_STR, DIHEDRAL_COUNT_STR,  uR(d5,{MI: 0, MA: 10})  ],
            [ RES_LEVEL, CING_STR, RDC_COUNT_STR,       uR(d5,{MI: 0, MA: 10})  ],
#            [ RES_LEVEL, CING_STR, PEAK_COUNT_STR,      uR(d5,{MI: 0, MA: 4000})  ], # These will come later.
            [ RES_LEVEL, CING_STR, CS_COUNT_STR,        uR(d5,{MI: 0, MA: 40})  ],
            [ RES_LEVEL, CING_STR, CS1H_COUNT_STR,      uR(d5,{MI: 0, MA: 25})  ],
            [ RES_LEVEL, CING_STR, CS13C_COUNT_STR,     uR(d5,{MI: 0, MA: 20})  ],
            [ RES_LEVEL, CING_STR, CS15N_COUNT_STR,     uR(d5,{MI: 0, MA: 4000})  ],
#            [ RES_LEVEL, CING_STR, OMEGA_DEV_AV_ALL_STR,{} ],                       # ABSENT
            [ RES_LEVEL, CING_STR, CV_BACKBONE_STR,     uR({},   {MI: 0, MA: 1}) ],
            [ RES_LEVEL, CING_STR, CV_SIDECHAIN_STR,    uR({},   {MI: 0, MA: 1}) ],
            [ RES_LEVEL, CING_STR, CHK_RAMACH_STR,      uR({},   {MI:-3, MA: 3}) ],
            [ RES_LEVEL, CING_STR, CHK_JANIN_STR,       uR({},   {MI:-3, MA: 3}) ],
            [ RES_LEVEL, CING_STR, CHK_D1D2_STR,        uR({},   {MI:-3, MA: 3}) ],
            [ RES_LEVEL, CING_STR, DIS_MAX_ALL_STR,     uR(d5,{MI: 0, MA: 10})  ],   
            [ RES_LEVEL, CING_STR, DIS_RMS_ALL_STR,     uR(d5,{MI: 0, MA: 2})  ],   
            [ RES_LEVEL, CING_STR, DIS_AV_ALL_STR ,     uR(d5,{MI:-2, MA: 2})  ],   
            [ RES_LEVEL, CING_STR, DIS_AV_VIOL_STR,     uR(d5,{MI:-2, MA: 2})  ],   
            [ RES_LEVEL, CING_STR, DIS_C1_VIOL_STR,     uR(d5,{MI: 0, MA: 1000})  ],   
            [ RES_LEVEL, CING_STR, DIS_C3_VIOL_STR,     uR(d5,{MI: 0, MA: 1000})  ],   
            [ RES_LEVEL, CING_STR, DIS_C5_VIOL_STR,     uR(d5,{MI: 0, MA: 1000})  ],   
            [ RES_LEVEL, DSSP_STR, DSSP_ID_STR,         {} ],
            [ RES_LEVEL, PC_STR, pc_gf_STR       ,      {} ],
            [ RES_LEVEL, PC_STR, pc_gf_PHIPSI_STR,      {} ],
            [ RES_LEVEL, PC_STR, pc_gf_CHI12_STR ,      {MA: 5.0}  ],
            [ RES_LEVEL, PC_STR, pc_gf_CHI1_STR  ,      {} ],
            [ RES_LEVEL, WHATIF_STR, ACCLST_STR,        uR({},   {MI:-3, MA: 3}) ],   
            [ RES_LEVEL, WHATIF_STR, ANGCHK_STR,        uR({},   {MI: 0, MA:20}) ],   
            [ RES_LEVEL, WHATIF_STR, BBCCHK_STR,        {}],    # idx is 73
            [ RES_LEVEL, WHATIF_STR, BMPCHK_STR,        uR({},   {MI: 0, MA: 4}) ],   
            [ RES_LEVEL, WHATIF_STR, BNDCHK_STR,        uR({},   {MI: 0, MA:10}) ],   
            [ RES_LEVEL, WHATIF_STR, C12CHK_STR,        {}],   
            [ RES_LEVEL, WHATIF_STR, FLPCHK_STR,        uR({},   {MI: 0, MA: 4}) ],   
            [ RES_LEVEL, WHATIF_STR, INOCHK_STR,        {}],     
#            [ RES_LEVEL, WHATIF_STR, OMECHK_STR,        uR({},   {MI: 0, MA: 0.4}) ],    # ABSENT
#            [ RES_LEVEL, WHATIF_STR, PL2CHK_STR,        uR({},   {MI: 0, MA: 3}) ],    # ABSENT
            [ RES_LEVEL, WHATIF_STR, PL3CHK_STR,        uR({},   {MI: 0, MA: 0.4}) ],   
            [ RES_LEVEL, WHATIF_STR, PLNCHK_STR,        uR({},   {MI: 0, MA: 10}) ],   
            [ RES_LEVEL, WHATIF_STR, QUACHK_STR,        uR({},   {MI:-10, MA: 10}) ],   
            [ RES_LEVEL, WHATIF_STR, RAMCHK_STR,        uR({},   {MI:-2, MA: 3}) ],   
            [ RES_LEVEL, WHATIF_STR, ROTCHK_STR,        {}],   
#            [ RES_LEVEL, QSHIFT_STR, QCS_ALL_STR,       {} ], # ABSENT
#            [ RES_LEVEL, QSHIFT_STR, QCS_BB_STR,        {} ],
#            [ RES_LEVEL, QSHIFT_STR, QCS_HVY_STR,       {} ],
#            [ RES_LEVEL, QSHIFT_STR, QCS_PRT_STR,       {} ],
            [ RES_LEVEL, WATTOS_STR, NOE_COMPL4_STR   , uR(d5,   {MI: 0, MA: 100}) ],    #90
            [ RES_LEVEL, WATTOS_STR, NOE_COMPL_OBS_STR, uR(d5,   {MI: 0, MA: 100}) ],
            [ RES_LEVEL, WATTOS_STR, NOE_COMPL_EXP_STR, uR(d5,   {MI: 0, MA: 100}) ],
            [ RES_LEVEL, WATTOS_STR, NOE_COMPL_MAT_STR, uR(d5,   {MI: 0, MA: 100}) ],
            [ ATOM_LEVEL, WHATIF_STR, CHICHK_STR, {MI: -10.0, MA: 10.0} ], # 94
            [ ATOM_LEVEL, WHATIF_STR, HNDCHK_STR, {}  ], # ABSENT
            [ ATOM_LEVEL, WHATIF_STR, PL2CHK_STR, {MI:  0.0, MA:10.0}],
            [ CSLPA_LEVEL, VASCO_STR,          csd_STR,   {IS_OTHER_VALUE_STR: (( atomclass_STR, H_None_STR),),MI:-0.5, MA:0.5 } ], 
            [ CSLPA_LEVEL, VASCO_STR,          csd_STR,   {IS_OTHER_VALUE_STR: (( atomclass_STR, N_None_STR),),MI:-10,  MA: 10 } ],  
            [ CSLPA_LEVEL, VASCO_STR,          csd_STR,   {IS_OTHER_VALUE_STR: (( atomclass_STR, C_3_STR   ),),MI:-10,  MA: 10 } ],
            
        ]