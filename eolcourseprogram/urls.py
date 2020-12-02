from django.conf.urls import url
from django.conf import settings

from .views import get_course_programs

from django.contrib.auth.decorators import login_required

urlpatterns = (
    url(
        r'^eol_course_programs/{}/get_programs'.format(
            settings.COURSE_ID_PATTERN,
        ),
        login_required(get_course_programs),
        name='get_course_programs',
    ),
)