# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse

from opaque_keys.edx.keys import CourseKey
from django.contrib.auth.models import User
from .models import EolCourseProgram

import logging
logger = logging.getLogger(__name__)

def _has_access(request, course_id):
    course_key = CourseKey.from_string(course_id)
    return User.objects.filter(
        courseenrollment__course_id=course_key,
        courseenrollment__is_active=1,
        pk = request.user.id
    ).exists()

def get_course_programs(request, course_id):
    """
        GET REQUEST
        Get course programs that contains course_id 
    """
    # check method and access
    if request.method != "GET" or not _has_access(request, course_id):
        return HttpResponse(status=400)
    user = request.user

    course_programs = EolCourseProgram.objects.filter(
        courses__id__in=[course_id],
        is_active = True
    )

    course_programs_list = [
        {
            'program_id'    : cp.pk,
            'program_name'  : cp.program_name.title(),
            'courses_list'  : cp.courses_list
        }
        for cp in course_programs
    ]
    data = course_programs_list
    return JsonResponse(data, safe=False)

def get_program_info(request, course_id, program_id):
    """
        GET REQUEST
        Get program info (active or not)
    """
    # check method and access
    if request.method != "GET" or not _has_access(request, course_id):
        return HttpResponse(status=400)
    try:
        program = EolCourseProgram.objects.get(
            pk = program_id
        )
        data = {
            'program_name'  : program.program_name.title(),
            'courses_list'  : program.courses_list
        }
    except EolCourseProgram.DoesNotExist:
        return HttpResponse(status=409)
    return JsonResponse(data, safe=False)