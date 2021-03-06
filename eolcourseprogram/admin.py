# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import EolCourseProgram

class EolCourseProgramSetupAdmin(admin.ModelAdmin):
    autocomplete_fields = ['courses', 'final_course']
    list_display = ('program_name', 'is_active')

admin.site.register(EolCourseProgram, EolCourseProgramSetupAdmin)