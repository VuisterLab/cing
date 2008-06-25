# YASARA BioTools
# Visit www.yasara.org for more...
# Copyright by Elmar Krieger
from string import digits

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import fnmatch
import os
import shutil
import zipfile

#  ======================================================================
#                  D I S C   F U N C T I O N   G R O U P
#  ======================================================================

# MAKE PATH ABSOLUTE
# ==================
def abspath(path):
    if not os.path.isabs(path):
        path=os.path.join(os.getcwd(),path)
    return path

# COPY FILE
# =========
def copy(srcfilename,dstfilename,timespreserved=1,mod=None):
    """Throws an exception on some  failures and returns True
    on other. If all went fine it will return the default None
    """ 
    if timespreserved:
        # copy2 CAN FAIL ON FAT PARTITIONS
        try: 
            shutil.copy2(srcfilename,dstfilename)
        except: timespreserved=0
    if not timespreserved:
        try:
            shutil.copy(srcfilename,dstfilename)
        except: 
            shutil.copyfile(srcfilename,dstfilename)
    if mod != None: 
        chmod(dstfilename,mod)
    # Whatever above, if the target is absent now the copy failed.
    if not os.path.exists(dstfilename):
        return True

# COPY DIRECTORY
# ==============
# - srcpath IS A WILDCARD MATCHING THE FILES TO COPY
# - dstpath IS THE NAME OF THE DESTINATION DIRECTORY
def copydir(srcpath,dstpath,mod=None):
    filelist=dirlist(srcpath)
    for srcfilename in filelist:
        dstfilename=os.path.join(dstpath,os.path.basename(srcfilename))
        copy(srcfilename,dstfilename)
        if (mod!=None): chmod(dstfilename,mod)

# GET ALL FILES MATCHING A PATH+WILDCARD
# ======================================
def matchfilelist(path):
    path=os.path.split(path)
    wildcard=path[1]
    path=path[0]
    if (path==""): path="."
    try: files=os.listdir(path)
    except: return(None)
    matchfilelist=[]
    # CYCLE THROUGH ALL THE FILES
    for name in files:
        # CHECK IF FILENAME MATCHES WILDCARD
        filename=os.path.join(path,name)
        if (fnmatch.fnmatch(name,wildcard) and os.path.isfile(filename)):
            matchfilelist.append(filename)
    return(matchfilelist)

# REPLACE FILE
# ============
# dstfilename IS REPLACED WITH srcfilename, PERMISSIONS ARE SET TO mod.
def replace(srcfilename,dstfilename,mod):
    remove(dstfilename)
    copy(srcfilename,dstfilename)
    chmod(dstfilename,mod)
    remove(srcfilename)

# GET SIZE OF FILE
# ================
def filesize(filename):
    if (not os.path.exists(filename)): return(0)
    return(os.stat(filename)[6])

# INCREASE FILE NAME
# ==================
def incfilename(filename):
    i=len(filename)-1
    while (i>0 and filename[i] not in digits): i=i-1
    while (i>=0):
        num=ord(filename[i])
        if (num<48 or num>57): break
        num=num+1
        if (num==58): num=48
        filename=filename[:i]+chr(num)+filename[i+1:]
        if (num!=48): break
        i=i-1
    return(filename)

# MAKE DIRECTORY CHAIN
# ====================
def makedirs(path,permissions=0755):
    if (not os.path.exists(path)):
        os.makedirs(path,permissions)
    # THE PERMISSIONS ARE NOT ALWAYS SET CORRECTLY, DO IT AGAIN
    chmod(path,permissions)

# GET THE MODIFICATION TIME OF A FILE
# ===================================
def modtime(filename):
    if (not os.path.exists(filename)): return(0)
    else: return(os.path.getmtime(filename))

# GET ALL MODIFICATION TIMES FOR A LIST OF FILES
# ==============================================
def modtimes(filelist):
    timelist=[]
    for filename in filelist:
        if (not os.path.exists(filename)): timelist.append(0)
        else: timelist.append(os.path.getmtime(filename))
    return(timelist)

