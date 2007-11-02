## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##

model.manage_addProduct['SilvaNews'].manage_addCategoryFilter(id, title)
catfilter = getattr(model, id)

subjects = result['subjects']
target_audiences = result['target_audiences']

catfilter.set_subjects(subjects)
catfilter.set_target_audiences(target_audiences)

return catfilter


