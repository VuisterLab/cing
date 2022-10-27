from __future__ import unicode_literals, print_function, absolute_import, division

import random
import string
import os
import logging
# import json
# import sys
import tarfile
import subprocess

from django.core.exceptions import SuspiciousFileOperation

from .models import Submission


logger = logging.getLogger(__name__)
save_location = os.environ['ICING_DATA_DIRECTORY']

def handleUploadedFile(request):
    f = request.FILES['user_file']
    while True:
        dirname = makeRandomString(6)
        full_filename = os.path.join(save_location, 'anonymous', dirname, f.name)
        if dirname not in os.listdir(save_location):
            os.makedirs(os.path.join(save_location, 'anonymous', dirname))
            break
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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tfile, extractLocation)


def determineSubmissionType(submission_code):
    submittedLocation = os.path.join(save_location, 'anonymous', submission_code)
    submittedDirectory = os.listdir(submittedLocation)

    for i in submittedDirectory:
        if i.startswith('.'):
            continue
        elif os.path.isdir(os.path.join(submittedLocation, i)):
            continue
        else:
            if i.endswith('.pdb') or i.endswith('.ent'):
                return 'PDB'
            elif i.endswith('tgz') or i.endswith('tar.gz'):
                with tarfile.open(os.path.join(submittedLocation, i)) as tfile:
                    tfileFileNames = tfile.getnames()

                    for name in tfileFileNames:
                        if (name.startswith('/') or '..' in name):
                            raise SuspiciousFileOperation('non-relative file name {} in tar file'
                                                          .format(name))

                    memopsImplementatonPath = os.path.join('memops', 'Implementation')
                    if any([memopsImplementatonPath in f for f in tfileFileNames]):
                        return 'CCPN'

                    pdb = any(['.pdb' in f for f in tfileFileNames])
                    upl = any(['.upl' in f for f in tfileFileNames])
                    aco = any(['.aco' in f for f in tfileFileNames])
                    if all((pdb, upl, aco)):
                            return 'CYANA'
    logger.warn('Failed to determine project type for {}'.format(submission_code))
    return 'unknown'


class CingCommand(object):
    def __init__(self,
                 submission_code=None,
                 username='anonymous',
                 submissionName=None,
                 submissionFile=None,
                 submission_type=None,
                 verbosity=3,
                 ranges='',
                 ensemble=''):

        self.username = username
        self.submissionName = submissionName
        self.submissionFile = submissionFile
        self.submission_type = submission_type
        self.verbosity = verbosity
        self.ranges = ranges
        self.ensemble = ensemble
        if submission_code is not None:
            self.submission_code = submission_code

    @property
    def submission_code(self):
        return self._submission_code

    @submission_code.setter
    def submission_code(self, sc):
        self._submission_code = sc
        submission = Submission.objects.get(code=sc)
        self.username = submission.username
        self.submissionName = submission.name
        self.submissionFile = submission.filename
        self.submission_type = submission.submission_type
        self.verbosity = submission.verbosity
        self.ranges = submission.ranges
        self.ensemble = submission.ensemble

    @property
    def verbosity(self):
        return self._verbosity

    @verbosity.setter
    def verbosity(self, verbosity):
        verbMap = {'low': 3,
                   'medium': 6,
                   'high': 9}
        if verbosity in verbMap:
            self._verbosity = verbMap[verbosity]
        else:
            self._verbosity = verbosity


    def getRunDirectory(self):
        return os.path.join(os.environ['ICING_DATA_DIRECTORY'], self.username, self.submission_code)

    def getReportDirectory(self):
        return os.path.join(os.environ['ICING_DATA_DIRECTORY'], self.username, self.submission_code,
                            self.submissionName + '.cing')

    def getLogPath(self):
        return os.path.join(self.getReportDirectory(), 'Logs')


    def getRunCommand(self):
        print(os.environ['CINGROOT'])

        if 'CING_PYTHON' in os.environ:
            py = os.environ['CING_PYTHON']
        else:
            py = 'python'
        cing = os.path.join(os.environ['CINGROOT'], 'python', 'cing','main.py')

        if self.submission_type == 'CCPN':
            init_type = '--initCcpn'
        elif self.submission_type == 'CYANA':
            init_type = '--initCyana'
        elif self.submission_type == 'PDB':
            init_type = '--initPDB'

        validateEntryPyCallString = [py, '-u', cing,
                                              '--name', self.submissionName,
                                              '--script', 'doValidateiCing.py',
                                              init_type, self.submissionFile,
                                              '--verbosity', str(self.verbosity)
                                            ]
        if self.ranges != '':
            validateEntryPyCallString += ['--ranges', self.ranges]
        if self.ensemble != '':
            validateEntryPyCallString += ['--ensemble', self.ensemble]


        return validateEntryPyCallString



def startCingRun(submission_code):
    submission = Submission.objects.get(code=submission_code)
    cc = CingCommand(submission_code)

    env = dict(os.environ)

    logger.info('Starting: {} from {}'.format(submission_code, submission.ip))
    rd = cc.getRunDirectory()
    rc = cc.getRunCommand()
    logger.debug('ICING_DATA_DIRECTORY: {}'.format(os.environ['ICING_DATA_DIRECTORY']))
    logger.debug('Calling: {} in {}'.format(rc, rd))

    subprocess.Popen(cc.getRunCommand(), cwd=rd, env=env)
