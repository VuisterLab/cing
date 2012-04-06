'''
Execute as:
python -u $CINGROOT/python/cing/Scripts/CombineRestraints.py

Created on May 2, 2011

@author: Karen Berntsen

This script will combine restraints, such that xplor allows two
possible leucine conformations.This script will combine them on upper distance restraint.
First the script is going to deassign all HB's in the specific leucine, secondly it calculates
the violations in the trans and in the gauche+ combination and finally it combines the
restraints in the project. This script follows on script rotateleucinesinyasara.py. This script cannot yet
handle multimers.

!!Be careful: Make a copy of your project before you run this one. This script will alter
the restraints in you project. It is not possible to restore them!!
'''

from cing.Scripts.munkres import Munkres
from cing.core.classes import * #@UnusedWildImport
from cing.core.molecule import * #@UnusedWildImport
from collections import defaultdict
from itertools import combinations

CHI1_LOW_DEFAULT  = 120.
CHI2_LOW_DEFAULT  = 0.
CHI2_UPP_DEFAULT  = 240.

# The four (or twelve) chi dihedral angle values 
CHI1_LIST = [300, 180] # g-/t, t/g+
CHI2_LIST = [180,  60]
#CHI1_LIST=[-60,-49,-41,-48,-53,-63,-75,-79,-78,-70,180,-169,-163,-162,-170,180,171,168,166,173]
#CHI1_LIST=[-60, -60,-41,-53,-75,-78,180,-169,-162,180,168,173]
#CHI1_LIST=[-60,-53,180,173]
#CHI2_LIST=[-165,-173,180,169,161,154,157,167,180,-171,79,75,68,60,53,49,54,60,69,73]
#CHI2_LIST=[180,-165,180,161,157,180, 60,  75,  60, 49, 60, 73]
#CHI2_LIST=[180,161, 60, 73]
ROTL_STR = 'rotl'
CV_THRESHOLD_SELECTION = 0.1
LEU_STR = 'LEU'

def addDihRestr(proj, lower = CHI2_LOW_DEFAULT, upper = CHI2_UPP_DEFAULT, leuList=None):
    '''
    Adding CHI2 dihedral restraints to leucines, specified in leuList. lower and upper are the lower bound and upper bound of the restraint.
    The restraints will be put in a new restraint list
    '''
    nTmessage("Starting %s" % getCallerName())
    dihrestrlist = DihedralRestraintList(name='Artificial')
    for r in leuList:
        atoms = [r.CA, r.CB, r.CG, r.CD1]
        dihedralrestraint = DihedralRestraint(atoms=atoms, lower=CHI2_LOW_DEFAULT, upper=CHI2_UPP_DEFAULT)
        dihrestrlist.append(dihedralrestraint)
        nTmessage('Restraint appended %s' % dihedralrestraint)
    #end for
    proj.dihedrals.append(dihrestrlist)
    proj.partitionRestraints()
    return proj
# end def

def checkDoubleRestraints(proj, leu):
    '''
    After deassignment, some atomPairs occur twice in the distance restraint list. 
    This script will delete the one with the highest upper bound.
    TODO: fix this code for when the atom pair elements are swapped. E.g.:
            a,b == b,a for this purpose.
            Can easily be done with findDuplicates
    '''
    nTmessage("Starting %s" % getCallerName())
    nTmessage('Checking for double restraints after deassignment')
    delList = []
    drlist = leu.distanceRestraints
    for i,dr in enumerate(drlist):
        for j in range(i):
            dr2 = drlist[j]
            ap = dr.atomPairs
            ap2 = dr2.atomPairs
#            nTdebug("Checking between: %s and %s" % (str(ap),str(ap2)))
            if not ap == ap2:
#                nTdebug("Skipping different atom pairs.")
                continue
            #end if
            if dr.upper > dr2.upper:
#                nTdebug("Tagging first dr for removal.")
                delList.append(dr)
            else:
#                nTdebug("Tagging 2nd   dr for removal.")
                delList.append(dr2)
            #end if
        #end for
    #end for
    if delList:
        proj = deleteRestraints(delList, proj)
        checkRestraintsExistance(delList, proj)
    #end if
    return(proj)
# end def

def checkRestraintsExistance(restraintlist, proj):
    '''
    After deleting half of the double restraints, this script will check whether the other halve is still there.
    '''
    nTmessage("Starting %s" % getCallerName())
    if not restraintlist:
        nTdebug('No restraints involving this leucine presented.')
    # end if
#    nTdebug('Project still contains and should contain the following leucine restraints:')
    aplist = [] # list with unique atompairs in restraint list
    count = 0
    for dr in restraintlist:
        aplist.append(dr.atomPairs[0])
    #end for
    for ap in list(set(aplist)):
        for dr in proj.distances[0]:
            if ap == dr.atomPairs[0]:
                count += 1
#                nTdebug('%s,id=%s' % (str(ap), str(dr.id)))
            #end if
        #end for
    #end for                
    if count == 0:
        nTerror('No restraints found')
    #end if
#end def

