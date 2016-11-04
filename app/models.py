# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class tSchool(models.Model):
    city = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.city+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Школи'


class tUserSch(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    def __unicode__(self):
        return self.user.username
    class Meta:
        verbose_name = u'Школа'
        verbose_name_plural = u'Школа'

class tInvestor(models.Model):
    investor = models.TextField(max_length=50, default="")
    descr = models.TextField(max_length=500, default="", blank=True, null=True)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    message = models.TextField(max_length=500, default="", blank=True, null=True)
    def clean(self):
        if self.user is not None:
            try:
                u = tUserSch.objects.get(user = self.user)
                if u.school != None:
                    self.school = u.school
            except:
                pass

    def __unicode__(self):
        return self.investor+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Інвестори'

class tVisitors(models.Model):
    investorID = models.ForeignKey(tInvestor)
    date = models.DateTimeField(blank=True, null=True)
    userID = models.ForeignKey(User)
    def __unicode__(self):
        return self.investorID.investor+", "+self.date.strftime("%d.%m.%y, %H:%M")
    class Meta:
        verbose_name_plural = u'Відвідувачі сторінок з інвесторами'

class tAddInfoInv(models.Model):
    investorID = models.ForeignKey(tInvestor)
    text = models.TextField(max_length=50, default="", blank=True, null=True)
    url = models.TextField(max_length=50, default="", blank=True, null=True)
    file = models.FileField(upload_to='files/investors/', default="", blank=True, null=True)
    def __unicode__(self):
        return self.url+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Додаткова інформація по інвесторам'

class tInvestorContacts(models.Model):
    investorID = models.ForeignKey(tInvestor)
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="", blank=True, null=True)
    phone = models.TextField(max_length=15, default="", blank=True, null=True)
    mail = models.TextField(max_length=50, default="", blank=True, null=True)
    position = models.TextField(max_length=50, default="", blank=True, null=True)
    company = models.TextField(max_length=50, default="", blank=True, null=True)
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Контакти інвесторів'

class tStartuper(models.Model):
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="", blank=True, null=True)
    phone = models.TextField(max_length=15, default="", blank=True, null=True)
    mail = models.TextField(max_length=50, default="", blank=True, null=True)
    avatar = models.ImageField(upload_to='files/imgs/avatars/', default="", blank=True, null=True)
    fgrade = models.BooleanField(default=False, blank=True)
    sgrade = models.BooleanField(default=False, blank=True)
    finyear = models.TextField(max_length=5, default="-", blank=True, null=True)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Стартапери'

class tKeyWord(models.Model):
    word = models.TextField(max_length=50, default="", blank=True, null=True)
    def __unicode__(self):
        return self.word
    class Meta:
        verbose_name_plural = u'Теги'

class tProject(models.Model):
    title = models.TextField(max_length=50, default="")
    sector = models.TextField(max_length=50, default="", blank=True, null=True)
    descr = models.TextField(max_length=500, default="", blank=True, null=True)
    type = models.TextField(max_length=50, default="", blank=True, null=True)
    isreal = models.TextField(max_length=50, default="", blank=True, null=True)
    financeScale = models.TextField(max_length=50, default="", blank=True, null=True)
    isactive = models.BooleanField(default=True, blank=True)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Проекти'

class tKeyWordToProject(models.Model):
    projectID = models.ForeignKey(tProject)
    word = models.ForeignKey(tKeyWord)
    def __unicode__(self):
        return self.word.word+"-"+self.projectID.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Міст Теги-Проекти'

class tStatus(models.Model):
    projectID = models.ForeignKey(tProject)
    date = models.DateTimeField(blank=True, null=True)
    title = models.TextField(max_length=50, default="", blank=True, null=True)
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Статуси'

class tAddInfoProj(models.Model):
    projectID = models.ForeignKey(tProject)
    text = models.TextField(max_length=50, default="", blank=True, null=True)
    url = models.TextField(max_length=150, default="", blank=True, null=True)
    file = models.FileField(upload_to='files/projects/', default="", blank=True, null=True)
    def __unicode__(self):
        return self.text + " |" + str(self.id)
    class Meta:
        verbose_name_plural = u'Додаткова інформація по проектам'

class tActivities(models.Model):
    title = models.TextField(max_length=50, default="")
    date = models.DateField(blank=True, null=True)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Заходи'

class tActProj(models.Model):
    projectID = models.ForeignKey(tProject)
    eventID = models.ForeignKey(tActivities)
    def __unicode__(self):
        return self.projectID.title+" - "+self.eventID.title+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Міст Заходи-Проекти'

class tInvestition(models.Model):
    investorID = models.ForeignKey(tInvestor)
    projectID = models.ForeignKey(tProject)
    date = models.DateTimeField(blank=True, null=True)
    type = models.TextField(max_length=50, default="", blank=True, null=True)
    res = models.TextField(max_length=50, default="", blank=True, null=True)
    sum = models.TextField(max_length=15, default="", blank=True, null=True)
    descr = models.TextField(max_length=500, default="", blank=True, null=True)
    def __unicode__(self):
        return unicode(self.date)+self.projectID.title+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Інвестиції'

class tTeam(models.Model):
    projectID = models.ForeignKey(tProject)
    startuperID = models.ForeignKey(tStartuper)
    role = models.TextField(max_length=50, default="", blank=True, null=True)
    islead = models.BooleanField(default=False, blank=True)
    def __unicode__(self):
        return unicode(self.startuperID.surname)+"/ "+self.projectID.title+" |"+unicode(self.id)
    class Meta:
        verbose_name_plural = u'Міст Стартапери-Проекти'

class tDoc(models.Model):
    startuperID = models.ForeignKey(tStartuper)
    title = models.TextField(max_length=50, default="")
    date = models.DateField(blank=True, null=True)
    url = models.TextField(max_length=50, default="", blank=True, null=True)
    document = models.FileField(upload_to='files/docs/', default="", blank=True, null=True)
    def __unicode__(self):
        return unicode(self.date)+"/ "+self.title+"/ "+self.startuperID.surname+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Додаткова інформація по стартаперам'

class tMentor(models.Model):
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="", blank=True, null=True)
    phone = models.TextField(max_length=15, default="", blank=True, null=True)
    mail = models.TextField(max_length=50, default="", blank=True, null=True)
    school = models.ForeignKey(tSchool, on_delete=models.SET_NULL, default=None, blank=True, null=True)
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Ментори'

class tMentoproj(models.Model):
    projectID = models.ForeignKey(tProject)
    mentorID = models.ForeignKey(tMentor)
    date = models.DateTimeField(blank=True, null=True)
    def __unicode__(self):
        return self.projectID.title+" "+self.mentorID.surname+" "+self.mentorID.name+" |"+str(self.id)
    class Meta:
        verbose_name_plural = u'Міст Ментори-Проекти'


