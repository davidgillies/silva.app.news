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
    changed_metadata.append(('lists of subjects and target audiences', 'deleted %s to reflect the lists of the service' % str(deleted))) 

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

if result['show_agenda_items'] != model.show_agenda_items():
    model.set_show_agenda_items(result['show_agenda_items'])
    changed_metadata.append(('show_agenda_items', 'updated'))

if result['rss_description'] != model.rss_description():
    model.set_rss_description(result['rss_description'])
    changed_metadata.append(('rss_description', 'updated'))

if result['rss_link'] != model.rss_link():
    model.set_rss_link(result['rss_link'])
    changed_metadata.append(('rss_link','changed'))

if result['rss_copyright'] != model.rss_copyright():
    model.set_rss_copyright(result['rss_copyright'])
    changed_metadata.append(('rss_copyright', 'changed'))

if not not result['allow_rss_export'] != model.allow_rss_export():
    model.set_allow_rss_export(result['allow_rss_export'])
    changed_metadata.append(('allow_rss_export', 'changed'))

return context.tab_metadata(message_type="feedback", message="Metadata changed for: %s"%(context.quotify_list(changed_metadata)))
