## Script (Python) "prepare_objects"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=results
##title=
##
view = context
model = view.REQUEST.model

objlist = []
sessobjlist = []
model = view.REQUEST.model

# OLD CODE
for i in range(len(results)):
    obj = results[i]
    object_path = obj.object_path
    check_checkbox = obj.object_path not in model.excluded_items()
    oi = {'index': i, 'object': obj, 'check_checkbox': check_checkbox}
    os = (i, object_path, obj.id)
    objlist.append(oi)
    sessobjlist.append(os)

context.REQUEST.SESSION['objects'] = sessobjlist
return objlist
