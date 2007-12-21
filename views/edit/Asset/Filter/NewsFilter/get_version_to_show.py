## Script (Python) "get_version_to_show"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object
##title=
##
objectdict = object[1]

if objectdict.has_key('unapproved'):
    return objectdict['unapproved']
elif objectdict.has_key('approved'):
    return objectdict['approved']
elif objectdict.has_key('public'):
    return objectdict['public']
else:
    return objectdict['last_closed']
