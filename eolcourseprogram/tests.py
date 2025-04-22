# -*- coding: utf-8 -*-

import json
from mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from common.djangoapps.util.testing import UrlResetMixin
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory
from common.djangoapps.student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from common.djangoapps.student.tests.factories import UserFactory, CourseEnrollmentFactory
from xblock.field_data import DictFieldData
from common.djangoapps.student.roles import CourseStaffRole
from .eolcourseprogram import EolCourseProgramXBlock
from . import views
from .models import EolCourseProgram
from .views import _has_access
import logging

logger = logging.getLogger(__name__)

XBLOCK_RUNTIME_USER_ID = 99

def _generate_default_test_data(course):
    # create final course
    final_course = CourseFactory.create(
        org='mss',
        course='1234',
        display_name='eol final course'
    )

    # create 3 example courses
    course1 = CourseFactory.create(
        org='mss',
        course='1',
        display_name='eol 1 course'
    )

    course2 = CourseFactory.create(
        org='mss',
        course='2',
        display_name='eol 2 course'
    )

    course3 = CourseFactory.create(
        org='mss',
        course='3',
        display_name='eol 3 course'
    )

    # create course program
    cp = EolCourseProgram.objects.create(
        program_name    = "Program Name 1",
        final_course    = CourseOverview.get_from_id(final_course.id),
    )
    # add 4 courses
    cp.courses.add(
        CourseOverview.get_from_id(course.id),
        CourseOverview.get_from_id(course1.id),
        CourseOverview.get_from_id(course2.id),
        CourseOverview.get_from_id(course3.id)
    )
    return cp, final_course.id, course1.id

