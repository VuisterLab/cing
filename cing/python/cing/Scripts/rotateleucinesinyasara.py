'''
Created on May 25, 2011

@author: Karen Berntsen

This script will load a PDB-file, takes the first model and makes two extra models, one with the Leucines in g+
and one with the Leucines in tr. These three models will be saved as a new PDB-file.
The project will be copied and in the copy, all the models will be deleted and the new PDB-file with the three models
will be imported.
'''
import shutil
from cing.core.classes import * #@UnusedWildImport
from cing.core.molecule import * #@UnusedWildImport
from yasaramodule import * #@UnusedWildImport
import yasara

def leunumbers(proj,cv):
    leucines=[]
    leulist=[]
    leus=proj.molecules[0].residuesWithProperties('LEU')
    for i in leus:
        if i.CHI1.cav>125 and i.CHI2.cav>245 and i.CHI1.cv<cv and i.CHI2.cv<cv:
            leucines.append(str(i.resNum))
            leulist.append(i)
    #For this project also leu618 is taken
    leulist.append(leus[4])
    leucines.append(str(leus[4].resNum))
    NTmessage('Found wrong leucines:')
    for i in leulist:
        NTmessage('%s'%str(i.name))
    return(leucines,leulist)

def copyproject(proj_path,proj_name,prl_name):
    "copy project:"
    shutil.copytree('%s%s.cing'%(proj_path,proj_name),'%s%s.cing'%(proj_path,prl_name))
    NTmessage('project is copied to %s%s.cing'%(proj_path,prl_name))
    return

def rotating(proj_path,prl_name,molec_name,chainlist,leulist):
    "load original pdb"
    pdb_path='%s%s.cing/Export/PDB/%s.pdb'%(proj_path,proj_name,molec_name)
    for i in range(3):
        yasara.LoadPDB(pdb_path,model=1)
    NTmessage('Rotating Leucines with Yasara:')
    CHI1=[-60,180]
    CHI2=[180,60]
    for i in range(2):
        for j in range(3):
            res='Res LEU %s Mol %s Obj %s'%(leulist[j],chainlist[j],str(i+2))
            yasara.Dihedral('N %s'%res,'CA %s'%res,'CB %s'%res,'CG %s'%res,bound='Yes',set=CHI1[i])
            yasara.Dihedral('CA %s'%res,'CB %s'%res,'CG %s'%res,'CD1 %s'%res,bound='Yes',set=CHI2[i])
    yasara.SavePDB('objects 1-3','%s%s'%(proj_path,prl_name),format='IUPAC',transform='No')
    return

def deletedirs(proj_path,proj_name,molec_name):
    deldirlist=['Dssp','Macros','Procheck','Queeny','Shiftx','Wattos','Whatif','X3DNA','talosPlus']
    for i in deldirlist:
        shutil.rmtree('%s%s.cing/%s/%s'%(proj_path,proj_name,molec_name,i),[True])
    return

def changecoordinates(proj_path,prl_name):
    prl = Project.open('%s%s'%(proj_path,prl_name),status = 'old')
    molec=prl.molecule
    molec.initCoordinates()
    molec.importFromPDB('%s%s.pdb'%(proj_path,prl_name),convention='IUPAC')
    prl.save()
    return

def rotateleucines(proj_path,proj_name,molec_name,chainlist,leucines):
    yasara.info.mode = "txt"
    yasara.info.licenseshown = 0
    #yasara.Console('Off')
    prl_name='%s_%s_rotleucines'%(proj_name,str(len(leucines)))
    copyproject(proj_path,proj_name,prl_name)
    rotating(proj_path,prl_name,molec_name,chainlist,leucines)
    deletedirs(proj_path,proj_name,molec_name)
    changecoordinates(proj_path,prl_name)
    return

if __name__ == '__main__':
    "some definitions"
    #proj_path='/mnt/hgfs/Documents/'
#    proj_path='/home/i/tmp/karenVCdir/'
    proj_path='/Users/jd/workspace/'
    proj_name='H2_2Ca_64_100'
    molec_name='refine1'
    chainlist=['A','A','A']
    cv=0.1
    proj_path_full = os.path.join(proj_path, proj_name)
    proj = Project.open(proj_path_full,status = 'old')
    leucines,leulist=leunumbers(proj,cv)
    rotateleucines(proj_path,proj_name,molec_name,chainlist,leucines)
