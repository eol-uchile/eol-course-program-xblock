# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from openedx.features.course_experience import course_home_url_name
from django.urls import reverse
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

def _get_course_grade_passed(user, course_id):
    """
        Get 'passed' (Boolean representing whether the course has been
                passed according to the course's grading policy.)
    """
    course_key = CourseKey.from_string(course_id)
    course_grade = CourseGradeFactory().read(user, course_key=course_key)
    return course_grade.passed

def _get_course_url(course_id):
    """
        Return course home page url
    """
    course_key = CourseKey.from_string(course_id)
    return reverse(course_home_url_name(course_key), kwargs={'course_id': course_id})

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
            'courses_list'  : [
                {
                    'course_id'     : c["course_id"],
                    'display_name'  : c["display_name"],
                    'passed'        : _get_course_grade_passed(request.user, c["course_id"]),
                    'course_url'    : _get_course_url(c["course_id"])
                }
                for c in program.courses_list
            ]
        }
    except EolCourseProgram.DoesNotExist:
        return HttpResponse(status=409)
    return JsonResponse(data, safe=False)