def deassignHB(proj, leu):
    '''
    Deassigns HBs in specified leucines. It will replace the old restraint, in order to delete all the other information.
    TODO: adapt for ambiguous restraints.
    TODO: adapt for multiple DR lists.
    Returns list of atomPairs involving SSA HBs.
    '''
    nTmessage('In %s looking at restraints with SSA HBs of %s with %s DRs in %s' % (
        getCallerName(), leu, len(leu.distanceRestraints), proj))
    deassHBaplist = []
    for dr in leu.distanceRestraints: 
#        nTdebug("Looking at: %s" % dr)
        ap = dr.atomPairs[0] # TODO: adapt for ambiguous restraints by adding a loop here. 
        atom1 = ap[0]
        atom2 = ap[1]
        for ai in [0, 1]:
            atom = ap[ai]
#            if atom.residue.resNum != leu.resNum: # Fails for multimers.
            if atom.residue != leu:
#                nTdebug("Skipping this side of the DR not from this leucine.")
                continue
            #end if
            atomname = atom.name
            if not atomname.startswith('HB'):
#                nTdebug("Skipping this side of the DR that has a LEU atom other than a beta hydrogen.")
                continue
            #end if
            if ai == 0:
                atom1 = atom.pseudoAtom()
            else:
                atom2 = atom.pseudoAtom()
            #end if
            newList = NTlist()
            deassHBaplist.append((atom1, atom2))
            newList.append((atom1, atom2))
            nTmessage('Deassigning: %-50s -> %-50s' % (str(dr.atomPairs), str(newList)))
            dr.atomPairs = newList
            if True: # coverage fails to understand the indentation of a break at the end of a loop.
                break
            #end if
            pass # pylint: disable=W0107
        # end for
    # end for
    proj = checkDoubleRestraints(proj, leu)
    proj.distances[0].analyze() #TODO: adapt for multiple DR lists.
    return deassHBaplist
#end def

def checkDeasrHB(n, deassHBaplist):
    '''
    If an atom pair with a HB is already deassigned, it must be removed from the list to deassign. 
    deassHBaplist is the list which is already deassigned
    and n is the list of restraints, which violate in trans and gauche+, which should be deassigned.
    '''
    nTmessage("Starting %s" % getCallerName())
    atomIndexes = [0, 1]
    delList = []
    #l=len(deassHBaplist)
    #ln=len(n)
    for dr in n:
        for j in deassHBaplist:
            if str(dr[atomIndexes[0]]) == str(j[atomIndexes[0]]) and str(dr[atomIndexes[1]]) == str(j[atomIndexes[1]]):
                delList.append(dr)
            #end if
        #end for
    #end for
    for dr in delList:
        n.remove(dr)
        nTmessage('%s will not be removed.' % str(dr))
    #end for
    #if ln-len(n)==len(delList): #just a check,used while debugging.
    #    nTmessage('%s restraints with a QB will not be deleted.'%len(delList))
    return n
# end def

