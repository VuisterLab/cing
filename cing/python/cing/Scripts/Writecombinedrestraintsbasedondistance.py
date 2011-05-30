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

def adddihrestr(proj,lower,upper,leunumberlist):
    '''Adding dihedral restraints'''
    #molec=proj.molecule.A
    leu=[]
    for i in leunumberlist:
        leu.append(proj.molecules[0].residuesWithProperties('LEU')[i])
    #leu=[molec.LEU589,molec.LEU596,molec.LEU618]
    lower=0
    upper=245
    dihrestrlist=DihedralRestraintList(name='CHI2restr')
    for i in leu:
        atoms=[i.CA,i.CB,i.CG,i.CD1]
        dihedralrestraint=DihedralRestraint(atoms=atoms,lower=lower,upper=upper)
        dihrestrlist.append(dihedralrestraint)
        NTmessage('CHI2 restraint appended for %s'%i.name)
    #end for
    proj.dihedrals.append(dihrestrlist)
    proj.partitionRestraints()
    return proj

def checkdoublerestraints(proj,leu):
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
    proj=deleterestraints(dellist,proj)
    checkrestraintsexistance(dellist,proj)
    return(proj)

def checkrestraintsexistance(restraintlist,proj):
    NTmessage('Project contains still following restraints:')#Just a check
    aplist=[]#list with unique atompairs in dellist
    for i in restraintlist:
        aplist.append(i.atomPairs[0])
    for i in list(set(aplist)):
        for j in proj.distances[0]:
            if i==j.atomPairs[0]:
                NTmessage('%s,id=%s'%(str(i),str(j.id)))
    return()

def deassignHB(proj,leu):
    NTmessage('Following restraint pairs with HBs of %s are deassigned:'%leu.name)
    deassHBaplist=[]
    atomindexes=[0,1]
    for i in leu.distanceRestraints: #restraints in proj.distances[0] are automatically deassigned.
        atom1=i.atomPairs[0][atomindexes[0]]
        atom2=i.atomPairs[0][atomindexes[1]]
        for a in atomindexes:
            atom=i.atomPairs[0][a]
            if not atom.residue.resNum==leu.resNum:
                continue
            atomname=atom.name
            if not (atomname=='HB2' or atomname=='HB3'):
                continue
            if a==0:
                atom1=atom.pseudoAtom()
            elif a==1:
                atom2=atom.pseudoAtom()
            newlist=NTlist()
            deassHBaplist.append((atom1,atom2))
            newlist.append((atom1,atom2))
            NTmessage('%s -> %s'%(str(i.atomPairs),str(newlist)))
            i.atomPairs=newlist
            break
        #endfor
    #endfor
    proj=checkdoublerestraints(proj,leu)
    proj.distances[0].analyze()
    return (proj,deassHBaplist)

def checkdeasrHB(n,deassHBaplist):
    'If an atom pair with a HB is already deassigned, it must be removed from the list to deassign.'
    NTmessage('checkdeasrHB is running')
    atomindexes=[0,1]
    dellist=[]
    #l=len(deassHBaplist)
    #ln=len(n)
    for i in n:
        for j in deassHBaplist:
            if str(i[atomindexes[0]])==str(j[atomindexes[0]]) and str(i[atomindexes[1]])==str(j[atomindexes[1]]):
               dellist.append(i)
    for i in dellist:
        n.remove(i)
        NTmessage('%s will not be removed.'%str(i))
    #if ln-len(n)==len(dellist): #just a check,used while debugging.
    #    NTmessage('%s restraints with a QB will not be deleted.'%len(dellist))
    return n

