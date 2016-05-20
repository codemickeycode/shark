from shark.objects.layout import Row, Spacer
from shark.objects.text import Heading, Anchor
from shark.objects.ui_elements import SearchBox
from .handler import BasePageHandler


class Base404Handler(BasePageHandler):
    roles_required = []

    def render_page(self):
        self.append(Row(classes='text-center', items=[
            Heading("Oops, 404"),
                "Looks like we took a wrong turn somewhere. Please go back to the ",
                Anchor("homepage", '/'), " or search what you are looking for:", Spacer(40),
                SearchBox(), Spacer(80)
            ]))
