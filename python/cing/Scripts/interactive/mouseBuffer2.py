# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer2.py

from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.nrgCingRdb import bin_by
from pylab import * #@UnusedWildImport

cing.verbosity = 9
yearMin = 1990 # inclusive start
yearMax = 2012 # exclusive end
yearBinSize = 2
nbins = 11 # should match above. last bin will start at 2010
dateMin = datetime.date(yearMin, 1, 1)
dateMax = datetime.date(yearMax, 1, 1)
dateNumMin = date2num(dateMin)
dateNumMax = date2num(dateMax)
dateNumSpan = dateNumMax - dateNumMin
halfBinSize = datetime.timedelta(365*yearBinSize/2.)
nTmessage("Date number min/max: %s %s" % (dateNumMin, dateNumMax))

nr = 100 # number of records
x = np.random.random(nr) * dateNumSpan + dateNumMin
y = np.random.random(nr) * 10
binned_valueList, numBins = bin_by(y, x, nbins=nbins, ymin=dateNumMin, ymax=dateNumMax)
bins = []
widths = []
dataAll = []
for i,bin in enumerate(numBins):
    bins.append(num2date(bin) + halfBinSize )
    widths.append(datetime.timedelta(365)) # 1 year width for box
    spread = binned_valueList[i]
#    spread = [ spread[0][i] for i in range(len(spread))]
    spread.sort()
    #spread = [ 1.00381822,  1.45233061,  2.09650059,  2.55906362,  4.18107502,  6.29808237,
    #  6.42807352,  6.69683858,  7.96910586,  8.14422446,  8.98091822]

    aspread = asarray(spread)
    dataAll.append(spread)
    nTdebug("aspread: %s" % aspread)
# end for
nTdebug("numBins: %s" % numBins)
wiskLoL = boxplot(dataAll, positions=bins, widths=widths, sym='b+')
#scatter(x, y, s=0.1) # Plot of the data and the fit
xlim(xmin=dateMin, xmax=dateMax)
print 'wiskLoL: %s' % wiskLoL
#ylim(0,10)
savefig('/Users/jd/tmp/cingTmp/boxplot.png')


