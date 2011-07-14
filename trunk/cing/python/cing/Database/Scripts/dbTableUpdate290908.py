#@PydevCodeAnalysisIgnore
from cing.Libs.NTutils import *
from cing.core.database import ResidueDef
from cing import NTdb, printf
import cing

def renameKey( theDict, oldKey, newKey):
    if theDict.has_key(oldKey):
        tmp = theDict[oldKey]
        del(theDict[oldKey])
        theDict[newKey] = tmp
    #end if
#end def

#print out problematic cases; already name BMRB IUPAC
for rdef in NTdb:
    printf('===> residue INTERNAL_0: %-8s IUPAC: %-8s  CYANA2: %-8s', rdef.name, rdef.translate('BMRB'), rdef.translate('CYANA2'))
    if rdef.name != rdef.translate('BMRB'):
        printf(' ****\n')
    else:
        printf('\n')

    for adef in rdef:
        bname = adef.translate('BMRB')
        cname = adef.translate('CYANA2')
        if bname != cname:
            printf('IUPAC: %-8s  CYANA2: %-8s\n', bname, cname)
    #end for

    print('\n')
#end for

for adef in NTdb.atomsWithProperties('HN'):
    adef.aliases = ['HN','H']
for adef in NTdb.atomsWithProperties('C'): # This generated erros with the cys residues
    adef.aliases = ['C','CO']

printf('''
===================================================================================
- Changing existing BMRB->IUPAC
- Changing existing INTERNAL->INTERNAL_0
- Adding INTERNAL_1 ResidueDefs:
  keep original residue names (manual check required)
- Adding INTERNAL_1 atomDefs:
  Use BMRB/IUPAC or CYANA2 if BMRB/IUPAC undefined
  Add CYANA2 names as alias if different from BMRB/IUPAC
===================================================================================

''')

for rdef in NTdb.allResidueDefs():
    renameKey( rdef.nameDict, 'BMRB','IUPAC')
    renameKey( rdef.nameDict, 'INTERNAL','INTERNAL_0')
    rdef.nameDict['INTERNAL_1'] = rdef.name

for adef in NTdb.allAtomDefs():
    bname = adef.translate('BMRB')
    cname = adef.translate('CYANA2')
    renameKey( adef.nameDict, 'BMRB','IUPAC')
    renameKey( adef.nameDict, 'INTERNAL','INTERNAL_0')
    if bname == None:
        adef.nameDict['INTERNAL_1'] = cname
    else:
        adef.nameDict['INTERNAL_1'] = bname
        if bname != cname:
            adef.aliases.append(bname)
            adef.aliases.append(cname)
        #end if
    #end if

    # just a check; should not happen
    if adef.nameDict['INTERNAL_1'] == None:
        nTerror('INTERNAL_1 def of %s undefined', adef)
        exit(1)
    #end if
#end for

cing.INTERNAL = 'INTERNAL_0'

stream = open('dbTable.290908', 'w')
NTdb.exportDef(stream=stream, convention='INTERNAL_0')
stream.close()
