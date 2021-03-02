# -*- coding: utf-8 -*-

from six import text_type, iteritems

from django.db import models
from django.conf import settings

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

COURSE_MODE_SLUG_CHOICES = [(key, enrollment_mode['display_name'])
                            for key, enrollment_mode in iteritems(settings.COURSE_ENROLLMENT_MODES)]

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
    final_course_mode = models.CharField(
        max_length=100, 
        choices=COURSE_MODE_SLUG_CHOICES,
        help_text="Este valor se utiliza únicamente cuando el programa tiene definido un 'final course'. Si 'final course' está definido, y 'final course mode' está vacío, por defecto los estudiantes se inscribirán como 'honor'.",
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
                'display_name'  : c.display_name_with_default.capitalize()
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
            'display_name'  : self.final_course.display_name_with_default.capitalize()
        }