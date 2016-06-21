from __future__ import unicode_literals, print_function, absolute_import, division

import os
import logging
import subprocess
import time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView, UpdateView
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadFileForm, CcpnSubmissionForm
from .webUtils import handleUploadedFile, determineSubmissionType, startCingRun, CingCommand
from .ccpnUtils import processCcpnPost
from .models import Submission


logger = logging.getLogger(__name__)


class CingVersionMixin(object):
    """
    Mixin to inject cing version and update timestamp into views

    Views that use the {{ view.cing_XXX }} template tag will get the return value of these functions
    """

    def cing_version(self):
        version = subprocess.check_output(["git", "describe"], cwd=os.environ['CINGROOT']),
        return version[0][:-1]

    def cing_update(self):
        return time.ctime(os.path.getmtime(os.path.join(os.environ['CINGROOT'],'.git', 'FETCH_HEAD')))


class UploadView(CingVersionMixin, FormView):
    """
    Display the upload page if requested with a GET, and process the uploaded file from a POST.
    """
    template_name = 'iCing/upload.html'
    form_class = UploadFileForm

    def form_valid(self, form):
        submission = Submission(code=handleUploadedFile(self.request))

        determinedSubmissionType = determineSubmissionType(submission.code)
        submission.filename = self.request.FILES['user_file'].name
        submission.name = self.request.FILES['user_file'].name.split('.')[0]
        submission.ip = self.request.META['REMOTE_ADDR']
        requestedSubmissionType = self.request.POST['submission_type']
        if requestedSubmissionType != u'auto':
            if determinedSubmissionType != 'unknown':
                assert requestedSubmissionType == determinedSubmissionType
            submission.submission_type = requestedSubmissionType

        else:
            submission.submission_type = determinedSubmissionType

        submission.save()
        return redirect('icing:options', submission.code)


class OptionsView(CingVersionMixin, UpdateView):
    template_name = 'iCing/options.html'
    model = Submission
    fields = ['ranges',
              'ensemble',
              'verbosity']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.date = timezone.now()
        self.object.save()
        startCingRun(self.object.code)
        return redirect('icing:run', self.object.code)


class Run(CingVersionMixin, TemplateView):
    template_name = 'iCing/run.html'

    def run_finished(self):
        cc = CingCommand(self.kwargs['pk'])
        directory = cc.getReportDirectory()
        return is_run_finished(directory)


def logTextView(request, pk):
    cc = CingCommand(pk)

    try:
        logDirFiles = os.listdir(cc.getLogPath())
        logFile = [f for f in logDirFiles if f.endswith('.txt')][0]
        with open(os.path.join(cc.getLogPath(), logFile)) as f:
            logText = f.read()
    except (OSError, IndexError):
        logText = 'iCING run starting, please wait,...'

    return HttpResponse(logText, content_type='text/plain')


def runFinishedView(request, pk):
    cc = CingCommand(pk)
    reportDirectory = cc.getReportDirectory()
    runFinished = is_run_finished(reportDirectory)
    if runFinished:
        import subprocess
        cwd, reportName = os.path.split(reportDirectory)
        tgzName = reportName + '.tgz'
        subprocess.Popen(['/bin/tar', '-czf', tgzName, reportName], cwd=cwd)
    return HttpResponse(runFinished, content_type='text/plain')

def view(request, pk):
    submission = Submission.objects.get(code=pk)
    return redirect('../data/{0.username}/{0.code}/{0.name}.cing'.format(submission))


@csrf_exempt
def ccpnSubmit(request):
    if request.method == 'POST':
        logger.debug('CCPN POST request:{}'.format(request.POST))
        logger.debug('CCPN POST file:{}'.format(request.FILES))
        form = CcpnSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            response = processCcpnPost(request)
            logger.debug('Returning :{}'.format(response))
            return HttpResponse(response, content_type="application/json")
        else:
            print(form.errors)
    if request.method == 'GET':
        logger.debug('CCPN GET request:{}'.format(request.POST))


def is_run_finished(directory):
    if os.path.isfile(os.path.join(directory, 'index.html')):
        return not os.path.exists(os.path.join(directory, 'Temp'))
    return False
