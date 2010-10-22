#!/usr/bin/env python

import getopt
import httplib #@UnusedImport
import os
import re
import sys
import time
import urllib2
from sgmllib import SGMLParser

__author__="Jan Bot"
__author_institute__="Delft University of Technology"
__author_group__="The Delft Bioinformatics Lab"
__author_email__="j<dot>j<dot>bot<at>tudelft.nl"
__date__ ="$Dec 16, 2009 12:33:54 PM$"

class PoolParser(SGMLParser):
    """Parser for the ToPoS token pool directory."""

    token_re = re.compile("\d+")
    name_re = re.compile("[\w|\_]+")

    def reset(self):
        SGMLParser.reset(self)
        self.tokens = []
        self.in_directory_index = False
        self.in_row = False
        self.token = {}
        self.state = ''

    def start_table(self, attrs):
        """Method to find the directory listing."""
        ids = [v for k, v in attrs if k=='id']
        for id in ids:
            if id == 'directory_index':
                self.in_directory_index = True

    def end_table(self):
        """Directory listing is done, ignore all remaining table fields."""
        if self.in_directory_index:
            self.in_directory_index = False

    def start_td(self, attrs):
        """Start of table field, set status field."""
        if self.in_directory_index:
            for k, v in attrs:
                if(k == 'class'):
                    self.state = v.strip()

    def end_td(self):
        """End of table field, set status to nothing."""
        self.state = ''

    def start_tr(self, attrs):
        """Start of new table row."""
        if(self.in_directory_index):
            self.in_row = True
            self.token = {}

    def end_tr(self):
        """End of table row."""
        if(self.in_directory_index):
            if not len(self.token.keys()) == 0:
                self.tokens.append(self.token)
                self.in_row = False
                self.token = None

    def handle_data(self, data):
        """Adds the table data to the token, the name of the item has
        been specified before and should reside in self.state."""
        if self.in_directory_index and self.in_row:
            data = data.strip()
            if not self.state == '':
                self.token[self.state] = data

class TokenDownloader(object):
    """Class which downloads the tokens gathered by the PoolParser."""
    def __init__(self, url, tokens, outdir, timeout, useStamp):
        print outdir
        self.url = url
        self.tokens = tokens
        self.outdir = outdir
        self.timeout = timeout
        self.useStamp = useStamp

    def download(self):
        """Download function that does all the work."""
        for token in self.tokens:
            path = ''
            if(token.has_key('originalname')):
                path = os.path.join(self.outdir, token['originalname'])
            else:
                path = os.path.join(self.outdir, token['name'])

            if self.useStamp: # add the creation date to the filename
                (start, end) = path.rsplit('.', 1)
                path = start + '_' + token['created'] + '.' + end

            lsock = open(path, 'w')
            rsock = urllib2.urlopen(self.url + '/' + token['name'])
            lsock.write(rsock.read())
            rsock.close()
            lsock.close()
            time.sleep(self.timeout)

def usage():
    """Prints how the program should be used."""
    s = """
PoolDownloader.py
A program to download output files from ToPoS.

-b --base       Specifies the pool base when downloading tokens from
                multiple pools. Please specify the entire URL of the
                pool (http://topos.grid...)
-d  --dir       Directory where the files will be downloaded to, default
                is the current working directory.
-h  --help      Prints this help.
-m  --multi     Flag to specify that multiple pools will be downloaded.
-n  --nr        Number of pools that need to be downloaded. Can only be
                used in combination with the --base and --multi arguments.
-p  --pool      Pool URL. Only used when --multi is not set. Specify the
                entire URL of the pool (http://topos.grid...)
-r  --remove    Removes the pool after downloading all the files.
-s  --timestamp Adds the timestamp of the file to the filename.
-t  --timeout   Specifies the timeout between calls in seconds (default
                is 0.5 seconds).
-u  --update    Update only, retrieves the files not already present.
-x  --rstart    Start nr of pools to download (inclusive). Has to be used
                in combination with the -y / --rstop parameter.
-y  --rstop     Stop nr of pools to download (inclusive). Has to be used
                in combination with the -x / --rstart parameter.

Example:
To download all tokens that are not yet on disk from the first three test
output pools, use:
python PoolDownloader.py -m -b http://topos.grid.sara.nl/4/pools/test_output_
                         -n 3 -t 0.5 -d /tmp/ --update
    """
    print s

