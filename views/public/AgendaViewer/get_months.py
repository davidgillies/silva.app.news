## Script (Python) "get_months"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
months = []
for i in range(12):
    dt = DateTime("1970/%s/01" % str(i + 1))
    months.append(dt.aMonth())

return months
