# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse

from .models import EolCourseProgram

import logging
logger = logging.getLogger(__name__)

def get_course_programs(request, course_id):
    """
        GET REQUEST
        Get course programs that contains course_id 
    """
    # check method
    if request.method != "GET":
        return HttpResponse(status=400)
    user = request.user

    course_programs = EolCourseProgram.objects.filter(
        courses__id__in=[course_id],
        is_active = True
    )

    course_programs_list = [
        {
            'program_id'    : cp.pk,
            'program_name'  : cp.program_name,
            'courses_list'  : cp.courses_list
        }
        for cp in course_programs
    ]
    data = course_programs_list
    return JsonResponse(data, safe=False)