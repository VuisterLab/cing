'''
Created on May 2, 2011

@author: Karen
This script will combine restraints, such that xplor has to choose between two
possible leucine conformations.This script will combine them on upper distance restraint.
First the script is going to deassign all HB's in the specific Leucine, secondly it calculates
the violations in the trans and in the gauche + combination and finally it combines the
restraints in the project. Script follows on script rotateleucinesinyasara.py Script cannot
handle multimers.

!!Be careful: Make a copy of your project before you run this one. This script will alter
the restraints in you project. It is not possible to restore them!!
'''

from munkres import Munkres
from cing.core.classes import * #@UnusedWildImport
from cing.core.molecule import * #@UnusedWildImport
from collections import defaultdict
from itertools import combinations

def addDihRestr(proj,lower,upper,leuNumberList):
    '''
    Adding CHI2 dihedral restraints to leucines, specified in leuNumberList. lower and upper are the lower bound and upper bound of the restraint.
    The restraints will be put in a new restraintlist
    '''
    #molec=proj.molecule.A
    leu=[]
    for r in leuNumberList:
        leu.append(proj.molecules[0].residuesWithProperties('LEU')[r])
    #leu=[molec.LEU589,molec.LEU596,molec.LEU618]
    lower=0
    upper=245
    dihrestrlist=DihedralRestraintList(name='CHI2restr')
    for r in leu:
        atoms=[r.CA,r.CB,r.CG,r.CD1]
        dihedralrestraint=DihedralRestraint(atoms=atoms,lower=lower,upper=upper)
        dihrestrlist.append(dihedralrestraint)
        nTmessage('CHI2 restraint appended for %s'%r.name)
    #end for
    proj.dihedrals.append(dihrestrlist)
    proj.partitionRestraints()
    return proj

def checkDoubleRestraints(proj,leu):
    '''
    After deassignment, some atomPairs occur twice in the distance restraint list. 
    This script will delete the one with the highest upperbound.
    '''
    nTmessage('Checking for double restraints after deassignment')
    delList=[]
    drlist=leu.distanceRestraints
    for i in range(len(drlist)):
        for j in range(i):
            if not drlist[i].atomPairs==drlist[j].atomPairs:
                continue
            if drlist[i].upper>drlist[j].upper:
                delList.append(drlist[i])
            else:
                delList.append(drlist[j])
        #endfor
    #endfor
    if delList:
        proj=deleteRestraints(delList,proj)
        checkRestraintsExistance(delList,proj)
    #endif
    return(proj)

def checkRestraintsExistance(restraintlist,proj):
    '''After deleting halve of the double restraints, this script will check whether the other halve is still there.'''
    nTmessage('Project contains still following restraints:')#Just a check
    aplist=[]#list with unique atompairs in restraintlist
    count=0
    for dr in restraintlist:
        aplist.append(dr.atomPairs[0])
    for ap in list(set(aplist)):
        for dr in proj.distances[0]:
            if ap==dr.atomPairs[0]:
                count+=1
                nTmessage('%s,id=%s'%(str(ap),str(dr.id)))
    if count==0:
        nTerror('No restraints found')
    return()
#end def

def deassignHB(proj,leu):
    '''Deassignes HBs in specified leucines. It will replace the old restraint, in order to delete all the other information.'''
    nTmessage('Following restraint pairs with HBs of %s are deassigned:'%leu.name)
    deassHBaplist=[]
#    atomIndexes=[0,1]
    for dr in leu.distanceRestraints: #restraints in proj.distances[0] are automatically deassigned.
        ap = dr.atomPairs[0]
        atom1=ap[0]
        atom2=ap[1]
        for ai in [0,1]:
            atom=ap[ai]
            if atom.residue.resNum != leu.resNum:
                continue
            atomname=atom.name
            if not (atomname=='HB2' or atomname=='HB3'):
                continue            
            if ai==0:
                atom1=atom.pseudoAtom()
            else:
                atom2=atom.pseudoAtom()
            newList=NTlist()
            deassHBaplist.append((atom1,atom2))
            newList.append((atom1,atom2))
            nTmessage('%s -> %s'%(str(dr.atomPairs),str(newList)))
            dr.atomPairs=newList
            break
        # end for
    # end for
    proj=checkDoubleRestraints(proj,leu) # this line is causing problems with coverage 3.5. Don't see why though.
    proj.distances[0].analyze()
    return (proj,deassHBaplist)
#end def

