from .ui_elements import SearchBox
from .text import Heading, Anchor
from .layout import Row, Spacer
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
