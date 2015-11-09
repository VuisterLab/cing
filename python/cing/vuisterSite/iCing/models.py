from __future__ import unicode_literals, print_function, absolute_import, division

from django.db import models

import datetime
from django.utils import timezone

class Submission(models.Model):
    username = models.CharField(verbose_name='Username',
                                max_length=255, default='anonymous')

    code = models.CharField(verbose_name='Submission Code',
                            max_length=6, primary_key=True)

    date = models.DateTimeField(verbose_name='Submission Date',
                                null=True)

    ip = models.GenericIPAddressField(verbose_name='Submission IP')

    name = models.CharField(verbose_name='Project Name',
                            max_length=255, null=False)

    filename = models.CharField(verbose_name='Filename',
                                max_length=6, null=False)

    submission_type = models.CharField(verbose_name='Submission Type',
                                       max_length=5,
                                       choices=(('auto','Auto'),
                                                ('CCPN', 'CCPN'),
                                                # ('nef', 'NEF'),
                                                # ('cing', 'CING'),
                                                ('CYANA', 'CYANA'),
                                                ('PDB', 'PDB')),
                                       default='auto',
                                       null=False)

    ranges = models.CharField(verbose_name='CING residue specifier',
                              max_length=255, default='', blank=True)

    ensemble = models.CharField(verbose_name='CING ensemble specifier',
                                max_length=255, default='', blank=True)

    verbosity = models.IntegerField(verbose_name='Verbosity',
                                    choices=((0, 'Nothing'),
                                             (1, 'Error'),
                                             (2, 'Warning'),
                                             (3, 'Output'),
                                             (4, 'Detail'),
                                             (9, 'Debug')),
                                    default = 3,
                                    null=False)

    def __str__(self):
       return str((self.code, self.filename, self.format))

    def was_submitted_recently(self):
       now = timezone.now()
       return now - datetime.timedelta(days=90) <= self.submission_date <= now
