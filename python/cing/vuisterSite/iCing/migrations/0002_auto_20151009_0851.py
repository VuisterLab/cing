# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iCing', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='ensemble',
            field=models.CharField(default='', max_length=255, verbose_name='CING ensemble specifier'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='ranges',
            field=models.CharField(default='', max_length=255, verbose_name='CING residue specifier'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='verbosity',
            field=models.IntegerField(default=3, verbose_name='Verbosity', choices=[(0, 'Nothing'), (1, 'Error'), (2, 'Warning'), (3, 'Output'), (4, 'Detail'), (9, 'Debug')]),
        ),
    ]
