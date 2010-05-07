# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok

from Products.SilvaNews.interfaces import INewsItem
from Products.SilvaDocument.browser.kupu_content import KupuContent

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

META_TEMPLATE = (
    '<meta scheme="http://infrae.com/namespace/metadata/silva-news-network" '
    'name="%s" content="%s" />')


class NewsItemKupuContent(KupuContent):
    """Return content to edit in Kupu for a news item.
    """
    grok.context(INewsItem)

    def update(self):
        super(NewsItemKupuContent, self).update()

        # gather metadata
        version = self.context.get_editable()
        service = self.context.service_news
        timezone = service.get_timezone()

        audject = self.context.superValues('Silva News Category Filter')
        ta_filterby = []
        subject_filterby = []
        if audject:
            ta_filterby = audject[0].target_audiences()
            subject_filterby = audject[0].subjects()
        all_subjects = [(id, '%s%s' % (depth * u'\xa0\xa0', title)) for
                        (id, title, depth) in
                        service.subject_tree(subject_filterby)]
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
                    checked))

        target_audiences = []
        for id, title in all_target_audiences:
            checked = id in item_target_audiences and 'true' or 'false'
            target_audiences.append('%s|%s|%s' % (
                    entitize_and_escape_pipes(id),
                    entitize_and_escape_pipes(title),
                    checked))

        subjects = '||'.join(subjects)
        target_audiences = '||'.join(target_audiences)

        metas = [
            META_TEMPLATE % ('subjects', subjects),
            META_TEMPLATE % ('target_audiences', target_audiences)]

        if hasattr(version, 'start_datetime'):
            metas.append(
                META_TEMPLATE %
                ('start_datetime', version.start_datetime(timezone) or ''))

        if hasattr(version, 'end_datetime'):
            metas.append(
                META_TEMPLATE %
                ('end_datetime', version.end_datetime(timezone) or ''))

        if hasattr(version, 'location'):
            metas.append(META_TEMPLATE % ('location', version.location()))

        self.metadata = ''.join(metas)
