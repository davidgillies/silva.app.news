## Script (Python) "x_do_search"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=query, meta_types
##title=
##
view = context;
request = view.REQUEST;

query = {'meta_type': meta_types, 'fulltext': query}

return view.service_catalog(query)
