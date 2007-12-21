from Products.Silva import mangle
from Products.Formulator.Errors import ValidationError, FormValidationError
from Products.Silva.i18n import translate as _

request = context.REQUEST
model = request.model
view = context
editable = model.get_editable()


try:
    result = view.form.validate_all(request)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=view.render_form_errors(e))

subjects = result['subjects']
editable.set_subjects(subjects)

target_audiences = result['target_audiences']
editable.set_target_audiences(target_audiences)


return view.tab_edit(message_type='feedback', message='Silva News Category Filter saved.')
