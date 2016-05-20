from django.core import signing
from django.utils.html import escape

from shark.base import BaseObject, Default
from shark.common import iif, attr
from shark.resources import Resources

# Resources.add_resource('https://cdnjs.cloudflare.com/ajax/libs/1000hz-bootstrap-validator/0.10.1/validator.min.js', 'js', 'validator', 'main')

class FieldError(BaseObject):
    sub_classes = {}

    def __init__(self, field_name, **kwargs):
        self.init(kwargs)
        self.field_name = self.param(field_name, 'string', 'Name of the field to show errors for')

        if self.class_name not in SharkForm.sub_classes:
            FieldError.sub_classes[self.class_name] = self.__class__
            print(self.class_name)

    @property
    def class_name(self):
        return '{}.{}'.format(str(self.__class__.__module__), self.__class__.__name__)

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
        self.form.form_data['fld-' + self.field_name] = self.class_name
        self.add_class('form-error')
        self.add_class(self.html_class_name)
        self.render_container(html)

    @property
    def html_class_name(self):
        return 'error-{}'.format(self.field_name.replace('.', '--'))


class SpanBrFieldError(FieldError):
    def render_container(self, html):
        self.add_class('help-block with-errors')
        html.append('<span' + self.base_attributes + '></span>')

    def render_error(self, html, message):
        html.append('<span class="text-danger">')
        html.render('    ', message)
        html.append('</span><br>')


class FormError(BaseObject):
    sub_classes = {}

    def __init__(self, form_id=None, **kwargs):
        self.init(kwargs)
        self.form_id = form_id

        if self.class_name not in SharkForm.sub_classes:
            FormError.sub_classes[self.class_name] = self.__class__
            print(self.class_name)

    @property
    def class_name(self):
        return '{}.{}'.format(str(self.__class__.__module__), self.__class__.__name__)

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
        self.add_class(self.html_class_name)
        self.render_container(html)

    @property
    def html_class_name(self):
        return 'error-{}'.format(self.form_id or self.form.id)


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


class SharkFieldDefinition():
    def __init__(self, *args, required=False, **kwargs):
        self.name = None
        self.field = None
        self.validators = []
        if required:
            self.validators.append(RequiredValidator())

        for arg in args:
            if isinstance(arg, Validator):
                self.validators.append(arg)

        self.value = None
        self.value_set = False

    def set_field(self, field):
        self.field = field
        for validator in self.validators:
            validator.set_field(field)

    def set_value(self, value):
        self.value = value
        self.value_set = True

    def value_from_string(self, value):
        return value

    @property
    def default_object(self):
        return None


class CharField(SharkFieldDefinition):
    @property
    def default_object(self):
        return TextField


class EmailField(SharkFieldDefinition):
    pass


class IntField(SharkFieldDefinition):
    def value_from_string(self, value):
        return int(value)


class SharkField:
    def __init__(self, field_definition, form, name, full_name, value=Default):
        self.field_definition = field_definition
        self.form = form
        self.name = name
        self.full_name = full_name
        self.display_name = self.name.replace('_', ' ').title()
        if value == Default:
            if field_definition.value_set:
                self.value = field_definition.value
            else:
                self.value = ''
        else:
            self.value = value

        self.field_definition.set_field(self)

    def validate(self):
        for validator in self.field_definition.validators:
            validator.validate(self)

    def add_error(self, message):
        self.form.errors.append(ValidationError(self, message))


