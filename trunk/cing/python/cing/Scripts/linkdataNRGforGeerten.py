"""
Created on Nov 9, 2010

@author: Karen Berntsen

Querying the database for some specific conditions.
This script will open the file with input data and gives a file back with the input data and some extra information.

Some of this imports aren't necessary. I just copied them from some scripts from Jurgen.
I kept them all here in case of I'll need it another time.
"""
from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG import * #@UnusedWildImport
from cing.NRG.settings import * #@UnusedWildImport
from cing.PluginCode.required.reqDssp import * #@UnusedWildImport
from cing.PluginCode.required.reqProcheck import * #@UnusedWildImport
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.PluginCode.sqlAlchemy import cgenericSql
from cing.PluginCode.sqlAlchemy import csqlAlchemy
from pylab import * #@UnusedWildImport # imports plt too now.
from scipy import * #@UnusedWildImport
from sqlalchemy.schema import Table #@UnusedImport
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import select #@Reimport @UnusedImport
from cing import cingDirTestsData



db_name = PDBJ_DB_NAME
user_name = PDBJ_DB_USER_NAME
schema = NRG_DB_SCHEMA
schemaJ = PDBJ_DB_SCHEMA
HOST = 'nmr'

#filename='/mnt/hgfs/Documents/Analysis entries/opdracht_geerten_november2010.txt'
filename=os.path.join( cingDirTestsData, 'varia', 'opdracht_geerten_november2010kort.txt')
outputFnLinkData = 'output.csv'

