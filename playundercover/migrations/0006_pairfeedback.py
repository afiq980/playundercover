# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-12 07:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('playundercover', '0005_auto_20170909_2023'),
    ]

    operations = [
        migrations.CreateModel(
            name='PairFeedback',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('feedback', models.BooleanField()),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='playundercover.Pair')),
            ],
        ),
    ]