class SharkForm:
    sub_classes = {}

    def __init__(self):
        self.fields = {}
        self.errors = []

        if self.class_name not in SharkForm.sub_classes:
            SharkForm.sub_classes[self.class_name] = self.__class__
            print(self.class_name)

        for name, field in vars(self.__class__).items():
            if isinstance(field, SharkFieldDefinition):
                field.name = name

    @property
    def class_name(self):
        return '{}.{}'.format(str(self.__class__.__module__), self.__class__.__name__)

    def add_error(self, message):
        self.errors.append(ValidationError(None, message))

    def load_fields(self):
        fields = {}
        for name, field in vars(self.__class__).items():
            if isinstance(field, SharkFieldDefinition):
                fields[name] = field

        return fields

    def load_sub_forms(self):
        sub_forms = {}
        for name, form in vars(self.__class__).items():
            if isinstance(form, SharkForm):
                sub_forms[name] = form

        return sub_forms

    def setup_form(self, base_form=None, parent_field_name=None):
        base_form = base_form or self
        for field_name, field_definition in self.load_fields().items():
            full_field_name = (parent_field_name + '.' if parent_field_name else '') + field_name
            new_field = SharkField(field_definition, base_form, field_name, full_field_name)
            base_form.fields[full_field_name] = new_field
            self.__setattr__(field_name, new_field.value)

        for form_name, sub_form in self.load_sub_forms().items():
            self.__setattr__(form_name, sub_form)
            sub_form.setup_form(base_form, form_name)


    def setup_post(self, field_values, base_form=None, parent_field_name=None):
        base_form = base_form or self
        for field_name, field_definition in self.load_fields().items():
            full_field_name = (parent_field_name + '.' if parent_field_name else '') + field_name
            if full_field_name in field_values:
                new_field = SharkField(field_definition, base_form, field_name, full_field_name, field_definition.value_from_string(field_values[full_field_name]))
                base_form.fields[full_field_name] = new_field
                self.__setattr__(field_name, new_field.value)

        for form_name, sub_form in self.load_sub_forms().items():
            self.__setattr__(form_name, sub_form)
            sub_form.setup_post(field_values, base_form, form_name)

    def save(self):
        pass

    def validate(self):
        pass

    def _validate(self):
        for field in self.fields.values():
            field.validate()
        self.validate()

    def serialize(self):
        return ''

    def deserialize(self, value):
        if value!='':
            raise ValueError('Bad input')


class ValidationError:
    def __init__(self, field, message):
        self.field = field
        self.message = message


class Validator():
    def __init__(self, message=''):
        self.field = None
        self.message = message

    def init(self):
        pass

    def set_field(self, field):
        self.field = field
        self.init()

    def enable_live_validation(self, web_object):
        pass


class RequiredValidator(Validator):
    def init(self):
        if not self.message:
            self.message = '{} is required'.format(self.field.display_name)

    def validate(self, field):
        if not self.field.value:
            self.field.add_error(self.message)

    def enable_live_validation(self, web_object):
        web_object.add_attribute('required', 'required')
        web_object.add_attribute('data-required-error', self.message)


class RemoteValidator(Validator):
    def validate(self):
        pass #Server side

    def enable_live_validation(self, web_object):
        web_object.add_attribute('')

class Form(BaseObject):
    def __init__(self, form=None, items=None, **kwargs):
        self.init(kwargs)
        self.form = self.param(form, 'SharkForm', 'The form to render')
        self.items = self.param(items, 'Collection', 'Items in the form')
        self.id_needed()
        self.error_object = None
        self.form.setup_form()
        self.form_data = {'formid': self.id, 'form': '{}({})'.format(self.form.class_name, self.form.serialize())}

    def get_html(self, html):
        html.append('<form' + self.base_attributes + ' role="form" data-toggle="validator" data-async>')
        html.append('    <input type="hidden" name="action" value="_handle_form_post">')
        html.append('    <input type="hidden" name="post_action" value="">')
        html.render('    ', self.items)
        if not self.error_object:
            self.error_object = SpanBrFormError()
            self.error_object.parent = self
            html.render('    ', self.error_object)

        self.form_data['formerror'] = self.error_object.class_name
        #TODO: Is this secure, should we add session_id or user_id or csrf_token?
        form_data = signing.dumps('|'.join([key + '=' + value for key, value in self.form_data.items()]))
        html.append('    <input type="hidden" name="form_data" value="{}">'.format(form_data))
        html.append('</form>')