def removePool(pool):
    """Removes the provided token pool."""
    c = pycurl.Curl()
    c.setopt(pycurl.URL, pool)
    c.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
    c.perform()

def downloadPool(pool, outdir, timeout, update,  useStamp):
    print pool
    sock = urllib2.urlopen(pool)
    parser = PoolParser()
    parser.feed(sock.read())
    parser.close()
    tokens = parser.tokens

    if update:
        localfiles = os.listdir(outdir)
        # If the useStamp parameter is set checking wether the file already
        # exists is somewhat more involved.
        if useStamp:
            out = []
            for token in tokens:
                nameOut = ''
                if token.has_key('originalname'):
                    nameOut = token['originalname']
                else:
                    nameOut = token['name']
                (start, end) = nameOut.rsplit('.', 1)
                nameOut = start + '_' + token['created'] + '.' + end
                if not nameOut in localfiles:
                    out.append(token)
            tokens = out
        else:
            # if it is not set it is quite easy...
            tokens = [token for token in tokens
                    if not token['originalname'] in localfiles]

    print len(tokens), " tokens to download from pool: ", pool
    downloader = TokenDownloader(pool, tokens, outdir, timeout, useStamp)
    downloader.download()

if __name__ == "__main__":
    localfiles = []
    outdir = ''
    pool = ''
    update = False
    timeout = 0.5
    useStamp = False
    remove_pool = False
    poolBase = ""
    multi = False
    poolRange = []
    rstart = -1
    rstop = -1

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'b:hmn:ud:p:rst:x:y:',
                ['dir=', 'help', 'update', 'pool=', 'timestamp',
                'timeout=', '--remove',  '--base=',  '--nr=',  '--rstart=',
                '--rstop='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    # Set argument values
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt in ('-b',  '--base'):
            poolBase = arg
        elif opt in ('-d', '--dir'):
            outdir = arg
        elif opt in ('-m',  '--multi'):
            multi = True
        elif opt in ('-n',  '--nr'):
            poolRange = range(int(arg))
        elif opt in ('-u', '--update'):
            update = True
        elif opt in ('-p', '--pool'):
            pool = arg
        elif opt in ('-t', '--timeout'):
            timeout = float(arg)
        elif opt in ('-s', '--timestamp'):
            useStamp = True
        elif opt in ('-r', '--remove'):
            try:
                import pycurl
            except ImportError:
                print "Remove pool option only available when pycurl has been installed."
                exit(5)
            remove_pool = True
        elif opt in ('-v',  '--rstart'):
            rstart = arg
        elif opt in ('-w',  '--rstop'):
            rstop = arg

    # No arguments, print help
    if(len(opts) == 0):
        usage()
        exit(3)

    # No output dir specified, use current working directory
    if outdir == '':
        outdir = os.getcwd()

    # Check if multiple pools should be downloaded and wether all the
    # needed params are supplied
    if multi or poolBase or poolRange or rstart > -1 or rstop > -1:
        if(not poolRange and rstart == -1 and rstop == -1):
            print "No range parameter specified."
            exit(6)
        elif(not rstart == -1 and rstop == -1):
            print "Missing pool range stop argument."
            exit(6)
        elif(rstart == -1 and not rstop == -1):
            print "Missing pool range start argument."
            exit(6)
        elif(not rstart == -1 and not rstop == -1):
            poolRange = range(rstart,  rstop + 1)

        if not poolBase:
            print "Please specify the poolBase."
            exit(7)
        pools = [poolBase + str(x) + "/tokens" for x in poolRange]
        for pool in pools:
            poolOutdir = os.path.join(outdir,  pool.split("/")[-2])
            if not os.path.exists(poolOutdir):
                os.mkdir(poolOutdir)
            downloadPool(pool, poolOutdir, timeout, update,  useStamp)

    else:
        if pool == '':
            print "Please specify the ToPoS pool."
            exit(4)
        downloadPool(pool, outdir, timeout, update, useStamp)


    # if remove_pool:
    #    removePool(pool)