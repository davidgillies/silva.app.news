import Event, Article, Announcement, AgendaFilter, NewsFilter, ServiceNews
import NewsSource, NewsViewer, AgendaViewer, NewsBundle

def initialize(context):
    context.registerClass(
        Event.Event,
        constructors = (Event.manage_addEventForm,
                        Event.manage_addEvent),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        Event.EventVersion,
        constructors = (Event.manage_addEventVersionForm,
                        Event.manage_addEventVersion),
        icon="www/silvaresolutionversion.gif"
        )

    context.registerClass(
        Article.Article,
        constructors = (Article.manage_addArticleForm,
                        Article.manage_addArticle),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        Article.ArticleVersion,
        constructors = (Article.manage_addArticleVersionForm,
                        Article.manage_addArticleVersion),
        icon="www/silvaresolutionversion.gif"
        )

    context.registerClass(
        Announcement.Announcement,
        constructors = (Announcement.manage_addAnnouncementForm,
                        Announcement.manage_addAnnouncement),
        icon="www/silvaresolution.gif"
        )

    context.registerClass(
        Announcement.AnnouncementVersion,
        constructors = (Announcement.manage_addAnnouncementVersionForm,
                        Announcement.manage_addAnnouncementVersion),
        icon="www/silvaresolutionversion.gif"
        )

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
        NewsBundle.NewsBundle,
        constructors = (NewsBundle.manage_addNewsBundleForm,
                        NewsBundle.manage_addNewsBundle),
        icon="www/silvaresolution.gif"
        )
