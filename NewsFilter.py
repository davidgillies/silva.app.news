# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.14 $

from OFS import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
import OFS
# Silva
import Products.Silva.SilvaPermissions as SilvaPermissions
from Products.Silva.ViewRegistry import ViewAttribute
# misc
from Products.Silva.helpers import add_and_edit

from Filter import Filter, MetaTypeException
from INewsItem import INewsItemVersion
from IAgendaItem import IAgendaItemVersion

class NewsFilter(Filter):
    """Silva NewsFilter
    """
    security = ClassSecurityInfo()

    meta_type = "Silva News NewsFilter"

    search = ViewAttribute('public', 'index_html')

    def __init__(self, id, title):
        NewsFilter.inheritedAttribute('__init__')(self, id, title)
        self._show_agenda_items = 0
        self._rss_description = ''
        self._allow_rss_export = 0
        self._rss_link = ''
        self._rss_copyright = ''
        self._allow_rss_search = 0
        self._rss_search_description = ''

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_all_items')
    def get_all_items(self, meta_types=None):
        """Returns all items available to this filter. This function will probably only
        be used in the back-end, but nevertheless has AccessContentsInformation-security
        because it does not reveal any 'secret' information...
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        query = {}
        query['path'] = self._sources
        query['version_status'] = 'public'
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'creation_datetime'
        query['sort_order'] = 'descending'
        results = getattr(self, self._catalog)(query)
        return results

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_last_items')
    def get_last_items(self, number, number_is_days=0, meta_types=None):
        """Returns the last self._number_to_show published items
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        query = {}
        query['path'] = self._sources
        query['version_status'] = 'public'
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        if number_is_days:
            # the number specified must be used to restrict the on number of days instead of the number of items
            now = DateTime()
            last_night = DateTime(now.strftime("%Y/%m/%d"))
            query['publication_datetime'] = [last_night - number, now]
            query['publication_datetime_usage'] = 'range:min:max'
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'

        result = getattr(self, self._catalog)(query)
        filtered_result = [r for r in result if not r.object_path in self._excluded_items]
        output = []
        if not number_is_days:
            for i in range(len(filtered_result)):
                if i < number:
                    output.append(filtered_result[i])
                else:
                    break
        else:
            output = filtered_result

        return output

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_next_items')
    def get_next_items(self, numdays, meta_types=None):
        """Returns the next <number> AGENDAitems, called by AgendaViewer only and should return items
        that conform to the AgendaItem-interface (IAgendaItemVersion), although it will in any way because it
        requres start_datetime to be set. The NewsViewer uses only get_last_items.
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        date = DateTime()
        lastnight = DateTime(date.year(), date.month(), date.day(), 0, 0, 0)
        enddate = lastnight + numdays
        query = {}
        query['start_datetime'] = (lastnight, enddate)
        query['start_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'start_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in self._excluded_items]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_items_by_date')
    def get_items_by_date(self, month, year, meta_types=None):
        """Returns the last self._number_to_show published items
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        month = int(month)
        year = int(year)
        startdate = DateTime(year, month, 1)
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = DateTime(year, endmonth, 1)
        query = {}
        query['publication_datetime'] = (startdate, enddate)
        query['publication_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'publication_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in
                self._excluded_items]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'get_agenda_items_by_date')
    def get_agenda_items_by_date(self, month, year, meta_types=None):
        """Returns non-excluded published AGENDA-items for a particular month. This method is for
        exclusive use by AgendaViewers only, NewsViewers should use get_items_by_date instead (which filters
        on publication_datetime instead of start_datetime and returns all objects instead of only IAgendaItem-
        implementations)
        """
        self.verify_sources()
        if not self._sources:
            return []
        if not meta_types:
            meta_types = self.get_allowed_meta_types()
        self.verify_excluded_items()
        month = int(month)
        year = int(year)
        startdate = DateTime(year, month, 1)
        endmonth = month + 1
        if month == 12:
            endmonth = 1
            year = year + 1
        enddate = DateTime(year, endmonth, 1)
        query = {}
        query['start_datetime'] = [startdate, enddate]
        query['start_datetime_usage'] = 'range:min:max'
        query['version_status'] = 'public'
        query['path'] = self._sources
        query['subjects'] = self._subjects.keys()
        query['target_audiences'] = self._target_audiences.keys()
        query['meta_type'] = meta_types
        query['sort_on'] = 'start_datetime'
        query['sort_order'] = 'descending'
        result = getattr(self, self._catalog)(query)

        return [r for r in result if not r.object_path in self._excluded_items]

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'show_agenda_items')
    def show_agenda_items(self):
        return self._show_agenda_items

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_rss_description')
    def set_rss_description(self, value):
        """Sets the RSS description"""
        self._rss_description = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_description')
    def rss_description(self):
        """Returns the description"""
        return self._rss_description

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_show_agenda_items')
    def set_show_agenda_items(self, value):
        self._show_agenda_items = not not int(value)

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'allow_rss_export')
    def allow_rss_export(self):
        """Returns true if the filter allows RSS export"""
        return self._allow_rss_export

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_allow_rss_export')
    def set_allow_rss_export(self, yesorno):
        """Sets whether it is allowed to export to RSS"""
        self._allow_rss_export = not not yesorno

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'allow_rss_search')
    def allow_rss_search(self):
        """Returns true if searching through RSS is allowed"""
        return self._allow_rss_search

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_allow_rss_search')
    def set_allow_rss_search(self, yesorno):
        """Sets allow_rss_search"""
        self._allow_rss_search = not not yesorno

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_search_description')
    def rss_search_description(self):
        """Returns RSS search description"""
        return self._rss_search_description

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_rss_search_description')
    def set_rss_search_description(self, value):
        """Sets the description"""
        self._rss_search_description = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_link')
    def rss_link(self):
        """Returns the link to be used as the 'link' tag value for the RSS feed"""
        return self._rss_link

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_rss_link')
    def set_rss_link(self, value):
        """Sets the RSS link"""
        self._rss_link = value

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'rss_copyright')
    def rss_copyright(self):
        """Returns the copyright notice to be used for the RSS feed"""
        return self._rss_copyright

    security.declareProtected(SilvaPermissions.ChangeSilvaContent,
                              'set_rss_copyright')
    def set_rss_copyright(self, value):
        """Sets the RSS copyright notice"""
        self._rss_copyright = value

    security.declarePrivate('get_allowed_meta_types')
    def get_allowed_meta_types(self):
        """Returns the allowed meta_types for this filter"""
        allowed = []
        mts = self.get_root().filtered_meta_types()
        for mt in mts:
            if mt.has_key('instance'):
                if INewsItemVersion.isImplementedByInstancesOf(mt['instance']):
                    allowed.append(mt['name'])
                elif self._show_agenda_items:
                    if IAgendaItemVersion.isImplementedByInstancesOf(mt['instance']):
                        allowed.append(mt['name'])
        return allowed

    security.declarePublic('rss_feed')
    def rss_feed(self):
        """Returns the top 15 records as an RSS feed (RSS version 0.91)"""
        if not self.allow_rss_export():
            raise Exception, 'RSS export not allowed!'
        feed = '<?xml version="1.0" ?>\n'\
                '<!DOCTYPE rss PUBLIC "-//Netscape Communications//DTD RSS 0.91//EN" "http://my.netscape.com/publish/ formats/rss-0.91.dtd">\n'\
                '<rss version="0.91" encoding="ISO_8859-1">\n'\
                '<channel>\n'\
                '<title>' + self._xml_preformat(self.get_title_html()) + '</title>\n'\
                '<description>' + self._xml_preformat(self.rss_description()) + '</description>\n'\
                '<link>' + (self._xml_preformat(self.rss_link()) or self._xml_preformat(self.get_publication().absolute_url())) + '</link>\n'\
                '<language>en-us</language>\n'

        if self.rss_copyright():
            feed += '<copyright>' + self._xml_preformat(self.rss_copyright()) + '</copyright>\n'

        feed += '\n'

        last = self.get_last_items(15, 0)
        for item in last:
            # chop the last bit off lead if it's too large
            lead = item.lead
            if len(lead) > 256:
                lead = lead[:256]
                if lead.find(' ') > -1:
                    lead = lead[:lead.rfind(' ')]
                lead += '...'
            feed += '<item>\n'\
                    '<title>' + self._xml_preformat(item.get_title_html) + '</title>\n'\
                    '<link>' + self._xml_preformat(item.absolute_url()) + '</link>\n'\
                    '<description>' + self._xml_preformat(lead) + '</description>\n'\
                    '</item>\n\n'

        if self.allow_rss_search():
            feed += '<textinput>\n'\
                    '<title>Search</title>\n'\
                    '<name>query</name>\n'\
                    '<description>' + self.rss_search_description() + '</description>\n'\
                    '<link>' + self.aq_inner.absolute_url() + '/search</link>\n'\
                    '</textinput>\n\n'

        feed += '</channel>\n'\
                '</rss>\n'

        return feed

    def _xml_preformat(self, text, codepage='cp1252'):
        text = text.replace('&', '&amp;')
        text = text.replace('"', '&quot;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')

        return unicode(text, codepage)

InitializeClass(NewsFilter)

manage_addNewsFilterForm = PageTemplateFile("www/newsFilterAdd", globals(),
                                       __name__='manage_addNewsFilterForm')

def manage_addNewsFilter(self, id, title, REQUEST=None):
    """Add an NewsFilter."""
    if not self.is_id_valid(id):
        return
    object = NewsFilter(id, title)
    self._setObject(id, object)
    object = getattr(self, id)
    add_and_edit(self, id, REQUEST)
    return ''
