## Script (Python) "article_submit"
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
model.set_title(context.input_convert(result['object_title']))

version = model.get_editable()

return view.tab_edit(message_type="feedback", message="Article data changed")