def checkDeasrHB(n,deassHBaplist):
    '''
    If an atom pair with a HB is already deassigned, it must be removed from the list to deassign. 
    deassHBaplist is the list which is already deassigned
    and n is the list of restraints, which violate in trans and gauche+, which should be deassigned.
    '''
    nTmessage('checkDeasrHB is running')
    atomIndexes=[0,1]
    delList=[]
    #l=len(deassHBaplist)
    #ln=len(n)
    for dr in n:
        for j in deassHBaplist:
            if str(dr[atomIndexes[0]])==str(j[atomIndexes[0]]) and str(dr[atomIndexes[1]])==str(j[atomIndexes[1]]):
                delList.append(dr)
    for dr in delList:
        n.remove(dr)
        nTmessage('%s will not be removed.'%str(dr))
    #if ln-len(n)==len(delList): #just a check,used while debugging.
    #    nTmessage('%s restraints with a QB will not be deleted.'%len(delList))
    return n

def classifyRestraints(prl,leu,treshold):
    """This routine scans the restrains of leu in prl for violations in the second and third model. After thatl these restraints
    are classified in four groups, violated in the second(tr), violated in the third(g+), violated in both(n) and not violated in both(u).
    Treshold for the violation is the violation in the first original model with the Leucine rotated exactly in gp or tr."""
    #All atoms and pseudoatoms in the leucine sidechain, which have different positions in different rotameric states:
    scall=['HB2','HB3','MD1','MD2','QD','HG','CG','QB','HD11','HD12','HD13','HD21','HD22','HD23','CD1','CD2']#side chain atoms leucine list
    n=[] #atom pairs of restraints which violates in tr and g+
    u=[] #atom pairs of restraints which are unviolated in both tr and g+
    trdict={} #keys=atompairs of restraints which violate in tr, values=(upperbound,violation in tr)
    gpdict={} #keys=atompairs of restraints which violate in gauche+, values=(upperbound,violation in gp)
    atomIndexes=[0,1]
    modelCount=len(prl.models)
    halfModelCount=modelCount/2
    tresholdModelCount=10
    trind=range(halfModelCount) #trans index
    gpind=range(halfModelCount,modelCount,1) #gauche+ index
    #leu=prl.molecules[0].residuesWithProperties('LEU')[leunumber] #leucine g
    nTmessage('Divide restraints into classes for %s'%leu.name)
    drlleu=leu.distanceRestraints #distance restraints of leucine g
    for k in range(len(drlleu)):
        found=0
        dr=drlleu[k] #distance restraint k of this leucine
        for a in range(len(scall)): #loops over the atoms in scall
            if found==1:
                break
            for ai in atomIndexes: #specifies first or second atom in atompair of restraint
                if not dr.atomPairs[0][ai].atomsWithProperties('LEU',scall[a]):
                    continue
                if not dr.atomPairs[0][ai].residue.resNum==leu.resNum:
                    continue
                violCountTr=0
                violTr=0
                violTreshTr=dr.violations[0] #first model
                #violMinTr=min(dr.violations[:halfModelCount])
                #violTreshTr=violMinTr
                for i in trind:
                    if dr.violations[i]>treshold:
                        violCountTr+=1
                        violTr+=dr.violations[i]
                if violCountTr!=0:
                    violTr=violTr/violCountTr #average violation over all violated conformations
                violCountGp=0
                violGp=0
                violTreshGp=dr.violations[halfModelCount]
                #violMinGp=min(dr.violations[halfModelCount:])
                #violTreshGp=violMinGp
                for i in gpind:
                    if dr.violations[i]>treshold:
                        violCountGp+=1
                        violGp+=dr.violations[i]
                if violCountGp!=0:
                    violGp=violGp/violCountGp #average violation over all violated conformations
                if violCountGp+violCountTr==0:
                    u.append(dr.atomPairs[0])
                elif (violCountTr>(violCountGp+tresholdModelCount) and violTr>violGp):
                    trdict[dr.atomPairs[0]]=(dr.upper,violTreshTr)
                elif violCountGp>(violCountTr+tresholdModelCount) and violGp>violTr:
                    gpdict[dr.atomPairs[0]]=(dr.upper,violTreshGp)
                elif violCountGp<tresholdModelCount and violCountTr<tresholdModelCount: 
                    #less than 10 violations is not enough to classify restraint.
                    u.append(dr.atomPairs[0])
                else:
                    n.append(dr.atomPairs[0])
                found=1
                break
                #endif
            #endfor
        #endfor
    tmplist=[trdict.keys(),gpdict.keys(),n,u]
    namelist=['trans','gauche+','both','none']
    for i in range(4):
        if tmplist[i]:
            nTmessage('list violated in %s for %s contains %s restraints'%(namelist[i],leu.name,len(tmplist[i])))
    return(n,u,trdict,gpdict)

