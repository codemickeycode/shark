from shark.base import BaseObject, Default, Collection


class Modal(BaseObject):
    def __init__(self, title='', items=Default, buttons=Default, **kwargs):
        self.init(kwargs)
        self.title = self.param(title, 'string', 'Title of the modal dialog')
        self.items = self.param(items, 'Collection', 'Items that make up the modal dialog main area', Collection())
        self.buttons = self.param(buttons, 'Collection', 'Dialog\'s buttons', Collection())

    def get_html(self, html):
        html.append(u'<div class="modal fade" id="' + self.id + u'" tabindex="-1" role="dialog" aria-labelledby="' + self.id + u'Label" aria-hidden="true">')
        html.append(u'    <div class="modal-dialog">')
        html.append(u'        <div class="modal-content">')
        if self.title:
            html.append(u'            <div class="modal-header">')
            html.append(u'                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>')
            html.append(u'                <h4 class="modal-title" id="' + self.id + '">' + self.title + '</h4>')
            html.append(u'            </div>')
        html.append(u'            <div class="modal-body">')
        if not self.title:
            html.append(u'                  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>')
        html.render(u'                  ', self.items)
        html.append(u'            </div>')
        html.append(u'            <div class="modal-footer">')
        html.render(u'                ', self.buttons)
        html.append(u'            </div>')
        html.append(u'        </div>')
        html.append(u'    </div>')
        html.append(u'</div>')

    def show_code(self):
        return u'$(\'#' + self.id + '\').modal()'


