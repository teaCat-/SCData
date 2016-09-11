"""SCData URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^search', views.search, name='search'),
    url(r'^startupersearch', views.startupersearch, name='startupersearch'),
    url(r'^projectsearch', views.projectsearch, name='projectsearch'),
    url(r'^investorsearch', views.investorsearch, name='investorsearch'),
    url(r'^mentorsearch', views.mentorsearch, name='mentorsearch'),
    url(r'^infostartuper', views.infostartuper, name='infostartuper'),
    url(r'^infoproject', views.infoproject, name='infoproject'),
    url(r'^infoinvestor', views.infoinvestor, name='infoinvestor'),
    url(r'^infoinvcontact', views.infoinvcontact, name='infoinvcontact'),
    url(r'^infomentor', views.infomentor, name='infomentor'),
    url(r'^startuperstoproject', views.startuperstoproject, name='startuperstoproject'),
    url(r'^mentorstoproject', views.mentorstoproject, name='mentorstoproject'),
    url(r'^invcontactsadd', views.invcontactsadd, name='invcontactsadd'),
    url(r'^investitions', views.investitions, name='investitions'),
    url(r'^editstartuper', views.editstartuper, name='editstartuper'),
    url(r'^editproject', views.editproject, name='editproject'),
    url(r'^editinvestor', views.editinvestor, name='editinvestor'),
    url(r'^editinvcontact', views.editinvcontact, name='editinvcontact'),
    url(r'^editmentor', views.editmentor, name='editmentor'),
    url(r'^add', views.add, name='add'),
    url(r'^tagadd', views.tagadd, name='tagadd'),
    url(r'^fileadd', views.addfile, name='addfile'),
    url(r'^signadd', views.signadd, name='signadd'),
    url(r'^auth', views.auth, name='auth'),
    url(r'^regi', views.regi, name='regi'),
    url(r'^logout', views.logout, name='logout'),
]