def renameDicts(trdict,gpdict):
    '''Renames the dictionaries with distance restraint lists, called tr and g+, to dictionaries for the columns and the rows in a table,
    such that the amount of columns is never higher than the amount of rows.'''
    ltr=len(trdict)
    lgp=len(gpdict)
    if ltr>lgp:
        drlColumnsdict,drlColumns,lenDrlColumns=dictValues(gpdict)
        drlRowsdict,drlRows,lenDrlRows=dictValues(trdict)
    else:
        drlColumnsdict,drlColumns,lenDrlColumns=dictValues(trdict)
        drlRowsdict,drlRows,lenDrlRows=dictValues(gpdict)
    return drlColumnsdict,drlColumns,lenDrlColumns,drlRowsdict,drlRows,lenDrlRows

def dictValues(vdict):
    '''Returns the dictionary, the sorted list of values and the length of this list.'''
    v=vdict.values()
    v.sort()
    lenv=len(v)
    return(vdict,v,lenv,)

def reverseDict(vdict):
    '''
    Interchange of keys and values in a dictionary. 
    In case a value occurs twice, the dictionary will have two keys in a list for that value.
    '''
    rdict=defaultdict(list)
    for ii,jj in vdict.items():
        rdict[jj].append(ii)
    return rdict

def tablePrint(table,ln):
    'Just a handy script to print tables while debugging. Length is the number of characters per element in table'
    string=''
    fmt='%-'+str(ln)+'.2f' #to be able to print the table alligned, this value has to depend on the len of an element in the table
    for r in table:
        for c in r:
            string+=fmt %c
        string+='\n'
    return string

def makeDifferenceTable(drlColumns,drlRows,lenDrlColumns,lenDrlRows):
    '''
    table gives the absolute differences in upper-bounds between the restraints
    in the a-set and the b-set. So you can look up every difference in upperbound
    between two restraints, one of a and one of b.
    '''
    table=[ [ 0 for _i in range(lenDrlColumns) ] for _j in range(lenDrlRows) ] #table with only zeros
    for c in range(lenDrlColumns):
        for r in range(lenDrlRows):
            diff=drlColumns[c][0]-drlRows[r][0]
            table[r][c]=abs(diff)
    #stringTable=tablePrint(table,5)
    #nTmessage('Difference table is:\n%s'%stringTable)
    return(table)

def makeAllowedTable(table,drlColumns,drlRows,lenDrlColumns,lenDrlRows):
    '''
    Every element in allowed table is the element in table minus the
    largest violation of the pair of restraints. If the violation is
    bigger than the difference, the value becomes negative. This combination
    of restraints will not be used. Therefore all negative values are set to
    a very high value (maxi).The values are enlarged by a factor 1000 so that
    the munkres algorithm can work with it.
    '''
    maxi=9999999 #Munkres cannot work with float("infinity") and None objects
    allowedTable=[ [ 0 for _i in range(lenDrlColumns) ] for _j in range(lenDrlRows) ] #table with only zeros
    for c in range(lenDrlColumns):
        for r in range(lenDrlRows):
            diff=table[r][c]
            diffCor=diff
            if drlRows[r][0]>drlColumns[c][0]:
                diffCor-=drlColumns[c][1]
            elif drlRows[r][0]<drlColumns[c][0]:
                diffCor-=drlRows[r][1]
            elif drlRows[r][0]==drlColumns[c][0]:
                diffCor-=(drlColumns[c][1]+drlRows[r][1])/2
            #endif
            if diffCor<0:
                allowedTable[r][c]=diff*1000
            else:
                allowedTable[r][c]=maxi
            #endif
        #endfor
    #endfor
    #stringTable=tableprint(allowedTable,15)
    #nTmessage('Allowed table is:\n%s'%stringTable)
    return(allowedTable,maxi)

