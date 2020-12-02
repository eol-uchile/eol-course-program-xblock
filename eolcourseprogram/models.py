# -*- coding: utf-8 -*-

from six import text_type

from django.db import models

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class EolCourseProgram(models.Model):
    """
        Course Programs
    """
    program_name = models.CharField(max_length=80, blank=False)
    courses = models.ManyToManyField(CourseOverview)
    is_active = models.BooleanField(default=True)

    @property
    def courses_list(self):
        """
            Return list of courses display name
        """
        return [
            {
                'course_id'     : text_type(c.id),
                'display_name'  : c.display_name_with_default
            }
            for c in self.courses.all()
        ]