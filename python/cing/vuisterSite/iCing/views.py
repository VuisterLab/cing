from __future__ import unicode_literals, print_function, absolute_import, division

import os
import logging

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import generic
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import UploadFileForm, RunSetupForm, CcpnSubmissionForm
from .webUtils import handleUploadedFile, determineSubmissionType, startCingRun
from .ccpnUtils import processCcpnPost
from .models import Submission

logger = logging.getLogger(__name__)


class UploadView(generic.FormView):
    template_name = 'iCing/upload.html'
    form_class = UploadFileForm


    def form_valid(self, form):
        submission = Submission(code = handleUploadedFile(self.request))

        determinedSubmissionType = determineSubmissionType(submission.code)
        submission.filename = self.request.FILES['user_file'].name
        submission.name = submission.filename.split('.')[0]
        submission.ip = self.request.META['REMOTE_ADDR']
        requestedSubmissionType = self.request.POST['format']
        if requestedSubmissionType != u'auto':
            if determinedSubmissionType != 'unknown':
                assert requestedSubmissionType == determinedSubmissionType
            submission.format = requestedSubmissionType

        else:
            submission.format = determinedSubmissionType

        submission.save()
        return redirect('options', submission.code)



class OptionsView(generic.FormView):
    template_name = 'iCing/options.html'
    form_class = RunSetupForm


    def __init__(self, *args, **kwargs):
        super(OptionsView, self).__init__(*args, **kwargs)


    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)

        submission = Submission.objects.get(code=self.kwargs['submission_code'])
        context['ranges'] = ''
        context['ensemble'] = ''

        return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(OptionsView, self).get_context_data(**kwargs)
        submission = Submission.objects.get(code=self.kwargs['submission_code'])
        context['submission_code'] = submission.code
        context['submission_type'] = submission.format
        return context


    def form_valid(self, form):
        submission = Submission.objects.get(code=self.kwargs['submission_code'])
        submission.ranges = form.cleaned_data['ranges']
        submission.ensemble = form.cleaned_data['ensemble']
        submission.verbosity = form.cleaned_data['verbosity']
        submission.save()

        submission.date = timezone.now()
        submission.save()

        startCingRun(submission)
        return redirect('run', submission.code)



def run(request, submission_code):
    cing_log = str(os.environ)
    if request.method == 'POST':
        if 'report' in request.POST:
            return redirect('report', submission_code)
    return render(request, 'iCing/run.html', {'cing_log':cing_log,
                                               'submission_code': submission_code,
                                               'run_finished': True
                                              })

def report(request, submission_code):
    pass

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



