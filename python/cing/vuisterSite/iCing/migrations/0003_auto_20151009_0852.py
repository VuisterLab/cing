# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iCing', '0002_auto_20151009_0851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='ensemble',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='CING ensemble specifier'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='ranges',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='CING residue specifier'),
        ),
    ]
