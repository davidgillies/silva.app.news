## Script (Python) "use_items"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# Updates the items to show in this filter
view = context
request = view.REQUEST
sesslist = request.SESSION['objects']
model = request.model

# the only purpose retval serves is informatory, will be printed after submittance
retval = []

# add the physical path of the filter to the filterlist of each object if the checkbox is checked (too much overhead to check first?)
# and remove it if the checkbox is not checked and the object has the physical path of the current filter in its list
for (index, object_path, obj_id) in sesslist:
  on_or_off = request.has_key('cb') and 'cb_%s' % index in request['cb']
  model.set_excluded_item(object_path, not on_or_off)

  retval.append("%s - %s" % (str(object_path), on_or_off))

year = ''
if request.has_key('year'):
    year = request['year']

month = ''
if request.has_key('month'):
    year = request['month']

return view.tab_edit_items(message_type='feedback', message='The filter is updated.', month=month, year=year)
