# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.forms.models import BaseInlineFormSet

# Register your models here.
from models import *

admin.site.register(tInvestor)
admin.site.register(tInvestorContacts)
admin.site.register(tProject)
admin.site.register(tStatus)
admin.site.register(tActivities)
admin.site.register(tStartuper)
admin.site.register(tMentor)
admin.site.register(tSchool)

class RequiredInlineFormSet(BaseInlineFormSet):
    """
    Generates an inline formset that is required
    """

    def _construct_form(self, i, **kwargs):
        """
        Override the method to change the form attribute empty_permitted
        """
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserInline(admin.StackedInline):
    model = tUserSch
    can_delete = False
    verbose_name_plural = u'Школа'
    formset = RequiredInlineFormSet

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserInline,)


class MyUserAdmin(UserAdmin):
    list_display = (
    "username", "first_name", "last_name", "email", "is_active", "is_staff", "last_login", "date_joined")

    ## Static overriding
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Персональна інформація'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("user_permissions")
        ## Dynamically overriding
        self.fieldsets[2][1]["fields"] = ('is_active', 'is_staff', 'is_superuser', 'groups')
        form = super(MyUserAdmin, self).get_form(request, obj, **kwargs)
        return form


class MyGroupAdmin(GroupAdmin):
    fieldsets = ((None, {'fields': ('name', )}),)

    def get_form(self, request, obj=None, **kwargs):
        # Get form from original GroupAdmin.
        self.exclude = ("permissions")
        form = super(MyGroupAdmin, self).get_form(request, obj, **kwargs)
        return form

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)