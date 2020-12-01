# -*- coding: utf-8 -*-

import json

from django.http import HttpResponse, JsonResponse

import logging
logger = logging.getLogger(__name__)

EXAMPLE_COURSE_PROGRAMS = [
    {
        "program_name"  : "PROGRAM NAME 1",
        "courses"       : [
            "Course Name 1",
            "Course Name 2",
            "COurse Name 3"
        ]
    },
    {
        "program_name"  : "PROGRAM NAME 2",
        "courses"       : [
            "Course Name 4",
            "Course Name 5",
            "COurse Name 2"
        ]
    },
    {
        "program_name"  : "PROGRAM NAME 3",
        "courses"       : [
            "Course Name 1",
            "Course Name 4",
            "COurse Name 6"
        ]
    }
]

def get_course_programs(request):
    """
        GET REQUEST
        Get all course programs
    """
    # check method
    if request.method != "GET":
        return HttpResponse(status=400)
    user = request.user
    logger.warning("{} get_course_programs".format(user.username))
    return JsonResponse(EXAMPLE_COURSE_PROGRAMS, safe=False)