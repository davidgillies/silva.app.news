## Script (Python) "add_submit_continue"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
model = context.REQUEST.model
view = context
REQUEST = context.REQUEST

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    return view.tab_edit()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result_continue = view.form_subjects_target_audiences.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return view.continue_add(message_type="error", message=view.render_form_errors(e))

# if we don't have the right id, reject adding
if not model.is_id_valid(model.REQUEST.SESSION['id']):
  return view.add(message_type="error", message="%s is not a valid id." % view.quotify(model.REQUEST.SESSION['id']))

# process data in result and add using validation result
object = context.add_submit_helper(model, model.REQUEST.SESSION['id'], model.REQUEST.SESSION['title'], model.REQUEST.SESSION['result'], result_continue)

# update last author info in new object
object.sec_update_last_author_info()

# now go to tab_edit in case of add and edit, back to container if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    return view.tab_edit(message_type="feedback", 
                         message="Added %s %s." % (object.meta_type, view.quotify(model.REQUEST.SESSION['id'])))
