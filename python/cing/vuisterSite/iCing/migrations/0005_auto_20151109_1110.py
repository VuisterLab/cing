# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iCing', '0004_auto_20151103_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='username',
            field=models.CharField(default='anonymous', max_length=255, verbose_name='Username'),
        ),
    ]
