from shark.objects.glyph import glyph, Glyph
from shark.base import Enumeration, BaseObject, Default, Collection, iif, Size, ButtonStyle, ButtonState


class FormStyle(Enumeration):
    default = 0
    inline = 1
    horizontal = 2


class FormValidationState(Enumeration):
    none = 0
    success = 1
    warning = 2
    error = 3


class FormFieldState(Enumeration):
    default = 0
    disabled = 1
    readonly = 2


class Form(BaseObject):
    def __init__(self, items=Default, action=u'', identifier=Default, bss=(), **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Form elements', Collection())
        self.action = self.param(action, 'string', 'Form action')
        self.identifier = self.param(identifier, 'string', 'Hidden identifier', Default)
        self.bss = self.param(bss, 'ParagraphStyle', 'Visual style of the form')
        if isinstance(self.bss, tuple):
            for s in self.bss:
                if not s == FormStyle.default:
                    self.add_class('form-'+FormStyle.name(s))
        elif isinstance(self.bss, int):
            self.add_class('form-'+ FormStyle.name(self.bss))
        self.role = "form"

    def get_html(self, html):
        params = self.base_attributes
        if self.action:
            params += ' data-async'
        html.append('<form' + params + '>')
        html.append('    <input type="hidden" name="action" value="' + self.action + '">')
        if self.identifier != Default:
            html.append('    <input type="hidden" name="identifier" value="' + self.identifier + '">')
        html.render('    ', self.items)
        html.append('</form>')


class FormGroup(BaseObject):
    def __init__(self, items=Default, validation_state=FormValidationState.none, use_icon=False, size=Size.default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the formgroup', Collection())
        self.validation_state = self.param(validation_state, 'FormValidationState', 'indicate state of validation')
        self.use_icon = self.param(use_icon, 'boolean', 'Whether the input in the form group should have icons')
        self.size = self.param(size, 'Size', 'indicates the size of the formgroup')

    def get_html(self, html):
        validation_state = '' if not self.validation_state else (' has-' + FormValidationState.name(self.validation_state))
        html.append('<div class="form-group{validation_state}{has_feedback}{size}" id="{id}">'.format(
            validation_state=validation_state,
            has_feedback=' has-feedback' if self.use_icon else '',
            size=' form-group-{size}'.format(size=Size.name(self.size)) if self.size else '',
            id=self.id))
        html.render('    ', self.items)
        html.append('</div>')


class TextInputWithLabel(BaseObject):
    def __init__(self,  name='', label='', type='text', value='', placeholder='', auto_focus=False,
                 form_control=True, hide_label=False, label_col=0, static=False, static_content='',
                 state=FormFieldState.default, validation_state=FormValidationState.none, use_icon=False,
                 height=Size.default, width=Size.sm, help_text='', bss=ButtonStyle.default, as_button=False,
                 **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'name of value sent back in GET or POST of form')
        self.label = self.param(label, 'string', 'Text of the label')
        self.type = self.param(type, 'string', 'Type of input, such as text, password, datetime, etc.')
        self.value = self.param(value, 'string', 'Value in the input')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.form_control = self.param(form_control, 'boolean', 'Indicates whether use form-control class for <input>')
        self.hide_label = self.param(hide_label, 'boolean', 'Hide label')
        self.static = self.param(static, 'boolean', 'indicates whether the label is static')
        self.static_content = self.param(static_content, 'string', 'static content shown when static = True')
        self.state = self.param(state, 'FormFieldState', 'Indicates input field state')
        self.label_col = self.param(label_col, 'integer', 'The column number that the label occupies (must between [0, 12))', 0)
        self.use_icon = self.param(use_icon, 'boolean', 'indicates whether this input should use icons')
        self.validation_state = self.param(validation_state, 'FormValidationState', 'indicate state of validation')
        self.height = self.param(height, 'Size', 'indicate the height of the input')
        self.width = self.param(width, 'Size', 'indicate the width size of the column')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')
        self.bss = self.param(bss, 'ButtonStyle', 'button bootstrap style when used as button')
        self.as_button = self.param(as_button, 'boolean', 'indicates whether it is used as button')

        if self.as_button:
            self.add_class('btn btn-{button_type}'.format(button_type=ButtonStyle.name(self.bss)))

        if self.label_col < 0 or self.label_col >= 12:
            self.label_col = 0


    def get_html(self, html):
        if self.validation_state and self.use_icon:
            if FormValidationState.name(self.validation_state) == 'success':
                icon_name = 'ok'
            elif FormValidationState.name(self.validation_state) == 'warning':
                icon_name = 'warning-sign'
            elif FormValidationState.name(self.validation_state) == 'error':
                icon_name = 'remove'
            else:
                icon_name = 'none'

        if self.hide_label:
            label_class = ' class="sr-only"'
        else:
            if self.label_col:
                label_class = ' class="col-{width_size}-{col} control-label"'.format(width_size=Size.name(self.width), col=self.label_col)
            else:
                label_class = ' class="control-label"'

        if self.label:
            html.append('<label for="' + self.id + '"'+ label_class + '>' + self.label + '</label>')
        if self.label_col:
            html.append('<div class="col-{width_size}-{col}">'.format(width_size=Size.name(self.width), col=12-self.label_col))
        if not self.static:
            html.append('<input type="' + self.type + '"' \
                        + ((' class="form-control{size}"'.format(size=(' input-'+Size.name(self.height)) if self.height else '') if self.form_control else "") if not self.as_button else '')\
                        + self.base_attributes\
                        + (' name="' + self.name + '"' if self.name else '')\
                        + (' value="' + self.value + '"' if self.value else '')\
                        + ' placeholder="' + self.placeholder + '"'\
                        + (' data-autofocus' if self.auto_focus else '')\
                        + (' aria-describedby="{id_status}"'.format(id_status=self.id+"Status") if self.use_icon else '')\
                        + (' aria-describedby="{help_block}"'.format(help_block=self.id+"helpBlock" if self.help_text else ''))\
                        + '{}>'.format('' if not self.state else (' '+ FormFieldState.name(self.state))))
        else:
            html.append('<p class="form-control-static">{content}</p>'.format(content=self.static_content))
        if self.use_icon:
            html.append('<span class="glyphicon glyphicon-{icon_name} form-control-feedback" aria-hidden="true"></span>'.format(icon_name=icon_name))
            html.append('<span id="{id}Status" class="sr-only">({name})</span>'.format(id=self.id, name=FormValidationState.name(self.validation_state)))
        if self.help_text:
            html.append('<span id="{id}" class="help-block">{help_text}</span>'.format(id=self.id+"helpBlock", help_text=self.help_text))
        if self.label_col:
            html.append('</div>')


class PasswordInputWithLabel(BaseObject):
    def __init__(self,  name='', label='', type='text', value='', placeholder='', auto_focus=False,
                 form_control=True, hide_label=False, label_col=0, static=False, static_content='',
                 state=FormFieldState.default, validation_state=FormValidationState.none, use_icon=False,
                 height=Size.default, width=Size.sm, help_text='', bss=ButtonStyle.default, as_button=False,
                 **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'name of value sent back in GET or POST of form')
        self.label = self.param(label, 'string', 'Text of the label')
        self.type = self.param(type, 'string', 'Type of input, such as text, password, datetime, etc.')
        self.value = self.param(value, 'string', 'Value in the input')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.form_control = self.param(form_control, 'boolean', 'Indicates whether use form-control class for <input>')
        self.hide_label = self.param(hide_label, 'boolean', 'Hide label')
        self.static = self.param(static, 'boolean', 'indicates whether the label is static')
        self.static_content = self.param(static_content, 'string', 'static content shown when static = True')
        self.state = self.param(state, 'FormFieldState', 'Indicates input field state')
        self.label_col = self.param(label_col, 'integer', 'The column number that the label occupies (must between [0, 12))', 0)
        self.use_icon = self.param(use_icon, 'boolean', 'indicates whether this input should use icons')
        self.validation_state = self.param(validation_state, 'FormValidationState', 'indicate state of validation')
        self.height = self.param(height, 'Size', 'indicate the height of the input')
        self.width = self.param(width, 'Size', 'indicate the width size of the column')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')
        self.bss = self.param(bss, 'ButtonStyle', 'button bootstrap style when used as button')
        self.as_button = self.param(as_button, 'boolean', 'indicates whether it is used as button')

        if self.as_button:
            self.add_class('btn btn-{button_type}'.format(button_type=ButtonStyle.name(self.bss)))

        if self.label_col < 0 or self.label_col >= 12:
            self.label_col = 0


    def get_html(self, html):
        if self.validation_state and self.use_icon:
            if FormValidationState.name(self.validation_state) == 'success':
                icon_name = 'ok'
            elif FormValidationState.name(self.validation_state) == 'warning':
                icon_name = 'warning-sign'
            elif FormValidationState.name(self.validation_state) == 'error':
                icon_name = 'remove'
            else:
                icon_name = 'none'

        if self.hide_label:
            label_class = ' class="sr-only"'
        else:
            if self.label_col:
                label_class = ' class="col-{width_size}-{col} control-label"'.format(width_size=Size.name(self.width), col=self.label_col)
            else:
                label_class = ' class="control-label"'

        if self.label:
            html.append('<label for="' + self.id + '"'+ label_class + '>' + self.label + '</label>')
        if self.label_col:
            html.append('<div class="col-{width_size}-{col}">'.format(width_size=Size.name(self.width), col=12-self.label_col))
        if not self.static:
            html.append('<input type="password"' \
                        + ((' class="form-control{size}"'.format(size=(' input-'+Size.name(self.height)) if self.height else '') if self.form_control else "") if not self.as_button else '')\
                        + self.base_attributes\
                        + (' name="' + self.name + '"' if self.name else '')\
                        + (' value="' + self.value + '"' if self.value else '')\
                        + ' placeholder="' + self.placeholder + '"'\
                        + (' data-autofocus' if self.auto_focus else '')\
                        + (' aria-describedby="{id_status}"'.format(id_status=self.id+"Status") if self.use_icon else '')\
                        + (' aria-describedby="{help_block}"'.format(help_block=self.id+"helpBlock" if self.help_text else ''))\
                        + '{}>'.format('' if not self.state else (' '+ FormFieldState.name(self.state))))
        else:
            html.append('<p class="form-control-static">{content}</p>'.format(content=self.static_content))
        if self.use_icon:
            html.append('<span class="glyphicon glyphicon-{icon_name} form-control-feedback" aria-hidden="true"></span>'.format(icon_name=icon_name))
            html.append('<span id="{id}Status" class="sr-only">({name})</span>'.format(id=self.id, name=FormValidationState.name(self.validation_state)))
        if self.help_text:
            html.append('<span id="{id}" class="help-block">{help_text}</span>'.format(id=self.id+"helpBlock", help_text=self.help_text))
        if self.label_col:
            html.append('</div>')


class FormFieldSet(BaseObject):
    def __init__(self, items=Default, state=FormFieldState.default, **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the formfieldset', Collection())
        self.state = self.param(state, 'FormFieldStat', 'indicate the state for the formfieldset')

    def get_html(self, html):
        html.append('<fieldset{state}>'.format(state = '' if not self.state else (' ' + FormFieldState.name(self.state))))
        html.render('    ', self.items)
        html.append('</fieldset>')


class FormTextArea(BaseObject):
    def __init__(self, name='', data='', placeholder='', rows=0, form_control=True, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the field')
        self.data = self.param(data, 'string', 'Initial value')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.rows = self.param(rows, 'integer', 'Specify rows for textarea when necessary')
        self.form_control = self.param(form_control, 'boolean', 'Indicates whether use form-control class for <textarea>')

        if self.name:
            self.add_attribute('name', name)

    def get_html(self, html):
        html.append(u'<textarea '\
                    + (' class="form-control"' if self.form_control else "")\
                    + self.base_attributes\
                    + (' rows="{}"'.format(self.rows) if self.rows else '')\
                    + (' placeholder="{}"'.format(self.placeholder) if self.placeholder else '')\
                    + '>' + self.data + '</textarea>')

class FormHidden(BaseObject):
    def __init__(self, name='', value='', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'name of value sent back in GET or POST of form')
        self.value = self.param(value, 'string', 'value')

    def get_html(self, html):
        html.append('<input type=hidden id="' + self.id + '"' + (' name="' + self.name + '"' if self.name else '') + ' value="' + self.value + '">') #TODO: Quote value


class FormSelect(BaseObject):
    def __init__(self, items=Default,  name='', label='', auto_focus=False, auto_submit=False, multiple=False, height=Size.default, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'name of value sent back in GET or POST of form')
        self.label = self.param(label, 'string', 'Text of the label')
        self.items = self.param(items, 'Collection', 'Options in the dropdown', Collection())
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.auto_submit = self.param(auto_submit, 'boolean', 'Submit the form when a change ')
        self.multiple = self.param(multiple, 'boolean', 'Determines whether the select if multiple')
        self.height = self.param(height, 'Size', 'Indicates the size of the height')

    def get_html(self, html):
        if self.label:
            html.append('<label for="' + self.id + '">' + self.label + '</label>')
        html.append('<select'+ (' multiple' if self.multiple else '') +
                    ' class="form-control{size}"'.format(size=' input-'+Size.name(self.height) if self.height else '')+
                    ' id="{id}"'.format(id=self.id) +
                    (' name="' + self.name + '"' if self.name else '') +
                    (' data-autofocus' if self.auto_focus else '') +
                    (' onchange="$(this).closest(\'form\').submit();"' if self.auto_submit else '') +
                    '>')
        html.render('    ', self.items)
        html.append('</select>')


class FormSelectOption(BaseObject):
    def __init__(self, name='', value=Default, selected=False, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'name of the option')
        self.value = self.param(value, 'string', 'value of the option', Default)
        self.selected = self.param(selected, 'boolean', 'Is this the selected option?')

    def get_html(self, html):
        html.append('<option id="' + self.id + '" ' +
            (' value="' + self.value + '"' if self.value != Default else '') +
            (' selected="selected"' if self.selected else '') +
            '>' + self.name + '</option>'
        )


class Button(BaseObject):
    def __init__(self, text='', bss=ButtonStyle.default, glyph=Glyph.none, url='',
                 size=Size.default, state=ButtonState.none, block=False, **kwargs):
        self.init(kwargs)
        self.text = self.param(text, 'string', 'Text on the button')
        self.bss = self.param(bss, 'ButtonStyle', 'Visual style of the button')
        self.glyph = self.param(glyph, 'Glyph', 'Glyph to add in front of text')
        self.url = self.param(url, 'url', 'Url for the button')
        self.size = self.param(size, 'Size', 'indicates the button size')
        self.state = self.param(state, 'ButtonState', 'indicates the state of buttons, i.e. active, disabled')
        self.block = self.param(block, 'boolean', 'indicates whether the button is created as block-level button')

        self.add_class('btn {button_type}'.format(button_type='btn-' + ButtonStyle.name(self.bss)))
        if self.size:
            self.add_class('btn-' + Size.name(self.size))
        if self.block:
            self.add_class('btn-block')
        if self.state:
            if ButtonState.name(self.state) == 'active':
                self.add_class('active')

    button_type = 'button'

    def get_html(self, html):
        button_content = Collection()
        if self.glyph:
            button_content.append(glyph(self.glyph))
        button_content.append(self.text)

        button_html_pre = '<button type="' + self.button_type + self.base_attributes + iif(ButtonState.name(self.state)=='disabled', ' disabled="disabled"', '') + '>'
        button_html_post = '</button>'
        if self.url:
            button_html_pre = '<a href="' + self.url + '">' + button_html_pre
            button_html_post = button_html_post + '</a>'

        html.append(button_html_pre)
        html.render('    ', button_content)
        html.append(button_html_post)


class Submit(Button):
    button_type = 'submit'


class CheckBoxRadioStyle(Enumeration):
    default = 0
    inline = 1


class CheckBox(BaseObject):
    def __init__(self, label='', value='', state=FormFieldState.default, bss=CheckBoxRadioStyle.default, validation_state=FormValidationState.none, **kwargs):
        self.init(kwargs)
        self.label = self.param(label, 'string', 'Label tag for the checkbox', '')
        self.value = self.param(value, 'string', 'Value for checkbox input', '')
        self.state = self.param(state, 'FormFieldState', 'Indicates the checkbox state')
        self.bss = self.param(bss, 'CheckBoxRadioStyle', 'bss for checkbox')
        self.validation_state = self.param(validation_state, 'FormValidationState', 'validation state: success, warning, error')

    def get_html(self, html):
        div_class = 'checkbox{}'.format('' if not self.validation_state else (' ' + FormValidationState.name(self.validation_state)))
        if self.bss:
            div_class += '-'+CheckBoxRadioStyle.name(self.bss)
        html.append(u'<div class="{}'.format(div_class)\
                    + ('' if not self.state else (' '+ FormFieldState.name(self.state)))\
                    + '"' + '>')
        html.append(u'    <label>')
        html.append(u'        <input type="checkbox"' + (' value="{}"'.format(self.value) if self.value else '')\
                    + ('' if not self.state else (' '+ FormFieldState.name(self.state)))\
                    + ' id="{}"'.format(self.id) + '>' + self.label)
        html.append(u'    </label>')
        html.append(u'</div>')


class Radio(BaseObject):
    def __init__(self, label='', value='', name='', state=FormFieldState.default, bss=CheckBoxRadioStyle.default, checked=False, **kwargs):
        self.init(kwargs)
        self.label = self.param(label, 'string', 'Label tag for the radio', '')
        self.value = self.param(value, 'string', 'Value for radio input', '')
        self.name = self.param(name, 'string', 'name for radio choice')
        self.bss = self.param(bss, 'CheckBoxRadioStyle', 'bss for radio')
        self.state = self.param(state, 'FormFieldState', 'Indicates the radio button state')
        self.checked = self.param(checked, 'boolean', 'Whether the radio button is checked')

    def get_html(self, html):
        div_class = 'radio'
        if self.bss:
            div_class += '-'+CheckBoxRadioStyle.name(self.bss)
        html.append(u'<div class="{}'.format(div_class) \
                    + ('' if not self.state else (' '+ FormFieldState.name(self.state)))\
                    + '"' + '>')
        html.append(u'    <label>')
        html.append(u'        <input type="radio"' \
                    + (' name="{}"'.format(self.name) if self.name else '')\
                    + (' value="{}"'.format(self.value) if self.value else '')\
                    + ' id="{}"'.format(self.id)\
                    + ('' if not self.state else (' '+ FormFieldState.name(self.state)))\
                    + (' checked' if self.checked else '') +'>' + self.label)
        html.append(u'    </label>')
        html.append(u'</div>')



