# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 13:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='url',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='url',
        ),
        migrations.RemoveField(
            model_name='course',
            name='url',
        ),
        migrations.RemoveField(
            model_name='coursegroup',
            name='url',
        ),
    ]
