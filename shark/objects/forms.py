import pickle

from django.contrib.admin.utils import quote
from django.core import signing, validators
from django.core.exceptions import ValidationError, FieldDoesNotExist
from django.db.models import QuerySet
from shark.base import BaseObject, objectify, Default
from shark.common import listify, attr, iif


class FieldError(BaseObject):
    sub_classes = {}

    def __init__(self, field_name, **kwargs):
        self.init(kwargs)
        self.field_name = self.param(field_name, 'string', 'Name of the field to show errors for')
        self.id_needed()

    def render_container(self, html):
        html.append('<ul' + self.base_attributes + '></ul>')

    def render_error(self, html, message):
        html.append('<li>')
        html.render('    ', message)
        html.append('</li>')

    def _render_error(self, html, message):
        self.render_error(html, self.param(message, 'Collection'))

    def get_html(self, html):
        self.form = html.find_parent(Form)
        self.form.form_data['fld'][self.field_name]['err'] = (self.form.form_data_class(self.__class__), self.id)
        self.add_class('form-error')
        self.render_container(html)


class SpanBrFieldError(FieldError):
    def render_container(self, html):
        self.add_class('help-block with-errors')
        html.append('<span' + self.base_attributes + '></span>')

    def render_error(self, html, message):
        html.append('<span class="text-danger">')
        html.render('    ', objectify(message))
        html.append('</span><br>')


class FormError(BaseObject):
    sub_classes = {}

    def __init__(self, form_id=None, **kwargs):
        self.init(kwargs)
        self.form_id = form_id

    def render_container(self, html):
        html.append('<ul' + self.base_attributes + '></ul>')

    def render_error(self, html, message):
        html.append('<li>')
        html.render('    ', message)
        html.append('</li>')

    def _render_error(self, html, message):
        self.render_error(html, self.param(message, 'Collection'))

    def get_html(self, html):
        self.form = html.find_parent(Form)
        self.form.error_object = self
        self.add_class('form-error')
        self.render_container(html)


class ParagraphFormError(FormError):
    def render_container(self, html):
        html.append('<span' + self.base_attributes +'></span>')

    def render_error(self, html, message):
        html.append('<p>')
        html.render('    ', message)
        html.append('</p>')


class SpanBrFormError(FormError):
    def render_container(self, html):
        html.append('<span' + self.base_attributes + '></span>')

    def render_error(self, html, message):
        html.append('<span class="text-danger">')
        html.render('    ', message)
        html.append('</span><br>')


class Validator():
    def __init__(self, message='Invalid input.'):
        self.message = message
        self.init()

    def init(self):
        pass

    def validate(self, value):
        pass

    def enable_live_validation(self, web_object):
        pass

    def serialize(self):
        return self.message

    def deserialize(self, value):
        self.message = value


class RequiredValidator(Validator):
    def init(self):
        if not self.message:
            self.message = 'This field is required'

    def validate(self, value):
        if not value:
            return self.message

    def enable_live_validation(self, field):
        field.add_attribute('required', 'required')
        field.add_attribute('data-required-error', self.message)


class EmailValidator(Validator):
    def validate(self, value):
        try:
            validators.EmailValidator()(value)
        except ValidationError:
            return self.message


class Form(BaseObject):
    def __init__(self, data=None, items=None, style='', **kwargs):
        self.init(kwargs)
        self.data = self.param(data, 'Data', 'The model or DataHandler')
        self.items = self.param(items, 'Collection', 'Items in the form')
        self.style = self.param(style, 'str', 'Form style: inline or horizontal')

        if self.style:
            self.add_class('form-' + self.style)

        self.error_object = None
        self.form_data = {'id': self.id, 'fld': {}, 'cls': []}
        if self.data:
            self.form_data['data'] = (self.data.__class__, self.data.id)
        self.form_data_classes = {}
        self.fields = {}
        self.errors = []

        self.id_needed()

    def form_data_class(self, cls):
        if not cls in self.form_data_classes:
            self.form_data['cls'].append(cls)
            self.form_data_classes[cls] = self.form_data['cls'].index(cls)
        return self.form_data_classes[cls]

    def get_html(self, html):
        html.append('<form' + self.base_attributes + ' role="form" data-toggle="validator" data-async>')
        html.append('    <input type="hidden" name="action" value="_form_post">')
        html.append('    <input type="hidden" name="sub_action" value="">')
        html.render('    ', self.items)
        if not self.error_object:
            self.error_object = SpanBrFormError()
            self.error_object.parent = self
            html.render('    ', self.error_object)

        self.form_data['err'] = self.form_data_class(self.error_object.__class__)

        form_data = signing.dumps(self.form_data, compress=True, serializer=lambda: pickle)
        html.append('    <input type="hidden" name="form_data" value="{}">'.format(form_data))
        html.append('</form>')


class FormGroup(BaseObject):
    def __init__(self, items=Default, style='', **kwargs):
        self.init(kwargs)
        self.items = self.param(items, 'Collection', 'Items in the form group')
        self.add_class('form-group')
        self.add_class('has-feedback')

    def get_html(self, html):
        html.append('<div' + self.base_attributes + '>')
        html.render('    ', self.items)
        html.append('</div>')


def ensure_formgroup(func):
    def wrapper(self, html):
        formgroup = html.find_parent(FormGroup)
        if not formgroup:
            parent = self.parent
            formgroup = FormGroup(self)
            formgroup.parent = parent
            formgroup.get_html(html)
        else:
            func(self, html)

    return wrapper