def classifyrestraints(prl,leu,treshold):
    """This routine scans the restrains of leu in prl for violations in the second and third model. After that these restraints
    are classified in four groups, violated in the second(tr), violated in the third(g+), violated in both(n) and not violated in both(u)."""
    #All atoms and pseudoatoms in the leucine sidechain, which have different positions in different rotameric states:
    scal=['HB2','HB3','MD1','MD2','QD','HG','CG','QB','HD11','HD12','HD13','HD21','HD22','HD23','CD1','CD2']#side chain atoms leu
    n=[] #atom pairs of restraints which violates in tr and g+
    u=[] #atom pairs of restraints which violates not in tr and not in g+
    trdict={} #keys=atompairs of restraints which violate in tr, values=(upperbound,violation in tr)
    gpdict={} #keys=atompairs of restraints which violate in gauche +, values=(upperbound,violation in gp)
    atomindexes=[0,1]
    trind=1
    gpind=2
    #leu=prl.molecules[0].residuesWithProperties('LEU')[leunumber] #leucine g
    NTmessage('Divide restraints into classes for %s'%leu.name)
    drlleu=leu.distanceRestraints #distance restraints of leucine g
    for k in range(len(drlleu)):
        found=0;
        dr=drlleu[k] #distance restraint k of this leucine
        for j in range(len(scal)):
            if found==1:
                break
            for a in atomindexes: #specifies first or second atom in atompair of restraint
                if not dr.atomPairs[0][a].atomsWithProperties('LEU',scal[j]):
                    continue
                if not dr.atomPairs[0][a].residue.resNum==leu.resNum:
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
    v=vdict.values()
    v.sort()
    lenv=len(v)
    return(vdict,v,lenv,)

def reversedict(vdict):
#    from collections import defaultdict #@Reimport
    rdict=defaultdict(list)
    for ii,jj in vdict.items():
        rdict[jj].append(ii)
    return rdict

def tableprint(table,length):
    'Just a handy script to print tables while debugging.length is the number of characters per element in table'
    string=''
    fmt='%-'+str(length)+'.2f'
    for i in table:
        for j in i:
            string+=fmt %j
        string+='\n'
    return string

def makedifferencetable(drlcolumns,drlrows,lendrlcolumns,lendrlrows):
    """
    table gives the absolute differences in upper-bounds between the restraints
    in the a-set and the b-set. So you can look up every difference in upperbound
    between two restraints, one of a and one of b.
    """
    table=[ [ 0 for _i in range(lendrlcolumns) ] for _j in range(lendrlrows) ] #table with only zeros
    for c in range(lendrlcolumns):
        for r in range(lendrlrows):
            diff=drlcolumns[c][0]-drlrows[r][0]
            table[r][c]=abs(diff)
    stringtable=tableprint(table,5)
    NTmessage('Difference table is:\n%s'%stringtable)
    return(table)

def makeallowedtable(table,drlcolumns,drlrows,lendrlcolumns,lendrlrows):
    """
    Every element in allowed table is the element in table minus the
    largest violation of the pair of restraints. If the violation is
    bigger than the difference, the value becomes negative. This combination
    of restraints will not be used.
    """
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
    stringtable=tableprint(allowedtable,15)
    NTdebug('Allowed table is:\n%s'%stringtable)
    return(allowedtable,maxi)

def checkcolumn(lendrlrows,allowedtable,column,maxi,ncolumnlist):
    minix=[] #list of values of specified column
    newrow=[]
    newvalue=[]
    for i in range(lendrlrows):
        minix.append(allowedtable[i][column])
    mini=min(minix) #lowest value of specified column
    #endfor
    if mini==maxi:
        ncolumnlist.append(column) #needs to be deassigned
    else: #I don't expect this will be the case. Let me know if you find an example
        for i in range(lendrlrows):
            if not allowedtable[i][column]==mini:
                continue
            newrow=i
            newvalue=mini
            NTmessage('check data for column %s, row %s and value %s.' %(str(i),str(column),str(mini)))
        #endfor
    #endif
    return(ncolumnlist,newrow,newvalue)

def checkindexes(indexes,allowedtable,table,maxi,n,invdrlcolumnsdict,invdrlrowsdict,drlcolumns,drlrows,lendrlrows):
    'rows and columns with the same index will form restraintpairs'
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
        n.append(invdrlcolumnsdict[drlcolumns[i]][0])
    rows,columns,values,n=checkrow(lendrlrows,drlrows,invdrlrowsdict,allowedtable,maxi,rows,columns,values,n)
    NTmessage('Table indexes are:\n\n%-7s  %-7s  %-7s'%('row:','column:','value:'))
    for i in range(len(rows)):
        NTmessage('%-7s  %-7s  %-7s'%(rows[i],columns[i],float(values[i])/1000))
    return(n,rows,columns,values)

