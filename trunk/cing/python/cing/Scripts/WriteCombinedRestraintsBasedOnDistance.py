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

def adddihrestr(proj,lower,upper,leunumberlist):
    '''Adding CHI2 dihedral restraints to leucines, specified in leunumberlist. lower and upper are the lower bound and upper bound of the restraint.'''
    '''The restraints will be put in a new restraintlist'''
    #molec=proj.molecule.A
    leu=[]
    for r in leunumberlist:
        leu.append(proj.molecules[0].residuesWithProperties('LEU')[r])
    #leu=[molec.LEU589,molec.LEU596,molec.LEU618]
    lower=0
    upper=245
    dihrestrlist=DihedralRestraintList(name='CHI2restr')
    for r in leu:
        atoms=[r.CA,r.CB,r.CG,r.CD1]
        dihedralrestraint=DihedralRestraint(atoms=atoms,lower=lower,upper=upper)
        dihrestrlist.append(dihedralrestraint)
        NTmessage('CHI2 restraint appended for %s'%r.name)
    #end for
    proj.dihedrals.append(dihrestrlist)
    proj.partitionRestraints()
    return proj

def checkdoublerestraints(proj,leu):
    '''After deassignment, some atomPairs occur twice in the distance restraint list. This script will delete the one with the highest upperbound.'''
    NTmessage('Checking for double restraints after deassignment')
    dellist=[]
    drlist=leu.distanceRestraints
    for i in range(len(drlist)):
        for j in range(i):
            if not drlist[i].atomPairs==drlist[j].atomPairs:
                continue
            if drlist[i].upper>drlist[j].upper:
                dellist.append(drlist[i])
            else:
                dellist.append(drlist[j])
        #endfor
    #endfor
    if dellist:
        proj=deleterestraints(dellist,proj)
        checkrestraintsexistance(dellist,proj)
    #endif
    return(proj)

def checkrestraintsexistance(restraintlist,proj):
    '''After deleting halve of the double restraints, this script will check whether the other halve is still there.'''
    NTmessage('Project contains still following restraints:')#Just a check
    aplist=[]#list with unique atompairs in restraintlist
    count=0
    for dr in restraintlist:
        aplist.append(dr.atomPairs[0])
    for ap in list(set(aplist)):
        for dr in proj.distances[0]:
            if ap==dr.atomPairs[0]:
                count+=1
                NTmessage('%s,id=%s'%(str(ap),str(dr.id)))
    if count==0:
        NTerror('No restraints found')
    return()

def deassignHB(proj,leu):
    '''Deassignes HBs in specified leucines. It will replace the old restraint, in order to delete all the other information.'''
    NTmessage('Following restraint pairs with HBs of %s are deassigned:'%leu.name)
    deassHBaplist=[]
    atomindexes=[0,1]
    for dr in leu.distanceRestraints: #restraints in proj.distances[0] are automatically deassigned.
        atom1=dr.atomPairs[0][atomindexes[0]]
        atom2=dr.atomPairs[0][atomindexes[1]]
        for ai in atomindexes:
            atom=dr.atomPairs[0][ai]
            if not atom.residue.resNum==leu.resNum:
                continue
            atomname=atom.name
            if not (atomname=='HB2' or atomname=='HB3'):
                continue
            if ai==0:
                atom1=atom.pseudoAtom()
            elif ai==1:
                atom2=atom.pseudoAtom()
            newlist=NTlist()
            deassHBaplist.append((atom1,atom2))
            newlist.append((atom1,atom2))
            NTmessage('%s -> %s'%(str(dr.atomPairs),str(newlist)))
            dr.atomPairs=newlist
            break
        #endfor
    #endfor
    proj=checkdoublerestraints(proj,leu)
    proj.distances[0].analyze()
    return (proj,deassHBaplist)

