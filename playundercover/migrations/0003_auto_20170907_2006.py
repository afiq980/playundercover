# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-07 12:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playundercover', '0002_auto_20170827_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pair',
            name='word1',
            field=models.CharField(max_length=40),
        ),
        migrations.AlterField(
            model_name='pair',
            name='word2',
            field=models.CharField(max_length=40),
        ),
    ]
