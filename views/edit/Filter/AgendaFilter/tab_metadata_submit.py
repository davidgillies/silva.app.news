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
form = context.tab_metadata_form
changed_metadata = []

# delete all items removed in service_news from the internal items-lists
deleted = model.synchronize_with_service()
if deleted:
    deleted = str(deleted)[1:-1]
    changed_metadata.append(('lists of subjects and target audiences', 'deleted %s to reflect the lists of the service' % deleted)) 

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_metadata(message_type="error", message='Input form errors %s' % context.render_form_errors(e))

if not model.get_title_editable() == result['object_title']:
    model.set_title(model.input_convert(result['object_title']))
    changed_metadata.append(('title', 'changed'))

# now remove the things that should be removed
for subject in model.subjects():
    if subject not in result['subjects']:
        model.set_subject(subject, 0)
        changed_metadata.append((subject, 'removed'))

for target_audience in model.target_audiences():
    if target_audience not in result['target_audiences']:
        model.set_target_audience(target_audience, 0)
        changed_metadata.append((target_audience, 'removed'))

# now add what's to be added
current_subjects = model.subjects()
for subject in result['subjects']:
    if subject not in current_subjects:
        model.set_subject(subject, 1)
        changed_metadata.append((subject, 'added'))

current_target_audiences = model.target_audiences()
for target_audience in result['target_audiences']:
    if target_audience not in current_target_audiences:
        model.set_target_audience(target_audience, 1)
        changed_metadata.append((target_audience, 'added'))

return context.tab_metadata(message_type="feedback", message="Metadata changed for: %s"%(context.quotify_list(changed_metadata)))