def checkdeasrHB(n,deassHBaplist):
    '''If an atom pair with a HB is already deassigned, it must be removed from the list to deassign. deassHBaplist is the list which is already deassigned
    and n is the list of restraints, which violate in trans and gauche+, which should be deassigned.'''
    NTmessage('checkdeasrHB is running')
    atomindexes=[0,1]
    dellist=[]
    #l=len(deassHBaplist)
    #ln=len(n)
    for dr in n:
        for j in deassHBaplist:
            if str(dr[atomindexes[0]])==str(j[atomindexes[0]]) and str(dr[atomindexes[1]])==str(j[atomindexes[1]]):
               dellist.append(dr)
    for dr in dellist:
        n.remove(dr)
        NTmessage('%s will not be removed.'%str(dr))
    #if ln-len(n)==len(dellist): #just a check,used while debugging.
    #    NTmessage('%s restraints with a QB will not be deleted.'%len(dellist))
    return n

def classifyrestraints(prl,leu,treshold):
    """This routine scans the restrains of leu in prl for violations in the second and third model. After thatl these restraints
    are classified in four groups, violated in the second(tr), violated in the third(g+), violated in both(n) and not violated in both(u)."""
    #All atoms and pseudoatoms in the leucine sidechain, which have different positions in different rotameric states:
    scall=['HB2','HB3','MD1','MD2','QD','HG','CG','QB','HD11','HD12','HD13','HD21','HD22','HD23','CD1','CD2']#side chain atoms leucine list
    n=[] #atom pairs of restraints which violates in tr and g+
    u=[] #atom pairs of restraints which are unviolated in both tr and g+
    trdict={} #keys=atompairs of restraints which violate in tr, values=(upperbound,violation in tr)
    gpdict={} #keys=atompairs of restraints which violate in gauche+, values=(upperbound,violation in gp)
    atomindexes=[0,1]
    trind=1 #trans index
    gpind=2 #gauche+ index
    #leu=prl.molecules[0].residuesWithProperties('LEU')[leunumber] #leucine g
    NTmessage('Divide restraints into classes for %s'%leu.name)
    drlleu=leu.distanceRestraints #distance restraints of leucine g
    for k in range(len(drlleu)):
        found=0;
        dr=drlleu[k] #distance restraint k of this leucine
        for a in range(len(scall)): #loops over the atoms in scall
            if found==1:
                break
            for ai in atomindexes: #specifies first or second atom in atompair of restraint
                if not dr.atomPairs[0][ai].atomsWithProperties('LEU',scall[a]):
                    continue
                if not dr.atomPairs[0][ai].residue.resNum==leu.resNum:
                    continue
                if dr.violations[trind]>treshold:
                    if dr.violations[gpind]>treshold:
                        n.append(dr.atomPairs[0])
                    else:
                        trdict[dr.atomPairs[0]]=(dr.upper,dr.violations[1])
                    #endif
                else:
                    if dr.violations[gpind]>treshold:
                        gpdict[dr.atomPairs[0]]=(dr.upper,dr.violations[2])
                    else:
                        u.append(dr.atomPairs[0])
                    #endif
                found=1;
                break
                #endif
            #endfor
        #endfor
    tmplist=[trdict.keys(),gpdict.keys(),n,u]
    namelist=['trans','gauche+','both','none']
    for i in range(4):
        if tmplist[i]:
            NTmessage('list violated in %s for %s contains %s restraints'%(namelist[i],leu.name,len(tmplist[i])))
    return(n,u,trdict,gpdict)

def renamedicts(trdict,gpdict):
    '''Renames the dictionaries with distance restraint lists, called tr and g+, to dictionaries for the columns and the rows in a table,
    such that the amount of columns is never higher than the amount of rows.'''
    ltr=len(trdict)
    lgp=len(gpdict)
    if ltr>lgp:
        drlcolumnsdict,drlcolumns,lendrlcolumns=dictvalues(gpdict)
        drlrowsdict,drlrows,lendrlrows=dictvalues(trdict)
    else:
        drlcolumnsdict,drlcolumns,lendrlcolumns=dictvalues(trdict)
        drlrowsdict,drlrows,lendrlrows=dictvalues(gpdict)
    return drlcolumnsdict,drlcolumns,lendrlcolumns,drlrowsdict,drlrows,lendrlrows

