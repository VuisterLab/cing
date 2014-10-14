# From YASARA BioTools
# GWV 20130528: Added path routines
# Visit www.yasara.org for more...
# Copyright by Elmar Krieger
from glob import glob
from glob import glob1
from optparse import OptionParser
from string import digits
import fnmatch
import os
import re
import shutil
import sys
import time
import zipfile


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
    """Throws an exception on some failures and returns True
    on other. If all went fine it will return the default None
    """
    if timespreserved:
        # copy2 CAN FAIL ON FAT PARTITIONS
        try:
            shutil.copy2(srcfilename,dstfilename)
        except:
            timespreserved=0
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
        if (mod!=None):
            chmod(dstfilename,mod)

# GET ALL FILES MATCHING A PATH+WILDCARD
# ======================================
def matchfilelist(path):
    path=os.path.split(path)
    wildcard=path[1]
    path=path[0]
    if (path==""):
        path="."
    try:
        files=os.listdir(path)
    except:
        return(None)
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
    if (not os.path.exists(filename)):
        return(0)
    return(os.stat(filename)[6])

# INCREASE FILE NAME
# ==================
def incfilename(filename):
    i=len(filename)-1
    while (i>0 and filename[i] not in digits):
        i=i-1
    while (i>=0):
        num=ord(filename[i])
        if (num<48 or num>57):
            break
        num=num+1
        if (num==58):
            num=48
        filename=filename[:i]+chr(num)+filename[i+1:]
        if (num!=48):
            break
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
    if (not os.path.exists(filename)):
        return(0)
    else:
        return(os.path.getmtime(filename))

# GET ALL MODIFICATION TIMES FOR A LIST OF FILES
# ==============================================
def modtimes(filelist):
    timelist=[]
    for filename in filelist:
        if (not os.path.exists(filename)):
            timelist.append(0)
        else: timelist.append(os.path.getmtime(filename))
    return(timelist)

# CHECK IF TWO FILES ARE THE SAME
# ===============================
def havesamecontent(filename1,filename2):
    if (not os.path.exists(filename1) or not os.path.exists(filename2)):
        return(0)
    content1=open(filename1,"r").read()
    content2=open(filename2,"r").read()
    return (content1==content2)

# BUILD TEMPORARY FILE NAME
# =========================
def tmpfilename(filename):
    dotpos=filename.rfind(".")
    slashpos=filename.rfind(os.sep)
    if (dotpos==-1 or dotpos<slashpos):
        dotpos=len(filename)
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
    if (path==""):
        path="."
    try:
        files=os.listdir(path)
    except:
        return(0)
    # DELETE ALL LIST ENTRIES THAT DO NOT MATCH THE WILDCARD GIVEN IN PATH
    for name in files:
        # CHECK IF FILENAME MATCHES WILDCARD
        #   INCLUDING A POSSIBLE _MOD APPENDIX (LIKE EMBL DSSP FILES)
        if (fnmatch.fnmatch(name,wildcard)):
            return(1)
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
    if (path==""):
        path="."
    try:
        filelist=os.listdir(path)
    except:
        return([])
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
    if (dir==""):
        dir="."
    try:
        filenamelist=os.listdir(dir)
    except:
        return([])
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
        for filename2 in filename:
            remove(filename2)
    else:
        if (filename!=None and os.path.exists(filename)):
            os.remove(filename)

# RENAME A FILE
# =============
def rename(filenamesrc,filenamedst):
    if (filenamesrc and filenamedst and os.path.exists(filenamesrc)):
        os.rename(filenamesrc,filenamedst)

# DELETE ALL MATCHING FILES
# =========================
def removematch(path):
    if (type(path)==type([])):
        for pathname in path:
            removematch(pathname)
    else:
        # NORMALIZE PATH, IMPORTANT TO CONVERT UNIX FORWARD TO WINDOWS BACKWARD SLASHES
        path=os.path.normpath(os.path.normcase(path))
        # CREATE LIST OF ALL THE FILENAMES IN THE DIRECTORY SPECIFIED BY PATH
        path=os.path.split(path)
        wildcard=path[1]
        dir=path[0]
        if (dir==""):
            dir="."
        try:
            files=os.listdir(dir)
        except:
            return(0)
        # DELETE ALL LIST ENTRIES THAT DO NOT MATCH THE WILDCARD GIVEN IN PATH
        for name in files:
            # CHECK IF FILENAME MATCHES WILDCARD
            #   INCLUDING A POSSIBLE _MOD APPENDIX (LIKE EMBL DSSP FILES)
            if (fnmatch.fnmatch(name,wildcard)):
                remove(os.path.join(dir,name))
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
        for pathname in path:
            chmod(pathname,mods)
    else:
        try:
            os.chmod(path,mods)
        except:
            print "Could not change permissions for ",path

