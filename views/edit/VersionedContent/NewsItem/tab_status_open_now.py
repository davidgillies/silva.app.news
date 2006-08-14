from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
model = request.model


try:
    result = view.tab_status_form.validate_all_to_request(request)
except FormValidationError, e:
    return view.tab_status(
        message_type='error', 
        message=view.render_form_errors(e),
        refs=refs)

# set the display_date_time
now = DateTime()
if hasattr(obj, 'implements_newsitem') and model.implements_newsitem():
    unapproved = model.get_unapproved_version()
    if unapproved is None:
        continue
    unapproved = getattr(model, unapproved)
    if unapproved.display_datetime() is None:
        unapproved.set_display_datetime(now)

message = context.open_now(model, clear_expiration)

return view.tab_status(message_type='feedback', message=message)