def classifyRestraints(prl, leu, threshold):
    """
    This routine scans the restraints of leu in prl for violations in the second and third model. These restraints
    are then classified in four groups: 
        1 violated in the second (t), 
        2 violated in the third (g+), 
        3 violated in both (n) and 
        4 not violated in both(u).
    Threshold for the violation is the violation in the first original model with the Leucine rotated exactly in gp or tr.
    """
    nTmessage("Starting %s" % getCallerName())
    # All atoms and pseudoatoms in the leucine side chain, which have different positions in different rotameric states:
    # (all but CB)
    scall = ['HB2', 'HB3', 'MD1', 'MD2', 'QD', 'HG', 'CG', 'QB', 'HD11', 'HD12', 'HD13', 'HD21', 'HD22', 'HD23', 'CD1', 'CD2']
    #side chain atoms leucine list
    n = [] #atom pairs of restraints which violates in t and g+
    u = [] #atom pairs of restraints which are unviolated in both t and g+
    trdict = {} #keys=atompairs of restraints which violate in t, values=(upperbound,violation in t)
    gpdict = {} #keys=atompairs of restraints which violate in gauche+, values=(upperbound,violation in gp)
    atomIndexes = [0, 1]
    modelCount = len(prl.models)
    halfModelCount = modelCount / 2
    thresholdModelCount = 10
    trind = range(halfModelCount) #trans index
    gpind = range(halfModelCount, modelCount, 1) #gauche+ index
    #leu=prl.molecules[0].residuesWithProperties('LEU')[leunumber] #leucine g
    nTmessage('Divide restraints into classes for %s' % leu.name)
    drlleu = leu.distanceRestraints #distance restraints of leucine g
    for k in range(len(drlleu)):
        found = 0
        dr = drlleu[k] #distance restraint k of this leucine
        for a in range(len(scall)): #loops over the atoms in scall
            if found == 1:
                break
            #end if
            for ai in atomIndexes: #specifies first or second atom in atompair of restraint
                if not dr.atomPairs[0][ai].atomsWithProperties('LEU', scall[a]):
                    continue
                #end if
                if not dr.atomPairs[0][ai].residue.resNum == leu.resNum:
                    continue
                #end if
                violCountTr = 0
                violTr = 0
                violTreshTr = dr.violations[0] #first model
                #violMinTr=min(dr.violations[:halfModelCount])
                #violTreshTr=violMinTr
                for i in trind:
                    if dr.violations[i] > threshold:
                        violCountTr += 1
                        violTr += dr.violations[i]
                    #end if
                #end for
                if violCountTr != 0:
                    violTr = violTr / violCountTr #average violation over all violated conformations
                #end if
                violCountGp = 0
                violGp = 0
                violTreshGp = dr.violations[halfModelCount]
                #violMinGp=min(dr.violations[halfModelCount:])
                #violTreshGp=violMinGp
                for i in gpind:
                    if dr.violations[i] > threshold:
                        violCountGp += 1
                        violGp += dr.violations[i]
                    #end if
                #end for
                if violCountGp != 0:
                    violGp = violGp / violCountGp #average violation over all violated conformations
                #end if
                if violCountGp + violCountTr == 0:
                    u.append(dr.atomPairs[0])
                elif (violCountTr > (violCountGp + thresholdModelCount) and violTr > violGp):
                    trdict[dr.atomPairs[0]] = (dr.upper, violTreshTr)
                elif violCountGp > (violCountTr + thresholdModelCount) and violGp > violTr:
                    gpdict[dr.atomPairs[0]] = (dr.upper, violTreshGp)
                elif violCountGp < thresholdModelCount and violCountTr < thresholdModelCount:
                    #less than 10 violations is not enough to classify restraint.
                    u.append(dr.atomPairs[0])
                else:
                    n.append(dr.atomPairs[0])
                #end if
                found = 1
                break
            #end for ai
        #end for a
    #end for k (leu)
    tmplist = [trdict.keys(), gpdict.keys(), n, u]
    namelist = ['trans', 'gauche+', 'both', 'none']
    for i in range(4):
        if tmplist[i]:
            nTmessage('list violated in %s for %s contains %s restraints' % (namelist[i], leu.name, len(tmplist[i])))
        #end if
    #end for
    return(n, u, trdict, gpdict)
# end def

def renameDicts(trdict, gpdict):
    '''Renames the dictionaries with distance restraint lists, called tr and g+, to dictionaries for the columns and the rows in a table,
    such that the amount of columns is never higher than the amount of rows.'''
    nTmessage("Starting %s" % getCallerName())
    ltr = len(trdict)
    lgp = len(gpdict)
    if ltr > lgp:
        drlColumnsdict, drlColumns, lenDrlColumns = dictValues(gpdict)
        drlRowsdict, drlRows, lenDrlRows = dictValues(trdict)
    else:
        drlColumnsdict, drlColumns, lenDrlColumns = dictValues(trdict)
        drlRowsdict, drlRows, lenDrlRows = dictValues(gpdict)
    #end if
    return drlColumnsdict, drlColumns, lenDrlColumns, drlRowsdict, drlRows, lenDrlRows
# end def

def dictValues(vdict):
    '''Returns the dictionary, the sorted list of values and the length of this list.'''
    nTmessage("Starting %s" % getCallerName())
    v = vdict.values()
    v.sort()
    lenv = len(v)
    return(vdict, v, lenv,)
# end def

def reverseDict(vdict):
    '''
    Interchange of keys and values in a dictionary. 
    In case a value occurs twice, the dictionary will have two keys in a list for that value.
    '''
    nTmessage("Starting %s" % getCallerName())
    rdict = defaultdict(list)
    for ii, jj in vdict.items():
        rdict[jj].append(ii)
    #end for
    return rdict
# end def

def tablePrint(table, ln):
    'Just a handy script to print tables while debugging. Length is the number of characters per element in table'
    string = ''
    fmt = '%-' + str(ln) + '.2f' #to be able to print the table aligned, this value has to depend on the len of an element in the table
    for r in table:
        for c in r:
            string += fmt % c
        #end for
        string += '\n'
    #end for
    return string
# end def

def makeDifferenceTable(drlColumns, drlRows, lenDrlColumns, lenDrlRows):
    '''
    table gives the absolute differences in upper-bounds between the restraints
    in the a-set and the b-set. So you can look up every difference in upper bound
    between two restraints, one of a and one of b.
    '''
    nTmessage("Starting %s" % getCallerName())
    table = [ [ 0 for _i in range(lenDrlColumns) ] for _j in range(lenDrlRows) ] #table with only zeros
    for c in range(lenDrlColumns):
        for r in range(lenDrlRows):
            diff = drlColumns[c][0] - drlRows[r][0]
            table[r][c] = abs(diff)
        #end for
    #end for
    #stringTable=tablePrint(table,5)
    #nTmessage('Difference table is:\n%s'%stringTable)
    return table
# end def