def dictvalues(vdict):
    '''Returns the dictionary, the sorted list of values and the length of this list.'''
    v=vdict.values()
    v.sort()
    lenv=len(v)
    return(vdict,v,lenv,)

def reversedict(vdict):
    '''Interchange of keys and values in a dictionary. In case a value occurs twice, the dictionary will have two keys in a list for that value.'''
    rdict=defaultdict(list)
    for ii,jj in vdict.items():
        rdict[jj].append(ii)
    return rdict

def tableprint(table,length):
    'Just a handy script to print tables while debugging. Length is the number of characters per element in table'
    string=''
    fmt='%-'+str(length)+'.2f' #to be able to print the table alligned, this value has to depend on the length of an element in the table
    for r in table:
        for c in r:
            string+=fmt %c
        string+='\n'
    return string

def makedifferencetable(drlcolumns,drlrows,lendrlcolumns,lendrlrows):
    '''
    table gives the absolute differences in upper-bounds between the restraints
    in the a-set and the b-set. So you can look up every difference in upperbound
    between two restraints, one of a and one of b.
    '''
    table=[ [ 0 for _i in range(lendrlcolumns) ] for _j in range(lendrlrows) ] #table with only zeros
    for c in range(lendrlcolumns):
        for r in range(lendrlrows):
            diff=drlcolumns[c][0]-drlrows[r][0]
            table[r][c]=abs(diff)
    #stringtable=tableprint(table,5)
    #NTmessage('Difference table is:\n%s'%stringtable)
    return(table)

def makeallowedtable(table,drlcolumns,drlrows,lendrlcolumns,lendrlrows):
    '''
    Every element in allowed table is the element in table minus the
    largest violation of the pair of restraints. If the violation is
    bigger than the difference, the value becomes negative. This combination
    of restraints will not be used. Therefore all negative values are set to
    a very high value (maxi).The values are enlarged by a factor 1000 so that
    the munkres algorithm can work with it.
    '''
    maxi=9999999 #Munkres cannot work with float("infinity") and None objects
    allowedtable=[ [ 0 for _i in range(lendrlcolumns) ] for _j in range(lendrlrows) ] #table with only zeros
    for c in range(lendrlcolumns):
        for r in range(lendrlrows):
            diff=table[r][c]
            diffcor=diff
            if drlrows[r][0]>drlcolumns[c][0]:
                diffcor-=drlcolumns[c][1]
            elif drlrows[r][0]<drlcolumns[c][0]:
                diffcor-=drlrows[r][1]
            elif drlrows[r][0]==drlcolumns[c][0]:
                diffcor-=(drlcolumns[c][1]+drlrows[r][1])/2
            #endif
            if diffcor<0:
                allowedtable[r][c]=diff*1000
            else:
                allowedtable[r][c]=maxi
            #endif
        #endfor
    #endfor
    #stringtable=tableprint(allowedtable,15)
    #NTmessage('Allowed table is:\n%s'%stringtable)
    return(allowedtable,maxi)

