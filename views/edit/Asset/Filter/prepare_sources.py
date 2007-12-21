## Script (Python) "prepare_sources"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=results
##title=
##
model = context.REQUEST.model

sourcelist = []
sesslist = []

for i in range(len(results)):
    obj = results[i]
    ref = obj.getPath()
    check_checkbox = ref in model.sources()
    si = {'index': i, 'object': obj, 'check_checkbox': check_checkbox}
    ss = (i, ref)
    sourcelist.append(si)
    sesslist.append(ss)

context.REQUEST.SESSION['sources'] = sesslist
return sourcelist