# CHECK IF TWO FILES ARE THE SAME
# ===============================
def havesamecontent(filename1,filename2):
    if (not os.path.exists(filename1) or not os.path.exists(filename2)): return(0)
    content1=open(filename1,"r").read()
    content2=open(filename2,"r").read()
    return (content1==content2)

# BUILD TEMPORARY FILE NAME
# =========================
def tmpfilename(filename):
    dotpos=filename.rfind(".")
    slashpos=filename.rfind(os.sep)
    if (dotpos==-1 or dotpos<slashpos): dotpos=len(filename)
    filename=filename[:dotpos]+"_tmp%d"%os.getpid()+filename[dotpos:]
    return(filename)

# CHECK IF FILE(S) EXIST(S)
# =========================
def pathexists(path):
    # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
    path=os.path.normpath(os.path.normcase(path))
    # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
    path=os.path.split(path)
    wildcard=path[1]
    path=path[0]
    if (path==""): path="."
    try: files=os.listdir(path)
    except: return(0)
    # DELETE ALL LIST ENTRIES THAT DO NOT MATCH THE WILDCARD GIVEN IN PATH
    for name in files:
        # CHECK IF FILENAME MATCHES WILDCARD
        #   INCLUDING A POSSIBLE _MOD APPENDIX (LIKE EMBL DSSP FILES)
        if (fnmatch.fnmatch(name,wildcard)): return(1)
    return(0)

# CREATE DIRECTORY LISTING INCLUDING FULL PATH NAMES
# ==================================================
# all==0: ONLY FILES WILL BE RETURNED
# all==1: ALL ENTRIES WILL BE RETURNED
# all==-1: ONLY DIRECTORIES WILL BE RETURNED
def dirlist(path,all=0):
    # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
    path=os.path.normpath(os.path.normcase(path))
    # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
    (path,wildcard)=os.path.split(path)
    if (path==""): path="."
    try: filelist=os.listdir(path)
    except: return([])
    # CYCLE THROUGH ALL FILES AND CHECK IF THEY MATCH WILDCARD
    i=0
    while (i<len(filelist)):
        if (fnmatch.fnmatch(filelist[i],wildcard)):
            filelist[i]=os.path.join(path,filelist[i])
            if (all==1 or
                (all==0 and os.path.isfile(filelist[i])) or
                (all==-1 and os.path.isdir(filelist[i]))):
                i=i+1
            continue
        # NO MATCH
        del filelist[i]
    filelist.sort()
    return(filelist)

# CREATE RECURSIVE DIRECTORY LISTING INCLUDING FULL PATH NAMES
# ============================================================
def recursivedirlist(path):
    # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
    path=os.path.normpath(os.path.normcase(path))
    # LIST OF COMPLETE PATHS
    pathlist=[]
    # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
    (dir,wildcard)=os.path.split(path)
    if (dir==""): dir="."
    try: filenamelist=os.listdir(dir)
    except: return([])
    # CYCLE THROUGH ALL FILES AND CHECK IF THEY MATCH WILDCARD
    for filename in filenamelist:
        path=os.path.join(dir,filename)
        if (os.path.isfile(path)):
            if (fnmatch.fnmatch(filename,wildcard)):
                pathlist.append(path)
        else:
            # RECURSE DIRECTORY
            if (filename!="." and filename!=".."):
                subdirlist=recursivedirlist(os.path.join(path,wildcard))
                if (subdirlist==[]):
                    # EMPTY SUBDIRECTORY
                    pathlist.append(path)
                else:
                    pathlist=pathlist+subdirlist
    pathlist.sort()
    return(pathlist)
 
# DELETE A FILE
# =============
def remove(filename):
    if (type(filename)==type([])):
        for filename2 in filename: remove(filename2)
    else:
        if (filename!=None and os.path.exists(filename)): os.remove(filename)

# RENAME A FILE
# =============
def rename(filenamesrc,filenamedst):
    if (filenamesrc and filenamedst and os.path.exists(filenamesrc)):
        os.rename(filenamesrc,filenamedst)

