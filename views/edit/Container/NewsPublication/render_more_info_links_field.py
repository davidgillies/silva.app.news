## Script (Python) "render_more_info_links_field"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=more_info_list
##title=
##
retval = ''

for item in more_info_list:
    if len(item) == 2:
        retval += '%s|%s' % (item[0], item[1])
    else:
        retval += '%s|%s' % (item[0], item[0])

return retval
