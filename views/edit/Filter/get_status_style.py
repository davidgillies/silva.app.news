## Script (Python) "get_status_style"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=status
##title=
##
if status == 'not_approved':
    return 'redlink'
elif status == 'approved':
    return 'greenlink'
elif status == 'no_next_version' and public == 'closed':
    return 'graylink'
elif status == 'no_next_version':
    return 'bluelink'
else:
    return 'blacklink'
