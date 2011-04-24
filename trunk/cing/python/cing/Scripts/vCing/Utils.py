#!/usr/bin/env python
from cing.Libs.disk import * #@UnusedWildImport

MASTER_TARGET_DIR = '/home/jurgenfd/D'

def prepareMaster(MASTER_TARGET_DIR=MASTER_TARGET_DIR, doClean=False):
    "Return True on error."
    cwd = os.getcwd()
    if not os.path.exists(MASTER_TARGET_DIR):
        # Setup in April 2011. Where XXXXXX is the not to be committed pool id.
#            jd:dodos/vCingSlave/ pwd
#            /Library/WebServer/Documents/tmp/vCingSlave
#            jd:dodos/vCingSlave/ ls -l
#            lrwxr-xr-x  1 jd  admin  18 Apr 15 21:39 vCingXXXXX@ -> /Volumes/tetra/vCingXXXXX
        print "Creating path that probably should be created manually because it might be an indirect one: %s" % MASTER_TARGET_DIR
        mkdirs(MASTER_TARGET_DIR)
    if not os.path.exists(MASTER_TARGET_DIR):
        print "ERROR: Failed to create: " + MASTER_TARGET_DIR
        return True
    os.chdir(MASTER_TARGET_DIR)
    for d in 'log log2 result'.split():
        if doClean:
            print "DEBUG: Removing and recreating %s" % d
            rmdir(d)
        else:
            print "DEBUG: Creating if needed %s" % d
        mkdirs(d)
    # end for
    os.chdir(cwd)
# end def

if __name__ == "__main__":
    if prepareMaster():
        print "ERROR: Failed to prepareMaster"