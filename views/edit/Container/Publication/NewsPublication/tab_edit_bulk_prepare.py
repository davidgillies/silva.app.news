## Script (Python) "tab_edit_bulk_prepare"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


view = context
request = view.REQUEST
session = request.SESSION
model = request.model
form = view.tab_edit_bulk_edit_form

if (not request.has_key('ids') or not request['ids']) and not session.has_key('ids'):
    return view.tab_edit(message_type='error', message='No items selected')

if not session.has_key('ids'):
    # add ids to request for later processing
    session['ids'] = request['ids']

# now walk through the ids, if one (or more) of the items is a folder, ask if the folders should be recursively walked through
if not request.has_key('from_folder'):
    # we are not coming from the ask_recurse-zpt
    for id in session['ids']:
        obj = getattr(view, id)
        if obj.implements_container():
            return view.tab_edit_bulk_ask_recurse()

field_ids = form.get_field_ids()

fields, paths = model.get_fields_for_bulk_editing(field_ids, session['ids'])

session['fields'] = fields
session['paths'] = paths

return view.tab_edit_bulk()
