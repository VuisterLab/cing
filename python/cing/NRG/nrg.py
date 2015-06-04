#!/usr/bin/env python
from __future__ import division, print_function, absolute_import, unicode_literals
__author__ = 'TJ Ragan (tjr22@le.ac.uk)'

import begin

try:
    import cing.NRG.externalDataSources as edc
    import  cing.NRG.celeryShellCommandRunner as cCMD
except ImportError:
    import externalDataSources as edc
    import celeryShellCommandRunner as cCMD


settings = {}
settings['doDryRun'] = False

dataSource = None
VALIDATION_REPORT_LOCATION = '/mnt/data/D/NRG-CING/tj_test'
CING_HOME = '~/workspace/cing/python/cing/'

CELERY_QUEUE = 'priority.low'
# CELERY_QUEUE = 'testing'


def runValidateEntryCommands(commandList):
    for validateEntryCommand in commandList:
        if settings['doDryRun'] is True:
            print(validateEntryCommand)
        else:
            cCMD.call_validateEntryPy_once.apply_async( (validateEntryCommand,), queue=CELERY_QUEUE )

@begin.subcommand
def getEntriesFromServer():
    dataSource.retrieveFullEntryList()
    if settings['doDryRun'] is True:
        print("Found these entries:")
        print(dataSource.entryCodes)
    else:
        dataSource.saveEntryCodes()


@begin.subcommand
def queueUpdated():
    dataSource.retrieveFullEntryList()
    dataSource.addUpdatedEntriesToQueue()
    print('Preparing {} entries...'.format(len(dataSource.queuedEntryCodes)))
    dataSource.prepareEntriesInQueue()
    print('Queueing entries.')
    runValidateEntryCommands(dataSource.make_validateEntryPy_Commands())


@begin.subcommand
def queueNew():
    dataSource.retrieveFullEntryList()
    dataSource.addNewEntriesToQueue()
    print('Preparing at most {} entries...'.format(len(dataSource.queuedEntryCodes)))
    dataSource.prepareEntriesInQueue()
    print('Queueing entries.')
    runValidateEntryCommands(dataSource.make_validateEntryPy_Commands())


@begin.subcommand
def queueAll():
    dataSource.retrieveFullEntryList()
    dataSource.addAllEntriesToQueue()
    print('Preparing {} entries...'.format(len(dataSource.queuedEntryCodes)))
    dataSource.prepareEntriesInQueue(force=True)
    print('Queueing entries.')
    runValidateEntryCommands(dataSource.make_validateEntryPy_Commands())


@begin.subcommand
def queue(pdb_code):
    dataSource.loadEntryCodes()
    availableEntries = dataSource.entryCodes.pdb.tolist()
    if pdb_code in availableEntries:
        dataSource.queuedEntryCodes.append(pdb_code)
        print('Preparing {}...'.format( pdb_code ))
        dataSource.prepareEntriesInQueue()
        print('Queueing entry.')
        runValidateEntryCommands(dataSource.make_validateEntryPy_Commands())
    else:
        raise ValueError('Cannot find {0} in the list of available entries from {1}'.format(
            pdb_code,
            dataSource.DATA_URL_BASE
        ))


@begin.start
def main(source = 'bmrb',
         report_dir = '/mnt/data/D/NRG-CING/tj_test',
         dry_run = False,
         *pdbs):
    edc.VALIDATION_REPORT_LOCATION = report_dir

    global dataSource
    if source == 'bmrb':
        dataSource = edc.BMRBData()
    else:
        raise NotImplementedError('BMRB is currently the only datasource.')

    settings['doDryRun'] = dry_run


# if __name__ == '__main__':
#     main()

