import AgendaFilter, NewsFilter, ServiceNews
import NewsSource, NewsViewer, AgendaViewer
import PlainArticle

def initialize(context):

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

