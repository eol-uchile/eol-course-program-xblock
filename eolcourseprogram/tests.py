# -*- coding: utf-8 -*-

import json
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

class TestRequest(object):
    # pylint: disable=too-few-public-methods
    """
    Module helper for @json_handler
    """
    method = None
    body = None
    success = None
    params = None
    headers = None

class TestEolCourseProgramXBlock(UrlResetMixin, ModuleStoreTestCase):
    """
        XBlock tests
    """

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
        xblock.course_id = course.id
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

    def test_validate_default_field_data(self):
        """
            Validate that xblock is created successfully
        """
        self.assertEqual(self.xblock.display_name, 'Programa de Cursos')
        self.assertEqual(self.xblock.program_id, None)

    def test_student_view_without_configuration(self):
        """
            Check if error message is triggered when is not configured
        """
        student_view = self.xblock.student_view()
        student_view_html = student_view.content
        self.assertIn('El componente aún no se ha configurado.', student_view_html)
        self.assertNotIn('class="eolcourseprogram_block"', student_view_html)

    def test_student_view_with_configuration(self):
        """
            Check if error message is not triggered when is successfully configured
        """
        self.xblock.program_id = 5
        student_view = self.xblock.student_view()
        student_view_html = student_view.content
        self.assertNotIn('El componente aún no se ha configurado.', student_view_html)
        self.assertIn('class="eolcourseprogram_block"', student_view_html)

    def test_author_view(self):
        """
            Test author view:
            1. Without Configurations
            2. With Configurations
        """
        author_view = self.xblock.author_view()
        author_view_html = author_view.content
        self.assertIn('<p>El componente aún <strong>no</strong> se ha configurado.</p>', author_view_html)
        self.assertNotIn('<p>El componente está <strong>correctamente configurado</strong>. Ver en LMS.</p>', author_view_html)

        self.xblock.program_id = 5
        author_view = self.xblock.author_view()
        author_view_html = author_view.content
        self.assertNotIn('<p>El componente aún <strong>no</strong> se ha configurado.</p>', author_view_html)
        self.assertIn('<p>El componente está <strong>correctamente configurado</strong>. Ver en LMS.</p>', author_view_html)

    def test_studio_submit(self):
        """
            Test Studio submit handler
        """
        request = TestRequest()
        request.method = 'POST'
        post_data = {
            'program_id': 999,
        }
        data = json.dumps(post_data)
        request.body = data
        request.params = post_data
        response = self.xblock.studio_submit(request)
        self.assertEqual(self.xblock.display_name, 'Programa de Cursos')
        self.assertEqual(self.xblock.program_id, 999)
