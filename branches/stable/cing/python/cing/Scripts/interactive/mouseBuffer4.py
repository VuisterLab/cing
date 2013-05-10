# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer5.py
from cing.Libs.Imagery import convertImageMagick
from matplotlib.dates import date2num
import datetime
import os


def createPinUp(pdb_id, extraArgListStr):
    print 'pdb_id:             ' + pdb_id
    print 'extraArgListStr:    ' + extraArgListStr
    ch23 = pdb_id[1:3]
#    /Library/WebServer/Documents/NRG-CING/data/a2/1a24/1a24.cing/1a24/HTML
    htmlDir = '/Library/WebServer/Documents/%(results_base)s/data/%(ch23)s/%(pdb_id)s/%(pdb_id)s.cing/%(pdb_id)s/HTML' % {
                    'pdb_id':pdb_id,'ch23':ch23, 'results_base': extraArgListStr}
    inputPath = os.path.join(htmlDir, 'mol.gif')
    outputPath = os.path.join(htmlDir, 'mol_pin.gif')
    if convertImageMagick(inputPath, outputPath, options='-geometry 114x80'): # Dimension to match the one in molgrap.py
        print 'ERROR: failed for: ' + inputPath
# end def

yearIntMin = 1990 # inclusive start
yearIntMax = 2014 # exclusive end
yearIntBinSize = 2
nbins = ( yearIntMax - yearIntMin ) / yearIntBinSize  # should match above. last bin will start at 2010
dateDatMin = datetime.date(yearIntMin, 1, 1)
dateDatMax = datetime.date(yearIntMax, 1, 1)
dateMin = date2num(dateDatMin)
dateMax = date2num(dateDatMax)
binSizeTdel = datetime.timedelta(365*yearIntBinSize)
halfBinSizeTdel = datetime.timedelta(365*yearIntBinSize/2.)

