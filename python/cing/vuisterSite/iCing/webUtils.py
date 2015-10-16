from __future__ import unicode_literals, print_function, absolute_import, division

import random
import string
import os
import logging
# import json
# import sys
# import subprocess

logger = logging.getLogger(__name__)
save_location = '/Users/tjr22/Desktop/icingdevtemp/'

def handleUploadedFile(request):
    f = request.FILES['user_file']
    while True:
        dirname = makeRandomString(6)
        if dirname not in os.listdir(save_location):
            os.mkdir(os.path.join(save_location, dirname))
            break
        full_filename = os.path.join(save_location,'anonymous', dirname, f.name)
    with open(full_filename, 'wb+') as destination:
        logger.debug('Saving: {}'.format(full_filename))
        for chunk in f.chunks():
            destination.write(chunk)
        logger.debug('Saved: {}'.format(full_filename))

    return dirname

def makeRandomString(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))


def decompressFile(fileLocation):
    if fileLocation.endswith('.pdb'):
        pass
    elif fileLocation.endswith('.tgz'):
        import tarfile
        with tarfile.open(fileLocation) as tfile:
            extractLocation = os.path.join(os.path.split(fileLocation)[:-1])[0]
            tfile.extractall(extractLocation)


def determineSubmissionType(submission_code):
    submittedLocation = os.path.join(save_location, submission_code)
    submittedDirectory = os.listdir(submittedLocation)

    for i in submittedDirectory:
        if i.startswith('.'):
            continue
        elif os.path.isdir(os.path.join(submittedLocation, i)):
            continue
        else:
            if i.endswith('.pdb') or i.endswith('.ent'):
                return 'PDB'
            # elif i.endswith('.cyana.tgz') or i.endswith('.cyana.tar.gz'):
            #     return 'CYANA'
            # elif i.endswith('.ccpn.tgz') or i.endswith('.ccpn.tar.gz'):
            #     return 'CCPN'
            elif i.endswith('tgz') or i.endswith('tar.gz'):
                import tarfile
                with tarfile.open(os.path.join(submittedLocation, i)) as tfile:
                    tfileFileNames = tfile.getnames()

                    memopsImplementatonPath = os.path.join('memops', 'Implementation')
                    if any([memopsImplementatonPath in f for f in tfileFileNames]):
                        return 'CCPN'

                    pdb = any(['.pdb' in f for f in tfileFileNames])
                    upl = any(['.upl' in f for f in tfileFileNames])
                    aco = any(['.aco' in f for f in tfileFileNames])
                    lol = any(['.lol' in f for f in tfileFileNames])
                    if all((pdb, upl, aco, lol)):
                            return 'CYANA'
    logger.warn('Failed to determine project type for {}'.format(submission_code))
    return 'unknown'


def startCingRun(submission):
    submissionName = submission.name
    submissionFile = submission.filename
    submission_type = submission.format
    verbosity = submission.verbosity
    ranges = submission.ranges
    ensemble = submission.ensemble

    if submission_type == 'CCPN':
        init_type = '--initCcpn'
    elif submission_type == 'CYANA':
        init_type = '--initCyana'
    elif submission_type == 'PDB':
        init_type = '--initPDB'

    validateEntryPyCallString = ' '.join(('cing',
                                          '--name', submissionName,
                                          '--script doValidateiCing.py',
                                          init_type, submissionFile,
                                          '--verbosity', str(verbosity))
                                         )
    if ranges != '':
        validateEntryPyCallString += ' --ranges ' + ranges
    if ensemble != '':
        validateEntryPyCallString += ' --ensemble ' + ensemble

    logger.info('Starting: {} from {}'.format(submission.code, submission.ip))
    logger.debug('Calling: {}'.format(validateEntryPyCallString))
