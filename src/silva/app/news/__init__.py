# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from silva.app.news.installer import install

from silva.core import conf as silvaconf

silvaconf.extension_name("silva.app.news")
silvaconf.extension_title("Silva News Network")
silvaconf.extension_depends(["silva.app.document", "SilvaExternalSources"])


def initialize(context):
    from silva.app.news import indexing
    context.registerClass(
        indexing.IntegerRangesIndex,
        permission = 'Add Pluggable Index',
        constructors = (indexing.manage_addIntegerRangesIndexForm,
                        indexing.manage_addIntegerRangesIndex),
        visibility=None)


# Specify import path for old classes (for upgrade)
CLASS_CHANGES = {
        'silva.app.news.silvaxmlattribute SilvaXMLAttribute':
            'OFS.SimpleItem SimpleItem',

        # filters

        'silva.app.news.AgendaFilter AgendaFilter':
            'silva.app.news.filters.AgendaFilter AgendaFilter',
        'silva.app.news.CategoryFilter CategoryFilter':
            'silva.app.news.filters.CategoryFilter CategoryFilter',
        'silva.app.news.Filter Filter':
            'silva.app.news.filters.Filter Filter',
        'silva.app.news.NewsFilter NewsFilter':
            'silva.app.news.filters.NewsFilter NewsFilter',
        'silva.app.news.NewsItemFilter NewsItemFilter':
            'silva.app.news.filters.NewsItemFilter NewsItemFilter',

        # viewers

        'silva.app.news.AgendaViewer AgendaViewer':
            'silva.app.news.viewers.AgendaViewer AgendaViewer',
        'silva.app.news.NewsViewer NewsViewer':
            'silva.app.news.viewers.NewsViewer NewsViewer',
        'silva.app.news.RSSAggregator RSSAggregator':
            'silva.app.news.viewers.RSSAggregator RSSAggregator',

        # contents
        'silva.app.news.PlainAgendaItem PlainAgendaItem':
            'silva.app.news.AgendaItem AgendaItem',
        'silva.app.news.PlainAgendaItem PlainAgendaItemVersion':
            'silva.app.news.AgendaItem AgendaItemVersion',
        'silva.app.news.PlainArticle PlainArticle':
            'silva.app.news.NewsItem NewsItem',
        'silva.app.news.PlainArticle PlainArticleVersion':
            'silva.app.news.NewsItem NewsItemVersion',
    }