# DELETE AN ENTIRE DIRECTORY INCLUDING ALL THE FILES
# ==================================================
def rmdir(path):
    if (os.path.exists(path)):
        shutil.rmtree(path,1)

# REMOVE FILE EXTENSION
# =====================
def rmext(filename):
    dotpos=filename.rfind(".")
    if (dotpos!=-1):
        filename=filename[:dotpos]
    return(filename)

# GET FILE EXTENSION
# ==================
def ext(filename):
    dotpos=filename.rfind(".")
    if (dotpos!=-1):
        return(filename[dotpos+1:])
    return("")

# COUNT NUMBER OF FILENAMES PRESENT
# =================================
def countpresent(filenamelist):
    count=0
    for filename in filenamelist:
        if (os.path.exists(filename)):
            count=count+1
    return(count)

# UPDATE DIRECTORY
# ================
# - srcpath IS A WILDCARD MATCHING THE FILES TO UPDATE
# - dstdir IS THE NAME OF THE DESTINATION DIRECTORY
def updatedir(srcpath,dstdir,contentchecked=1,recursive=0,obsoleted=0,mod=None,excludelist=[]):
    if (os.path.isdir(srcpath)):
        srcpath=os.path.join(srcpath,"*")
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
            if (dstbasename not in srcbaselist):
                remove(dstfilename)

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


class Tailer(object):
    """\
    Courtesy of msthornton
    from: http://code.google.com/p/pytailer/
    Implements tailing and heading functionality like GNU tail and head
    commands.
    """
    line_terminators = ('\r\n', '\n', '\r')

    def __init__(self, file, read_size=1024, end=False):
        self.read_size = read_size
        self.file = file
        self.start_pos = self.file.tell()
        if end:
            self.seek_end()

    def splitlines(self, data):
        return re.split('|'.join(self.line_terminators), data)

    def seek_end(self):
        self.seek(0, 2)

    def seek(self, pos, whence=0):
        self.file.seek(pos, whence)

    def read(self, read_size=None):
        if read_size:
            read_str = self.file.read(read_size)
        else:
            read_str = self.file.read()

        return len(read_str), read_str

    def seek_line_forward(self):
        """\
        Searches forward from the current file position for a line terminator
        and seeks to the character after it.
        """
        pos = _start_pos = self.file.tell()

        bytes_read, read_str = self.read(self.read_size)

        start = 0
        if bytes_read and read_str[0] in self.line_terminators:
            # The first charachter is a line terminator, don't count this one
            start += 1

        while bytes_read > 0:
            # Scan forwards, counting the newlines in this bufferfull
            i = start
            while i < bytes_read:
                if read_str[i] in self.line_terminators:
                    self.seek(pos + i + 1)
                    return self.file.tell()
                i += 1

            pos += self.read_size
            self.seek(pos)

            bytes_read, read_str = self.read(self.read_size)

        return None

    def seek_line(self):
        """\
        Searches backwards from the current file position for a line terminator
        and seeks to the character after it.
        """
        pos = end_pos = self.file.tell()

        read_size = self.read_size
        if pos > read_size:
            pos -= read_size
        else:
            pos = 0
            read_size = end_pos

        self.seek(pos)

        bytes_read, read_str = self.read(read_size)

        if bytes_read and read_str[-1] in self.line_terminators:
            # The last charachter is a line terminator, don't count this one
            bytes_read -= 1

            if read_str[-2:] == '\r\n' and '\r\n' in self.line_terminators:
                # found crlf
                bytes_read -= 1

        while bytes_read > 0:
            # Scan backward, counting the newlines in this bufferfull
            i = bytes_read - 1
            while i >= 0:
                if read_str[i] in self.line_terminators:
                    self.seek(pos + i + 1)
                    return self.file.tell()
                i -= 1

            if pos == 0 or pos - self.read_size < 0:
                # Not enought lines in the buffer, send the whole file
                self.seek(0)
                return None

            pos -= self.read_size
            self.seek(pos)

            bytes_read, read_str = self.read(self.read_size)

        return None

    def tail(self, lines=10):
        """\
        Return the last lines of the file.
        """
        self.seek_end()
        end_pos = self.file.tell()

        for _i in xrange(lines):
            if not self.seek_line():
                break

        data = self.file.read(end_pos - self.file.tell() - 1)
        if data:
            return self.splitlines(data)
        else:
            return []

    def head(self, lines=10):
        """\
        Return the top lines of the file.
        """
        self.seek(0)

        for _i in xrange(lines):
            if not self.seek_line_forward():
                break

        end_pos = self.file.tell()

        self.seek(0)
        data = self.file.read(end_pos - 1)

        if data:
            return self.splitlines(data)
        else:
            return []

    def follow(self, delay=1.0):
        """\
        Iterator generator that returns lines as data is added to the file.

        Based on: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/157035
        """
        trailing = True

        while 1:
            where = self.file.tell()
            line = self.file.readline()
            if line:
                if trailing and line in self.line_terminators:
                    # This is just the line terminator added to the end of the file
                    # before a new line, ignore.
                    trailing = False
                    continue

                if line[-1] in self.line_terminators:
                    line = line[:-1]
                    if line[-1:] == '\r\n' and '\r\n' in self.line_terminators:
                        # found crlf
                        line = line[:-1]

                trailing = False
                yield line
            else:
                trailing = True
                self.seek(where)
                time.sleep(delay)

    def __iter__(self):
        return self.follow()

    def close(self):
        self.file.close()

