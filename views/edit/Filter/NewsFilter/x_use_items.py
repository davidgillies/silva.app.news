## Script (Python) "x_use_items"
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
sesslist = request.SESSION['objects']
phPath = request.model.getPhysicalPath()

# the only purpose retval serves is informatory, will be printed after submittance
retval = []

# add the physical path of the source to the sourcelist of each object if the checkbox is checked (too much overhead to check first?)
# and remove it if the checkbox is not checked and the object has the physical path of the current source in its list
for (id, ref) in sesslist:
    obj = context.restrictedTraverse(ref)
    on_or_off = request.has_key('cb') and 'cb_%s' % id in request['cb']
    obj.set_source(phPath, on_or_off)

    retval.append("%s - %s" % (str(obj), on_or_off))

year = ''
if request.has_key('year'):
    year = request['year']

month = ''
if request.has_key('month'):
    month = request['month']

return view.tab_edit(message_type='feedback', message='The source is updated.', month=month, year=year, startat=request['start'])