def makeAllowedTable(table, drlColumns, drlRows, lenDrlColumns, lenDrlRows):
    '''
    Every element in allowed table is the element in table minus the
    largest violation of the pair of restraints. If the violation is
    bigger than the difference, the value becomes negative. This combination
    of restraints will not be used. Therefore all negative values are set to
    a very high value (maxi).The values are enlarged by a factor 1000 so that
    the munkres algorithm can work with it.
    '''
    nTmessage("Starting %s" % getCallerName())
    maxi = 9999999 #Munkres cannot work with float("infinity") and None objects
    allowedTable = [ [ 0 for _i in range(lenDrlColumns) ] for _j in range(lenDrlRows) ] #table with only zeros
    for c in range(lenDrlColumns):
        for r in range(lenDrlRows):
            diff = table[r][c]
            diffCor = diff
            if drlRows[r][0] > drlColumns[c][0]:
                diffCor -= drlColumns[c][1]
            elif drlRows[r][0] < drlColumns[c][0]:
                diffCor -= drlRows[r][1]
            elif drlRows[r][0] == drlColumns[c][0]:
                diffCor -= (drlColumns[c][1] + drlRows[r][1]) / 2
            #end if
            if diffCor < 0:
                allowedTable[r][c] = diff * 1000
            else:
                allowedTable[r][c] = maxi
            #end if
        #end for
    #end for
    #stringTable=tableprint(allowedTable,15)
    #nTmessage('Allowed table is:\n%s'%stringTable)
    return(allowedTable, maxi)
# end def

def checkAllowedTable(allowedTable, table, maxi, n, lenDrlColumns, lenDrlRows, drlColumns, drlRows, invdrlColumnsdict, invdrlRowsdict):
    '''
    Checks whether allowedTable has columns or rows which consist only of maximum values. In that case, the row or column
    cannot be combined and should be deassigned or deleted, so the restraint will be added to the list of restraints which
    violate both in tr as in g+, because these restraints also have to be deassigned or deleted.
    This check happens before calculating the best combination, because the deletion of these columns/rows will lead to
    better combinations and less computation time.
    '''
    nTmessage("Starting %s" % getCallerName())
    delListrows = []
    delListcolumns = []
    for r in range(lenDrlRows):
        if min(allowedTable[r]) == maxi:
            delListrows.append(r)
        #end if
    #end for            
    for c in range(lenDrlColumns):
        column = []
        for r in range(lenDrlRows):
            column.append(allowedTable[r][c])
        #end for
        if min(column) == maxi:
            delListcolumns.append(c)
        #end if
    #end for
    newAllowedTable = allowedTable[:]
    newTable = table[:]
    delListrows.sort(reverse=True)
    for r in delListrows:
        newAllowedTable.pop(r)
        table.pop(r)
    #end for
    delListcolumns.sort(reverse=True)
    for c in delListcolumns:
        for r in newAllowedTable:
            r.pop(c)
        #end for
        for r in newTable:
            r.pop(c)
    #end for
    if newAllowedTable == []:
        lenDrlRows = 0
        lenDrlColumns = 0
        nTmessage('Cannot make combinations according to allowedTable.')
        newAllowedTable = [[]]
    else:
        lenDrlRows = len(newAllowedTable)
        lenDrlColumns = len(newAllowedTable[0])
    #end if
    for c in delListcolumns:
        n.append(invdrlColumnsdict[drlColumns[c]][0])
    #end for
    for r in delListrows:
        n.append(invdrlRowsdict[drlRows[r]][0])
    #end for
    for r in delListrows:
        drlRows.pop(r)
    #end for
    for c in delListcolumns:
        drlColumns.pop(c)
    #end for
    return newAllowedTable, table, lenDrlRows, lenDrlColumns, drlRows, drlColumns, n
# end def

def interChange(a, b):
    '''interchanges (swaps) two objects of the same type.'''
    nTdebug("Starting %s" % getCallerName())
    if type(b) == type(a):
        return b, a
    #end if
# end def

def transposeTable(table):
    '''
    Transposes a table, so the rows will be columns and the columns will be rows.
    Returns an empty 1d array if the table is empty.
    '''
    nTmessage("Starting %s" % getCallerName())
    if not table:
        return []
    #end if    
    return map(lambda *row: list(row), *table)
# end def

def calculateIndexes(allowedTable, lenDrlColumns, lenDrlRows):
    '''
    Calculates ideal combination of restraints, based on the allowedTable. It returns the indexes of the table.
    '''
    nTmessage('Calculating optimal indexes')
    totalValueNew = 'INF'
    if not lenDrlRows != lenDrlColumns:
        nCr = calcnCr(lenDrlRows, lenDrlColumns)
        if nCr > 30000: #to reduce the amount of calculation time. If nCr>30000 a faster but less optimal algorithm will be used.
            nTmessage('nCr = %s. It will take too long to calculate all possibilities first.\nCombinations may be not optimal' % nCr)
            indexes = munkIndexes(allowedTable)
        else:
            combs = calculateCombs(lenDrlColumns, lenDrlRows)
            for i in combs:#for all possible combinations:
                totalvalue, indexes1, indexes2, table1, table2 = calulateAllCombinations(i, allowedTable, lenDrlRows)
                if totalvalue < totalValueNew:#the lower totalvalue, the more information is kept.
                    totalValueNew = totalvalue
                    finalIndexes1 = indexes1
                    finalIndexes2 = indexes2
                    _finalTable1 = table1
                    _finalTable2 = table2
                    finalcomb = i
                #end if
            indexes = translateIndexes(finalcomb, finalIndexes1, finalIndexes2, lenDrlRows)
            #end for
        #end if
    else:
        indexes = munkIndexes(allowedTable)
    #end if
    return indexes, totalValueNew
