# -*- coding: utf-8 -*-
# Python Standard Libraries
import json
import traceback
import logging

# Installed packages (via pip)
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.models import User

# Edx dependencies
from common.djangoapps.course_modes.models import CourseMode
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.access import has_access
from lms.djangoapps.courseware.courses import get_course_with_access
from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from openedx.features.course_experience import course_home_url_name

# Internal project dependencies
from .models import EolCourseProgram


logger = logging.getLogger(__name__)

def _has_access(request, course_id):
    try:
        course_key = CourseKey.from_string(course_id)
        course = get_course_with_access(request.user, "load", course_key)
        return User.objects.filter(
            courseenrollment__course_id=course_key,
            courseenrollment__is_active=1,
            pk = request.user.id
        ).exists() or bool(has_access(request.user, 'staff', course))
    except Exception:
        return False

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
        Return course about page url
    """
    return reverse('about_course', args=[course_id])

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

    try:
        course_programs_list = [
            {
                'program_id'    : cp.pk,
                'program_name'  : cp.program_name.capitalize(),
                'courses_list'  : cp.courses_list_info,
                'courses_modes': {
                    course["course_id"]: list(
                        CourseMode.modes_for_course_dict(course_id=CourseKey.from_string(course["course_id"])).keys()
                    ) for course in cp.courses_list_info
                },
                'final_course'  : cp.final_course_info
            } for cp in course_programs
        ]
        return JsonResponse(course_programs_list, safe=False)
    except Exception as e:
        logger.error("Error in get_course_programs: %s", traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)

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
            'program_name'          : program.program_name.capitalize(),
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
        final_course_mode = program.final_course_mode if program.final_course_mode is not None else 'honor'
        CourseEnrollment.enroll(
            request.user,
            course_key,
            mode = final_course_mode # honor by default
        )
    return redirect(
        reverse(
            course_home_url_name(course_key),
            kwargs={'course_id': final_course_id}
        )
    )

def enroll_student(request, program_id, course_id):
    """"
        Enroll a user in a course of the program
    """
    # check if course_id is valid
    try:
        course_key = CourseKey.from_string(course_id)
    except InvalidKeyError:
        return HttpResponse(status=400,content=u"Invalid course_key")

    course_mode = json.loads(request.body).get('mode')
    if (course_mode != 'Do not enroll') and (course_mode != None):
        enrollment = CourseEnrollment.get_or_create_enrollment(request.user,course_key)
        new_enrollment = not enrollment.is_active
        enrollment.activate()
        enrollment.change_mode(course_mode)
        if new_enrollment:
            program = EolCourseProgram.objects.get(pk = program_id)
            logger.info("User %s enrolled in %s course through eol_course_program %s (id: %s)", request.user, course_id, program.program_name, program_id)

    return JsonResponse({"course_id":course_id})
