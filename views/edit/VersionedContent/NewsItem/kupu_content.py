## Script (Python) "get_edit_mode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
view = context
request = view.REQUEST
model = request.model
version = model.get_editable()

def entitize_and_escape_pipes(str):
    """Escapes all XML entities in str and escapes all pipes.
    
        This is done so the str can be used as the value of a pipe-seperated
        string, which is used as the value of a metadata tag (to be used by
        Kupu's SilvaPropertyTool later on).

        Escaping of a pipe happens with an invented entity '&pipe;'.
    """
    str = str.replace('&', '&amp;')
    str = str.replace('"', '&quot;')
    str = str.replace('<', '&lt;')
    str = str.replace('>', '&gt;')
    str = str.replace('|', '&pipe;')
    return str

context.set_cache_headers()
context.set_content_type()
docref = model.create_ref(model)
doctitle = version.get_title()
xhtml = version.content.editorHTML()

# gather metadata
service = context.service_news
all_subjects = service.subjects()
all_target_audiences = service.target_audiences()

item_subjects = version.subjects()
item_target_audiences = version.target_audiences()

subjects = []
for id, title in all_subjects:
    checked = id in item_subjects and 'true' or 'false'
    subjects.append('%s|%s|%s' % (
        entitize_and_escape_pipes(id), 
        entitize_and_escape_pipes(title), 
        checked)
    )

target_audiences = []
for id, title in all_target_audiences:
    checked = id in item_target_audiences and 'true' or 'false'
    target_audiences.append('%s|%s|%s' % (
        entitize_and_escape_pipes(id), 
        entitize_and_escape_pipes(title), 
        checked)
    )

subjects = '||'.join(subjects)
target_audiences = '||'.join(target_audiences)

return ('<html>\n'
        '<head>\n'
        '<title>%s</title>\n'
        '<link href="%s" type="text/css" rel="stylesheet" />\n'
        '<meta scheme="http://infrae.com/namespaces/metadata/silva-news" '
        'name="subjects" content="%s" />\n'
        '<meta scheme="http://infrae.com/namespaces/metadata/silva-news" '
        'name="target_audiences" content="%s" />\n'
        '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />\n'
        '</head>\n'
        '<h2>%s</h2>\n'
        '%s\n'
        '</html>' % (doctitle, 
                        getattr(context.globals, 'kupu.css').absolute_url(),
                        subjects,
                        target_audiences,
                        doctitle,
                        xhtml))