# end def

def munkIndexes(table):
    '''Calculate combination of lowest elements in table'''
    munk = Munkres()
    indexes = munk.compute(table)
    return indexes
# end def

def calcnCr(n, k):
    '''
    Calculates nCr; the amount of combinations when you take r out of n.
    '''
    nTmessage('Calculates %s nCr %s' % (n, k))
    if n >= k and k >= 0:
        facn = fac(n)
        fack = fac(k)
        facnk = fac(n - k)
        nCr = facn / (fack * facnk)
    else:
        #: k<0 or k>n; cannot calculate n nCr k.
        nCr = None
    #end if
    return nCr
# end def

def fac(n):
    '''Calculates n! n must be a positive integer.'''
    if type(n) != int:
        nTmessage('%s is not an integer, %s! will be calculated instead' % (n, int(n)))
        n = int(n)
    #end if        
    if n == 1 or n == 0:
        return 1
    else:
        return n * fac(n - 1)
    #end if
# end def

def calculateCombs(lenDrlColumns, lenDrlRows):
    '''Calculates all possible ways to define a square matrix, given the size of it.'''
    li = range(lenDrlRows)
    comb = combinations(li, lenDrlColumns)
    combs = []
    for i in comb: #Calculates all combinations of square matrices to give to munkres.
        j = list(i)
        combs.append(j)
    #end for
    return combs
# end def

def calulateAllCombinations(comb, allowedTable, lenDrlRows):
    '''
    Calculates the total sum of the differences in upper bound of distance restraints for the given combinations. 
    The lower the sum, the less information is lost.
    '''
    munk = Munkres()
    totalvalue = 0
    table1 = []
    table2 = []
    count = 0
    for j in range(lenDrlRows):
        if count < len(comb) and comb[count] == j:
            table1.append(allowedTable[j])
            count += 1
        else:
            table2.append(allowedTable[j])
        #end if
    #end for
    indexes1 = munk.compute(table1)
    for row, column in indexes1:
        value = table1[row][column]
        totalvalue += value
    #end for
    indexes2 = []
    for k in range(len(table2)):
        mini = min(table2[k])
        for ii, jj in enumerate(table2[k]): #finding column index for the lowest value in the row.
            if jj == mini:
                columnind = ii
            #end if
        #end for
        indexes2.append((k, columnind))
    #end for
    #indexes2=munk.compute(table2) #I used this before I realised that taking the minima will give a better result.
    for row, column in indexes2:
        value = table2[row][column]
        totalvalue += value
    #end for
    return(totalvalue, indexes1, indexes2, table1, table2)
# end def

def translateIndexes(comb, indexes1, indexes2, lenDrlRows):
    '''Translates the calculated indexes of munkres-part and the other part back to indexes of the original table.'''
    count1 = 0
    count2 = 0
    finalIndexes = []
    for j in range(lenDrlRows):
        if count1 < len(comb) and comb[count1] == j:
            index = indexes1[count1]
            newindex = (j, index[1])
            finalIndexes.append(newindex)
            count1 += 1
        else:
            index = indexes2[count2]
            newindex = (j, index[1])
            finalIndexes.append(newindex)
            count2 += 1
        #end if
    #end for
    return finalIndexes
# end def

def checkIndexes(indexes, allowedTable, table, maxi, deassignList, invdrlColumnsdict, invdrlRowsdict, drlColumns, drlRows, lenDrlRows):
    '''
    Rows and columns represent the restraintpairs. Checks wether there is choosen a maximum (=not allowed) value and if all rows are 
    combined with a column.
    '''
    values = []#values of allowedTable of restraint combinations in rows and columns. Not necessary.
    rows = []
    columns = []
    ncolumnlist = [] #columns of table which should be deassigned.
    for row, column in indexes:
        value = allowedTable[row][column]
        if value == maxi: #checks if combination is possible
            nTmessage('Warning: index combination (%s,%s)->%s is not allowed. Needs to be deassigned.' % (row, column, table[row][column]))
            ncolumnlist, newrow, newvalue = checkColumn(lenDrlRows, allowedTable, column, maxi, ncolumnlist)
            if not newrow:
                continue
            #end if
            rows.append(newrow)
            columns.append(column)
            values.append(newvalue)
        else:
            rows.append(row)
            columns.append(column)
            values.append(value)
        #end if
    #end for
    for i in ncolumnlist:
        deassignList.append(invdrlColumnsdict[drlColumns[i]][0])
    #end for
    rows, columns, values, deassignList = checkRow(
        lenDrlRows, drlRows, invdrlRowsdict, allowedTable, maxi, rows, columns, values, deassignList)
    nTmessage('Table indexes are:\n\n%-7s  %-7s  %-7s' % ('row:', 'column:', 'value:'))
    for i in range(len(rows)):
        nTmessage('%-7s  %-7s  %-7s' % (rows[i], columns[i], float(values[i]) / 1000))
    #end for
    return (deassignList, rows, columns, values)
