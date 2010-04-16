python -u $CINGROOT/python/cing/NRG/doAnnotateCasdNmrLoop.py
python -u $CINGROOT/python/cing/NRG/validateForCASD_NMR.py
python -u $CINGROOT/python/cing/NRG/storeCASDCING2dbLoop.py

set nrgDir = $CINGROOT/python/cing/NRG
set list = (  $nrgDir/doAnnotateCasdNmrLoop.py $nrgDir/validateForCASD_NMR.py $nrgDir/storeCASDCING2dbLoop.py )
foreach x ( $list )
	vi $x
end

foreach x ( $list )
  python -u $x
end

vi $CINGROOT/python/cing/Scripts/validateEntry.py

