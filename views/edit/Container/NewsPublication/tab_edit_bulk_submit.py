## Script (Python) "tab_edit_bulk_submit"
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

view = context
request = view.REQUEST
session = request.SESSION
model = request.model
form = view.tab_edit_bulk_edit_form

messages = {}

# walk through all objects and set the data if neccesary
for path in session['paths']:
    obj = view.restrictedTraverse(path)
    version = obj.get_editable()
    for key in session['fields'].keys():
        if session['fields'][key] is not None and hasattr(version, 'set_%s' % key):
            value = form.get_field(key).validate(request)
            if value and not value == DateTime(0):
                if key == 'more_info_links':
                    linklist = []
                    for entry in value.split('\n'):
                        if entry.find('|') > -1:
                            linklist.append(entry.split('|'))
                        else:
                            linklist.append([entry, entry])
                    value = linklist
                getattr(version, 'set_%s' % key)(value)
                m = _('${path} is updated', 'silva_news')
                m.set_mapping('path':path[-1])
                messages[path] = unicode(m)
##                 messages[path] = '%s is updated' % path[-1]

del session['ids']
del session['fields']
del session['paths']

return view.tab_edit(message_type='feedback', message=u', '.join(messages.values()))