def checkrow(lendrlrows,drlrows,invdrlrowsdict,allowedtable,maxi,rows,columns,values,n):
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
        if mini==maxi: #if there is no combination allowed for this row it will be deassigned
            nrowlist.append(i)
        else:
            for ii,jj in enumerate(allowedtable[i]): #finding column index for the lowest value in the row.
                if jj==mini:
                    columnind=ii
            #endfor
            rows.append(i)
            columns.append(columnind)
            values.append(mini)
        #endif
    #endfor
    for i in nrowlist:
        n.append(invdrlrowsdict[drlrows[i]][0])
    return(rows,columns,values,n)

def makerestraintpairdict(invdrlrowsdict,invdrlcolumnsdict,drlrows,drlcolumns,rows,columns):
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
    NTmessage('Following restraint pairs are written:')
    for i in disrlist:
        proj.distances[0].append(i)
        NTmessage('%s,id=%s'%(str(i.atomPairs),str(i.id)))
    proj.partitionRestraints()
    return proj

def deassignrestraints(n,proj,leu,deldeasrestr):
    NTmessage('Following restraint pairs are deassigned:')
    atomindexes=[0,1]
    for i in n: #deassign restraints in n
        delrestr=0
        for j in proj.distances[0]: #looks for the same restraints
            atom1=j.atomPairs[0][atomindexes[0]]
            atom2=j.atomPairs[0][atomindexes[1]]
            if not (str(atom1)==str(i[atomindexes[0]]) and str(atom2)==str(i[atomindexes[1]])):
                continue
            for jj in atom1,atom2:
                if not jj.residue.name==leu.name:
                    continue
                if delrestr==1:#if it is an intra residual restraint
                    delrestr=0
                if jj.hasPseudoAtom():
                    if jj==atom1:
                        atom1=jj.pseudoAtom()
                    elif jj==atom2:
                        atom2=jj.pseudoAtom()
                    #endif
                else:
                    delrestr=1
                #endif
            #endfor
            if delrestr==1:
                if deldeasrestr==True: #if restraint cannot be deassigned it will be deleted.
                    NTmessage('no pseudoatoms for %s. Restraint will be removed.' %str(j.atomPairs[0]))
                    proj=deleterestraints([j],proj)
                    if i!=n[-1]:#if this is not the last restraint which will be deassigned
                        NTmessage('Following restraint pairs are deassigned:')
                    break
                else:
                    NTmessage('Restraint %s cannot be deassigned.'%str(j.atomPairs[0]))
                #endif
            else:
                newlist=NTlist()
                newlist.append((atom1,atom2))
                NTmessage('%s -> %s'%(str(j.atomPairs),str(newlist)))
                j.atomPairs=newlist
                break
            #endif
        #endfor
    #endfor
    proj.partitionRestraints()
    proj=checkdoublerestraints(proj, leu)
    return(proj)

def writerestraintsforleu(prl,proj,prlleu,projleu,treshold,deasHB=True):

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
    munk = Munkres() #algorithm to make combinations of lowest costs
    indexes = munk.compute(allowedtable)
    n,rows,columns,_values=checkindexes(indexes,allowedtable,table,maxi,n,invdrlcolumnsdict,invdrlrowsdict,drlcolumns,drlrows,lendrlrows)
    #n=checkdeasrHB(n,deassHBaplistproj) Not necessary anymore since distances are recalculated after deassignment HB's.
    restraintpairdict=makerestraintpairdict(invdrlrowsdict,invdrlcolumnsdict,drlrows,drlcolumns,rows,columns)
    disrlist,dellist=makedisrlist(restraintpairdict,proj)
    proj=deleterestraints(dellist,proj)
    proj=appendrestraints(disrlist,proj)
    proj=deassignrestraints(n,proj,projleu,deldeasrestr=True)
    return proj

def alterrestraintsforleus(leunumberlist,proj,prl,treshold,deasHB,dihrCHI2):
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
#    proj_path='/home/i/tmp/karenVCdir/'
    proj_path='/Users/jd/workspace/'
    proj_name='H2_2Ca_64_100'
    molec_name='refine1'
    prl_name='H2_2Ca_64_100_3_rotleucines'
    proj = Project.open('%s%s'%(proj_path,proj_name),status = 'old')
    prl = Project.open('%s%s'%(proj_path,prl_name),status = 'old')
    leunumberlist=[2,3,4]
    treshold=0
    proj=alterrestraintsforleus(leunumberlist,proj,prl,treshold,deasHB=True,dihrCHI2=True)
    if True:
        proj.save()