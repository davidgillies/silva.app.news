## Script (Python) "article_submit_subjects_target_audiences"
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
    result = view.form_subjects_target_audiences.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=view.render_form_errors(e))

model.sec_update_last_author_info()
editable = model.get_editable()
editable.set_subjects(result['subjects'])
editable.set_target_audiences(result['target_audiences'])

return view.tab_edit(message_type="feedback", message="Data changed")