def checkallowedtable(allowedtable,table,maxi,n,lendrlcolumns,lendrlrows,drlcolumns,drlrows,invdrlcolumnsdict,invdrlrowsdict):
    '''Checks wether allowedtable has columns or rows which consist only of maximum values. In that case, the row or column
    cannot be combined and should be deassigned or deleted, so the restraint will be added to the list of restraints which
    violate both in tr as in g+, because these restraints also have to be deassigned or deleted.
    This check happens before calculating the best combination, because the deletion of these columns/rows will lead to
    better combinations and less computation time.'''
    NTmessage('Checks allowedtable')
    dellistrows=[]
    dellistcolumns=[]
    for r in range(lendrlrows):
        if min(allowedtable[r])==maxi:
            dellistrows.append(r)
    for c in range(lendrlcolumns):
        column=[]
        for r in range(lendrlrows):
            column.append(allowedtable[r][c])
        if min(column)==maxi:
            dellistcolumns.append(c)
    newallowedtable=allowedtable
    newtable=table
    dellistrows.sort(reverse=True)
    for r in dellistrows:
        newallowedtable.pop(r)
        table.pop(r)
    dellistcolumns.sort(reverse=True)
    for c in dellistcolumns:
        for r in newallowedtable:
            r.pop(c)
        for r in newtable:
            r.pop(c)
    lendrlrows=len(newallowedtable)
    lendrlcolumns=len(newallowedtable[0])
    for c in dellistcolumns:
        n.append(invdrlcolumnsdict[drlcolumns[c]][0])
    for r in dellistrows:
        n.append(invdrlrowsdict[drlrows[r]][0])
    for r in dellistrows:
        drlrows.pop(r)
    for c in dellistcolumns:
        drlcolumns.pop(c)
    return newallowedtable,table,lendrlrows,lendrlcolumns,drlrows,drlcolumns,n

def interchange(a,b):
    '''interchanges two objects of the same type.'''
    if type(b)==type(a):
        return b,a

def transpose(table):
    '''transposes a table, so the rows will be columns and the columns will be rows.'''
    if not table:
        return []
    return map(lambda *row: list(row), *table)

def calculateindexes(allowedtable,lendrlcolumns,lendrlrows):
    '''Calculates ideal combination of restraints, based on the allowedtable. It returns the indexes of the table.'''
    combs=calculatecombs(lendrlcolumns,lendrlrows)
    totalvaluenew='INF'
    if not lendrlrows!=lendrlcolumns:
        nCr=calcnCr(lendrlrows,lendrlcolumns)
        if nCr>30000: #to reduce the amount of calculation time. If nCr>30000 a faster but less optimal algorithm will be used.
            NTmessage('nCr = %s. It will take too long to calculate all possibilities first.\nCombinations may be not optimal'%nCr)
            indexes=munkindexes(allowedtable)
        else:
            for i in combs:#for all possible combinations:
                totalvalue,indexes1,indexes2,table1,table2=calulateallcombinations(i,allowedtable,lendrlrows)
                if totalvalue<totalvaluenew:#the lower totalvalue, the more information is kept.
                    totalvaluenew=totalvalue
                    finalindexes1=indexes1
                    finalindexes2=indexes2
                    _finaltable1=table1
                    _finaltable2=table2
                    finalcomb=i
                #endif
            indexes=translateindexes(finalcomb,finalindexes1,finalindexes2,lendrlrows)
            #endfor
        #endif
    else:
        indexes=munkindexes(allowedtable)
    #endif
    return indexes,totalvaluenew

def munkindexes(table):
    '''Calculate combination of lowest elements in table'''
    munk=Munkres()
    indexes=munk.compute(table)
    return indexes

def calcnCr(n,k):
    '''Calculates nCr; the amount of combinations when you take r out of n.'''
    if n>=k and k>=0:
        facn=fac(n)
        fack=fac(k)
        facnk=fac(n-k)
        nCr=facn/(fack*facnk)
    else:
        'k<0 or k>n; cannot calculate n nCr k.'
        nCr=None
    #endif
    return nCr

def fac(n):
    '''Calculates n! n must be a positive integer.'''
    if type(n)!=int:
        NTmessage('%s is not an integer, %s! will be calculated instead'%(n,int(n)))
        n=int(n)
    if n==1 or n==0:
        return 1
    else:
        return n*fac(n-1)

def calculatecombs(lendrlcolumns,lendrlrows):
    '''Calculates all possible ways to define a square matrix, given the size of it.'''
    li=range(lendrlrows)
    comb=combinations(li,lendrlcolumns)
    combs=[]
    for i in comb: #Calculates all combinations of square matrices to give to munkres.
        j=list(i)
        combs.append(j)
    return combs

