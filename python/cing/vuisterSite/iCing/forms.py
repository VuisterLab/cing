from __future__ import unicode_literals, print_function, absolute_import, division

from django import forms
from .models import Submission

class UploadFileForm(forms.ModelForm):
    user_file = forms.FileField()

    class Meta:
        model = Submission
        fields = ['submission_type']


class RunSetupForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['ranges',
                  'ensemble',
                  'verbosity']


class CcpnSubmissionForm(forms.Form):
    Action = forms.ChoiceField(choices=(('Save', 'Save'),
                                        ('ProjectName', 'ProjectName'),
                                        ('Run', 'Run'),
                                        ('Status', 'Status'),
                                       )
                               )
    AccessKey = forms.CharField(max_length=6, min_length=6, required=True)
    UserId = forms.CharField(max_length=255, required=True)