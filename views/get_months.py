## Script (Python) "get_months"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# I18N stuff
from Products.Silva.i18n import translate as _


months = [ _('Jan','silva_news'),
           _('Feb','silva_news'),
           _('Mar','silva_news'),
           _('Apr','silva_news'),
           _('May','silva_news'),
           _('Jun','silva_news'),
           _('Jul','silva_news'),
           _('Aug','silva_news'),
           _('Sep','silva_news'),
           _('Oct','silva_news'),
           _('Nov','silva_news'),
           _('Dec','silva_news') ]

return [ unicode(m) for m in months ]
