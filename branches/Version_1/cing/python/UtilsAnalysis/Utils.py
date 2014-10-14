'''
Created on Jun 2, 2010

Do not include any cing specific code.
Fold code into CING when the two are made consistent on
matplotlib, Imagery
@author: jd
'''

def getExperimentList(project):
    experiments = []
    for experiment in project.currentNmrProject.sortedExperiments():
        if experiment.refExperiment:
            experiments.append(experiment)
    return experiments

def getPeakLists(project, excludeSimulated=True):
  """
  Get all peak lists

  .. describe:: Input

  Implementation.MemopsRoot

  .. describe:: Output

  List of Nmr.Peaks
  """

  experiments = getExperimentList(project)
  peakLists = []
  for experiment in experiments:
      for spectrum in experiment.sortedDataSources():
            if (spectrum.dataType == 'processed') and (spectrum.numDim > 1):
                for peakList in spectrum.sortedPeakLists():
                    if excludeSimulated and peakList.isSimulated:
                        continue
                    peakLists.append(peakList)
  return peakLists

