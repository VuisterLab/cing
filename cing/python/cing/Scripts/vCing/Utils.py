#!/usr/bin/env python
'''
Execute like: $CINGROOT/python/cing/Scripts/vCing/Utils.py
or execute from vCing.py
'''

from cing.Libs.disk import * #@UnusedWildImport
import commands

def prepareMaster(master_target_dir, doClean=False):
    "Return True on error."
    cwd = os.getcwd()
    if not os.path.exists(master_target_dir):
        # Setup in April 2011. Where XXXXXX is the not to be committed pool id.
#            jd:dodos/vCingSlave/ pwd
#            /Library/WebServer/Documents/tmp/vCingSlave
#            jd:dodos/vCingSlave/ ls -l
#            lrwxr-xr-x  1 jd  admin  18 Apr 15 21:39 vCingXXXXX@ -> /Volumes/tetra/vCingXXXXX
        print "Creating path that probably should be created manually because it might be an indirect one: %s" % master_target_dir
        mkdirs(master_target_dir)
    if not os.path.exists(master_target_dir):
        print "ERROR: Failed to create: " + master_target_dir
        return True
    os.chdir(master_target_dir)
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

def onEachSlave( cmd='uptime', slaveListFile="slaveList.py"):
    slaveList = []
    slaveList += [ '145.100.57.%s' % x for x in range(202,204) ]
    slaveList += [ '145.100.57.%s' % x for x in [206,210,212] ]
    # Disable some security checks.
    sshOptionList = '-o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
    sshOptionList += ' -q'
    for slave in slaveList:
        cmdComplete = 'ssh %(sshOptionList)s i@%(slave)s %(cmd)s' % {                                                             
                'sshOptionList':sshOptionList, 'slave':slave, 'cmd':cmd}
        status, result = commands.getstatusoutput(cmdComplete)
        if not status:
            print slave, result
            continue
        # end if
        print slave, "ERROR: Failed command: %s with status: %s with result: %s" % (cmd, status, result)        
    # end for    
# end def
    
if __name__ == "__main__":
    if False:    
        if prepareMaster(sys.argv[1]):
            print "ERROR: Failed to prepareMaster"
        # end if
    # end if
    if 1:    
        if onEachSlave():
            print "ERROR: Failed to prepareMaster"
        # end if
    # end if
# end if
        