from shark.base import Object, Default, Objects, StringParam
from shark.param_converters import ObjectsParam


class Modal(Object):
    def __init__(self, title='', items=Default, buttons=Default, **kwargs):
        self.init(kwargs)
        self.title = self.param(title, StringParam, 'Title of the modal dialog')
        self.items = self.param(items, ObjectsParam, 'Items that make up the modal dialog main area', Objects())
        self.buttons = self.param(buttons, ObjectsParam, 'Dialog\'s buttons', Objects())

    def get_html(self, html):
        html.append('<div class="modal fade" id="' + self.id + '" tabindex="-1" role="dialog" aria-labelledby="' + self.id + 'Label" aria-hidden="true">')
        html.append('    <div class="modal-dialog">')
        html.append('        <div class="modal-content">')
        if self.title:
            html.append('            <div class="modal-header">')
            html.append('                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>')
            html.append('                <h4 class="modal-title" id="' + self.id + '">' + self.title + '</h4>')
            html.append('            </div>')
        html.append('            <div class="modal-body">')
        if not self.title:
            html.append('                  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>')
        html.render('                  ', self.items)
        html.append('            </div>')
        html.append('            <div class="modal-footer">')
        html.render('                ', self.buttons)
        html.append('            </div>')
        html.append('        </div>')
        html.append('    </div>')
        html.append('</div>')

    def show_code(self):
        return '$(\'#' + self.id + '\').modal()'


