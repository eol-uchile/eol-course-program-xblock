# -*- coding: utf-8 -*-

from six import text_type

from django.db import models

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


class EolCourseProgram(models.Model):
    """
        Course Programs
    """
    program_name = models.CharField(max_length=80, blank=False)
    courses = models.ManyToManyField(
        CourseOverview, 
        related_name="courses"
    )
    final_course = models.ForeignKey(
        CourseOverview, 
        on_delete=models.CASCADE, 
        related_name="final_course", 
        blank=True,
        null=True
    )
    is_active = models.BooleanField(default=True)

    @property
    def courses_list_info(self):
        """
            Return list of courses info
        """
        return [
            {
                'course_id'     : text_type(c.id),
                'display_name'  : c.display_name_with_default.title()
            }
            for c in self.courses.all()
        ]
    @property
    def final_course_info(self):
        """
            Return final course info
        """
        if not self.final_course:
            return None
        return {
            'course_id'     : text_type(self.final_course.id),
            'display_name'  : self.final_course.display_name_with_default.title()
        }