from __future__ import unicode_literals, print_function, absolute_import, division

import os
import json
import logging

from django.utils import timezone

from .models import Submission

save_location = '/Users/tjr22/Desktop/icingdevtemp/'
logger = logging.getLogger(__name__)


def processCcpnPost( request ):
    if request.POST['Action'] == 'Save':
        response = saveRequest( request )
    elif request.POST['Action'] == 'ProjectName':
        response = projectNameRequest( request )
    elif request.POST['Action'] == 'Run':
        response = runRequest( request )
    elif request.POST['Action'] == 'Status':
        response = statusRequest( request )
    elif request.POST['Action'] == 'Log':
        response = logRequest( request )
    elif request.POST['Action'] == 'Purge':
        response = purgeRequest( request )
    elif request.POST['Action'] == 'Criteria':
        response = criteriaRequest( request )
    else:
        raise NotImplementedError

    return json.dumps( response, separators=(',', ':') )


def criteriaRequest( ):
    pass


def purgeRequest( ):
    pass


def logRequest( ):
    pass


def saveRequest( request ):
    # {u'Action': [u'Save'], u'AccessKey': [u'o77cf6'], u'UserId': [u'ccpnAp']}
        # {"Result":"3.37 Mb","ExitCode":"Success","Action":"Save"}
    response = {'Action': 'Save'}

    try:
        submission = Submission(username=request.POST['UserId'],
                                code=request.POST['AccessKey'])
        f = request.FILES['UploadFile']
        submission.filename = f.name
        submission.name = submission.filename.split('.')[0]
        submission.ip = request.META['REMOTE_ADDR']

        fileSavePath = os.path.join(save_location, submission.code)
        os.mkdir(fileSavePath)
        with open(os.path.join(fileSavePath, submission.filename), 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        fileSize = round(os.path.getsize(fileSavePath)/(1024*1024), 2)
        submission.save()
        response[ 'Result' ] = str(fileSize) + ' MB' # Original response was Mb, which is Megabits
        response[ 'ExitCode' ] = 'Success'
        return response
    except:
        response[ 'ExitCode' ] = 'Error'
        raise


def projectNameRequest( request ):
    # {u'Action': [u'ProjectName'], u'AccessKey': [u'o77cf6'], u'UserId': [u'ccpnAp']}
        # {"Result":"__CcpnCourse3e_innit","ExitCode":"Success","Action":"ProjectName"}
    response = {'Action': 'ProjectName'}

    try:
        # logger.debug('Trying to get {} from the database...'.format(request.POST['AccessKey']))
        submission = Submission.objects.get(code=request.POST['AccessKey'])
        # logger.debug('Name from DB: {}'.format(submission.name))
        response[ 'Result' ] = submission.name
        response[ 'ExitCode' ] = 'Success'
        return response
    except:
        response[ 'ExitCode' ] = 'Error'
        raise


def runRequest( request ):
    # {u'Action': [u'Run'], u'AccessKey': [u'o77cf6'], u'UserId': [u'ccpnAp']}
        # {"Result":"started","ExitCode":"Success","Action":"Run"}
    response = {'Action': 'Run'}

    try:
        submission = Submission.objects.get(code=request.POST['AccessKey'])

        submissionName = submission.name
        submissionFile = submission.filename
        submission_type = submission.submission_type
        verbosity = submission.verbosity
        ranges = submission.ranges
        ensemble = submission.ensemble

        validateEntryPyCallString = ' '.join(('cing',
                                      '--name', submissionName,
                                      '--script doValidateiCing.py',
                                      '--initCcpn', submissionFile,
                                      '--verbosity', str(verbosity))
                                     )
        if ranges != '':
            validateEntryPyCallString += ' --ranges ' + ranges
        if ensemble != '':
            validateEntryPyCallString += ' --ensemble ' + ensemble

        logger.debug('Calling: {}'.format(validateEntryPyCallString))
        logger.info('Starting: {} from CCPN:{}'.format(submission.code, submission.ip))

        submission.submission_date = timezone.now()
        submission.save()
        response['Result'] = 'Started'
        response['ExitCode'] = 'Success'
        return response
    except:
        response['ExitCode'] = 'Error'
        raise


def statusRequest( request ):
    # {u'Action': [u'Status'], u'AccessKey': [u'o77cf6'], u'UserId': [u'ccpnAp']}
        # {"Result":"notDone","ExitCode":"Success","Action":"Status"}
    response = {'Action': 'Status'}

    try:
        submission = Submission.objects.get(code=request.POST['AccessKey'])

        htmlFileSavePath = os.path.join(save_location,
                                        submission.code,
                                        str(submission.name)+'.cing',
                                        'index.html')
        if os.path.isfile(htmlFileSavePath):
            response['Result'] = 'done'
        else:
            response['Result'] = 'notDone'
        response['ExitCode'] = 'Success'
        return response
    except:
        response['ExitCode'] = 'Error'
        raise