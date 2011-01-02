<SML> 0.24

#=======================================================================
#             	name     convention
<ResidueDef>  	ILE      INTERNAL_1
#=======================================================================
	commonName = 'ILE'
	shortName  = 'I'
	comment    = 'Regular Ile residue'
	nameDict   = {'CCPN': 'protein Ile neutral', 'INTERNAL_0': 'ILE', 'CYANA': 'ILE', 'CYANA2': 'ILE', 'INTERNAL_1': 'ILE', 'IUPAC': 'ILE', 'AQUA': 'ILE', 'BMRBd': 'ILE', 'XPLOR': 'ILE', 'PDB': 'ILE'}
	properties = ['protein', 'aliphatic', 'methyl_containing', 'large', 'neutral']

	dihedrals  = <NTlist>
	#---------------------------------------------------------------
	<DihedralDef> PHI     
	#---------------------------------------------------------------
		atoms    = [(-1, 'C'), (0, 'N'), (0, 'CA'), (0, 'C')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> PSI     
	#---------------------------------------------------------------
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'C'), (1, 'N')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI1    
	#---------------------------------------------------------------
		atoms    = [(0, 'N'), (0, 'CA'), (0, 'CB'), (0, 'CG1')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> CHI2    
	#---------------------------------------------------------------
		atoms    = [(0, 'CA'), (0, 'CB'), (0, 'CG1'), (0, 'CD1')]
		karplus  = None
	</DihedralDef>
	#---------------------------------------------------------------
	<DihedralDef> OMEGA   
	#---------------------------------------------------------------
		atoms    = [(-1, 'CA'), (-1, 'C'), (0, 'N'), (0, 'CA')]
		karplus  = None
	</DihedralDef>
	</NTlist>

	atoms      = <NTlist>
	#---------------------------------------------------------------
	<AtomDef> N       
	#---------------------------------------------------------------
		topology   = [(-1, 'C'), (0, 'H'), (0, 'CA')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'N', 'INTERNAL_0': 'N', 'CYANA': 'N', 'CYANA2': 'N', 'INTERNAL_1': 'N', 'IUPAC': 'N', 'AQUA': 'N', 'BMRBd': 'N', 'XPLOR': 'N', 'PDB': 'N'}
		aliases    = []
		type       = 'N_AMI'
		spinType   = '15N'
		shift      = NTdict( average = 121.59, sd = 4.8600000000000003 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNitrogen', 'nitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H       
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'H', 'INTERNAL_0': 'HN', 'CYANA': 'HN', 'CYANA2': 'H', 'INTERNAL_1': 'H', 'IUPAC': 'H', 'AQUA': 'H', 'BMRBd': 'H', 'XPLOR': 'HN', 'PDB': 'H'}
		aliases    = ['HN', 'H']
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2799999999999994, sd = 0.70999999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CA      
	#---------------------------------------------------------------
		topology   = [(0, 'N'), (0, 'HA'), (0, 'CB'), (0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CA', 'INTERNAL_0': 'CA', 'CYANA': 'CA', 'CYANA2': 'CA', 'INTERNAL_1': 'CA', 'IUPAC': 'CA', 'AQUA': 'CA', 'BMRBd': 'CA', 'XPLOR': 'CA', 'PDB': 'CA'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 61.600000000000001, sd = 2.7799999999999998 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HA      
	#---------------------------------------------------------------
		topology   = [(0, 'CA')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HA', 'INTERNAL_0': 'HA', 'CYANA': 'HA', 'CYANA2': 'HA', 'INTERNAL_1': 'HA', 'IUPAC': 'HA', 'AQUA': 'HA', 'BMRBd': 'HA', 'XPLOR': 'HA', 'PDB': 'HA'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 4.1900000000000004, sd = 0.57999999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CB      
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'HB'), (0, 'CG2'), (0, 'CG1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CB', 'INTERNAL_0': 'CB', 'CYANA': 'CB', 'CYANA2': 'CB', 'INTERNAL_1': 'CB', 'IUPAC': 'CB', 'AQUA': 'CB', 'BMRBd': 'CB', 'XPLOR': 'CB', 'PDB': 'CB'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 38.659999999999997, sd = 2.75 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HB      
	#---------------------------------------------------------------
		topology   = [(0, 'CB')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'HB', 'INTERNAL_0': 'HB', 'CYANA': 'HB', 'CYANA2': 'HB', 'INTERNAL_1': 'HB', 'IUPAC': 'HB', 'AQUA': 'HB', 'BMRBd': 'HB', 'XPLOR': 'HB', 'PDB': 'HB'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.8, sd = 0.54000000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> MG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = ['HG21', 'HG22', 'HG23']
		pseudo     = None
		nameDict   = {'CCPN': 'HG2*', 'INTERNAL_0': 'QG2', 'CYANA': 'QG2', 'CYANA2': 'QG2', 'INTERNAL_1': 'MG', 'IUPAC': 'MG', 'AQUA': 'MG', 'BMRBd': 'HG2', 'XPLOR': 'HG2*,HG2#,HG2%,HG2+', 'PDB': None}
		aliases    = ['MG', 'QG2']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 0.78000000000000003, sd = 0.40000000000000002 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG2     
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG21'), (0, 'HG22'), (0, 'HG23')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CG2', 'INTERNAL_0': 'CG2', 'CYANA': 'CG2', 'CYANA2': 'CG2', 'INTERNAL_1': 'CG2', 'IUPAC': 'CG2', 'AQUA': 'CG2', 'BMRBd': 'CG2', 'XPLOR': 'CG2', 'PDB': 'CG2'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 17.670000000000002, sd = 2.9199999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG21    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'CCPN': 'HG21', 'INTERNAL_0': 'HG21', 'CYANA': 'HG21', 'CYANA2': 'HG21', 'INTERNAL_1': 'HG21', 'IUPAC': 'HG21', 'AQUA': 'HG21', 'BMRBd': None, 'XPLOR': 'HG21', 'PDB': '1HG2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG22    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'CCPN': 'HG22', 'INTERNAL_0': 'HG22', 'CYANA': 'HG22', 'CYANA2': 'HG22', 'INTERNAL_1': 'HG22', 'IUPAC': 'HG22', 'AQUA': 'HG22', 'BMRBd': None, 'XPLOR': 'HG22', 'PDB': '2HG2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG23    
	#---------------------------------------------------------------
		topology   = [(0, 'CG2')]
		real       = []
		pseudo     = 'MG'
		nameDict   = {'CCPN': 'HG23', 'INTERNAL_0': 'HG23', 'CYANA': 'HG23', 'CYANA2': 'HG23', 'INTERNAL_1': 'HG23', 'IUPAC': 'HG23', 'AQUA': 'HG23', 'BMRBd': None, 'XPLOR': 'HG23', 'PDB': '3HG2'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CG1     
	#---------------------------------------------------------------
		topology   = [(0, 'CB'), (0, 'HG12'), (0, 'HG13'), (0, 'CD1')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CG1', 'INTERNAL_0': 'CG1', 'CYANA': 'CG1', 'CYANA2': 'CG1', 'INTERNAL_1': 'CG1', 'IUPAC': 'CG1', 'AQUA': 'CG1', 'BMRBd': 'CG1', 'XPLOR': 'CG1', 'PDB': 'CG1'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 27.800000000000001, sd = 3.8100000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG12    
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'CCPN': 'HG12', 'INTERNAL_0': 'HG12', 'CYANA': 'HG12', 'CYANA2': 'HG12', 'INTERNAL_1': 'HG12', 'IUPAC': 'HG12', 'AQUA': 'HG12', 'BMRBd': 'HG12', 'XPLOR': 'HG12', 'PDB': '1HG1'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.26, sd = 0.62 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HG13    
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = []
		pseudo     = 'QG'
		nameDict   = {'CCPN': 'HG13', 'INTERNAL_0': 'HG13', 'CYANA': 'HG13', 'CYANA2': 'HG13', 'INTERNAL_1': 'HG13', 'IUPAC': 'HG13', 'AQUA': 'HG13', 'BMRBd': 'HG13', 'XPLOR': 'HG11', 'PDB': '2HG1'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = NTdict( average = 1.22, sd = 0.72999999999999998 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> QG      
	#---------------------------------------------------------------
		topology   = [(0, 'CG1')]
		real       = ['HG12', 'HG13']
		pseudo     = None
		nameDict   = {'CCPN': 'HG1*', 'INTERNAL_0': 'QG1', 'CYANA': 'QG1', 'CYANA2': 'QG1', 'INTERNAL_1': 'QG', 'IUPAC': 'QG', 'AQUA': 'QG', 'BMRBd': None, 'XPLOR': 'HG1*,HG1#,HG1%,HG1+', 'PDB': None}
		aliases    = ['QG', 'QG1']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 1.24, sd = 0.67500000000000004 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isMethylene', 'methylene', 'isMethyleneProton', 'methyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> MD      
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = ['HD11', 'HD12', 'HD13']
		pseudo     = None
		nameDict   = {'CCPN': 'HD1*', 'INTERNAL_0': 'QD1', 'CYANA': 'QD1', 'CYANA2': 'QD1', 'INTERNAL_1': 'MD', 'IUPAC': 'MD', 'AQUA': 'MD', 'BMRBd': 'HD1', 'XPLOR': 'HD1*,HD1#,HD1%,HD1+,HD*,HD#', 'PDB': None}
		aliases    = ['MD', 'QD1']
		type       = 'PSEUD'
		spinType   = '1H'
		shift      = NTdict( average = 0.67000000000000004, sd = 0.45000000000000001 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isPseudoAtom', 'pseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> CD1     
	#---------------------------------------------------------------
		topology   = [(0, 'CG1'), (0, 'HD11'), (0, 'HD12'), (0, 'HD13')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'CD1', 'INTERNAL_0': 'CD1', 'CYANA': 'CD1', 'CYANA2': 'CD1', 'INTERNAL_1': 'CD1', 'IUPAC': 'CD1', 'AQUA': 'CD1', 'BMRBd': 'CD1', 'XPLOR': 'CD1', 'PDB': 'CD1'}
		aliases    = []
		type       = 'C_ALI'
		spinType   = '13C'
		shift      = NTdict( average = 13.69, sd = 3.6000000000000001 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD11    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'CCPN': 'HD11', 'INTERNAL_0': 'HD11', 'CYANA': 'HD11', 'CYANA2': 'HD11', 'INTERNAL_1': 'HD11', 'IUPAC': 'HD11', 'AQUA': 'HD11', 'BMRBd': None, 'XPLOR': 'HD11', 'PDB': '1HD1'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD12    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'CCPN': 'HD12', 'INTERNAL_0': 'HD12', 'CYANA': 'HD12', 'CYANA2': 'HD12', 'INTERNAL_1': 'HD12', 'IUPAC': 'HD12', 'AQUA': 'HD12', 'BMRBd': None, 'XPLOR': 'HD12', 'PDB': '2HD1'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> HD13    
	#---------------------------------------------------------------
		topology   = [(0, 'CD1')]
		real       = []
		pseudo     = 'MD'
		nameDict   = {'CCPN': 'HD13', 'INTERNAL_0': 'HD13', 'CYANA': 'HD13', 'CYANA2': 'HD13', 'INTERNAL_1': 'HD13', 'IUPAC': 'HD13', 'AQUA': 'HD13', 'BMRBd': None, 'XPLOR': 'HD13', 'PDB': '3HD1'}
		aliases    = []
		type       = 'H_ALI'
		spinType   = '1H'
		shift      = None
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isSidechain', 'sidechain', 'isNotAromatic', 'notaromatic', 'isMethyl', 'methyl', 'isMethylProton', 'methylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasPseudoAtom', 'haspseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> C       
	#---------------------------------------------------------------
		topology   = [(0, 'CA'), (0, 'O'), (1, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'C', 'INTERNAL_0': 'C', 'CYANA': 'C', 'CYANA2': 'C', 'INTERNAL_1': 'C', 'IUPAC': 'C', 'AQUA': 'C', 'BMRBd': 'C', 'XPLOR': 'C', 'PDB': 'C'}
		aliases    = ['C', 'CO']
		type       = 'C_BYL'
		spinType   = '13C'
		shift      = NTdict( average = 175.94, sd = 1.9299999999999999 )
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isCarbon', 'carbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> O       
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'CCPN': 'O', 'INTERNAL_0': 'O', 'CYANA': 'O', 'CYANA2': 'O', 'INTERNAL_1': 'O', 'IUPAC': 'O', 'AQUA': 'O', 'BMRBd': 'O', 'XPLOR': 'O', 'PDB': 'O'}
		aliases    = ['O', "O'"]
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H1      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H1', 'INTERNAL_1': 'H1', 'IUPAC': 'H1', 'CCPN': 'H1', 'XPLOR': 'H1'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2799999999999994, sd = 0.70999999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H2      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H2', 'INTERNAL_1': 'H2', 'IUPAC': 'H2', 'CCPN': 'H2', 'XPLOR': 'H2'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2799999999999994, sd = 0.70999999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> H3      
	#---------------------------------------------------------------
		topology   = [(0, 'N')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'H3', 'INTERNAL_1': 'H3', 'IUPAC': 'H3', 'CCPN': 'H3', 'XPLOR': 'H3'}
		aliases    = []
		type       = 'H_AMI'
		spinType   = '1H'
		shift      = NTdict( average = 8.2799999999999994, sd = 0.70999999999999996 )
		hetatm     = False
		properties = ['isProton', 'proton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	#---------------------------------------------------------------
	<AtomDef> OXT     
	#---------------------------------------------------------------
		topology   = [(0, 'C')]
		real       = []
		pseudo     = None
		nameDict   = {'INTERNAL_0': 'OXT', 'INTERNAL_1': 'OXT', 'IUPAC': "OXT,O''", 'CCPN': "O''", 'XPLOR': 'OXT'}
		aliases    = ['OXT', "O''"]
		type       = 'O_BYL'
		spinType   = '16O'
		shift      = None
		hetatm     = False
		properties = ['isNotProton', 'notproton', 'isNotCarbon', 'notcarbon', 'isNotNitrogen', 'notnitrogen', 'isNotSulfur', 'isNotSulphur', 'notsulfur', 'notsulphur', 'isBackbone', 'backbone', 'isNotAromatic', 'notaromatic', 'isNotMethyl', 'notmethyl', 'isNotMethylProton', 'notmethylproton', 'isNotPseudoAtom', 'notpseudoatom', 'hasNoPseudoAtom', 'hasnopseudoatom', 'isSidechain', 'sidechain', 'isNotMethylene', 'notmethylene', 'isNotMethyleneProton', 'notmethyleneproton']
	</AtomDef>
	</NTlist>
</ResidueDef>
#=======================================================================
</SML>
