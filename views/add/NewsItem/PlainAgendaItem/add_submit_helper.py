## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result, result_continue
##title=
##
model.manage_addProduct['SilvaNews'].manage_addPlainAgendaItem(id, title)
pai = getattr(model, id)

#  Add empty default-data to the object so there will be no exceptions if the data is retrieved
# add the data to the object
editable = pai.get_editable()

editable.set_start_datetime(result['start_datetime'])
editable.set_location(result['location'])
editable.set_location_manual(result['location_manual'])

editable.set_subjects(result_continue['subjects'])
editable.set_target_audiences(result_continue['target_audiences'])

return pai
