## Script (Python) "register_silva_news"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.register('edit', 'Silva AgendaFilter', ['edit', 'Filter', 'AgendaFilter'])
context.register('public', 'Silva AgendaFilter', ['public', 'Filter', 'AgendaFilter'])
context.register('add', 'Silva AgendaFilter', ['add', 'AgendaFilter'])

context.register('edit', 'Silva NewsFilter', ['edit', 'Filter', 'NewsFilter'])
context.register('public', 'Silva NewsFilter', ['public', 'Filter', 'NewsFilter'])
context.register('add', 'Silva NewsFilter', ['add', 'NewsFilter'])

context.register('edit', 'Silva NewsSource', ['edit', 'Container', 'NewsSource'])
context.register('public', 'Silva NewsSource', ['public', 'NewsSource'])
context.register('add', 'Silva NewsSource', ['add', 'NewsSource'])

context.register('edit', 'Silva NewsViewer', ['edit', 'Content', 'NewsViewer'])
context.register('public', 'Silva NewsViewer', ['public', 'NewsViewer'])
context.register('add', 'Silva NewsViewer', ['add', 'NewsViewer'])

context.register('edit', 'Silva AgendaViewer', ['edit', 'Content', 'AgendaViewer'])
context.register('public', 'Silva AgendaViewer', ['public', 'AgendaViewer'])
context.register('add', 'Silva AgendaViewer', ['add', 'AgendaViewer'])

context.register('edit', 'Silva News PlainArticle', ['edit', 'VersionedContent', 'NewsItem', 'PlainArticle'])
context.register('public', 'Silva News PlainArticle', ['public', 'PlainArticle'])
context.register('add', 'Silva News PlainArticle', ['add', 'NewsItem', 'PlainArticle'])

context.register('edit', 'Silva News PlainAgendaItem', ['edit', 'VersionedContent', 'NewsItem', 'PlainAgendaItem'])
context.register('public', 'Silva News PlainAgendaItem', ['public', 'PlainAgendaItem'])
context.register('add', 'Silva News PlainAgendaItem', ['add', 'NewsItem', 'PlainAgendaItem'])

return "Done"
