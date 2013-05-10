- Create cing project from ccpn:
python $CINGROOT/python/cing/PluginCode/test/test_ccpn.py

- Move to separate dir:
\cp -rf ../1brv_cs_pk_2mdl.cing .

- Initialize Queen project:
queen --project 1brv_cs_pk_2mdl --cing --initCing --overwrite

- Start checking
queen --project 1brv_cs_pk_2mdl --cing --dataset all --check

This currently still fails instead an installation of QUEEN 1.1 was tested on VC:

cd $WS/queen/queen
# Generate data for
./testsuite.py

cd $WS/nmr_valibase
./nmr_valibase.py -info_atomuncertainty example noe bb
./nmr_valibase.py -info_atomuncertainty example noe res

# Then this was repeated for 1brv on VC following help at:
http://www.cmbi.kun.nl/software/queen/index.spy?site=queen&action=Documentation&subaction=Running%20QUEEN

./nmr_valibase.py -info_atomuncertainty 1brv yourdataset res


Resulting imagery is in:
$WS/queen/projects/example/plot
copied to CING at:
$CINGROOT/queen/example/data/plot/atom_yourdataset_res.ps and bb.

