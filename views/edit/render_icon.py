## Script (Python) "render_icon"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=meta_type
##title=
##
dict = { 'Silva Root' : 'silva.gif',
         'Silva Publication' : 'silvapublication.gif',
         'Silva Folder' : 'silvafolder.gif',
         'Silva Document' : 'silvadoc.gif',
         'Silva Image' : 'silvaimage.gif',
         'Silva Course' : 'silvacourse.gif',
         'Silva Contact Info' : 'silvacontactinfo.gif',
         'Silva Ghost' : 'silvaghost.gif',
         'Silva DemoObject' : 'silvageneric.gif',
         'Silva News AgendaViewer': 'silvanewsviewer.gif',
         'Silva News NewsViewer': 'silvanewsviewer.gif',
         'Silva News NewsFilter': 'silvanewsfilter.gif',
         'Silva News AgendaFilter': 'silvanewsfilter.gif',
         'Silva News Plain Article': 'silvaagendaitem.gif',
         'Silva News Plain AgendaItem': 'silvanewsitem.gif',
         'Silva News NewsSource': 'silvanewssource.gif',
         }

icon_name = dict.get(meta_type, 'silvageneric.gif')
return '<img src="%s/globals/%s" width="16" height="16" border="0" alt="%s" />' % (context.silva_root(),icon_name, meta_type)
