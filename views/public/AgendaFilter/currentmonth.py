## Script (Python) "currentmonth"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
months = context.get_months()
currentmonth = months[DateTime().month() - 1]

return currentmonth