def calulateallcombinations(comb,allowedtable,lendrlrows):
    '''Calculates the total sum of the differences in upper bound of distance restraints for the given combinations. The lower the sum, the less information
    is lost.'''
    munk=Munkres()
    totalvalue=0
    table1=[]
    table2=[]
    count=0
    for j in range(lendrlrows):
        if count<len(comb) and comb[count]==j:
            table1.append(allowedtable[j])
            count+=1
        else:
            table2.append(allowedtable[j])
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

def translateindexes(comb,indexes1,indexes2,lendrlrows):
    '''Translates the calculated indexes of munkres-part and the other part back to indexes of the original table.'''
    count1=0
    count2=0
    finalindexes=[]
    for j in range(lendrlrows):
        if count1<len(comb) and comb[count1]==j:
            index=indexes1[count1]
            newindex=(j,index[1])
            finalindexes.append(newindex)
            count1+=1
        else:
            index=indexes2[count2]
            newindex=(j,index[1])
            finalindexes.append(newindex)
            count2+=1
        #endif
    #endfor
    return finalindexes

def checkindexes(indexes,allowedtable,table,maxi,deassignlist,invdrlcolumnsdict,invdrlrowsdict,drlcolumns,drlrows,lendrlrows):
    '''rows and columns represent the restraintpairs. Checks wether there is choosen a maximum (=not allowed) value and if all rows are combined with a column.'''
    values=[]#values of allowedtable of restraint combinations in rows and columns. Not necessary.
    rows=[]
    columns=[]
    ncolumnlist=[] #columns of table which should be deassigned.
    for row, column in indexes:
        value=allowedtable[row][column]
        if value ==maxi: #checks if combination is possible
            NTmessage('Warning: index combination (%s,%s)->%s is not allowed. Needs to be deassigned.'%(row,column,table[row][column]))
            ncolumnlist,newrow,newvalue=checkcolumn(lendrlrows,allowedtable,column,maxi,ncolumnlist)
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
        deassignlist.append(invdrlcolumnsdict[drlcolumns[i]][0])
    rows,columns,values,deassignlist=checkrow(lendrlrows,drlrows,invdrlrowsdict,allowedtable,maxi,rows,columns,values,deassignlist)
    NTmessage('Table indexes are:\n\n%-7s  %-7s  %-7s'%('row:','column:','value:'))
    for i in range(len(rows)):
        NTmessage('%-7s  %-7s  %-7s'%(rows[i],columns[i],float(values[i])/1000))
    return(deassignlist,rows,columns,values)

def checkcolumn(lendrlrows,allowedtable,column,maxi,ncolumnlist):
    '''Checks wether a not-allowed combination is taken by the algorithm. In this case the lowest value in the column is set as
    new combination. In case the whole column is not allowed, the restraint has to be deassigned. However, this last case shouldn't
    happen at this point. It is just there to check.'''
    minix=[] #list of values of specified column
    newrow=[]
    newvalue=[]
    for i in range(lendrlrows):
        minix.append(allowedtable[i][column])
    mini=min(minix) #lowest value of specified column
    #endfor
    if mini==maxi: #should not be the case, because columns with all maximum values are deleted from the table before.
        ncolumnlist.append(column) #needs to be deassigned
    else:
        for i in range(lendrlrows):
            if not allowedtable[i][column]==mini:
                continue
            newrow=i
            newvalue=mini
            NTmessage('check data for column %s, row %s and value %s.' %(str(i),str(column),str(mini))) #I haven't seen an example yet.
        #endfor
    #endif
    return(ncolumnlist,newrow,newvalue)

def checkrow(lendrlrows,drlrows,invdrlrowsdict,allowedtable,maxi,rows,columns,values,deassinglist):
    '''Checks wether all rows are combined, if not, this function will add the combination which belongs to
    the lowest value in this row to the restraintset. For exampl, if checkcolumns has altered the combinations, it might
    be that a row is not combined anymore.'''
    nrowlist=[] #rows of table which should be deassigned.
    left=[] #rows of table which are not yet combined with a column
    for i in range(lendrlrows):
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
        mini=min(allowedtable[i])
        if mini==maxi: #if there is no combination allowed for this row it will be deassigned. I don't expect this to be the case
            nrowlist.append(i)
        else:
            columnind=allowedtable[i].index(mini)#finding column index for the lowest value in the row.
            rows.append(i)
            columns.append(columnind)
            values.append(mini)
        #endif
    #endfor
    for i in nrowlist:
        deassinglist.append(invdrlrowsdict[drlrows[i]][0])
    return(rows,columns,values,deassinglist)

