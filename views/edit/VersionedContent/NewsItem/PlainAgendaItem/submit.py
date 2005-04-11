## Script (Python) "pai_submit"
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
view = context
try:
    result = view.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return view.tab_edit(message_type="error", message=view.render_form_errors(e))

model.sec_update_last_author_info()
editable = model.get_editable()

editable.set_title(result['object_title'])
editable.set_display_time(result['display_time'])
editable.set_start_datetime(result['start_datetime'])
editable.set_end_datetime(result['end_datetime'])
editable.set_location(result['location'])

m = _("AgendaItem-data changed")
msg = unicode(m)

return view.tab_edit(message_type="feedback", message=msg)
