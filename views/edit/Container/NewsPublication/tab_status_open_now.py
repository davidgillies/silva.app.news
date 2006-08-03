##parameters=refs=None
from Products.Silva.i18n import translate as _
view = context
request = view.REQUEST
model = request.model

if not refs:
  return view.tab_status(message_type='error', 
          message=_('Nothing was selected, so nothing was approved.'))

try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e),
        refs=refs)

clear_expiration = result['clear_expiration']

objects = [model.resolve_ref(ref) for ref in refs]


# set the display_date_time
now = DateTime()
for obj in objects:
    if hasattr(obj, 'implements_newsitem') and obj.implements_newsitem():
        unapproved = getattr(obj, obj.get_unapproved_version())
        if unapproved.display_datetime() is None:
            unapproved.set_display_datetime(now)

message = context.open_now(objects, clear_expiration)

return view.tab_status(message_type='feedback', message=message)
