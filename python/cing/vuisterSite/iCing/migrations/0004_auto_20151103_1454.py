# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iCing', '0003_auto_20151009_0852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='ensemble',
            field=models.CharField(default='', max_length=255, verbose_name='CING ensemble specifier', blank=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='format',
            field=models.CharField(default='auto', max_length=5, verbose_name='Submission Type', choices=[('auto', 'Auto'), ('CCPN', 'CCPN'), ('CYANA', 'CYANA'), ('PDB', 'PDB')]),
        ),
        migrations.AlterField(
            model_name='submission',
            name='ranges',
            field=models.CharField(default='', max_length=255, verbose_name='CING residue specifier', blank=True),
        ),
    ]
