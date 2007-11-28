
#############################################
# adjust these, if needed 
#############################################
setenv  xplorPath /usr/local/bin/xplor
setenv  profitPath /Users/jd/progs/ProFitV2.5.4/src/profit
setenv  procheckPath $UJ/progs/procheck/procheck_nmr.scr
setenv  whatifPath /home/vriend/whatif/DO_WHATIF.COM
#############################################
# No changes needed below this line.
#############################################
setenv  CINGROOT /Users/jd/workspace/cing

if ($?PYTHONPATH) then
    setenv PYTHONPATH .:/Users/jd/workspace/cing/python:$PYTHONPATH
else
    setenv PYTHONPATH .:/Users/jd/workspace/cing/python
endif

alias cing 'python /Users/jd/workspace/cing/python/cing/main.py'
