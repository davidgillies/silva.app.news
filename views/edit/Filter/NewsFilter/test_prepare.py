## Script (Python) "test_prepare"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
results = context.REQUEST.model.get_all_items()
objects = context.prepare_objects(results)

return "Objects: %s" % [o['object'].getURL() for o in objects]
