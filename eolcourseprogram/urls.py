from django.conf.urls import url
from django.conf import settings

from .views import get_course_programs, get_program_info, enroll_and_redirect, enroll_student

from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(
        r'^eol_course_programs/{}/get_programs'.format(
            settings.COURSE_ID_PATTERN,
        ),
        login_required(get_course_programs),
        name='get_course_programs',
    ),
    url(
        r'^eol_course_programs/{}/get_program_info/(?P<program_id>.*)'.format(
            settings.COURSE_ID_PATTERN,
        ),
        login_required(get_program_info),
        name='get_program_info',
    ),
    url(
        r'^eol_course_programs/enroll_and_redirect/(?P<program_id>.*)',
        login_required(enroll_and_redirect),
        name='enroll_and_redirect',
    ),
    url(
        r'^eol_course_programs/enroll_student/(?P<course_id>.*)',
        login_required(enroll_student),
        name='enroll_student',
    ),
)