def makerestraintpairdict(invdrlrowsdict,invdrlcolumnsdict,drlrows,drlcolumns,rows,columns):
    '''Makes a restraintpair dict. Every combination in this dictionary has to be rewritten into a restraint later.
    The keys are the restraintpairs and the values are the upperbound.'''
    restraintpairdict={} #keys are the restraintpairs, values are the maximum upperbound of the two restraintpairs.
    for i in range(len(rows)):
        restrpairone=invdrlrowsdict[drlrows[rows[i]]][0]
        restrpairtwo=invdrlcolumnsdict[drlcolumns[columns[i]]][0]
        newupperbound=max(drlrows[rows[i]][0],drlcolumns[columns[i]][0])
        restraintpairdict[(restrpairone,restrpairtwo)]=newupperbound
    return(restraintpairdict)

def makedisrlist(restraintpairdict,proj):
    'Makes list of new distance restraints.'
    low=0
    dellist=[]#restraints to be removed
    disrlist=[]#new restraints
    atomindexes=[0,1]
    for i in restraintpairdict.keys():
        ap1=[]
        ap2=[]
        for j in proj.distances[0]:
            if str(j.atomPairs[0][atomindexes[0]])==str(i[0][atomindexes[0]]) and str(j.atomPairs[0][atomindexes[1]])==str(i[0][atomindexes[1]]):
                ap1=j.atomPairs[:]
                dellist.append(j)
            elif str(j.atomPairs[0][atomindexes[0]])==str(i[1][atomindexes[0]]) and str(j.atomPairs[0][atomindexes[1]])==str(i[1][atomindexes[1]]):
                ap2=j.atomPairs[0][:]
                dellist.append(j)
            #endif
        #endfor
        if ap1 and ap2:
            ap1.append(ap2)
            upp=restraintpairdict[i]
            disr=DistanceRestraint(atomPairs=ap1,lower=low,upper=upp)
            disrlist.append(disr)
        else: #if the atompair can't be matched between the two projects. I don't expect this will happen
            if ap1:
                NTerror('only first atompair found')
            elif ap2:
                NTerror('only second atompair found')
            else:
                NTerror('No corresponding atom pair found in project')
            NTerror('atom pair = %s'%str(i))
            #endif
        #endif
    #endfor
    return(disrlist,dellist)

def deleterestraints(dellist,proj):
    '''Deletes the restraints in dellist in project proj.'''
    dellist=list(set(dellist)) #sort dellist and remove double elements
    NTmessage('Following restraint pairs are removed:')
    for i in dellist:
        for j in proj.distances[0]:
            if j==i:
                proj.distances[0].remove(i)
                NTmessage('%s,id=%s'%(str(i.atomPairs),str(i.id)))
            #endif
        #endfor
    #endfor
    proj.partitionRestraints()
    return proj

def appendrestraints(disrlist,proj):
    '''Appends restraint in disrlist to proj.'''
    NTmessage('Following restraint pairs are written:')
    for i in disrlist:
        proj.distances[0].append(i)
        NTmessage('%s,id=%s'%(str(i.atomPairs),str(i.id)))
    proj.partitionRestraints()
    return proj