# end def

def checkColumn(lenDrlRows, allowedTable, column, maxi, ncolumnlist):
    '''
    Checks wether a not-allowed combination is taken by the algorithm. In this case the lowest value in the column is set as
    new combination. In case the whole column is not allowed, the restraint has to be deassigned. However, this last case shouldn't
    happen at this point. It is just there to check.
    '''
    minix = [] #list of values of specified column
    newrow = []
    newvalue = []
    for i in range(lenDrlRows):
        minix.append(allowedTable[i][column])
    #end for
    mini = min(minix) #lowest value of specified column
    if mini == maxi: #should not be the case, because columns with all maximum values are deleted from the table before.
        ncolumnlist.append(column) #needs to be deassigned
    else:
        for i in range(lenDrlRows):
            if not allowedTable[i][column] == mini:
                continue
            #end i
            newrow = i
            newvalue = mini
            nTmessage('check data for column %s, row %s and value %s.' % (str(i), str(column), str(mini))) #I haven't seen an example yet.
        #end for
    #end if
    return (ncolumnlist, newrow, newvalue)

def checkRow(lenDrlRows, drlRows, invdrlRowsdict, allowedTable, maxi, rows, columns, values, deassinglist):
    '''
    Checks wether all rows are combined, if not, this function will add the combination which belongs to
    the lowest value in this row to the restraintset. For exampl, if checkcolumns has altered the combinations, it might
    be that a row is not combined anymore.
    '''
    nrowlist = [] #rows of table which should be deassigned.
    left = [] #rows of table which are not yet combined with a column
    for i in range(lenDrlRows):
        found = 0
        for j in rows:
            if i == j:
                found = 1 #this row is already combined with a column
                break
            #end if
        #end for
        if found == 0: #this row needs to be combined with a column
            left.append(i)
        #end if
    #end for
    for i in left:
        mini = min(allowedTable[i])
        if mini == maxi: #if there is no combination allowed for this row it will be deassigned. I don't expect this to be the case
            nrowlist.append(i)
        else:
            columnind = allowedTable[i].index(mini)#finding column index for the lowest value in the row.
            rows.append(i)
            columns.append(columnind)
            values.append(mini)
        #end if
    #end for
    for i in nrowlist:
        deassinglist.append(invdrlRowsdict[drlRows[i]][0])
    #end for
    return (rows, columns, values, deassinglist)
# end def

def makeRestraintPairDict(invdrlRowsdict, invdrlColumnsdict, drlRows, drlColumns, rows, columns):
    '''Makes a restraintpair dict. Every combination in this dictionary has to be rewritten into a restraint later.
    The keys are the restraintpairs and the values are the upperbound.'''
    restraintPairDict = {} #keys are the restraintpairs, values are the maximum upperbound of the two restraintpairs.
    for i in range(len(rows)):
        restrpairone = invdrlRowsdict[drlRows[rows[i]]][0]
        restrpairtwo = invdrlColumnsdict[drlColumns[columns[i]]][0]
        newupperbound = max(drlRows[rows[i]][0], drlColumns[columns[i]][0])
        restraintPairDict[(restrpairone, restrpairtwo)] = newupperbound
    #end for
    return(restraintPairDict)
# end def

def makeDisRList(restraintPairDict, proj):
    'Makes list of new distance restraints.'
    low = 0
    delList = []#restraints to be removed
    disRList = []#new restraints
    atomIndexes = [0, 1]
    for i in restraintPairDict.keys():
        ap1 = []
        ap2 = []
        for j in proj.distances[0]:
            if str(j.atomPairs[0][atomIndexes[0]]) == str(i[0][atomIndexes[0]]) and \
               str(j.atomPairs[0][atomIndexes[1]]) == str(i[0][atomIndexes[1]]):
                ap1 = j.atomPairs[:]
                delList.append(j)
            elif str(j.atomPairs[0][atomIndexes[0]]) == str(i[1][atomIndexes[0]]) and \
                 str(j.atomPairs[0][atomIndexes[1]]) == str(i[1][atomIndexes[1]]):
                ap2 = j.atomPairs[0][:]
                delList.append(j)
            #end if
        #end for
        if ap1 and ap2:
            ap1.append(ap2)
            upp = restraintPairDict[i]
            disr = DistanceRestraint(atomPairs=ap1, lower=low, upper=upp)
            disRList.append(disr)
        else: #if the atompair can't be matched between the two projects. I don't expect this will happen
            if ap1:
                nTerror('only first atompair found')
            elif ap2:
                nTerror('only second atompair found')
            else:
                nTerror('No corresponding atom pair found in project')
            #end if
            nTerror('atom pair = %s' % str(i))
        #end if
    #end for
    return(disRList, delList)
