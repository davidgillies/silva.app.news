## Script (Python) "settings_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# I18N stuff
from Products.Silva.i18n import translate as _

view = context
request = view.REQUEST
model = request.model

message = 'Nothing changed.'
message_type = 'error'
current_private = model.is_private()
is_private = request.has_key('is_private')

if is_private != current_private:
    model.set_private(is_private)
    m = _('Settings changed.', 'silva_news')
    message = unicode(m)
    message_type = 'feedback'
    model.sec_update_last_author_info()

return view.tab_edit(message_type=message_type, message=message)