def deassignrestraints(deassignlist,proj,leu,deldeasrestr):
    '''deassigns restraints in deassignlist. If they cannot be deassigned, they will be removed
    if deldeasrestr=True.'''
    NTmessage('Following restraint pairs are deassigned:')
    atomindexes=[0,1]
    for ap in deassignlist: #deassign restraints in deassignlist
        delrestr=0
        for dr in proj.distances[0]: #looks for the same restraints
            atom1=dr.atomPairs[0][atomindexes[0]]
            atom2=dr.atomPairs[0][atomindexes[1]]
            if not (str(atom1)==str(ap[atomindexes[0]]) and str(atom2)==str(ap[atomindexes[1]])):
                continue
            for a in atom1,atom2:
                if not a.residue.name==leu.name:
                    continue
                if delrestr==1:#if it is an intra residual restraint, it might be possible that the other leucine atom can be deassigned.
                    delrestr=0
                if a.hasPseudoAtom():
                    if a==atom1:
                        atom1=a.pseudoAtom()
                    elif a==atom2:
                        atom2=a.pseudoAtom()
                    #endif
                else:
                    delrestr=1
                #endif
            #endfor
            if delrestr==1: #The restraint cannot be deassigned.
                if deldeasrestr==True: #if restraint cannot be deassigned it will be deleted.
                    NTmessage('no pseudoatoms for %s. Restraint will be removed.' %str(dr.atomPairs[0]))
                    proj=deleterestraints([dr],proj)
                    if ap!=deassignlist[-1]:#if this is not the last restraint which will be deassigned
                        NTmessage('Following restraint pairs are deassigned:')
                    break
                else:
                    NTmessage('Restraint %s cannot be deassigned.'%str(dr.atomPairs[0]))
                #endif
            else:
                newlist=NTlist()
                newlist.append((atom1,atom2))
                NTmessage('%s -> %s'%(str(dr.atomPairs),str(newlist)))
                dr.atomPairs=newlist #replace the atomPairs.
                break
            #endif
        #endfor
    #endfor
    proj.partitionRestraints()
    proj=checkdoublerestraints(proj, leu)
    return(proj)

def writerestraintsforleu(prl,proj,prlleu,projleu,treshold,deasHB):
    '''This is an overall script which coordinates through all other functions.
    prl=project created in rotateLeucines.py
    proj=project you want to change
    prlleu and projleu are the leucineobjects in cing. They need to have the same residuenumber.
    treshold is the treshold for the violations
    if deasHB=True, all HB's of the specified leucine will be deassigned.'''
    if prlleu.resNum!=projleu.resNum:
        NTerror('Residuenumbers %s and %s are not the same.'%(prlleu.resNum,projleu.resNum))
    if deasHB==True: #if HB's needs to be deassigned
        proj,_deassHBaplistproj=deassignHB(proj,projleu)
        prl,_deassHBaplistprl=deassignHB(prl,prlleu)#just to be able to compare the two projects later on
    #endif
    n,_u,trdict,gpdict=classifyrestraints(prl,prlleu,treshold)
    drlcolumnsdict,drlcolumns,lendrlcolumns,drlrowsdict,drlrows,lendrlrows=renamedicts(trdict,gpdict)
    invdrlcolumnsdict=reversedict(drlcolumnsdict)
    invdrlrowsdict=reversedict(drlrowsdict)
    table=makedifferencetable(drlcolumns, drlrows,lendrlcolumns,lendrlrows)
    allowedtable,maxi=makeallowedtable(table,drlcolumns,drlrows,lendrlcolumns,lendrlrows)
    allowedtable,table,lendrlrows,lendrlcolumns,drlrows,drlcolumns,n=checkallowedtable(allowedtable,table,maxi,n,lendrlcolumns,lendrlrows,drlcolumns,drlrows,invdrlcolumnsdict,invdrlrowsdict)
    if lendrlrows<lendrlcolumns:
        drlcolumnsdict,drlrowsdict=interchange(drlcolumnsdict,drlrowsdict)
        lendrlcolumns,lendrlrows=interchange(lendrlcolumns,lendrlrows)
        drlcolumns,drlrows=interchange(drlcolumns,drlrows)
        table=transpose(table)
        allowedtable=transpose(allowedtable)
    stringtable=tableprint(table,5)
    NTmessage('Difference table is:\n%s'%stringtable)
    stringallowedtable=tableprint(allowedtable,15)
    NTmessage('Allowed table is:\n%s'%stringallowedtable)
    if False: #this is the old version of the algorithm; works faster, but gives less optimal results.
        munk = Munkres() #algorithm to make combinations of lowest costs
        _indexes = munk.compute(allowedtable)
    indexes,totalvaluenew=calculateindexes(allowedtable,lendrlcolumns,lendrlrows)
    #Code below was only used to set the indexes of the table by hand.
    #if projleu.resNum==589:
    #    indexes=[(0,0),(1,3),(2,1),(3,2),(4,4),(5,6),(6,5),(7,7),(8,7),(9,10),(10,9),(11,12),(12,11),(13,11),(14,12),(15,8),(16,13),(17,14),(18,14),(19,15),(20,8),(21,8)]
    #elif projleu.resNum==596:
    #    indexes=[(0,1),(1,0),(2,0),(3,3),(4,4),(5,5),(6,12),(7,2),(8,6),(9,8),(10,7),(11,9),(12,10),(13,11)]
    #elif projleu.resNum==618:
    #    indexes=[(0,0),(1,1)]
    #totalvaluenew='INF'
    n,rows,columns,_values=checkindexes(indexes,allowedtable,table,maxi,n,invdrlcolumnsdict,invdrlrowsdict,drlcolumns,drlrows,lendrlrows)
    if totalvaluenew!='INF':
        NTmessage('total sum of differences between upperbounds of combined restraints is %.2f A.'%(float(totalvaluenew)/1000))
    #n=checkdeasrHB(n,deassHBaplistproj) Not necessary anymore since distances are recalculated after deassignment HB's.
    restraintpairdict=makerestraintpairdict(invdrlrowsdict,invdrlcolumnsdict,drlrows,drlcolumns,rows,columns)
    disrlist,dellist=makedisrlist(restraintpairdict,proj)
    proj=deleterestraints(dellist,proj)
    proj=appendrestraints(disrlist,proj)
    proj=deassignrestraints(n,proj,projleu,deldeasrestr=True)
    return proj

