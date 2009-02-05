"""
Script to import CCPN nomenclature (from file generate by TIM) into CING database

python -u addCCPN.py

Adjust sourceFile where needed
"""

from cing import * #@UnusedWildImport

sourceFile = 'CcpnResAtomNomenclature_081103.txt'

resdef = None
for line in AwkLike(sourceFile, commentString = '#'):
    d = line.dollar
    #print d[1]
    if d[1] == 'RESIDUE':
        ccpnName = ' '.join(d[13:])
        iupacName = d[9]
        if iupacName == '-': iupacName = None
        cyanaName = d[5]
        if cyanaName == '-': cyanaName = None
        dyanaName = d[7]
        if dyanaName == '-': dyanaName = None
        cingName  = d[3]
        if cingName == '-': cingName = None

        resdef = NTdb.getResidueDefByName(cingName, 'INTERNAL_0')
        if resdef:
            printf('==> line %d, Found CING: %s  IUPAC: "%s"  CCPN: "%s"\n', line.NR, resdef, iupacName, ccpnName)

            # check  names in CING database
            if resdef.translate(CYANA2) != cyanaName:
                NTwarning('line %d %s: CYANA2 nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, resdef,
                          resdef.translate(CYANA2), cyanaName)
            if resdef.translate(DYANA) != dyanaName:
                NTwarning('line %d %s: DYANA nomenclature CING database "%s" vrs CCPN database "%s"',  line.NR, resdef,
                          resdef.translate(DYANA), dyanaName)
            if resdef.translate(IUPAC) != iupacName:
                NTwarning('line %d %s: IUPAC nomenclature CING database "%s" vrs CCPN database "%s"',  line.NR, resdef,
                          resdef.translate(IUPAC), iupacName)
            #end if
            print ''
            # Add to nameDict
            resdef.nameDict[CCPN] = ccpnName
        else:
            printf( '==> line %d, Skipping residue IUPAC: "%s", CCPN: "%s"\n', line.NR, iupacName, ccpnName)
        #end if
    #end if

    elif d[1] == 'ENDRES':
        resdef = None
        print ''
        print ''

    elif d[1] == 'ATOM' and resdef != None:
        ccpnName = d[13]

        if d[9] == '-':
            iupacName = None
        else:
            iupacName = d[9]

        if d[7] == '-':
            dianaName = None
        else:
            dianaName = d[7]

        if d[5] == '-':
            cyanaName = None
        else:
            cyanaName = d[5]

        if d[3] == '-':
            cingName = dianaName
        else:
            cingName = d[3]

        atomdef = resdef.getAtomDefByName( cingName, INTERNAL)

        if resdef.name == 'HOH':
            print '>>', dianaName, cingName, ccpnName, resdef, atomdef

        if ccpnName in ['next_1','prev_1','prev_2']: # skip these lines as they are ccpn specific
            pass

        elif cingName == None:
            pass

        elif not atomdef:
            NTerror('line %d: %s undefined atom in CING; ccpn names DIANA: "%s" IUPAC: "%s" CCPN "%s"',
                     line.NR, resdef, dianaName, iupacName, ccpnName)
        else:
#            atomdef = resdef[dianaName]

            # check  names in CING database
            if atomdef.translate(CYANA2) != cyanaName:
                NTwarning('line %d %s: CYANA2 nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, atomdef,
                          atomdef.translate(CYANA2), cyanaName)
            #end if
            if atomdef.translate(IUPAC) != iupacName:
                NTwarning('line %d %s: IUPAC nomenclature CING database "%s" vrs CCPN database "%s"', line.NR, atomdef,
                          atomdef.translate(IUPAC), iupacName)
            #end if

            # add to nameDict
            atomdef.nameDict[CCPN] = ccpnName
        #end if
    #end fi
#end for

# Check all residueDefs and atomDefs
for res in NTdb.allResidueDefs():
    print '===================================='
    print res, 'CCPN:', res.translate(CCPN)

    for atm in res.allAtomDefs():
        print atm, 'CCPN:', atm.translate(CCPN)

f = open('database.txt','w')
NTdb.exportDef( stream = f )
f.close()