def checkAllowedTable(allowedTable,table,maxi,n,lenDrlColumns,lenDrlRows,drlColumns,drlRows,invdrlColumnsdict,invdrlRowsdict):
    '''Checks wether allowedTable has columns or rows which consist only of maximum values. In that case, the row or column
    cannot be combined and should be deassigned or deleted, so the restraint will be added to the list of restraints which
    violate both in tr as in g+, because these restraints also have to be deassigned or deleted.
    This check happens before calculating the best combination, because the deletion of these columns/rows will lead to
    better combinations and less computation time.'''
    nTmessage('Checks allowedTable')
    delListrows=[]
    delListcolumns=[]
    for r in range(lenDrlRows):
        if min(allowedTable[r])==maxi:
            delListrows.append(r)
    for c in range(lenDrlColumns):
        column=[]
        for r in range(lenDrlRows):
            column.append(allowedTable[r][c])
        if min(column)==maxi:
            delListcolumns.append(c)
    newAllowedTable=allowedTable[:]
    newTable=table[:]
    delListrows.sort(reverse=True)
    for r in delListrows:
        newAllowedTable.pop(r)
        table.pop(r)
    delListcolumns.sort(reverse=True)
    for c in delListcolumns:
        for r in newAllowedTable:
            r.pop(c)
        for r in newTable:
            r.pop(c)
    if newAllowedTable==[]:
        lenDrlRows=0
        lenDrlColumns=0
        nTmessage('Cannot make combinations according to allowedTable.')
        newAllowedTable=[[]]
    else:
        lenDrlRows=len(newAllowedTable)
        lenDrlColumns=len(newAllowedTable[0])
    for c in delListcolumns:
        n.append(invdrlColumnsdict[drlColumns[c]][0])
    for r in delListrows:
        n.append(invdrlRowsdict[drlRows[r]][0])
    for r in delListrows:
        drlRows.pop(r)
    for c in delListcolumns:
        drlColumns.pop(c)
    return newAllowedTable,table,lenDrlRows,lenDrlColumns,drlRows,drlColumns,n

def interChange(a,b):
    '''interchanges two objects of the same type.'''
    if type(b)==type(a):
        return b,a

def transposeTable(table):
    '''transposes a table, so the rows will be columns and the columns will be rows.'''
    if not table:
        return []
    return map(lambda *row: list(row), *table)

def calculateIndexes(allowedTable,lenDrlColumns,lenDrlRows):
    '''Calculates ideal combination of restraints, based on the allowedTable. It returns the indexes of the table.'''
    nTmessage('Calculating optimal indexes')
    totalValueNew='INF'
    if not lenDrlRows!=lenDrlColumns:
        nCr=calcnCr(lenDrlRows,lenDrlColumns)
        if nCr>30000: #to reduce the amount of calculation time. If nCr>30000 a faster but less optimal algorithm will be used.
            nTmessage('nCr = %s. It will take too long to calculate all possibilities first.\nCombinations may be not optimal'%nCr)
            indexes=munkIndexes(allowedTable)
        else:
            combs=calculateCombs(lenDrlColumns,lenDrlRows)
            for i in combs:#for all possible combinations:
                totalvalue,indexes1,indexes2,table1,table2=calulateAllCombinations(i,allowedTable,lenDrlRows)
                if totalvalue<totalValueNew:#the lower totalvalue, the more information is kept.
                    totalValueNew=totalvalue
                    finalIndexes1=indexes1
                    finalIndexes2=indexes2
                    _finalTable1=table1
                    _finalTable2=table2
                    finalcomb=i
                #endif
            indexes=translateIndexes(finalcomb,finalIndexes1,finalIndexes2,lenDrlRows)
            #endfor
        #endif
    else:
        indexes=munkIndexes(allowedTable)
    #endif
    return indexes,totalValueNew

def munkIndexes(table):
    '''Calculate combination of lowest elements in table'''
    munk=Munkres()
    indexes=munk.compute(table)
    return indexes

def calcnCr(n,k):
    '''Calculates nCr; the amount of combinations when you take r out of n.'''
    nTmessage('Calculates %s nCr %s'%(n,k))
    if n>=k and k>=0:
        facn=fac(n)
        fack=fac(k)
        facnk=fac(n-k)
        nCr=facn/(fack*facnk)
    else:
        #: k<0 or k>n; cannot calculate n nCr k.
        nCr=None
    #endif
    return nCr

def fac(n):
    '''Calculates n! n must be a positive integer.'''
    if type(n)!=int:
        nTmessage('%s is not an integer, %s! will be calculated instead'%(n,int(n)))
        n=int(n)
    if n==1 or n==0:
        return 1
    else:
        return n*fac(n-1)