def alterrestraintsforleus(leunumberlist,proj,prl,treshold,deasHB,dihrCHI2):
    '''This script rotates over all leucines and combines its restraints. After that, a CHI2restraint will be added to each of the specified leucines.
    leunumberlist=list of indices which leucines should be taken. So if you have 5 leucines and you want the first and the fourth, leunumberlist=[1,4]
    proj=project that you want to change
    prl=copy of project with 3 models with leucines in different conformations, created in rotateLeucines.py
    treshold gives the treshold value for the violations.
    deasHB=True means that all HBs of the specified leucines will be deassigned.
    dihrCHI2=True means that a dihedral restraint will be added to the leucines.'''
    for i in leunumberlist:
        prlleu=prl.molecules[0].residuesWithProperties('LEU')[i]
        projleu=proj.molecules[0].residuesWithProperties('LEU')[i]
        NTmessage('\nStart calculations for %s:'%prlleu.name)
        proj=writerestraintsforleu(prl,proj,prlleu,projleu,treshold,deasHB)
    if dihrCHI2==True:
        upper=245
        lower=0
        adddihrestr(proj,lower,upper,leunumberlist)
    return proj

if __name__ == '__main__':
#    proj_path='/Users/jd/workspace/'
    proj_path='/home/i/tmp/karenVCdir'
    proj_name='H2_2Ca_64_100'
    prl_name='H2_2Ca_64_100_3_rotleucines'
    proj = Project.open('%s/%s'%(proj_path,proj_name),status = 'old')
    prl = Project.open('%s/%s'%(proj_path,prl_name),status = 'old')
    leunumberlist=[2,3,4]
    treshold=0 #minimal violation, necessary to classify the restraints.
    deasHB=True #first deassign all HBs in the specified leucines
    dihrCHI2=True #add a dihedral restraint on the leucines.
    proj=alterrestraintsforleus(leunumberlist,proj,prl,treshold,deasHB,dihrCHI2)
    if True:
        proj.save()