## Script (Python) "get_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model
##title=
##
context.service_editor.setViewer('service_webshop_sub_viewer')
return context.service_editor.getViewer().getWidget(model.content.documentElement).render()