def calculateCombs(lenDrlColumns,lenDrlRows):
    '''Calculates all possible ways to define a square matrix, given the size of it.'''
    li=range(lenDrlRows)
    comb=combinations(li,lenDrlColumns)
    combs=[]
    for i in comb: #Calculates all combinations of square matrices to give to munkres.
        j=list(i)
        combs.append(j)
    return combs

def calulateAllCombinations(comb,allowedTable,lenDrlRows):
    '''
    Calculates the total sum of the differences in upper bound of distance restraints for the given combinations. 
    The lower the sum, the less information is lost.
    '''
    munk=Munkres()
    totalvalue=0
    table1=[]
    table2=[]
    count=0
    for j in range(lenDrlRows):
        if count<len(comb) and comb[count]==j:
            table1.append(allowedTable[j])
            count+=1
        else:
            table2.append(allowedTable[j])
        #endif
    #endfor
    indexes1=munk.compute(table1)
    for row, column in indexes1:
        value=table1[row][column]
        totalvalue+=value
    indexes2=[]
    #endfor
    for k in range(len(table2)):
        mini=min(table2[k])
        for ii,jj in enumerate(table2[k]): #finding column index for the lowest value in the row.
            if jj==mini:
                columnind=ii
            #endif
        #endfor
        indexes2.append((k,columnind))
    #endfor
    #indexes2=munk.compute(table2) #I used this before I realised that taking the minima will give a better result.
    for row, column in indexes2:
        value=table2[row][column]
        totalvalue+=value
    #endfor
    return(totalvalue,indexes1,indexes2,table1,table2)

def translateIndexes(comb,indexes1,indexes2,lenDrlRows):
    '''Translates the calculated indexes of munkres-part and the other part back to indexes of the original table.'''
    count1=0
    count2=0
    finalIndexes=[]
    for j in range(lenDrlRows):
        if count1<len(comb) and comb[count1]==j:
            index=indexes1[count1]
            newindex=(j,index[1])
            finalIndexes.append(newindex)
            count1+=1
        else:
            index=indexes2[count2]
            newindex=(j,index[1])
            finalIndexes.append(newindex)
            count2+=1
        #endif
    #endfor
    return finalIndexes

def checkIndexes(indexes,allowedTable,table,maxi,deassignList,invdrlColumnsdict,invdrlRowsdict,drlColumns,drlRows,lenDrlRows):
    '''
    Rows and columns represent the restraintpairs. Checks wether there is choosen a maximum (=not allowed) value and if all rows are 
    combined with a column.
    '''
    values=[]#values of allowedTable of restraint combinations in rows and columns. Not necessary.
    rows=[]
    columns=[]
    ncolumnlist=[] #columns of table which should be deassigned.
    for row, column in indexes:
        value=allowedTable[row][column]
        if value ==maxi: #checks if combination is possible
            nTmessage('Warning: index combination (%s,%s)->%s is not allowed. Needs to be deassigned.'%(row,column,table[row][column]))
            ncolumnlist,newrow,newvalue=checkColumn(lenDrlRows,allowedTable,column,maxi,ncolumnlist)
            if not newrow:
                continue
            rows.append(newrow)
            columns.append(column)
            values.append(newvalue)
        else:
            rows.append(row)
            columns.append(column)
            values.append(value)
        #endif
    #endfor
    for i in ncolumnlist:
        deassignList.append(invdrlColumnsdict[drlColumns[i]][0])
    rows,columns,values,deassignList=checkRow(lenDrlRows,drlRows,invdrlRowsdict,allowedTable,maxi,rows,columns,values,deassignList)
    nTmessage('Table indexes are:\n\n%-7s  %-7s  %-7s'%('row:','column:','value:'))
    for i in range(len(rows)):
        nTmessage('%-7s  %-7s  %-7s'%(rows[i],columns[i],float(values[i])/1000))
    return(deassignList,rows,columns,values)

def checkColumn(lenDrlRows,allowedTable,column,maxi,ncolumnlist):
    '''Checks wether a not-allowed combination is taken by the algorithm. In this case the lowest value in the column is set as
    new combination. In case the whole column is not allowed, the restraint has to be deassigned. However, this last case shouldn't
    happen at this point. It is just there to check.'''
    minix=[] #list of values of specified column
    newrow=[]
    newvalue=[]
    for i in range(lenDrlRows):
        minix.append(allowedTable[i][column])
    mini=min(minix) #lowest value of specified column
    #endfor
    if mini==maxi: #should not be the case, because columns with all maximum values are deleted from the table before.
        ncolumnlist.append(column) #needs to be deassigned
    else:
        for i in range(lenDrlRows):
            if not allowedTable[i][column]==mini:
                continue
            newrow=i
            newvalue=mini
            nTmessage('check data for column %s, row %s and value %s.' %(str(i),str(column),str(mini))) #I haven't seen an example yet.
        #endfor
    #endif
    return(ncolumnlist,newrow,newvalue)

