import pkg_resources
from django.template import Context, Template
from webob import Response
from xblock.core import XBlock
from xblock.fields import Integer, String, Scope, Dict
from xblock.fragment import Fragment
from django.urls import reverse
import simplejson as json
from six import text_type
import logging
logger = logging.getLogger(__name__)
# Make '_' a no-op so we can scrape strings
_ = lambda text: text


class EolCourseProgramXBlock(XBlock):
    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Programa de Cursos",
        scope=Scope.settings,
    )
    icon_class = String(
        default="other",
        scope=Scope.settings,
    )
    program_id = Integer(
        display_name = _("Programa"),
        help = _("Al seleccionar un programa se desplegará el listado de cursos asociados."),
        scope = Scope.settings
    )
    program_courses_enrollment_modes = Dict(
        display_name=_("Modos de inscripción"),
        help=_("Modos de inscripción para cada curso"),
        scope=Scope.settings,
    )
    next_course_enunciate = String(
        display_name=_("Enunciado Curso Final"),
        help=_("Enunciado para el curso final o siguiente curso del programa"),
        default="Curso Final",
        scope=Scope.settings,
    )

    has_author_view = True

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template('static/html/eolcourseprogram.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/eolcourseprogram.css"))
        frag.add_javascript(self.resource_string("static/js/src/eolcourseprogram.js"))
        settings = {
            'url_get_program_info':reverse(
                'get_program_info',
                    kwargs={
                        'course_id': text_type(self.course_id),
                        'program_id': self.program_id
                    }
            ),
            'url_enroll_and_redirect':reverse(
                'enroll_and_redirect',
                    kwargs={
                        'program_id': self.program_id
                    }
            ),
            'xblock_program_id': self.program_id,
            'xblock_program_courses_enrollment_modes': self.program_courses_enrollment_modes
        }
        frag.initialize_js('EolCourseProgramXBlock', json_args=settings)
        return frag

    def author_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template(
            'static/html/author_view.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/eolcourseprogram.css"))
        return frag
    
    def studio_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template('static/html/studio.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/eolcourseprogram.css"))
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        settings = {
            'url_get_course_programs':reverse(
                'get_course_programs',
                    kwargs={
                        'course_id': text_type(self.course_id)
                    }
            ),
            'xblock_program_id': self.program_id,
            'xblock_program_courses_enrollment_modes': self.program_courses_enrollment_modes
        }
        frag.initialize_js('EolCourseProgramStudioXBlock', json_args=settings)
        return frag

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        self.program_id = request.params['program_id']
        self.next_course_enunciate = request.params['next_course_enunciate']
        self.program_courses_enrollment_modes = json.loads(request.params['program_courses_enrollment_modes'])
        logger.info(self.program_courses_enrollment_modes)
        logger.info(type(self.program_courses_enrollment_modes))
        return Response({'result': 'success'})

    def get_context(self):
        return {
            'field_program_id': self.fields['program_id'],
            'xblock': self
        }
    
    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("EolCourseProgramXBlock",
             """<eolcourseprogram/>
             """),
        ]
