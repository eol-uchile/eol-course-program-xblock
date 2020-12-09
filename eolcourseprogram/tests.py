# -*- coding: utf-8 -*-


from mock import patch, Mock


from django.test import TestCase, Client

from util.testing import UrlResetMixin
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from xmodule.modulestore.tests.factories import CourseFactory
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from xblock.field_data import DictFieldData
from student.roles import CourseStaffRole
from .eolcourseprogram import EolCourseProgramXBlock

import logging
logger = logging.getLogger(__name__)

XBLOCK_RUNTIME_USER_ID = 99


class TestEolCourseProgramXBlock(UrlResetMixin, ModuleStoreTestCase):

    def make_an_xblock(self, **kw):
        """
        Helper method that creates a EolCourseProgram XBlock
        """
        course = self.course
        runtime = Mock(
            course_id=course.id,
            user_is_staff=True,
            service=Mock(
                return_value=Mock(_catalog={}),
            ),
            user_id=XBLOCK_RUNTIME_USER_ID,
        )
        scope_ids = Mock()
        field_data = DictFieldData(kw)
        xblock = EolCourseProgramXBlock(runtime, field_data, scope_ids)
        xblock.xmodule_runtime = runtime
        return xblock

    def setUp(self):

        super(TestEolCourseProgramXBlock, self).setUp()

        # create a course
        self.course = CourseFactory.create(org='mss', course='998',
                                           display_name='EolCourseProgram tests')

        # create Xblock
        self.xblock = self.make_an_xblock()
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('student.models.cc.User.save'):
            uname = 'student'
            email = 'student@edx.org'
            password = 'test'

            # Create and enroll student
            self.student = UserFactory(
                username=uname, password=password, email=email)
            CourseEnrollmentFactory(
                user=self.student, course_id=self.course.id)

            # Create and Enroll staff user
            self.staff_user = UserFactory(
                username='staff_user',
                password='test',
                email='staff@edx.org',
                is_staff=True)
            CourseEnrollmentFactory(
                user=self.staff_user,
                course_id=self.course.id)
            CourseStaffRole(self.course.id).add_users(self.staff_user)

            # Log the student in
            self.client = Client()
            self.assertTrue(
                self.client.login(
                    username=uname,
                    password=password))

            # Log the user staff in
            self.staff_client = Client()
            self.assertTrue(
                self.staff_client.login(
                    username='staff_user',
                    password='test'))

    def test_workbench_scenarios(self):
        """
            Checks workbench scenarios title and basic scenario
        """
        result_title = 'EolCourseProgramXBlock'
        basic_scenario = "<eolcourseprogram/>"
        test_result = self.xblock.workbench_scenarios()
        self.assertEqual(result_title, test_result[0][0])
        self.assertIn(basic_scenario, test_result[0][1])