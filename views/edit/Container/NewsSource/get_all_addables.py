## Script (Python) "get_all_addables"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return [(item, item) for item in context.get_silva_addables_all()]
