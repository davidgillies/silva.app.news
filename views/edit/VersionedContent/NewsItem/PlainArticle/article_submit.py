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
model.set_title(result['object_title'])

version = model.get_editable()

version.set_subheader(result['subheader'])
version.set_lead(result['lead'])

model.set_unapproved_version_publication_datetime(result['publication_datetime'])

return view.tab_edit(message_type="feedback", message="Article data changed")
