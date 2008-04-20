## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
model.manage_addProduct['SilvaNews'].manage_addPlainAgendaItem(id, title)
pai = getattr(model, id)
version = pai.get_editable()
version.set_subjects(result['subjects'])
version.set_target_audiences(result['target_audiences'])
version.set_start_datetime(result['start_datetime'])
version.set_end_datetime(result['end_datetime'])
version.set_location(result['location'])

return pai
