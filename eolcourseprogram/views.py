# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from student.models import CourseEnrollment
from openedx.features.course_experience import course_home_url_name
from django.urls import reverse
from django.shortcuts import redirect
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
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

def _get_course_info(user, course):
    """
        Return course info 
    """
    return {
        'course_id'     : course["course_id"],
        'display_name'  : course["display_name"],
        'passed'        : _get_course_grade_passed(user, course["course_id"]),
        'course_url'    : _get_course_url(course["course_id"])
    }

def _get_courses_list_with_status(user, list_info):
    """
        Return courses list, approved courses count and final_course_allowed
    """
    list = []
    approved_count = 0
    for c in list_info:
        course_info = _get_course_info( user, c ) # get info
        list.append( course_info ) # append to list
        approved_count += 1 if course_info["passed"] else 0 # increase counter if course is passed
    final_course_allowed = approved_count == len(list_info) # verify if 'courses passed' counter is equal to 'courses list' length
    return {
        "list" : list,
        "approved_count" : approved_count,
        "final_course_allowed" : final_course_allowed
    }

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
            'courses_list'  : cp.courses_list_info,
            'final_course'  : cp.final_course_info
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
        courses_list = _get_courses_list_with_status( request.user, program.courses_list_info )
        data = {
            'program_name'          : program.program_name.title(),
            'final_course'          : _get_course_info( request.user, program.final_course_info ) if program.final_course_info else None,
            'courses_list'          : courses_list["list"],
            'approved_count'        : courses_list["approved_count"],
            'final_course_allowed'  : courses_list["final_course_allowed"]
        }
    except EolCourseProgram.DoesNotExist:
        return HttpResponse(status=409)
    return JsonResponse(data, safe=False)

def enroll_and_redirect(request, program_id):
    """"
        Enroll and redirect FINAL COURSE
    """
    program = EolCourseProgram.objects.get(
        pk = program_id
    )
    final_course_id = program.final_course_info["course_id"] if program.final_course_info else None
    # get courses list with status => final_course_allowed required to enroll
    courses_list = _get_courses_list_with_status( request.user, program.courses_list_info )
    # check if final_course_id is valid
    try:
        course_key = CourseKey.from_string(final_course_id)
    except InvalidKeyError:
        raise Http404(u"Invalid course_key")

    if(not _has_access(request, final_course_id) and courses_list["final_course_allowed"]):
        # enroll as honor student
        CourseEnrollment.enroll(
            request.user,
            course_key,
            mode='honor'
        )
    return redirect(
        reverse(
            course_home_url_name(course_key), 
            kwargs={'course_id': final_course_id}
        )
    )
    