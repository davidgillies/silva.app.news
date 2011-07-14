# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from OFS.SimpleItem import SimpleItem

# Silva
from five import grok
from silva.core import conf as silvaconf
from silva.core.conf.interfaces import ITitledContent
from zeam.form import silva as silvaforms
from zope.i18nmessageid import MessageFactory

# SilvaNews
from Products.SilvaNews.NewsCategorization import NewsCategorization
from Products.SilvaNews.NewsCategorization import INewsCategorizationSchema
from Products.Silva.Publishable import NonPublishable
from Products.SilvaNews.interfaces import ICategoryFilter

_ = MessageFactory('silva_news')


class CategoryFilter(NonPublishable, NewsCategorization, SimpleItem):
    """A Category Filter is useful in large sites where the news articles have
       (too) many subjects and target audiences defined. The Filter will limit
       those that display so only the appropriate ones for that area of the
       site appear.
    """
    meta_type = "Silva News Category Filter"
    grok.implements(ICategoryFilter)
    silvaconf.icon("www/category_filter.png")
    silvaconf.priority(3.6)


class CategoryFilterAddForm(silvaforms.SMIAddForm):
    grok.context(ICategoryFilter)
    grok.name(u'Silva News Category Filter')

    fields = silvaforms.Fields(ITitledContent, INewsCategorizationSchema)


class CategoryFilterEditForm(silvaforms.SMIEditForm):
    """ Base form for filters """
    grok.context(ICategoryFilter)

    fields = silvaforms.Fields(ITitledContent, INewsCategorizationSchema).omit('id')