class Field:
    def __new__(cls, field_description, *args, **kwargs):
        obj = object.__new__(field_description.default_object, *args, **kwargs)
        obj.__init__(field_description.name, *args, **kwargs)
        return obj

    def __init__(self, *args, **kwargs):
        pass


class BaseField(BaseObject):
    def __init__(self, name=None, value=Default, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the field')
        self.value = self.param(value, 'string', 'Starting value of the field', Default)

    def get_html(self, html):
        form = html.find_parent(Form).form
        field = form.fields[self.name]
        html.append('<input type="text" name="{}" value="{}">'.format(field.name, field.value if self.value==Default else self.value))


class TextField(BaseField):
    def __init__(self,  name='', label='', placeholder='', auto_focus=False,
                 help_text='', value=Default, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the field')

        self.label = self.param(label, 'string', 'Text of the label')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')

        self.value = self.param(value, 'string', 'Starting value of the field', Default)

    def get_html(self, html):
        form = html.find_parent(Form).form
        field = form.fields[self.name]
        for validator in field.field_definition.validators:
            validator.enable_live_validation(self)

        html.append('<div class="form-group has-feedback">')

        if self.label or field.display_name:
            html.append('    <label for="' + self.id + '">' + (self.label or escape(field.display_name)) + '</label>')

        html.append('    <input type="text" class="form-control"' +
                    self.base_attributes +
                    attr('name', self.name) +
                    attr('value', field.value if self.value == Default else self.value) +
                    attr('placeholder', self.placeholder) +
                    iif(self.auto_focus, ' data-autofocus') +
                    '>')
        html.append('    <span class="glyphicon form-control-feedback" aria-hidden="true"></span>')

        field_error = SpanBrFieldError(self.name)
        html.append('    <span class="help-block">')
        field_error.get_html(html)
        html.append('        ' + self.help_text)
        html.append('    </span>')

        html.append('</div>')


class TextField(BaseField):
    def __init__(self,  name='', label='', placeholder='', auto_focus=False,
                 help_text='', value=Default, **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'string', 'Name of the field')

        self.label = self.param(label, 'string', 'Text of the label')
        self.placeholder = self.param(placeholder, 'string', 'Placeholder if input is empty')
        self.auto_focus = self.param(auto_focus, 'boolean', 'Place the focus on this element')
        self.help_text = self.param(help_text, 'string', 'help text for the input field')

        self.value = self.param(value, 'string', 'Starting value of the field', Default)

    def get_html(self, html):
        form = html.find_parent(Form).form
        field = form.fields[self.name]
        for validator in field.field_definition.validators:
            validator.enable_live_validation(self)

        html.append('<div class="form-group has-feedback">')

        if self.label or field.display_name:
            html.append('    <label for="' + self.id + '">' + (self.label or escape(field.display_name)) + '</label>')

        html.append('    <input type="text" class="form-control"' +
                    self.base_attributes +
                    attr('name', self.name) +
                    attr('value', field.value if self.value == Default else self.value) +
                    attr('placeholder', self.placeholder) +
                    iif(self.auto_focus, ' data-autofocus') +
                    '>')
        html.append('    <span class="glyphicon form-control-feedback" aria-hidden="true"></span>')

        field_error = SpanBrFieldError(self.name)
        html.append('    <span class="help-block">')
        field_error.get_html(html)
        html.append('        ' + self.help_text)
        html.append('    </span>')

        html.append('</div>')


class Submit(BaseObject):
    def __init__(self, action='', **kwargs):
        self.init(kwargs)
        self.action = self.param(action, 'string', 'Action to run when the form is submitted with this button')

    def get_html(self, html):
        on_click = '$("#" + this.form.id + " .form-error").children().remove();'
        on_click += '$(this.form).find("[name=post_action]").attr("value", "{}");'.format(self.action)
        on_click += 'send_action($(this.form).serialize());'
        html.append('<div class="form-group">')
        html.append('    <button type="submit" class="btn btn-primary" onclick=\'{};return false;\'>Submit</button>'.format(on_click))
        html.append('</div>')