# DELETE ALL MATCHING FILES
# =========================
def removematch(path):
    if (type(path)==type([])):
        for pathname in path: removematch(pathname)
    else:
        # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
        path=os.path.normpath(os.path.normcase(path))
        # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
        path=os.path.split(path)
        wildcard=path[1]
        dir=path[0]
        if (dir==""): dir="."
        try: files=os.listdir(dir)
        except: return(0)
        # DELETE ALL LIST ENTRIES THAT DO NOT MATCH THE WILDCARD GIVEN IN PATH
        for name in files:
            # CHECK IF FILENAME MATCHES WILDCARD
            #   INCLUDING A POSSIBLE _MOD APPENDIX (LIKE EMBL DSSP FILES)
            if (fnmatch.fnmatch(name,wildcard)): remove(os.path.join(dir,name))
    return(0)

# SET MODIFICATION TIME
# =====================
def setmodtime(filename,modtime):
    os.utime(filename,(modtime,modtime))

# COPY MODIFICATION TIME
# ======================
def copymodtime(srcfilename,dstfilename):
    setmodtime(dstfilename,modtime(srcfilename))

# CHMOD A FILE
# ============
def chmod(path,mods):
    if (type(path)==type([])):
        for pathname in path: chmod(pathname,mods)
    else:
        try: os.chmod(path,mods)
        except: print "Could not change permissions for ",path

# DELETE AN ENTIRE DIRECTORY INCLUDING ALL THE FILES
# ==================================================
def rmdir(path):
    if (os.path.exists(path)): shutil.rmtree(path,1)

# REMOVE FILE EXTENSION
# =====================
def rmext(filename):
    dotpos=filename.rfind(".")
    if (dotpos!=-1): filename=filename[:dotpos]
    return(filename)

# GET FILE EXTENSION
# ==================
def ext(filename):
    dotpos=filename.rfind(".")
    if (dotpos!=-1): return(filename[dotpos+1:])
    return("")

# COUNT NUMBER OF FILENAMES PRESENT
# =================================
def countpresent(filenamelist):
    count=0
    for filename in filenamelist:
        if (os.path.exists(filename)): count=count+1
    return(count)

# UPDATE DIRECTORY
# ================
# - srcpath IS A WILDCARD MATCHING THE FILES TO UPDATE
# - dstdir IS THE NAME OF THE DESTINATION DIRECTORY
def updatedir(srcpath,dstdir,contentchecked=1,recursive=0,obsoleted=0,mod=None,excludelist=[]):
    if (os.path.isdir(srcpath)): srcpath=os.path.join(srcpath,"*")
    srcfilelist=dirlist(srcpath,recursive)
    srcbaselist=[]
    for srcfilename in srcfilelist:
        srcbasename=os.path.basename(srcfilename)
        srcbaselist.append(srcbasename)
        if (srcbasename not in excludelist):
            dstfilename=os.path.join(dstdir,srcbasename)
            if (os.path.isdir(srcfilename)):
                if (recursive):
                    updatedir(srcfilename,dstfilename,contentchecked,1,obsoleted,mod,excludelist)
            else:
                if ((contentchecked and not havesamecontent(srcfilename,dstfilename)) or
                    (not contentchecked and modtime(srcfilename)>modtime(dstfilename))):
                    copy(srcfilename,dstfilename,0,mod)
    if (obsoleted):
        # ALSO DELETE OBSOLETE FILES
        dstfilelist=dirlist(os.path.join(dstdir,os.path.basename(srcpath)))
        for dstfilename in dstfilelist:
            dstbasename=os.path.basename(dstfilename)
            if (dstbasename not in srcbaselist): remove(dstfilename)

# ZIP A FILE
# ==========
def zip(filename):
    print "Deflating",filename
    zipfilename=filename+".zip"
    zip=zipfile.ZipFile(zipfilename,"w",zipfile.ZIP_DEFLATED)
    zip.write(filename,os.path.basename(filename))
    zip.close()
    remove(filename)

# RETURN AN UNZIPPED FILE
# =======================
def unzipped(filename):
    zipfilename=filename+".zip"
    zip=zipfile.ZipFile(zipfilename,"r",zipfile.ZIP_DEFLATED)
    data=zip.read(os.path.basename(filename))
    zip.close()
    return(data)
