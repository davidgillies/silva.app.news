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

response = request.RESPONSE
headers = [('Expires', 'Mon, 26 Jul 1997 05:00:00 GMT'),
            ('Last-Modified', 
                DateTime("GMT").strftime("%a, %d %b %Y %H:%M:%S GMT")),
            ('Cache-Control', 'no-cache, must-revalidate'),
            ('Cache-Control', 'post-check=0, pre-check=0'),
            ('Pragma', 'no-cache'),
            ]

placed = []
for key, value in headers:
    if key not in placed:
        response.setHeader(key, value)
        placed.append(key)
    else:
        response.addHeader(key, value)

response.setHeader('Content-Type', 'text/html;charset=utf-8')

docref = model.create_ref(model)
doctitle = version.get_title()
xhtml = version.content.editorHTML()

# gather metadata
service = context.service_news

audject = model.superValues('Silva News Category Filter')
ta_filterby = []
subject_filterby = []
if audject:
    ta_filterby = audject[0].target_audiences()
    subject_filterby = audject[0].subjects()
all_subjects = [(id, '%s%s' % (depth * u'\xa0\xa0', title)) for
                    (id, title, depth) in service.subject_tree(subject_filterby)]
all_target_audiences = [(id, '%s%s' % (depth * u'\xa0\xa0', title)) for
                            (id, title, depth) in 
                                service.target_audience_tree(ta_filterby)]

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

scheme = 'http://infrae.com/namespace/metadata/silva-news-network'
meta_template = (
    '<meta scheme="http://infrae.com/namespace/metadata/silva-news-network" '
    'name="%s" content="%s" />')
metas = [
    meta_template % ('subjects', subjects),
    meta_template % ('target_audiences', target_audiences),
]

if hasattr(version, 'start_datetime'):
    metas.append(meta_template % 
            ('start_datetime', version.start_datetime() or ''))

if hasattr(version, 'end_datetime'):
    metas.append(meta_template % 
            ('end_datetime', version.end_datetime() or ''))

if hasattr(version, 'location'):
    metas.append(meta_template % ('location', version.location()))

return ('<html>\n'
        '<head>\n'
        '<title>%s</title>\n'
        '<link href="%s" type="text/css" rel="stylesheet" />\n'
        '<link href="%s" type="text/css" rel="stylesheet" />\n'
        '%s\n'
        '<meta http-equiv="Content-Type" '
        'content="text/html; charset=UTF-8" />\n'
        '<meta name="docref" content="%s" />\n'
        '</head>\n'
        '<body>\n'
        '<h2>%s</h2>\n'
        '%s\n'
        '</body>\n'
        '</html>' % (doctitle, 
                        getattr(context.globals, 'frontend.css').absolute_url(),
                        getattr(context.globals, 'kupu.css').absolute_url(),
                        '\n'.join(metas),
                        docref,
                        doctitle,
                        xhtml))
