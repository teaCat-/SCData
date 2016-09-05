from __future__ import unicode_literals

from django.db import models

# Create your models here.

class tInvestor(models.Model):
    investor = models.TextField(max_length=50, default="")
    descr = models.TextField(max_length=500, default="")
    def __unicode__(self):
        return self.investor+" |"+str(self.id)
    class Meta:
        verbose_name = u'Investor'

class tAddInfoInv(models.Model):
    investorID = models.ForeignKey(tInvestor)
    text = models.TextField(max_length=50, default="")
    url = models.TextField(max_length=50, default="")
    file = models.FileField(upload_to='files/investors/', default="")
    def __unicode__(self):
        return self.url+" |"+str(self.id)
    class Meta:
        verbose_name = u'Investors additional info'

class tInvestorContacts(models.Model):
    investorID = models.ForeignKey(tInvestor)
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="")
    phone = models.TextField(max_length=15, default="")
    mail = models.TextField(max_length=50, default="")
    position = models.TextField(max_length=50, default="")
    company = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name = u'Investors contacts'

class tStartuper(models.Model):
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="")
    phone = models.TextField(max_length=15, default="")
    mail = models.TextField(max_length=50, default="")
    avatar = models.ImageField(upload_to='files/imgs/avatars/', default="")
    fgrade = models.BooleanField(default=False)
    sgrade = models.BooleanField(default=False)
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name = u'Startuper'

class tKeyWord(models.Model):
    word = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.word
    class Meta:
        verbose_name = u'Tags'

class tProject(models.Model):
    title = models.TextField(max_length=50, default="")
    sector = models.TextField(max_length=50, default="")
    descr = models.TextField(max_length=500, default="")
    type = models.TextField(max_length=50, default="")
    isreal = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Project'

class tKeyWordToProject(models.Model):
    projectID = models.ForeignKey(tProject)
    word = models.ForeignKey(tKeyWord)
    def __unicode__(self):
        return self.word.word+"-"+self.projectID.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Tags to Project'

class tStatus(models.Model):
    projectID = models.ForeignKey(tProject)
    date = models.DateTimeField()
    title = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Statuses'

class tAddInfoProj(models.Model):
    projectID = models.ForeignKey(tProject)
    text = models.TextField(max_length=50, default="")
    url = models.TextField(max_length=150, default="")
    file = models.FileField(upload_to='files/projects/', default="")
    def __unicode__(self):
        return self.text + " |" + str(self.id)
    class Meta:
        verbose_name = u'Projects additional info'

class tActivities(models.Model):
    title = models.TextField(max_length=50, default="")
    projectID = models.ForeignKey(tProject)
    date = models.DateField()
    def __unicode__(self):
        return self.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Events'

class tInvestition(models.Model):
    investorID = models.ForeignKey(tInvestor)
    projectID = models.ForeignKey(tProject)
    date = models.DateTimeField()
    type = models.TextField(max_length=50, default="")
    res = models.TextField(max_length=50, default="")
    sum = models.TextField(max_length=15, default="")
    descr = models.TextField(max_length=500, default="")
    def __unicode__(self):
        return unicode(self.date)+self.projectID.title+" |"+str(self.id)
    class Meta:
        verbose_name = u'Investitions'

class tTeam(models.Model):
    projectID = models.ForeignKey(tProject)
    startuperID = models.ForeignKey(tStartuper)
    role = models.TextField(max_length=50, default="")
    islead = models.BooleanField(default=False)
    def __unicode__(self):
        return unicode(self.startuperID.surname)+"/ "+self.projectID.title+" |"+unicode(self.id)
    class Meta:
        verbose_name = u'Startuper to Project'

class tDoc(models.Model):
    startuperID = models.ForeignKey(tStartuper)
    title = models.TextField(max_length=50, default="")
    date = models.DateField()
    url = models.TextField(max_length=50, default="")
    document = models.FileField(upload_to='files/docs/', default="")
    def __unicode__(self):
        return unicode(self.date)+"/ "+self.title+"/ "+self.startuperID.surname+" |"+str(self.id)
    class Meta:
        verbose_name = u'Startuper documents'

class tMentor(models.Model):
    name = models.TextField(max_length=50, default="")
    surname = models.TextField(max_length=50, default="")
    midname = models.TextField(max_length=50, default="")
    phone = models.TextField(max_length=15, default="")
    mail = models.TextField(max_length=50, default="")
    def __unicode__(self):
        return self.name+" "+self.surname+" "+self.midname+" |"+str(self.id)
    class Meta:
        verbose_name = u'Mentor'

class tMentoproj(models.Model):
    projectID = models.ForeignKey(tProject)
    mentorID = models.ForeignKey(tMentor)
    date = models.DateTimeField()
    def __unicode__(self):
        return self.projectID.title+" "+self.mentorID.surname+" "+self.mentorID.name+" |"+str(self.id)
    class Meta:
        verbose_name = u'Mentor to Project'

class tReqInvests(models.Model):
    projectID = models.ForeignKey(tProject)
    res = models.TextField(max_length=50, default="")
    sum = models.TextField(max_length=15, default="")
    type = models.TextField(max_length=50, default="")

