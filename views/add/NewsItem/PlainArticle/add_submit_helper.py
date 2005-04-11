## Script (Python) "add_submit_helper"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=model, id, title, result
##title=
##
model.manage_addProduct['SilvaNews'].manage_addPlainArticle(id, title)
article = getattr(model, id)
version = article.get_editable()
version.set_subjects(result['subjects'])
version.set_target_audiences(result['target_audiences'])

return article