def linkdataNRG():
    #connection to the database:
    csql = csqlAlchemy(host=HOST, user=PDBJ_DB_USER_NAME, db=PDBJ_DB_NAME, schema=NRG_DB_SCHEMA)
    csql.connect()
    execute = csql.conn.execute

    jsql = cgenericSql(host=HOST, user=PDBJ_DB_USER_NAME, db=PDBJ_DB_NAME, schema=PDBJ_DB_SCHEMA)
    jsql.connect()
    jsql.autoload()

    #These few lines will load the tables brief_summary and cingentry.
    #jsql.loadTable('brief_summary')
    #bs=jsql.brief_summary.alias()

    csql.loadTable('cingentry')
    e1=csql.cingentry.alias()
    csql.loadTable('cingresidue')
    r1=csql.cingresidue.alias()

    #The file opdracht_geerten_november2010.txt bevat alle input.
    in_file = open(filename,"r")
    text = in_file.read()
    in_file.close()

    i=0 # i indicates a new block with information in the input file.
    pdbid=''
    pdbid2=''
    pdbidlist0=[]
    pdbidlist1=[]
    pdbidlist2=[]
    extrainfolist=[]
    m=0 # m indicates a new line.

    '''
    The following script reads the pdbid's in the text file and put them in four different columns.
    one for all different pdbids in the first column,
    one for all pdbid's in the first column,
    one for pdbids in the second column and
    one for the extra information. The // between the blocks are
    deleted in order to make it easier to add some information later.
    '''
    pdbidlist0.append(text[0:4]) #the file starts with an pdbid.
    ltext =len(text)
    for n in range(ltext):
        if n<(ltext-2) and text[n:n+2]=='//':
            if not (n<(ltext-3) and text[n+4]=='/'):
                pdbid=text[n+3:n+7]
                if not is_pdb_code(pdbid): #at the end of the file an empty pdbid is selected. I haven't removed it yet, so you'll see an error.
                    NTerror('[%s] is not a pdb localpdbid.'%pdbid)
                    #os._exit(1)
                pdbidlist0.append(pdbid)
                i=1
        if n==(ltext-1) or text[n:n+4]==pdbid:
            pdbidlist1.append(text[n:n+4])
            if m!=0:
                if n==(ltext-1): # at the end of the document there is for one entry extra information left.
                    extrainfo=text[m+9:n-3]
                elif i==1: # if the extra information is followed by an //,these signs are excluded from the extra information
                    extrainfo=text[m+9:n-4]
                    i=0
                else: # if it is a random 'line'  in the text file, just take the part between m+9 and n-1 (before the new pdbid)
                    extrainfo=text[m+9:n-1]
                extrainfokort=extrainfo.replace('/','') #all extra enters and / are deleted
                extrainfokort=extrainfokort.replace('\n','')
                extrainfolist.append(extrainfokort)
                m=0
            # end if
            pdbid2=text[n+5:n+9]
            pdbidlist2.append(pdbid2)
            m=n #m indicates the beginning of a new line with information.
        # end if
    # end for
    pdbidlist2=pdbidlist2[0:-1] # removes the '' at the end
    pdbidlist1=pdbidlist1[0:-1]
    pdbidlisttotal=pdbidlist0+pdbidlist2 #this includes all pdbid's in the file.
    #Create some empty dictionaries
    pc_rama_coredict = NTdict()
    ramchkdict = NTdict()
    bbcchkdict = NTdict()
    rotchkdict = NTdict()
    perEntryRogdict = NTdict()

    #The ROG percentages are load from the database and put in a dictionary.
    s5 = select([e1.c.pdb_id, r1.c.rog, 100.0 * func.count(r1.c.rog) / e1.c.res_count], from_obj=[e1.join(r1)]).group_by(e1.c.pdb_id, r1.c.rog, e1.c.res_count)
    NTdebug("SQL: %s" % s5)
    result=execute(s5).fetchall()
    #NTdebug("ROG percentage per entry: %s" % result)
    for row in result:
        k = str(row[0])
        if not perEntryRogdict.has_key(k):
            perEntryRogdict[k] = NTfill(0.0, 3)
        perEntryRogdict[k][int(row[1])] = float(row[2])
    for d in range(len(pdbidlisttotal)):
        if not perEntryRogdict.has_key(str(pdbidlisttotal[d])):
            perEntryRogdict[pdbidlisttotal[d]]=['','','']
    #Below is a script that will select the pdb_id column, pc_gf, wi_ramchk, wi_bbcchk and wi_rotchk columns from the entry table.
    s1=select([e1.c.pdb_id,e1.c.pc_rama_core,e1.c.wi_ramchk,e1.c.wi_bbcchk,e1.c.wi_rotchk])
    for n in range(len(pdbidlisttotal)):
        localpdbid=pdbidlisttotal[n]
        s2=s1.where(e1.c['pdb_id']==localpdbid)
        s2=execute(s2).fetchall()
        if s2==[]:
            s2=[(localpdbid,'','','','','')] # if there is no information, the pdbid is shown and the others are set empty.
        if not pc_rama_coredict.has_key(localpdbid):
            pc_rama_coredict.appendFromTable(s2, 0, 1)
            ramchkdict.appendFromTable(s2, 0, 2)
            bbcchkdict.appendFromTable(s2, 0, 3)
            rotchkdict.appendFromTable(s2, 0, 4)

    #Below, the finaltext is composed. First the original 4 columns are set back. After that, some other information is added. All information is
    #separated by a acomma.
    finaltext='pdbid1,pdbid2,length_total,length_match,matchfraction,experimental_meth_pdb2,Perc_most_fav_1,Ramchk_1,Bbcchk_1,Rotchk_1,ROG_Groen_1,ROG_Oranje_1,ROG_Rood_1,Perc_most_fav_2,Ramchk_2,Bbcchk_2,C12chk_2,ROG_Groen_2,ROG_Oranje_2,ROG_Rood_2\n'
    dictList = [pc_rama_coredict,ramchkdict,bbcchkdict,rotchkdict,perEntryRogdict]
    for k in range(len(pdbidlist1)):
        if k>1 and pdbidlist1[k]!=pdbidlist1[k-1]:
            finaltext+='\n'
        pdb_id1=pdbidlist1[k]
        pdb_id2=pdbidlist2[k]
        finaltext+=pdb_id1+','+pdb_id2+extrainfolist[k]
        for g in [pdb_id1,pdb_id2]:
            strList = [str(x[str(g)]) for x in dictList]
            finaltext += ',' + ','.join(strList)
        finaltext +='\n'
        #for g in [pdb_id1,pdb_id2]:
        #    strList = []
        #    for x in dictList:
        #        print x
        #        y = str(g)
        #        print y
        #        z = x[y]
        #        z_str = str(z)
        #        strList.append( z_str )
        #    finaltext += ',' + ','.join(strList)
        #finaltext +='\n'
    #Some corrections to make it a parsable csv-file.
    finaltext=finaltext.replace('None','')
    finaltext=finaltext.replace('\t',',')
    finaltext=finaltext.replace(']','')
    finaltext=finaltext.replace('[','')
    finaltext=finaltext.replace("''",'')
    finaltext=finaltext.replace(' ','')

    #writes the file:
#    out_file = open("/mnt/hgfs/Documents/Analysis entries/output.csv","w")
    out_file = open(outputFnLinkData,"w")
    out_file.write(finaltext)
    out_file.close()


if __name__ == '__main__':
    linkdataNRG()