class BaseField(BaseObject):
    def __init__(self, name=None, value=Default, required=False, min_length=None, max_length=None, validators=None, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the field')
        self.value = self.param(value, 'string', 'Starting value of the field', Default)
        self.required = self.param(required, 'boolean', 'Is this field required?')
        self.min_length = self.param(min_length, 'int', 'Is this field required?')
        self.max_length = self.param(max_length, 'int', 'Is this field required?')
        self.validators = listify(self.param(validators, 'Validator or list', 'Validator instance or a list of Validators.'))

        self.display_name = self.name.replace('_', ' ').title()
        if self.required:
            self.validators.append(RequiredValidator())

        for validator in self.validators:
            validator.enable_live_validation(self)


class TextField(BaseField):
    def __init__(self,  name=None, label='', placeholder='', auto_focus=False,
                 help_text='', value=Default, **kwargs):
        super().__init__(name, value, **kwargs)
        self.label = self.param(label, 'string', 'Text of the label')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')
        self.type = 'text'
        self.add_class('form-control')

    @ensure_formgroup
    def get_html(self, html):
        for validator in self.validators:
            if isinstance(validator, EmailValidator):
                self.type = 'email'

        html.add_resource('https://cdnjs.cloudflare.com/ajax/libs/1000hz-bootstrap-validator/0.10.1/validator.min.js', 'js', 'validator', 'main')

        form = html.find_parent(Form)
        form.form_data['fld'][self.name] = {
            'cls': form.form_data_class(self.__class__),
            'valid': [(form.form_data_class(validator.__class__), validator.serialize()) for validator in self.validators]
        }

        if self.value == Default and form.data:
            try:
                field = form.data._meta.get_field(self.name)
                self.value = form.data.__getattribute__(self.name)
            except FieldDoesNotExist:
                pass


        if self.label or self.display_name:
            html.append('<label for="{}">{}</label>'.format(self.id, self.label or self.display_name))

        html.append('<input type="' + self.type + '"' +
                    self.base_attributes +
                    attr('name', self.name) +
                    attr('value', '' if self.value == Default else self.value) +
                    attr('placeholder', self.placeholder) +
                    iif(self.auto_focus, ' data-autofocus') +
                    '>')
        html.append('<span class="glyphicon form-control-feedback" aria-hidden="true"></span>')

        field_error = SpanBrFieldError(self.name)
        html.append('<span class="help-block">')
        field_error.get_html(html)
        html.append('    ' + self.help_text)
        html.append('</span>')


class BooleanField(BaseField):
    def __init__(self,  name=None, label='', value=Default, **kwargs):
        super().__init__(name, value, **kwargs)
        self.label = self.param(label, 'string', 'Text of the label')

    @ensure_formgroup
    def get_html(self, html):
        html.add_resource('https://cdnjs.cloudflare.com/ajax/libs/1000hz-bootstrap-validator/0.10.1/validator.min.js', 'js', 'validator', 'main')

        form = html.find_parent(Form)
        form.form_data['fld'][self.name] = {
            'cls': form.form_data_class(self.__class__),
            'valid': [(form.form_data_class(validator.__class__), validator.serialize()) for validator in self.validators]
        }

        if self.value == Default and form.data:
            try:
                field = form.data._meta.get_field(self.name)
                self.value = form.data.__getattribute__(self.name)
            except FieldDoesNotExist:
                pass

        if self.value:
            self.add_attribute('checked', 'checked')

        field_error = SpanBrFieldError(self.name)
        html.append('<div class="checkbox">')
        html.append('    <label>')
        html.append('        <input type="checkbox"' + self.base_attributes + attr('name', self.name) + '>')
        html.append('        ' + self.label)
        html.append('    </label>')
        field_error.get_html(html)
        html.append('</div>')


class EmailField(TextField):
    def __init__(self,  name=None, label='', placeholder='', auto_focus=False,
                 help_text='', value=Default, **kwargs):
        super().__init__(name, label, placeholder, auto_focus, help_text, value, **kwargs)

        validator_found = False
        for validator in self.validators:
            if isinstance(validator, EmailValidator):
                validator_found = True

        if not validator_found:
            self.validators.append(EmailValidator('Not a valid email address.'))


class DropDownField(BaseField):
    def __init__(self,  name=None, choices=None, label='', auto_focus=False,
                 help_text='', value=Default, **kwargs):
        super().__init__(name, value, **kwargs)
        self.choices = self.param(choices, 'data', 'List of tuples of (value, text) or the result of a database query with two columns')
        self.label = self.param(label, 'string', 'Text of the label')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')
        self.add_class('form-control')

    @ensure_formgroup
    def get_html(self, html):
        html.append('<select' + self.base_attributes + '>')
        if isinstance(self.choices, QuerySet):
            fieldname_1 = self.choices._fields[0]
            fieldname_2 = self.choices._fields[1]
            for choice in self.choices:
                html.append('<option value="{}">{}</option>'.format(quote(choice[fieldname_1]), quote(choice[fieldname_2])))
        else:
            for choice in self.choices:
                html.append('<option value="{}">{}</option>'.format(quote(choice[0]), quote(choice[1])))
        html.append('</select>')


class Submit(BaseObject):
    def __init__(self, action='', **kwargs):
        self.init(kwargs)
        self.action = self.param(action, 'string', 'Action to run when the form is submitted with this button')

    @ensure_formgroup
    def get_html(self, html):
        on_click = '$("#" + this.form.id + " .form-error").children().remove();'
        on_click += '$(this.form).find("[name=sub_action]").attr("value", "{}");'.format(self.action)
        on_click += 'send_action($(this.form).serialize());'
        html.append('<button type="submit" class="btn btn-primary" onclick=\'{};return false;\'>Submit</button>'.format(on_click))