# end def

def deleteRestraints(delList, proj):
    '''
    Deletes the restraints in delList in project proj.
    '''
    delList = list(set(delList)) #sort delList and remove double elements
    nTmessage('Following restraint pairs are removed:')
    for i in delList:
        for j in proj.distances[0]:
            if j == i:
                proj.distances[0].remove(i)
                nTmessage('%s,id=%s' % (str(i.atomPairs), str(i.id)))
            #end if
        #end for
    #end for
    proj.partitionRestraints()
    return proj
# end def

def appendRestraints(disRList, proj):
    '''
    Appends restraint in disRList to proj.
    '''
    nTmessage('Following restraint pairs are written:')
    for i in disRList:
        proj.distances[0].append(i)
        nTmessage('%s,id=%s' % (str(i.atomPairs), str(i.id)))
    #end for
    proj.partitionRestraints()
    return proj
# end def

def deassignRestraints(deassignList, proj, leu, delDeassRestr):
    '''
    Deassigns restraints in deassignList. If they cannot be deassigned, they will be removed
    if delDeassRestr=True.
    '''
    nTmessage('Following restraint pairs are deassigned:')
    atomIndexes = [0, 1]
    for ap in deassignList: #deassign restraints in deassignList
        delRestr = 0
        for dr in proj.distances[0]: #looks for the same restraints
            atom1 = dr.atomPairs[0][atomIndexes[0]]
            atom2 = dr.atomPairs[0][atomIndexes[1]]
            if not (str(atom1) == str(ap[atomIndexes[0]]) and str(atom2) == str(ap[atomIndexes[1]])):
                continue
            #end if
            for a in atom1, atom2:
                if not a.residue.name == leu.name:
                    continue
                #end if
                if delRestr == 1:#if it is an intra residual restraint, it might be possible that the other leucine atom can be deassigned.
                    delRestr = 0
                #end if
                if a.hasPseudoAtom():
                    if a == atom1:
                        atom1 = a.pseudoAtom()
                    elif a == atom2:
                        atom2 = a.pseudoAtom()
                    #end if
                else:
                    delRestr = 1
                #end if
            #end for
            if delRestr == 1: #The restraint cannot be deassigned.
                if delDeassRestr == True: #if restraint cannot be deassigned it will be deleted.
                    nTmessage('no pseudoatoms for %s. Restraint will be removed.' % str(dr.atomPairs[0]))
                    proj = deleteRestraints([dr], proj)
                    if ap != deassignList[-1]:#if this is not the last restraint which will be deassigned
                        nTmessage('Following restraint pairs are deassigned:')
                    #end if
                    break
                else:
                    nTmessage('Restraint %s cannot be deassigned.' % str(dr.atomPairs[0]))
                #end if
            else:
                newList = NTlist()
                newList.append((atom1, atom2))
                nTmessage('%s -> %s' % (str(dr.atomPairs), str(newList)))
                dr.atomPairs = newList #replace the atomPairs.
                break
            #end if
        #end for
    #end for
    proj.partitionRestraints()
    proj = checkDoubleRestraints(proj, leu)
    return proj
# end def

def massageRestraintsForLeu(prl, proj, prlleu, projleu, threshold, deasHB):
    '''
    This is an overall script which coordinates through all other functions.
    prl    =project created in rotateLeucines.py
    proj   =project you want to change
    prlleu and projleu are the leucine objects in cing.
    threshold is the threshold for the violations
    if deasHB=True, all HB's of the specified leucine will be deassigned.
    '''
    if prlleu.resNum != projleu.resNum:
        nTerror('Residuenumbers %s and %s are not the same.' % (prlleu.resNum, projleu.resNum))
    #end if        
    if deasHB == True: #if HB's needs to be deassigned
        _deassHBaplistproj = deassignHB(proj, projleu)
        _deassHBaplistprl  = deassignHB(prl, prlleu)#just to be able to compare the two projects later on
    #end if
    n, _u, trdict, gpdict = classifyRestraints(prl, prlleu, threshold)
    drlColumnsdict, drlColumns, lenDrlColumns, drlRowsdict, drlRows, lenDrlRows = renameDicts(trdict, gpdict)
    invdrlColumnsdict = reverseDict(drlColumnsdict)
    invdrlRowsdict = reverseDict(drlRowsdict)
    table = makeDifferenceTable(drlColumns, drlRows, lenDrlColumns, lenDrlRows)
    allowedTable, maxi = makeAllowedTable(table, drlColumns, drlRows, lenDrlColumns, lenDrlRows)
    allowedTable, table, lenDrlRows, lenDrlColumns, drlRows, drlColumns, n = checkAllowedTable(allowedTable, table, maxi, n,
        lenDrlColumns, lenDrlRows, drlColumns, drlRows, invdrlColumnsdict, invdrlRowsdict)
    if lenDrlRows < lenDrlColumns:
        drlColumnsdict, drlRowsdict = interChange(drlColumnsdict, drlRowsdict)
        lenDrlColumns, lenDrlRows = interChange(lenDrlColumns, lenDrlRows)
        drlColumns, drlRows = interChange(drlColumns, drlRows)
        table = transposeTable(table)
        allowedTable = transposeTable(allowedTable)
    #end if
    stringTable = tablePrint(table, 5)
    nTmessage('Difference table is:\n%s' % stringTable)
    stringAllowedTable = tablePrint(allowedTable, 15)
    nTmessage('Allowed table is:\n%s' % stringAllowedTable)
    if False: #this is the old version of the algorithm; works faster, but gives less optimal results.
        munk = Munkres() #algorithm to make combinations of lowest costs
        _indexes = munk.compute(allowedTable)
    #end if
    if allowedTable != [[]]: #checks wether there are allowed combinations.
        indexes, totalValueNew = calculateIndexes(allowedTable, lenDrlColumns, lenDrlRows)
        #Code below was only used to set the indexes of the table by hand.
        #if projleu.resNum==589:
        #    indexes=[(0,0),(1,3),(2,1),(3,2),(4,4),(5,6),(6,5),(7,7),(8,7),(9,10),(10,9),(11,12),(12,11),(13,11),
