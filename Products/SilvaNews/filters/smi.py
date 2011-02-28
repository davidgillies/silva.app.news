# from five import grok
# from zope.i18nmessageid import MessageFactory
# from silva.core.smi.menu import SMIEditMenuItem
# from silva.core.smi.menu import SMIEditPreviewMenuItem as \
#     SMIEditPreviewMenuItemBase
# from Products.SilvaNews.interfaces import INewsItemFilter

# _ = MessageFactory('silva_news')

# class SMIEditFilterItemsMenuItem(SMIEditMenuItem):
#     grok.context(INewsItemFilter)
#     grok.order(20)

#     name = _(u'items')
#     tab = None
#     path = u'tab_edit_items'


# class SMIEditPreviewMenuItem(SMIEditPreviewMenuItemBase):
#     grok.context(INewsItemFilter)

#     def available(self):
#         """ Disable tab preview for filters """
#         return False
