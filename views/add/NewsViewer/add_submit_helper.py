## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
model.manage_addProduct['SilvaNews'].manage_addNewsViewer(id, title)
viewer = getattr(model, id)

return viewer