#            (14,12),(15,8),(16,13),(17,14),(18,14),(19,15),(20,8),(21,8)]
        #elif projleu.resNum==596:
        #    indexes=[(0,1),(1,0),(2,0),(3,3),(4,4),(5,5),(6,12),(7,2),(8,6),(9,8),(10,7),(11,9),(12,10),(13,11)]
        #elif projleu.resNum==618:
        #    indexes=[(0,0),(1,1)]
        #totalValueNew='INF'
        n, rows, columns, _values = checkIndexes(indexes, allowedTable, table, maxi, n, invdrlColumnsdict,
                                            invdrlRowsdict, drlColumns, drlRows, lenDrlRows)
        if totalValueNew != 'INF':
            nTmessage('total sum of differences between upper bounds of combined restraints is %.2f A.' % (float(totalValueNew) / 1000))
        #end if
        #n=checkDeasrHB(n,deassHBaplistproj) Not necessary anymore since distances are recalculated after deassignment HB's.
        restraintPairDict = makeRestraintPairDict(invdrlRowsdict, invdrlColumnsdict, drlRows, drlColumns, rows, columns)
        disRList, delList = makeDisRList(restraintPairDict, proj)
        proj = deleteRestraints(delList, proj)
        proj = appendRestraints(disRList, proj)
    #end if
    proj = deassignRestraints(n, proj, projleu, delDeassRestr=True)
    return proj
# end def

def alterRestraintsForLeus(leuList, proj, prl, threshold, deasHB, dihrCHI2):
    '''
    This script rotates over all leucines and combines its restraints. After that, a CHI2 restraint will be added to each of the 
    specified leucines if specified.
    
    leuList     = list of which project 'proj' leucines should be taken.
    proj        = project that you want to change
    prl         = copy of project with 3 models with leucines in different conformations, created in rotateLeucines.py
                    threshold gives the threshold value for the violations.
    deasHB      = True means that all HBs of the specified leucines will be deassigned.
    dihrCHI2    = True means that a dihedral restraint will be added to the leucines.
    '''
    for projleu in leuList:
#        prlleu = prl.molecules[0].residuesWithProperties('LEU')[i]
        prlleu = projleu.getMatchInOtherProject( prl )
#        projleu = proj.molecules[0].residuesWithProperties('LEU')[i]
        nTmessage('\nStart massageRestraintsForLeu for %s:' % str(prlleu))
        proj = massageRestraintsForLeu(prl, proj, prlleu, projleu, threshold, deasHB)
    #end for
    if dihrCHI2 == True:
        addDihRestr(proj, leuList=leuList)
    #end if
    return proj
# end def        

def runScript():
    '''
    Main entry point of this script.
    See $C/python/cing/Scripts/test/test_combineRestraints.py for similar unit check.
    '''
#    proj_path='/Users/jd/workspace/'
    proj_path = '/home/i/tmp/karenVCdir'
    proj_name = 'H2_2Ca_64_100'
    prl_name = proj_name + '_' + ROTL_STR 
    
    proj = Project.open('%s/%s' % (proj_path, proj_name), status='old')
    prl = Project.open('%s/%s' % (proj_path, prl_name), status='old')
    leuNumberList = [0] #please define leunumbers.
    if prl_name.startswith('H2_2Ca_64_100'):
        leuNumberList = [2, 3, 4]
    #end if
    threshold = 0 #minimal violation, necessary to classify the restraints.
    deasHB = True #first deassign all HBs in the specified leucines
    dihrCHI2 = True #add a dihedral restraint on the leucines.
    proj = alterRestraintsForLeus(leuNumberList, proj, prl, threshold, deasHB, dihrCHI2)
    if True:
        proj.save()
    #end if
# end def        

if __name__ == '__main__':
    runScript()
