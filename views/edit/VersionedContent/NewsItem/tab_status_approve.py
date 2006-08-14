from Products.Silva.i18n import translate as _
from Products.Formulator.Errors import ValidationError, FormValidationError

model = context.REQUEST.model
view = context

if not model.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # See also edit/Container/tab_status_approve.py
    if model.is_version_published():
        return view.tab_status(
            message_type="error", 
            message=_("There is no unapproved version to approve."))
    model.create_copy()

try:
    result = view.tab_status_form_editor.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_status(
        message_type="error", message=view.render_form_errors(e))

try:
    result_news_form = view.tab_status_form_news.validate_all(context.REQUEST)
except FormValidationError, e:
    # highly unlikely
    return view.tab_status(message_type='error', 
                                message='Error in display datetime fields')

import DateTime

unapproved = getattr(model, model.get_unapproved_version())
if (hasattr(unapproved, 'implements_newsitem') and 
        unapproved.implements_newsitem()):
    # set display datetime
    pdt = result['publish_datetime']
    ddt = result_news_form['display_datetime']
    if ddt is None:
        ddt = pdt
    unapproved.set_display_datetime(ddt)
elif unapproved.display_datetime() is None:
    # there's no initial display datetime yet, let's set it
    unapproved.set_display_datetime(pdt)
else:
    raise 'not a news item'
    
model.set_unapproved_version_publication_datetime(result['publish_datetime'])

expiration = result['expiration_datetime']
if expiration:
    model.set_unapproved_version_expiration_datetime(expiration)

model.approve_version()

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()
    
return view.tab_status(message_type="feedback", message=_("Version approved."))
