
===============  developer/submitter ===================
- Adjust $CINGROOT/scripts/vcing/settings.csh
    setenv TARGET_SDIR 'jd@dodos.dyndns.org:/Users/jd/tmp/cingTmp'
- Adjust $CINGROOT/python/cing/NRG/nrgCing.py 
        inputUrl = 'http://nmr.cmbi.umcn.nl/NRG-CING/input'
        outputUrl = 'jd@dodos.dyndns.org:/Library/WebServer/Documents/NRG-CING'

        
===============  source ===============  
- sync input to source.
        inputUrl = 'http://dodos.dyndns.org/NRG-CING/input'
        On nmr use: 
        scp -rp input jd@dodos.dyndns.org:/Volumes/tetra/NRG-CING
        
===============   target ===============  
- Create the TARGET_SDIR directory perhaps by using a different mount with ln -s.

===============   submitter ===============  
svn update $CINGROOT 
ensure in $CINGROOT/python/cing/NRG/nrgCing.py      
        inputUrl = 'http://dodos.dyndns.org/NRG-CING/input'
        outputUrl = 'jd@dodos.dyndns.org:/Library/WebServer/Documents/NRG-CING'


On VCs:
- svn update $CINGROOT 
- pay real good attention to settings to match developper's.
    This is not in svn for security reasons.
    $CINGROOT/python/cing/Scripts/vCing/localConstants.py

    
    
cvs -z3 -d:pserver:anonymous@ccpn.cvs.sourceforge.net:/cvsroot/ccpn login
cvs -z3 -d:pserver:anonymous@ccpn.cvs.sourceforge.net:/cvsroot/ccpn co -r stable ccpn

vi ../.cshrc
sc
python -u $CCPNMR_TOP_DIR/python/memops/scripts_v2/makePython.py

$CINGROOT/scripts/vcing/syncVCcode.csh

python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py

cing --testQ

