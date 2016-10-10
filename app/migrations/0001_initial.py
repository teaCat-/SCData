# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-28 12:03
from __future__ import unicode_literals

import app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='tActivities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(default='', max_length=50)),
                ('date', models.DateField()),
            ],
            options={
                'verbose_name': 'Events',
            },
        ),
        migrations.CreateModel(
            name='tAddInfoInv',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', max_length=50)),
                ('url', models.TextField(default='', max_length=50)),
                ('file', models.FileField(default='', upload_to='files/investors/')),
            ],
            options={
                'verbose_name': 'Investors additional info',
            },
        ),
        migrations.CreateModel(
            name='tAddInfoProj',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', max_length=50)),
                ('url', models.TextField(default='', max_length=150)),
                ('file', models.FileField(default='', upload_to='files/projects/')),
            ],
            options={
                'verbose_name': 'Projects additional info',
            },
        ),
        migrations.CreateModel(
            name='tDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(default='', max_length=50)),
                ('date', models.DateField()),
                ('url', models.TextField(default='', max_length=50)),
                ('document', models.FileField(default='', upload_to='files/docs/')),
            ],
            options={
                'verbose_name': 'Startuper documents',
            },
        ),
        migrations.CreateModel(
            name='tInvestition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('type', models.TextField(default='', max_length=50)),
                ('res', models.TextField(default='', max_length=50)),
                ('sum', models.TextField(default='', max_length=15)),
                ('descr', models.TextField(default='', max_length=500)),
            ],
            options={
                'verbose_name': 'Investitions',
            },
        ),
        migrations.CreateModel(
            name='tInvestor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investor', models.TextField(default='', max_length=50)),
                ('descr', models.TextField(default='', max_length=500)),
            ],
            options={
                'verbose_name': 'Investor',
            },
        ),
        migrations.CreateModel(
            name='tInvestorContacts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='', max_length=50)),
                ('surname', models.TextField(default='', max_length=50)),
                ('midname', models.TextField(default='', max_length=50)),
                ('phone', models.TextField(default='', max_length=15)),
                ('mail', models.TextField(default='', max_length=50)),
                ('position', models.TextField(default='', max_length=50)),
                ('company', models.TextField(default='', max_length=50)),
                ('investorID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tInvestor')),
            ],
            options={
                'verbose_name': 'Investors contacts',
            },
        ),
        migrations.CreateModel(
            name='tKeyWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.TextField(default='', max_length=50)),
            ],
            options={
                'verbose_name': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='tKeyWordToProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Tags to Project',
            },
        ),
        migrations.CreateModel(
            name='tMentoproj',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Mentor to Project',
            },
        ),
        migrations.CreateModel(
            name='tMentor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='', max_length=50)),
                ('surname', models.TextField(default='', max_length=50)),
                ('midname', models.TextField(default='', max_length=50)),
                ('phone', models.TextField(default='', max_length=15)),
                ('mail', models.TextField(default='', max_length=50)),
            ],
            options={
                'verbose_name': 'Mentor',
            },
        ),
        migrations.CreateModel(
            name='tProject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(default='', max_length=50)),
                ('sector', models.TextField(default='', max_length=50)),
                ('descr', models.TextField(default='', max_length=500)),
                ('type', models.TextField(default='', max_length=50)),
                ('isreal', models.TextField(default='', max_length=50)),
                ('financeScale', models.TextField(default='', max_length=50)),
                ('isactive', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Project',
            },
        ),
        migrations.CreateModel(
            name='tSchool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.TextField(default='', max_length=50)),
            ],
            options={
                'verbose_name': '\u0428\u043a\u043e\u043b\u0438',
            },
        ),
        migrations.CreateModel(
            name='tStartuper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='', max_length=50)),
                ('surname', models.TextField(default='', max_length=50)),
                ('midname', models.TextField(default='', max_length=50)),
                ('phone', models.TextField(default='', max_length=15)),
                ('mail', models.TextField(default='', max_length=50)),
                ('avatar', models.ImageField(default='', upload_to='files/imgs/avatars/')),
                ('fgrade', models.BooleanField(default=False)),
                ('sgrade', models.BooleanField(default=False)),
                ('finyear', models.TextField(default='-', max_length=5)),
                ('school', models.ForeignKey(default=None, on_delete=models.SET(app.models.getDefSchool), to='app.tSchool')),
            ],
            options={
                'verbose_name': 'Startuper',
            },
        ),
        migrations.CreateModel(
            name='tStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('title', models.TextField(default='', max_length=50)),
                ('projectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject')),
            ],
            options={
                'verbose_name': 'Statuses',
            },
        ),
        migrations.CreateModel(
            name='tTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.TextField(default='', max_length=50)),
                ('islead', models.BooleanField(default=False)),
                ('projectID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject')),
                ('startuperID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tStartuper')),
            ],
            options={
                'verbose_name': 'Startuper to Project',
            },
        ),
        migrations.CreateModel(
            name='tUserSch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(default=None, on_delete=models.SET(app.models.getDefSchool), to='app.tSchool')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '\u041a\u043e\u0440\u0438\u0447\u0442\u0443\u0432\u0430\u0447\u0456',
            },
        ),
        migrations.AddField(
            model_name='tproject',
            name='school',
            field=models.ForeignKey(default=None, on_delete=models.SET(app.models.getDefSchool), to='app.tSchool'),
        ),
        migrations.AddField(
            model_name='tmentor',
            name='school',
            field=models.ForeignKey(default=None, on_delete=models.SET(app.models.getDefSchool), to='app.tSchool'),
        ),
        migrations.AddField(
            model_name='tmentoproj',
            name='mentorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tMentor'),
        ),
        migrations.AddField(
            model_name='tmentoproj',
            name='projectID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject'),
        ),
        migrations.AddField(
            model_name='tkeywordtoproject',
            name='projectID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject'),
        ),
        migrations.AddField(
            model_name='tkeywordtoproject',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tKeyWord'),
        ),
        migrations.AddField(
            model_name='tinvestor',
            name='school',
            field=models.ForeignKey(default=None, on_delete=models.SET(app.models.getDefSchool), to='app.tSchool'),
        ),
        migrations.AddField(
            model_name='tinvestition',
            name='investorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tInvestor'),
        ),
        migrations.AddField(
            model_name='tinvestition',
            name='projectID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject'),
        ),
        migrations.AddField(
            model_name='tdoc',
            name='startuperID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tStartuper'),
        ),
        migrations.AddField(
            model_name='taddinfoproj',
            name='projectID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject'),
        ),
        migrations.AddField(
            model_name='taddinfoinv',
            name='investorID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tInvestor'),
        ),
        migrations.AddField(
            model_name='tactivities',
            name='projectID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.tProject'),
        ),
    ]
