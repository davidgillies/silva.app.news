import AgendaFilter, NewsFilter, ServiceNews
import NewsSource, NewsViewer, AgendaViewer
import PlainArticle, PlainAgendaItem
from Products.PythonScripts.Utility import allow_module
from AccessControl import ModuleSecurityInfo

def initialize(context):

    ModuleSecurityInfo('Products').declarePublic('SilvaNews')
    ModuleSecurityInfo('Products.SilvaNews').declarePublic('install')
    ModuleSecurityInfo('Products.SilvaNews.install').declarePublic('NewsInstaller')

    context.registerClass(
        AgendaFilter.AgendaFilter,
        constructors = (AgendaFilter.manage_addAgendaFilterForm,
                        AgendaFilter.manage_addAgendaFilter),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        NewsFilter.NewsFilter,
        constructors = (NewsFilter.manage_addNewsFilterForm,
                        NewsFilter.manage_addNewsFilter),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        ServiceNews.ServiceNews,
        constructors = (ServiceNews.manage_addServiceNewsForm,
                        ServiceNews.manage_addServiceNews),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        NewsSource.NewsSource,
        constructors = (NewsSource.manage_addNewsSourceForm,
                        NewsSource.manage_addNewsSource),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        NewsViewer.NewsViewer,
        constructors = (NewsViewer.manage_addNewsViewerForm,
                        NewsViewer.manage_addNewsViewer),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        AgendaViewer.AgendaViewer,
        constructors = (AgendaViewer.manage_addAgendaViewerForm,
                        AgendaViewer.manage_addAgendaViewer),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        PlainArticle.PlainArticle,
        constructors = (PlainArticle.manage_addPlainArticleForm,
                        PlainArticle.manage_addPlainArticle),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        PlainArticle.PlainArticleVersion,
        constructors = (PlainArticle.manage_addPlainArticleVersionForm,
                        PlainArticle.manage_addPlainArticleVersion),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        PlainAgendaItem.PlainAgendaItem,
        constructors = (PlainAgendaItem.manage_addPlainAgendaItemForm,
                        PlainAgendaItem.manage_addPlainAgendaItem),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        PlainAgendaItem.PlainAgendaItemVersion,
        constructors = (PlainAgendaItem.manage_addPlainAgendaItemVersionForm,
                        PlainAgendaItem.manage_addPlainAgendaItemVersion),
        icon="www/silvaresolution.gif"
        )

