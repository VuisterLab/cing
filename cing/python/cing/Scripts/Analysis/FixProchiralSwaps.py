from ccpnmr.analysis.core.AssignmentBasic import assignResToDim

def fixProchiralSwapsMacro(argServer):

  project = argServer.getProject()

  sdt = argServer.askFloat('Max allowed shift SD (ppm)') or 0.04

  swaps = 1
  n = 0
  while (swaps and n < 10):
#    swaps = fixProchirals(project, sdt)
    nSwaps = fixProchiralSwaps(project, sdt) # JFD found this in Analysis version 2.1.3 on 2010-05-25
    n += 1
    print 'Iteration %d swaps: %d' % (n, nSwaps) # JFD found count swaps is returned.

def fixProchiralSwaps(project, sdt=0.04):
  # Threshold shift SD for action

  nmr = project.currentNmrProject

  prochirals = set()
  for resonance in nmr.resonances:
    resonanceSet = resonance.resonanceSet

    if not resonanceSet:
      continue

    resonances = resonanceSet.resonances

    if len(resonances) == 2:
      prochirals.add(resonances)

  shiftLists = nmr.findAllMeasurementLists(className='ShiftList')
  shiftLists = [(len(sl.measurements), sl) for sl in shiftLists if sl.experiments]
  shiftLists.sort()

  shiftList = shiftLists[-1][1]

  nSwaps = 0

  for resonanceA, resonanceB in prochirals:
    shiftA = resonanceA.findFirstShift(parentList=shiftList)
    shiftB = resonanceB.findFirstShift(parentList=shiftList)

    if not (shiftA and shiftB):
      continue


    sdA = shiftA.error
    sdB = shiftB.error

    if (sdA > sdt) or (sdB > sdt):

      if shiftB.value < shiftA.value:
        resonanceA, resonanceB = resonanceB, resonanceA

      contribsA = resonanceA.peakDimContribs
      contribsB = resonanceB.peakDimContribs

      peakDimsA = set([c.peakDim for c in contribsA])
      peakDimsB = set([c.peakDim for c in contribsB])

      #peakDimsA = [pd for pd in peakDimsA0 if pd not in peakDimsB0]
      #peakDimsB = [pd for pd in peakDimsB0 if pd not in peakDimsA0]

      ppms = []
      peakDims = []
      for peakDim in peakDimsA:
        ppms.append(peakDim.value)
        peakDims.append(peakDim)
      for peakDim in peakDimsB:
        ppms.append(peakDim.value)
        peakDims.append(peakDim)

      if not ppms:
        continue

      centers, clusters, clusterIndices = kMeansPlusPlus(ppms, 2) #@UnusedVariable clusters
      centerA, centerB = centers

      if abs(centerA - centerB) < sdt:
        continue

      peakDimsA = [peakDims[i] for i in clusterIndices[0]]
      peakDimsB = [peakDims[i] for i in clusterIndices[1]]

      if centerB < centerA:
        peakDimsA, peakDimsB = peakDimsB, peakDimsA

      for peakDim in peakDimsA:
        contribA = peakDim.findFirstPeakDimContrib(resonance=resonanceA)
        contribB = peakDim.findFirstPeakDimContrib(resonance=resonanceB)

        if contribB:
          peakContribs = contribB.peakContribs
          contribB.delete()

          if not contribA:
            assignResToDim(peakDim, resonanceA, peakContribs=peakContribs)
          nSwaps += 1

      for peakDim in peakDimsB:
        contribB = peakDim.findFirstPeakDimContrib(resonance=resonanceB)
        contribA = peakDim.findFirstPeakDimContrib(resonance=resonanceA)

        if contribA:
          peakContribs = contribA.peakContribs
          contribA.delete()

          if not contribB:
            assignResToDim(peakDim, resonanceB, peakContribs=peakContribs)
          nSwaps += 1

  return nSwaps

from numpy import array, random, vstack

def kMeansPlusPlus(data, k):

  data = array(data)
  n = len(data)
  index = random.randint(0, n)
  centers = array( [data[index],] )
  nearest = vstack([centers] * n)

  while len(centers) < k:

    diff = data - nearest
    sqDists = (diff * diff).sum(axis=1)

    stopPoint = random.random() * sqDists.sum()
    point = sqDists[0]

    index = 0
    while point < stopPoint:
      point += sqDists[index]
      index += 1

    centers = vstack( (centers, data[index]) )

    # Re-find closest center
    for i, vector in enumerate(data):
      diffs = centers - vector
      dists = (diffs * diffs).sum(axis=1)
      nearest[i] = centers[dists.argmin()]

  change = 1.0

  while change > 0.0001:

    clusters = [[] for _x in range(k)]
    clusterIndices = [[] for _x in range(k)]
    for i, vector in enumerate(data):
      diffs = centers - vector
      dists = (diffs * diffs).sum(axis=1)
      closest = dists.argmin()
      clusters[closest].append(vector)
      clusterIndices[closest].append(i)

    change = 0
    for i, cluster in enumerate(clusters):
      cluster = array(cluster)
      center = cluster.sum(axis=0)/len(cluster)
      diff = center - centers[i]
      change += (diff * diff).sum()
      centers[i] = center

    #print change

  return centers, clusters, clusterIndices


