##parameters=ids=None
from Products.Silva.i18n import translate as _
view = context
request = view.REQUEST
model = request.model

if not ids:
  return view.tab_edit(message_type='error', 
          message=_('Nothing was selected, so nothing was approved.'))

objects = [getattr(model, id) for id in ids]

# set the display_date_time
now = DateTime()
for obj in objects:
    if hasattr(obj, 'implements_newsitem') and obj.implements_newsitem():
        unapproved = obj.get_unapproved_version()
        if unapproved is None:
            continue
        unapproved = getattr(obj, unapproved)
        if unapproved.display_datetime() is None:
            unapproved.set_display_datetime(now)

message = context.open_now(objects)

return view.tab_edit(message_type='feedback', message=message)
