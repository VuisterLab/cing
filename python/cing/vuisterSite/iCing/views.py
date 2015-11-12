from __future__ import unicode_literals, print_function, absolute_import, division

import os
import logging
import subprocess
import time

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import generic
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadFileForm, RunSetupForm, CcpnSubmissionForm
from .webUtils import handleUploadedFile, determineSubmissionType, startCingRun, CingCommand
from .ccpnUtils import processCcpnPost
from .models import Submission

logger = logging.getLogger(__name__)
cing_version = subprocess.check_output(["git", "describe"], cwd=os.environ['CINGROOT'])
cing_update = time.ctime(os.path.getmtime(os.path.join(os.environ['CINGROOT'],'.git', 'FETCH_HEAD')))

class UploadView(generic.FormView):
    template_name = 'iCing/upload.html'
    form_class = UploadFileForm

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)
        context['cing_version'] = cing_version
        context['cing_update'] = cing_update
        return context

    def form_valid(self, form):
        submission = Submission(code = handleUploadedFile(self.request))

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
        return redirect('options', submission.code)



class OptionsView(generic.FormView):
    template_name = 'iCing/options.html'
    form_class = RunSetupForm


    # def __init__(self, *args, **kwargs):
    #     super(OptionsView, self).__init__(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)

        # submission = Submission.objects.get(code=self.kwargs['submission_code'])
        context['ranges'] = ''
        context['ensemble'] = ''

        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(OptionsView, self).get_context_data(**kwargs)
        submission = Submission.objects.get(code=self.kwargs['submission_code'])
        context['cing_version'] = cing_version
        context['cing_update'] = cing_update
        context['submission_code'] = submission.code
        context['submission_type'] = submission.submission_type
        return context


    def form_valid(self, form):
        submission = Submission.objects.get(code=self.kwargs['submission_code'])
        submission.ranges = form.cleaned_data['ranges']
        submission.ensemble = form.cleaned_data['ensemble']
        submission.verbosity = form.cleaned_data['verbosity']
        submission.save()

        submission.date = timezone.now()
        submission.save()

        startCingRun(submission.code)
        return redirect('run', submission.code)



def run(request, submission_code):
    cc = CingCommand(submission_code)

    if request.method == 'POST':
        if 'view' in request.POST:
            return redirect('view', submission_code)
    return render(request, 'iCing/run.html', {'submission_code': submission_code,
                                              'run_finished': run_finished(cc.getReportDirectory()),
                                              'cing_version': cing_version,
                                              'cing_update': cing_update
                                             })

def logTextView(request, submission_code):
    cc = CingCommand(submission_code)

    try:
        logDirFiles = os.listdir(cc.getLogPath())
        logFile = [f for f in logDirFiles if f.endswith('.txt')][0]
        with open(os.path.join(cc.getLogPath(), logFile)) as f:
            logText = f.read()
    except (OSError, IndexError):
        logText = 'iCING run starting, please wait,...'

    return HttpResponse(logText, content_type='text/plain')


def runFinishedView(request, submission_code):
    cc = CingCommand(submission_code)
    return HttpResponse(run_finished(cc.getReportDirectory()), content_type='text/plain')


def view(request, submission_code):
    submission = Submission.objects.get(code=submission_code)
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


def run_finished(directory):
    if os.path.isfile(os.path.join(directory, 'index.html')):
        return not os.path.exists(os.path.join(directory, 'Temp'))
    return False
