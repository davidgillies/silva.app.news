## Script (Python) "clear_session_for_bulk"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
session = context.REQUEST.SESSION

if session.has_key('ids'):
    del session['ids']

if session.has_key('paths'):
    del session['paths']

if session.has_key('fields'):
    del session['fields']
