# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer5.py
from pylab import * #@UnusedWildImport # imports plt too now.
import time

clf()
ion()
hold(False)

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

xDat = range(1990,2012)
yDat = range(1990,2012)


scatter(xDat, yDat, s=0.5, marker='o', facecolors='k', edgecolors='k')
#                plot(t, fitDatefuncD2(p, t), "r--", linewidth=1) # Plot of the data and the fit
#                nTdebug("Setting xlimits to %s - %s" % (dateDatMin, dateDatMax))
#                xlim(xmin=dateMin, xmax=dateMax, auto=True)
#                xticks( range(dateDatMin, dateDatMax, binSizeTdel)) #     
plot( (1990,2012), (1990,2012) )
time.sleep(1000)

