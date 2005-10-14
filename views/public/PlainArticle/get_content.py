## Script (Python) "get_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model
##title=
##
return context.REQUEST.model.content.render()