def checkRow(lenDrlRows,drlRows,invdrlRowsdict,allowedTable,maxi,rows,columns,values,deassinglist):
    '''Checks wether all rows are combined, if not, this function will add the combination which belongs to
    the lowest value in this row to the restraintset. For exampl, if checkcolumns has altered the combinations, it might
    be that a row is not combined anymore.'''
    nrowlist=[] #rows of table which should be deassigned.
    left=[] #rows of table which are not yet combined with a column
    for i in range(lenDrlRows):
        found=0
        for j in rows:
            if i==j:
                found=1 #this row is already combined with a column
                break
        #endfor
        if found==0: #this row needs to be combined with a column
            left.append(i)
    #endfor
    for i in left:
        mini=min(allowedTable[i])
        if mini==maxi: #if there is no combination allowed for this row it will be deassigned. I don't expect this to be the case
            nrowlist.append(i)
        else:
            columnind=allowedTable[i].index(mini)#finding column index for the lowest value in the row.
            rows.append(i)
            columns.append(columnind)
            values.append(mini)
        #endif
    #endfor
    for i in nrowlist:
        deassinglist.append(invdrlRowsdict[drlRows[i]][0])
    return(rows,columns,values,deassinglist)

def makeRestraintPairDict(invdrlRowsdict,invdrlColumnsdict,drlRows,drlColumns,rows,columns):
    '''Makes a restraintpair dict. Every combination in this dictionary has to be rewritten into a restraint later.
    The keys are the restraintpairs and the values are the upperbound.'''
    restraintPairDict={} #keys are the restraintpairs, values are the maximum upperbound of the two restraintpairs.
    for i in range(len(rows)):
        restrpairone=invdrlRowsdict[drlRows[rows[i]]][0]
        restrpairtwo=invdrlColumnsdict[drlColumns[columns[i]]][0]
        newupperbound=max(drlRows[rows[i]][0],drlColumns[columns[i]][0])
        restraintPairDict[(restrpairone,restrpairtwo)]=newupperbound
    return(restraintPairDict)

def makeDisRList(restraintPairDict,proj):
    'Makes list of new distance restraints.'
    low=0
    delList=[]#restraints to be removed
    disRList=[]#new restraints
    atomIndexes=[0,1]
    for i in restraintPairDict.keys():
        ap1=[]
        ap2=[]
        for j in proj.distances[0]:
            if str(j.atomPairs[0][atomIndexes[0]])==str(i[0][atomIndexes[0]]) and \
               str(j.atomPairs[0][atomIndexes[1]])==str(i[0][atomIndexes[1]]):
                ap1=j.atomPairs[:]
                delList.append(j)
            elif str(j.atomPairs[0][atomIndexes[0]])==str(i[1][atomIndexes[0]]) and \
                 str(j.atomPairs[0][atomIndexes[1]])==str(i[1][atomIndexes[1]]):
                ap2=j.atomPairs[0][:]
                delList.append(j)
            #endif
        #endfor
        if ap1 and ap2:
            ap1.append(ap2)
            upp=restraintPairDict[i]
            disr=DistanceRestraint(atomPairs=ap1,lower=low,upper=upp)
            disRList.append(disr)
        else: #if the atompair can't be matched between the two projects. I don't expect this will happen
            if ap1:
                nTerror('only first atompair found')
            elif ap2:
                nTerror('only second atompair found')
            else:
                nTerror('No corresponding atom pair found in project')
            nTerror('atom pair = %s'%str(i))
            #endif
        #endif
    #endfor
    return(disRList,delList)

def deleteRestraints(delList,proj):
    '''Deletes the restraints in delList in project proj.'''
    delList=list(set(delList)) #sort delList and remove double elements
    nTmessage('Following restraint pairs are removed:')
    for i in delList:
        for j in proj.distances[0]:
            if j==i:
                proj.distances[0].remove(i)
                nTmessage('%s,id=%s'%(str(i.atomPairs),str(i.id)))
            #endif
        #endfor
    #endfor
    proj.partitionRestraints()
    return proj

