Use case creating validation reports for NRG-CING at Sara's cloud with results back to nmr.cmbi.umcn.nl (master)

### Short order of steps ###
  * Start up one VC on the cloud
  * Create input in general
  * Ensure there's enough space for receiving and subsequent unpacking. 10 gigs should do.
  * Clean up master
```
$C/python/cing/Scripts/vCing/vCing.py cleanMaster
ls $D/tmp/vCingSlave
```
  * Create tokens on any machine let's call it Duvel:
`$C/python/cing/NRG/nrgCing.py createToposTokens`
  * Fill topos with tokens on Duvel:
`$C/python/cing/Scripts/vCing/vCing.py addTokenListToTopos $D/NRG-CING/token_list_todo.txt`
  * Check topos queue at: https://topos.grid.sara.nl/4.1/pools/vCingmyVissie/tokens/. It takes about 5 minutes from deploying a VC before a slave will pull it's first token. It will take about 30 minutes from deployment before the average successful job will be pushed back to the master.
  * Breed more VCs as needed but slowly (2 a time) as we don't want to upset the svn updates from Google Code on any side. Two VCs at a time seems to work. Five was failing 2 of them once. But that might have been GC being busy with people moving away from sf.net. Or perhaps the wait of 1 second was too small for the network capacities in VC to be up already. Adjusted to 120 sec. Better safe than sorry because access from VC to master is also needed right away.
  * Make sure the revisions got updated from the master getting the results back:
`cd $D/tmp/vCingSlave/vCingmyVissie/log; grep "NMR structure Generation" *.log`
  * If the revision didn't get updated check the error message: (This log should have been elsewhere)
  * Check the load average on the pool set (define it first within the code) by running:
`$C/python/cing/Scripts/vCing/Utils.py`
  * Wait until all tokens are done. Kill any single tokens left.
  * Kill the VCs
  * Post process the results on the master
`python -u $C/python/cing/NRG/nrgCing.py 1brv postProcessEntryAfterVc`
  * This was taking about 10 hours per 3500 entries.
  * Put the results into RDb. Takes about 4 hours.

### Common pitfalls ###
  * Processing only one model
  * Processing without imagery
  * Processing to devNRG-CING (development)

### Handy commands ###
  * Copy 'n paste: Use waves inside VC as well as on own machine.
  * Clean up temp files inside VC:
`\rm -rf ~/tmp/cingTmp $C/startVC*.log ~/startVC*.log`