class TestEolCourseProgramAPI(UrlResetMixin, ModuleStoreTestCase):
    def setUp(self):
        super(TestEolCourseProgramAPI, self).setUp()
        # create a course
        self.course = CourseFactory.create(org='mss', course='999',
                                           display_name='eol course')

        self.course_program, self.final_course_id, self.first_course_id = _generate_default_test_data(self.course)
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('common.djangoapps.student.models.cc.User.save'):
            # Create the student
            self.student = UserFactory(username='student', password='test', email='student@edx.org')
            # Enroll the student in the course
            CourseEnrollmentFactory(user=self.student, course_id=self.course.id)
            # Log the student in
            self.client = Client()
            self.assertTrue(self.client.login(username='student', password='test'))

    def test_get_course_programs(self):
        """
            Test get course programs
        """
        response = self.client.get(
            reverse(
                'get_course_programs',
                    kwargs={'course_id': self.course.id}
            )
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), 1)

        cp = EolCourseProgram.objects.create(
            program_name    = "Program Name 2",
        )
        cp.courses.add(CourseOverview.get_from_id(self.course.id))
        response = self.client.get(
            reverse(
                'get_course_programs',
                    kwargs={'course_id': self.course.id}
            )
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), 2)
        self.assertEqual(content[0]["program_name"], 'Program name 1')
        self.assertEqual(len(content[0]["courses_list"]), 4)

    def test_get_course_programs_wrong_method(self):
        """
            Test get course programs wrong method
        """
        response = self.client.post(
            reverse(
                'get_course_programs',
                    kwargs={'course_id': self.course.id}
            )
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_course_programs_wrong_course_id(self):
        """
            Test get course programs wrong course_id
        """
        response = self.client.post(
            reverse(
                'get_course_programs',
                    kwargs={'course_id': self.course.id}
            )
        )
        self.assertEqual(response.status_code, 400)
    
    @patch('eolcourseprogram.views.EolCourseProgram.objects.filter')
    def test_get_course_programs_object_filter_error(self, mock_EolCourseProgram_filter):
        """
            Test get course programs wrong EolCourseProgram.objects.filter
        """
        mock_EolCourseProgram_filter.return_value = None
        response = self.client.get(
            reverse(
                'get_course_programs',
                    kwargs={'course_id': self.course.id}
            )
        )
        self.assertEqual(response.status_code, 500)

    def test_get_program_info_without_progress(self):
        """
            Test get program info without student progress
        """
        response = self.client.get(
            reverse(
                'get_program_info',
                kwargs={
                    'course_id': self.course.id,
                    'program_id': 1
                }
            )
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["program_name"], 'Program name 1')
        self.assertEqual(len(content["courses_list"]), 4)
        self.assertEqual(content["approved_count"], 0)
        self.assertEqual(content["final_course_allowed"], False)

    def test_get_program_info_with_wrong_send_method(self):
        """
            Test get program info with wrong method
        """
        response = self.client.post(
            reverse(
                'get_program_info',
                kwargs={
                    'course_id': self.course.id,
                    'program_id': 1
                }
            )
        )
        self.assertEqual(response.status_code, 400)

    def test_get_program_info_with_wrong_program_id(self):
        """
            Test get program info with wrong program_id
        """
        response = self.client.get(
            reverse(
                'get_program_info',
                kwargs={
                    'course_id': self.course.id,
                    'program_id': 6
                }
            )
        )
        self.assertEqual(response.status_code, 409)

    @patch('lms.djangoapps.grades.course_grade_factory.CourseGradeFactory.read')
    def test_get_program_info_with_progress(self, coursegradefractory_read):
        """
            Test get program info with student progress
        """
        grade_true = Mock()
        grade_true.passed = True
        grade_false = Mock()
        grade_false.passed = False

        # with 3/4 course approved
        coursegradefractory_read.side_effect = [grade_true, grade_true, grade_false, grade_true, grade_true] # 4 program courses + 1 final course
        response = self.client.get(
            reverse(
                'get_program_info',
                kwargs={
                    'course_id': self.course.id,
                    'program_id': 1
                }
            )
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["program_name"], 'Program name 1')
        self.assertEqual(len(content["courses_list"]), 4)
        self.assertEqual(content["approved_count"], 3)
        self.assertEqual(content["final_course_allowed"], False)

        # with 4/4 course approved
        coursegradefractory_read.side_effect = [grade_true, grade_true, grade_true, grade_true, grade_true] # 4 program courses + 1 final course
        response = self.client.get(
            reverse(
                'get_program_info',
                kwargs={
                    'course_id': self.course.id,
                    'program_id': 1
                }
            )
        )
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content["program_name"], 'Program name 1')
        self.assertEqual(len(content["courses_list"]), 4)
        self.assertEqual(content["approved_count"], 4)
        self.assertEqual(content["final_course_allowed"], True)


    @patch('lms.djangoapps.grades.course_grade_factory.CourseGradeFactory.read')
    def test_enroll_and_redirect(self, coursegradefractory_read):
        """
            Test Enroll and redirect
        """
        # Student should not be enrolled
        mode, is_active = CourseEnrollment.enrollment_mode_for_user(self.student, self.final_course_id)
        self.assertFalse(is_active)
        self.assertEqual(mode, None)

        grade_true = Mock()
        grade_true.passed = True

        # Set approved => final_course_allowed will be True
        coursegradefractory_read.side_effect = [grade_true, grade_true, grade_true, grade_true, grade_true] # 4 program courses + 1 final course
        response = self.client.get(
            reverse(
                'enroll_and_redirect',
                kwargs={
                    'program_id': 1
                }
            )
        )
        self.assertEqual(response.status_code, 302)
        # Student should be enrolled as 'honor' by default
        mode, is_active = CourseEnrollment.enrollment_mode_for_user(self.student, self.final_course_id)
        self.assertTrue(is_active)
        self.assertEqual(mode, 'honor')

    @patch('lms.djangoapps.grades.course_grade_factory.CourseGradeFactory.read')
    def test_enroll_mode(self, coursegradefractory_read):
        """
            Test successful enroll mode
        """
        grade_true = Mock()
        grade_true.passed = True
        # Set final course mode
        course_program = EolCourseProgram.objects.get(pk=1)
        course_program.final_course_mode = 'verified'
        course_program.save()
        coursegradefractory_read.side_effect = [grade_true, grade_true, grade_true, grade_true, grade_true] # 4 program courses + 1 final course
        response = self.client.get(
            reverse(
                'enroll_and_redirect',
                kwargs={
                    'program_id': 1
                }
            )
        )
        self.assertEqual(response.status_code, 302)
        # Student should be enrolled as 'verified'
        mode, is_active = CourseEnrollment.enrollment_mode_for_user(self.student, self.final_course_id)
        self.assertTrue(is_active)
        self.assertEqual(mode, 'verified')
    
    def test_enroll_and_redirect_program_without_final_course_info(self):
        """
            Test Enroll and redirect when a program have final course as None
        """
         # create course program
        EolCourseProgram.objects.create(
            program_name    = "Program Name 2",
            final_course    = None,
        )
        response = self.client.get(
            reverse(
                'enroll_and_redirect',
                kwargs={
                    'program_id': 2
                }
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_student_enrollment_modes(self):
        """
        Test student enrollment in any course of the program based on modes
        """
        # Test enrollment for course_1
        response = self.client.post(
            reverse(
                'enroll_student',
                kwargs={
                    'program_id': 1,
                    'course_id': self.first_course_id
                }
            ),
            json.dumps({'mode': 'audit'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mode, is_active = CourseEnrollment.enrollment_mode_for_user(self.student, self.first_course_id)
        self.assertTrue(is_active)
        self.assertEqual(mode, 'audit')

    def test_student_enrollment_modes_with_wrong_course_id(self):
        """
        Test student enrollment with wrong course id
        """
        response = self.client.post(
            reverse(
                'enroll_student',
                kwargs={
                    'program_id': 1,
                    'course_id': '11111111111111'
                }
            ),
            json.dumps({'mode': 'audit'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

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
        self.course = CourseFactory.create(org='mss', course='998', display_name='EolCourseProgram tests')

        # create Xblock
        self.xblock = self.make_an_xblock()
        # Patch the comment client user save method so it does not try
        # to create a new cc user when creating a django user
        with patch('common.djangoapps.student.models.cc.User.save'):
            uname = 'student'
            email = 'student@edx.org'
            password = 'test'

            # Create and enroll student
            self.student = UserFactory(username=uname, password=password, email=email)
            CourseEnrollmentFactory(user=self.student, course_id=self.course.id)

            # Create and Enroll staff user
            self.staff_user = UserFactory(
                username='staff_user',
                password='test',
                email='staff@edx.org',
                is_staff=True
            )
            CourseEnrollmentFactory(
                user=self.staff_user,
                course_id=self.course.id
            )
            CourseStaffRole(self.course.id).add_users(self.staff_user)

            # Log the student in
            self.client = Client()
            self.assertTrue(self.client.login(username=uname, password=password))

            # Log the user staff in
            self.staff_client = Client()
            self.assertTrue(self.staff_client.login(username='staff_user', password='test'))

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
        self.assertEqual(self.xblock.next_course_enunciate, 'Curso Final')
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
            'next_course_enunciate': 'test',
            'program_courses_enrollment_modes':json.dumps({"course_1": "audit", "course_2": "verified"})
        }
        data = json.dumps(post_data)
        request.body = data
        request.params = post_data
        response = self.xblock.studio_submit(request)
        self.assertEqual(self.xblock.display_name, 'Programa de Cursos')
        self.assertEqual(self.xblock.next_course_enunciate, 'test')
        self.assertEqual(self.xblock.program_id, 999)
        self.assertEqual(self.xblock.program_courses_enrollment_modes, {"course_1": "audit", "course_2": "verified"})

    def test_studio_view_render(self):
        """
            Check if xblock studio template loaded correctly
        """
        studio_view = self.xblock.studio_view()
        studio_view_html = studio_view.content
        self.assertIn('id="settings-tab"', studio_view_html)

    def test_has_access_wrong_course_id(self):
        """
            Check if _has_access worked correctly with wrong course_id
        """
        request = TestRequest()
        request.method = 'POST'
        course_id = '1111111111'
        response = _has_access(request,course_id)
        self.assertFalse(response)
