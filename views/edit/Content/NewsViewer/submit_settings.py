## Script (Python) "newsviewer_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError
model = context.REQUEST.model
view = context
try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=view.render_form_errors(e))

model.sec_update_last_author_info()

if model.number_to_show() != result['number_to_show']:
    model.set_number_to_show(result['number_to_show'])

model.set_number_is_days(result['number_is_days'])

for path in model.findfilters():
    if path in result['filters']:
        model.set_filter(path, 1)
    else:
        model.set_filter(path, 0)

return view.tab_edit(message_type="feedback", message="Viewer data changed")