def tail(file, lines=10):
    """\
    Return the last lines of the file.

    >>> import StringIO
    >>> f = StringIO.StringIO()
    >>> for i in range(11):
    ...     f.write('Line %d\\n' % (i + 1))
    >>> tail(f, 3)
    ['Line 9', 'Line 10', 'Line 11']
    """
    return Tailer(file).tail(lines)

def head(file, lines=10):
    """\
    Return the top lines of the file.

    >>> import StringIO
    >>> f = StringIO.StringIO()
    >>> for i in range(11):
    ...     f.write('Line %d\\n' % (i + 1))
    >>> head(f, 3)
    ['Line 1', 'Line 2', 'Line 3']
    """
    return Tailer(file).head(lines)

def follow(file, delay=1.0):
    """\
    Iterator generator that returns lines as data is added to the file.

    >>> import os
    >>> f = file('test_follow.txt', 'w')
    >>> fo = file('test_follow.txt', 'r')
    >>> generator = follow(fo)
    >>> f.write('Line 1\\n')
    >>> f.flush()
    >>> generator.next()
    'Line 1'
    >>> f.write('Line 2\\n')
    >>> f.flush()
    >>> generator.next()
    'Line 2'
    >>> f.close()
    >>> fo.close()
    >>> os.remove('test_follow.txt')
    """
    return Tailer(file, end=True).follow(delay)

def _test():
    import doctest
    doctest.testmod()

def _main(filepath, options):
    tailer = Tailer(open(filepath, 'rb'))

    try:
        try:
            if options.lines > 0:
                if options.head:
                    if options.follow:
                        print >>sys.stderr, 'Cannot follow from top of file.'
                        sys.exit(1)
                    lines = tailer.head(options.lines)
                else:
                    lines = tailer.tail(options.lines)

                for line in lines:
                    print line
            elif options.follow:
                # Seek to the end so we can follow
                tailer.seek_end()

            if options.follow:
                for line in tailer.follow(delay=options.sleep):
                    print line
        except KeyboardInterrupt:
            # Escape silently
            pass
    finally:
        tailer.close()

    def main(): # pylint: disable=W0612
        parser = OptionParser(usage='usage: %prog [options] filename')
        parser.add_option('-f', '--follow', dest='follow', default=False, action='store_true',
                          help='output appended data as  the  file  grows')

        parser.add_option('-n', '--lines', dest='lines', default=10, type='int',
                          help='output the last N lines, instead of the last 10')

        parser.add_option('-t', '--top', dest='head', default=False, action='store_true',
                          help='output lines from the top instead of the bottom. Does not work with follow')

        parser.add_option('-s', '--sleep-interval', dest='sleep', default=1.0, metavar='S', type='float',
                          help='with  -f,  sleep  for  approximately  S  seconds between iterations')

        parser.add_option('', '--test', dest='test', default=False, action='store_true',
                          help='Run some basic tests')

        (options, args) = parser.parse_args()

        if options.test:
            _test()
        elif not len(args) == 1:
            parser.print_help()
            sys.exit(1)
        else:
            _main(args[0], options)


def globMultiplePatterns(dirname, patternList):
    """Uses glob1(dirname, pattern) multiple times"""
    result = []
    for pattern in patternList:
        result += glob1(dirname, pattern)
    return result


# Stolen from macostools
EEXIST  =   17  #File exists
def mkdirs(dst):
    """Make directories leading to 'dst' if they don't exist yet"""
    if dst == '' or os.path.exists(dst):
        return
    head, _tail = os.path.split(dst)
    if os.sep == ':' and not ':' in head:
        head = head + ':'
    mkdirs(head)

    try:
        os.mkdir(dst, 0777)
    except OSError, e:
        # be happy if someone already created the path
        if e.errno != EEXIST:
            raise

def removeEmptyFiles( theDir ):
    for fn in glob(theDir):
        if os.path.getsize(fn) == 0:
            print "Removing empty file."
            os.unlink(fn)

