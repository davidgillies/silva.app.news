## Script (Python) "tab_metadata_submit"
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
form = context.settingsform
messages = []

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message='Input form errors %s' % context.render_form_errors(e))

if model.subjects() != result['subjects']:
    model.set_subjects(result['subjects'])
    messages.append('subjects changed')

if model.target_audiences() != result['target_audiences']:
    model.set_target_audiences(result['target_audiences'])
    messages.append('target audiences changed')

if model.keep_to_path() != result['keep_to_path']:
    model.set_keep_to_path(result['keep_to_path'])
    messages.append('stick to path changed')

return context.tab_edit(message_type="feedback", message="Settings changed for: %s" % (context.quotify_list(messages)))
