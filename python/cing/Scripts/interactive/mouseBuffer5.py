# python -u $CINGROOT/python/cing/Scripts/interactive/mouseBuffer5.py
from cing.Libs.NTutils import * #@UnusedWildImport
from pylab import * #@UnusedWildImport # imports plt too now.

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


# For analyzing the leucine DRs and chi values for 2fwu
p = None # Just for misleading pylint and pydev.
# START
#p = project
m = p.molecule
#p = chi1.atoms[0].residue.chain.molecule.project
nmodels = m.modelCount
res = m.A.LEU596
chi1 = res.CHI1
d = 10 # deviation
t = 240# target
a = t - d
b = t + d
drViolThreshold = 0.1
chi1ViolModels = []

for i in range(nmodels):
    v = chi1[i]
    if not (v > a and v < b):
        continue
    # end if
    chi1ViolModels.append(i)
    for dr in res.distanceRestraints:
        dviol = dr.violations[i]
        if dviol > drViolThreshold:
            nTmessage("%-230s in model %s is: %8.3f" % (format(dr), i, dviol))
        # end if
    # end for dr
# end for model

disList = p.distances[0]
dis1 = disList[1936]


