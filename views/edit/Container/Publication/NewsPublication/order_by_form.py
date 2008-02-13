## Script (Python) "order_by_form"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=form, inlist
##title=
##
# returns the list, ordered the same as the form (so for each key that is a formfield in the form, the item gets the place it has in the form)

sorted = []
for key in form.get_field_ids():
    if key in inlist:
         inlist.remove(key)
         sorted.append(key)

return sorted + inlist # add any extra fields (probably none) if not processed
