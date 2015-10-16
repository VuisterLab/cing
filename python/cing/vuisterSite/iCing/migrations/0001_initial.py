# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('username', models.CharField(default='Anonymous', max_length=255, verbose_name='Username')),
                ('code', models.CharField(max_length=6, serialize=False, verbose_name='Submission Code', primary_key=True)),
                ('date', models.DateTimeField(null=True, verbose_name='Submission Date')),
                ('ip', models.GenericIPAddressField(verbose_name='Submission IP')),
                ('name', models.CharField(max_length=255, verbose_name='Project Name')),
                ('filename', models.CharField(max_length=6, verbose_name='Filename')),
                ('format', models.CharField(max_length=5, verbose_name='Submission Type', choices=[('auto', 'Auto'), ('CCPN', 'CCPN'), ('CYANA', 'CYANA'), ('PDB', 'PDB')])),
                ('ranges', models.CharField(max_length=255, verbose_name='CING residue specifier')),
                ('ensemble', models.CharField(max_length=255, verbose_name='CING ensemble specifier')),
                ('verbosity', models.IntegerField(default=3, verbose_name='Username', choices=[('0', 'Nothing'), ('1', 'Error'), ('2', 'Warning'), ('3', 'Output'), ('4', 'Detail'), ('9', 'Debug')])),
            ],
        ),
    ]
