## Script (Python) "tab_metadata_submit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Formulator.Errors import ValidationError, FormValidationError

model = context.REQUEST.model
form = context.tab_metadata_form
changed_metadata = []

try:
    result = form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_metadata(message_type="error", message='Input form errors %s' % context.render_form_errors(e))

for id, value in result.items():
    if value:
        #---Document title hack---#
        if id == 'object_title':
            if not model.get_title_editable() == value:
                model.set_title(model.input_convert(value))            
                changed_metadata.append(('title', 'changed'))
            continue
        
        # One more hack: is_private is set in a somewhat peculiar manner...
        if id == 'is_private':
           # do something with it outside this loop...
           continue
        
        if model.hasProperty(id):
            if model.getProperty(id) == value:
                continue
            model.manage_changeProperties({id:value})
            changed_metadata.append((id, 'changed'))
        else:
            type = 'string'
            model.manage_addProperty(id, value, type)        
            changed_metadata.append((id, 'added'))
    else:
        if model.hasProperty(id):
            model.manage_delProperties([id])
            changed_metadata.append((id, 'removed'))    

if result.has_key('is_private') and result['is_private']:
    if not model.is_private():
        model.set_private(1)
        changed_metadata.append(('restrict', 'set'))
else:
    if model.is_private():
        model.set_private(0)
        changed_metadata.append(('restrict', 'unset'))

return context.tab_metadata(message_type="feedback", message="Metadata changed for: %s"%(context.quotify_list(changed_metadata)))
