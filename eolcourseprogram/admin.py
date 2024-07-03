# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import EolCourseProgram
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from django.db.models import Subquery, OuterRef

class EolCourseProgramSetupAdmin(admin.ModelAdmin):
    autocomplete_fields = ['courses', 'final_course']
    list_display = ('program_name', 'is_active')

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'courses' and request.resolver_match.kwargs.get('object_id'):
            program_id = request.resolver_match.kwargs.get('object_id')
            subquery = EolCourseProgram.courses.through.objects.filter(
                eolcourseprogram_id=program_id,
                courseoverview_id=OuterRef('pk')
            ).values('id')
            kwargs['queryset'] = CourseOverview.objects.annotate(
                intermediary_id=Subquery(subquery)
            ).order_by('intermediary_id')
        return super().formfield_for_manytomany(db_field, request, **kwargs)
admin.site.register(EolCourseProgram, EolCourseProgramSetupAdmin)
