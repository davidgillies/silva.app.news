from Products.Silva.i18n import translate as _
model = context.REQUEST.model
view = context

if not model.get_unapproved_version():
    # SHORTCUT: To allow approval of closed docs with no new version available,
    # first create a new version. This "shortcuts" the workflow.
    # See also edit/Container/tab_status_approve.py
    if model.is_version_published():
        return view.tab_edit(
            message_type="error", 
            message=_("There is no unapproved version to approve."))
    model.create_copy()

import DateTime

now = DateTime.DateTime()
editable = model.get_editable()
model.set_unapproved_version_publication_datetime(now)
if editable.display_datetime() is None:
    editable.set_display_datetime(now)
model.approve_version()

if hasattr(model, 'service_messages'):
    model.service_messages.send_pending_messages()
    
return view.tab_preview(message_type="feedback", message=_("Version approved."))