def getNewestFileFromList( fnList ):
    """
    Return empty list if input is empty
    Return False on error
    """
    # thanks to http://www.daniweb.com/code/snippet216688.html for the example.
    if not fnList:
        print "WARNING: In getNewestFileFromList got no valid input: %s" % fnList
        return False

    date_file_list = []
    for fileName in fnList:
        if not os.path.exists(fileName):
            print "WARNING: Skipping missing fileName %s" % fileName
            continue
        # retrieves the stats for the current fileName as a tuple
        # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        # the tuple element mtime at index 8 is the last-modified-date
        stats = os.stat(fileName)
        # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
        # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
        # note:  this tuple can be sorted properly by date and time
        lastmod_date = time.localtime(stats.st_mtime)
        #print image_file, lastmod_date   # test
        # create list of tuples ready for sorting by date
        date_file_tuple = lastmod_date, fileName
        date_file_list.append(date_file_tuple)
    #print date_file_list  # test

    date_file_list.sort()
#    date_file_list.reverse()  # newest mod date now first
    return date_file_list[-1][1]

def globLast( pattern ):
    """
    Tries to return the newest file by creation date.
    Returns False on error
    """
    fnList = glob(pattern)
    if not fnList:
        return False
    return getNewestFileFromList( fnList )
# end def

def isRootDirectory(f):
    """
    Algorithm for finding just the root dir.
    See unit test for examples.
    """
#    nTdebug("Checking _isRootDirectory on : ["+f+"]")
    idxSlash = f.find("/")
    if idxSlash < 0:
        # Happens for every toplevel file. E.g. 1brv_aria.xml in issue 146 for 1brv_ccpngrid.tgz
#        nTdebug("Found no forward slash in entry in tar file.")
        return None

    idxLastChar = len(f) - 1
    if idxSlash == idxLastChar or idxSlash == (idxLastChar - 1):
#        nTdebug("If the first slash is the last or second last BINGO: ["+f+"]")
        return True
    return False
# end def

#--------------------------------------------------------------------------------------------------------------
def splitall(thePath):
    allParts = []
    while True:
        parts = os.path.split(thePath)
        if parts[0] == thePath:
            allParts.insert(0, parts[0])
            break
        elif parts[1] == thePath:
            allParts.insert(0, parts[1])
            break
        else:
            thePath = parts[0]
            allParts.insert(0, parts[1])
        #end if
    return allParts
#end if

_translate = {"..": os.pardir}
class Path( str ):
    """Path routines, adapted from: Python Cookbook, A. Martelli and D. Ascher (eds), O'Reilly 2002, pgs 140-142
    Features:
    - newpath = path1 / path2 + ext
    - slicing to address elements of path
    - tilde expansion
    - several os.path methods
    - iteration over files in self (if directory)
    - recursive walk using os.walk
    - split3 method: returns (directory, basename, extension) triple
    """
    def __str__( self ):
        p = os.path.normpath(self)
        return os.path.expanduser(p)
        #return os.path.normpath(self)
    def __div__(self, other):
        other = _translate.get(other, other)
        return Path(os.path.join(str(self),str(other)))
    def __add__(self, other):
        other = _translate.get(other, other)
        return Path(str(self)+str(other))
    def __len__( self ):
        return len(splitall(str(self)))
    def __getslice__( self, start, stop ):
        parts = splitall(str(self))[start:stop]
        if len(parts) > 0:
            return Path(os.path.join(*parts))
        else:
            return Path('')
    def __getitem__(self, i):
        return Path(splitall(str(self))[i])
    def exists( self ):
        return os.path.exists(str(self))
    def isdir( self ):
        return os.path.isdir(str(self))
    def isfile( self ):
        return os.path.isfile(str(self))
    def islink( self ):
        return os.path.islink(str(self))
    def glob(self):
        return [Path(f) for f in glob(str(self ))]
    def makedirs(self):
        mkdirs(str(self))
    def rmdir(self):
        rmdir(str(self))
    def remove(self):
        remove(str(self))
    def abspath( self ):
        return os.path.abspath(str(self))
    def relpath( self, start='' ):
        return Path(os.path.relpath(str(self),start))
    def splitext( self ):
        f,ext = os.path.splitext(str(self))
        return (Path(f), ext)
    def split3(self):
        "Return directory, basename, extension triple so that directory/basename+extension == self"
        if len(self) == 0:     # empty path
            return '', '', ''
        else:
            b, ext = self.splitext()
            return b[:-1], b[-1:], ext
    #end def
    def walk( self, topdown=True, onerror=None ):
        "Call os.walk() on self"
        return os.walk(str(self), topdown, onerror )
    def listdir( self ):
        if self.exists() and self.isdir():
            files = []
            for f in os.listdir(str(self)):
                files.append( self / f )
            return files
        else:
            return []
        #end if
    #end def
    def __iter__(self):
        for f in self.listdir():
            yield f
        #end for
    #end def
#end class
#--------------------------------------------------------------------------------------------------------------
