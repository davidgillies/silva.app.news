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

# I18N stuff
from Products.Silva.i18n import translate as _


model = context.REQUEST.model
form = context.settingsform
rssform = context.rssform
messages = []

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error", message='Input form errors %s' % context.render_form_errors(e))

try:
    rss_result = rssform.validate_all(context.REQUEST)
except FormValidationError, e:
    m = _('RSS form errors ${errors}', 'silva_news')
    m.set_mapping({'errors':context.render_form_errors(e)})
    msg = unicode(m)
    return context.tab_edit(message_type="error", message=msg )

if model.subjects() != result['subjects']:
    model.set_subjects(result['subjects'])
    m = _('subjects changed', 'silva_news')
    msg = unicode(m)
    messages.append(msg)

if model.target_audiences() != result['target_audiences']:
    model.set_target_audiences(result['target_audiences'])
    m = _('target audiences changed', 'silva_news')
    msg = unicode(m)
    messages.append(msg)

if model.show_agenda_items() != result['show_agenda_items']:
    model.set_show_agenda_items(result['show_agenda_items'])
    m = _('show agendaitems changed', 'silva_news')
    msg = unicode(m)
    messages.append(msg)

if model.keep_to_path() != result['keep_to_path']:
    model.set_keep_to_path(result['keep_to_path'])
    m = _('stick to path changed', 'silva_news')
    msg = unicode(m)
    messages.append(msg)

# RSS export disabled, might want to turn it on later
"""
if model.allow_rss_export() != result['allow_rss_export']:
    model.set_allow_rss_export(result['allow_rss_export'])
    messages.append('allow rss export changed')

if model.rss_description() != rss_result['rss_description']:
    model.set_rss_description(rss_result['rss_description'])
    messages.append('rss description changed')

if model.rss_link() != rss_result['rss_link']:
    model.set_rss_link(rss_result['rss_link'])
    messages.append('rss link changed')

if model.rss_copyright() != rss_result['rss_copyright']:
    model.set_rss_copyright(rss_result['rss_copyright'])
    messages.append('rss copyright changed')

if model.allow_rss_search() != rss_result['allow_rss_search']:
    model.set_allow_rss_search(rss_result['allow_rss_search'])
    messages.append('allow rss search changed')

if model.rss_search_description() != rss_result['rss_search_description']:
    model.set_rss_search_description(rss_result['rss_search_description'])
    messages.append('rss search description')
"""

m = _('Settings changed for: ', 'silva_news')
msg = unicode(m)

msg = msg + u', '.join(messages)

return context.tab_edit(message_type="feedback", message=msg)