def appendRestraints(disRList,proj):
    '''Appends restraint in disRList to proj.'''
    nTmessage('Following restraint pairs are written:')
    for i in disRList:
        proj.distances[0].append(i)
        nTmessage('%s,id=%s'%(str(i.atomPairs),str(i.id)))
    proj.partitionRestraints()
    return proj

def deassignRestraints(deassignList,proj,leu,delDeassRestr):
    '''deassigns restraints in deassignList. If they cannot be deassigned, they will be removed
    if delDeassRestr=True.'''
    nTmessage('Following restraint pairs are deassigned:')
    atomIndexes=[0,1]
    for ap in deassignList: #deassign restraints in deassignList
        delRestr=0
        for dr in proj.distances[0]: #looks for the same restraints
            atom1=dr.atomPairs[0][atomIndexes[0]]
            atom2=dr.atomPairs[0][atomIndexes[1]]
            if not (str(atom1)==str(ap[atomIndexes[0]]) and str(atom2)==str(ap[atomIndexes[1]])):
                continue
            for a in atom1,atom2:
                if not a.residue.name==leu.name:
                    continue
                if delRestr==1:#if it is an intra residual restraint, it might be possible that the other leucine atom can be deassigned.
                    delRestr=0
                if a.hasPseudoAtom():
                    if a==atom1:
                        atom1=a.pseudoAtom()
                    elif a==atom2:
                        atom2=a.pseudoAtom()
                    #endif
                else:
                    delRestr=1
                #endif
            #endfor
            if delRestr==1: #The restraint cannot be deassigned.
                if delDeassRestr==True: #if restraint cannot be deassigned it will be deleted.
                    nTmessage('no pseudoatoms for %s. Restraint will be removed.' %str(dr.atomPairs[0]))
                    proj=deleteRestraints([dr],proj)
                    if ap!=deassignList[-1]:#if this is not the last restraint which will be deassigned
                        nTmessage('Following restraint pairs are deassigned:')
                    break
                else:
                    nTmessage('Restraint %s cannot be deassigned.'%str(dr.atomPairs[0]))
                #endif
            else:
                newList=NTlist()
                newList.append((atom1,atom2))
                nTmessage('%s -> %s'%(str(dr.atomPairs),str(newList)))
                dr.atomPairs=newList #replace the atomPairs.
                break
            #endif
        #endfor
    #endfor
    proj.partitionRestraints()
    proj=checkDoubleRestraints(proj, leu)
    return(proj)

def writeRestraintsForLeu(prl,proj,prlleu,projleu,treshold,deasHB):
    '''
    This is an overall script which coordinates through all other functions.
    prl=project created in rotateLeucines.py
    proj=project you want to change
    prlleu and projleu are the leucineobjects in cing. They need to have the same residuenumber.
    treshold is the treshold for the violations
    if deasHB=True, all HB's of the specified leucine will be deassigned.
    '''
    if prlleu.resNum!=projleu.resNum:
        nTerror('Residuenumbers %s and %s are not the same.'%(prlleu.resNum,projleu.resNum))
    if deasHB==True: #if HB's needs to be deassigned
        proj,_deassHBaplistproj=deassignHB(proj,projleu)
        prl,_deassHBaplistprl=deassignHB(prl,prlleu)#just to be able to compare the two projects later on
    #endif
    n,_u,trdict,gpdict=classifyRestraints(prl,prlleu,treshold)
    drlColumnsdict,drlColumns,lenDrlColumns,drlRowsdict,drlRows,lenDrlRows=renameDicts(trdict,gpdict)
    invdrlColumnsdict=reverseDict(drlColumnsdict)
    invdrlRowsdict=reverseDict(drlRowsdict)
    table=makeDifferenceTable(drlColumns, drlRows,lenDrlColumns,lenDrlRows)
    allowedTable,maxi=makeAllowedTable(table,drlColumns,drlRows,lenDrlColumns,lenDrlRows)
    allowedTable,table,lenDrlRows,lenDrlColumns,drlRows,drlColumns,n=checkAllowedTable(allowedTable,table,maxi,n,
                                                            lenDrlColumns,lenDrlRows,drlColumns,drlRows,invdrlColumnsdict,invdrlRowsdict)
    if lenDrlRows<lenDrlColumns:
        drlColumnsdict,drlRowsdict=interChange(drlColumnsdict,drlRowsdict)
        lenDrlColumns,lenDrlRows=interChange(lenDrlColumns,lenDrlRows)
        drlColumns,drlRows=interChange(drlColumns,drlRows)
        table=transposeTable(table)
        allowedTable=transposeTable(allowedTable)
    stringTable=tablePrint(table,5)
    nTmessage('Difference table is:\n%s'%stringTable)
    stringAllowedTable=tablePrint(allowedTable,15)
    nTmessage('Allowed table is:\n%s'%stringAllowedTable)
    if False: #this is the old version of the algorithm; works faster, but gives less optimal results.
        munk = Munkres() #algorithm to make combinations of lowest costs
        _indexes = munk.compute(allowedTable)
    if allowedTable!=[[]]: #checks wether there are allowed combinations.
        indexes,totalValueNew=calculateIndexes(allowedTable,lenDrlColumns,lenDrlRows)
        #Code below was only used to set the indexes of the table by hand.
        #if projleu.resNum==589:
        #    indexes=[(0,0),(1,3),(2,1),(3,2),(4,4),(5,6),(6,5),(7,7),(8,7),(9,10),(10,9),(11,12),(12,11),(13,11),
