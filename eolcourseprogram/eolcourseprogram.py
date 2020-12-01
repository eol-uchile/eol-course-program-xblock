import pkg_resources
from django.template import Context, Template
from webob import Response
from xblock.core import XBlock
from xblock.fields import Integer, String, Scope
from xblock.fragment import Fragment

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
        help = _("Selecciona el programa"),
        scope = Scope.settings
    )

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
        frag.initialize_js('EolCourseProgramXBlock')
        return frag

    def studio_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template('static/html/studio.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/eolcourseprogram.css"))
        frag.add_javascript(self.resource_string("static/js/src/studio.js"))
        frag.initialize_js('EolCourseProgramStudioXBlock')
        return frag

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        self.program_id = request.params['program_id']
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
