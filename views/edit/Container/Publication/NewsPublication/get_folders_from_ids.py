## Script (Python) "get_folders_from_ids"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=idlist
##title=
##
view = context
request = view.REQUEST
model = request.model

retval = []

for id in idlist:
    obj = getattr(model, id)
    if obj.implements_container():
        retval.append(id)

return retval
