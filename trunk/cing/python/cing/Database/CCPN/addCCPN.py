"""
Script to import CCPN nomenclature (from file generate by TIM) into CING database
"""

from cing import *

resdef = None
for line in AwkLike('CcpnResAtomNomenclature.txt'):
    d = line.dollar
    #print d[1]
    if d[1] == 'RESIDUE':
        ccpnName = ' '.join(d[13:])
        iupacName = d[9]
        cyanaName = d[5]
        dyanaName = d[7]

        if d[3] in NTdb:
            resdef = NTdb[d[3]]
            printf('==> line %d, Found CING: %s  IUPAC: "%s"  CCPN: "%s"\n', line.NR, resdef, iupacName, ccpnName)

            # check  names in CING database
            if resdef.translate(CYANA2) != cyanaName:
                NTwarning('line %d %s: CYANA nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, resdef,
                          resdef.translate(CYANA2), cyanaName)
            if resdef.translate(CYANA) != d[7]:
                NTwarning('line %d %s: DYANA nomenclature CING database "%s" vrs CCPN database "%s"',  line.NR, resdef,
                          resdef.translate(CYANA), dyanaName)
            if resdef.translate(IUPAC) != d[9]:
                NTwarning('line %d %s: IUPAC nomenclature CING database "%s" vrs CCPN database "%s"',  line.NR, resdef,
                          resdef.translate(IUPAC), iupacName)
            #end if
            print ''
        else:
            printf( '==> line %d, Skipping residue IUPAC: "%s", CCPN: "%s"\n', line.NR, iupacName, ccpnName)
            resdef = None
        #end if
    #end if

    elif d[1] == 'ENDRES':
        resdef = None
        print ''
        print ''

    elif d[1] == 'ATOM' and resdef != None:
        ccpnName = d[13]
        iupacName = d[9]
        if d[7] == '-':
            dianaName = ccpnName
        else:
            dianaName = d[7]
        if d[5] == '-':
            cyanaName = ccpnName
        else:
            cyanaName = d[5]

        if not dianaName in resdef:
            NTerror('line %d: %s undefined atom DIANA: "%s" IUPAC: "%s" CCPN "%s"', line.NR, resdef, dianaName, iupacName, ccpnName)
        else:
            atomdef = resdef[dianaName]

            # check  names in CING database
            if atomdef.translate(CYANA2) != cyanaName:
                NTwarning('line %d %s: CYANA nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, atomdef,
                          atomdef.translate(CYANA2), cyanaName)
            if atomdef.translate(IUPAC) != iupacName:
                NTwarning('line %d %s: IUPAC nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, atomdef,
                          atomdef.translate(IUPAC), iupacName)
            #end if

    #end fi
#end for