#            (14,12),(15,8),(16,13),(17,14),(18,14),(19,15),(20,8),(21,8)]
        #elif projleu.resNum==596:
        #    indexes=[(0,1),(1,0),(2,0),(3,3),(4,4),(5,5),(6,12),(7,2),(8,6),(9,8),(10,7),(11,9),(12,10),(13,11)]
        #elif projleu.resNum==618:
        #    indexes=[(0,0),(1,1)]
        #totalValueNew='INF'
        n,rows,columns,_values=checkIndexes(indexes,allowedTable,table,maxi,n,invdrlColumnsdict,
                                            invdrlRowsdict,drlColumns,drlRows,lenDrlRows)
        if totalValueNew!='INF':
            nTmessage('total sum of differences between upperbounds of combined restraints is %.2f A.'%(float(totalValueNew)/1000))
        #n=checkDeasrHB(n,deassHBaplistproj) Not necessary anymore since distances are recalculated after deassignment HB's.
        restraintPairDict=makeRestraintPairDict(invdrlRowsdict,invdrlColumnsdict,drlRows,drlColumns,rows,columns)
        disRList,delList=makeDisRList(restraintPairDict,proj)
        proj=deleteRestraints(delList,proj)
        proj=appendRestraints(disRList,proj)
    proj=deassignRestraints(n,proj,projleu,delDeassRestr=True)
    return proj

def alterRestraintsForLeus(leuNumberList,proj,prl,treshold,deasHB,dihrCHI2):
    '''
    This script rotates over all leucines and combines its restraints. After that, a CHI2restraint will be added to each of the 
    specified leucines.
    leuNumberList=list of indices which leucines should be taken. So if you have 5 leucines and you want the first and the fourth, 
    leuNumberList=[1,4]
    proj=project that you want to change
    prl=copy of project with 3 models with leucines in different conformations, created in rotateLeucines.py
    treshold gives the treshold value for the violations.
    deasHB=True means that all HBs of the specified leucines will be deassigned.
    dihrCHI2=True means that a dihedral restraint will be added to the leucines.'''
    for i in leuNumberList:
        prlleu=prl.molecules[0].residuesWithProperties('LEU')[i]
        projleu=proj.molecules[0].residuesWithProperties('LEU')[i]
        nTmessage('\nStart calculations for %s:'%prlleu.name)
        proj=writeRestraintsForLeu(prl,proj,prlleu,projleu,treshold,deasHB)
    if dihrCHI2==True:
        upper=245
        lower=0
        addDihRestr(proj,lower,upper,leuNumberList)
    return proj
# end def        

def runScript():
    'Main entry point of this script.'
#    proj_path='/Users/jd/workspace/'
    proj_path='/home/i/tmp/karenVCdir'
    proj_name='H2_2Ca_64_100'
    prl_name='H2_2Ca_64_100_3_rotleucines'
    proj = Project.open('%s/%s'%(proj_path,proj_name),status = 'old')
    prl = Project.open('%s/%s'%(proj_path,prl_name),status = 'old')
    leuNumberList=[0] #please define leunumbers.
    if prl_name.startswith('H2_2Ca_64_100'):
        leuNumberList=[2,3,4]
    treshold=0 #minimal violation, necessary to classify the restraints.
    deasHB=True #first deassign all HBs in the specified leucines
    dihrCHI2=True #add a dihedral restraint on the leucines.
    proj=alterRestraintsForLeus(leuNumberList,proj,prl,treshold,deasHB,dihrCHI2)
    if True:
        proj.save()
# end def        

if __name__ == '__main__':
    runScript()
