# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iCing', '0005_auto_20151109_1110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submission',
            old_name='format',
            new_name='submission_type',
        ),
    ]
