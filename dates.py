"""Module that contains formatting code for dates

    includes code to create localized dates
"""

DEFAULT_LOCALE_STRING = 'en'

# I'm going to stick to plain class and functions here, no 'fancy'
try:
    from AccessControl import ModuleSecurityInfo
except ImportError:
    # no Zope
    class ModuleSecurityInfo:
        """Dummy module security info class"""
        def __init__(self, modulename):
            pass
        def declareProtected(self, permission, attr):
            pass
        def declarePublic(self, attr):
            pass

try:
    from Products import z3locales
    import localdatetime
except ImportError:
    # put the Z3Locale/src dir in your PYTHONPATH to test this stand-alone
    import localdatetime

from datetime import datetime

module_security = ModuleSecurityInfo('Products.SilvaNews.dates')
__allow_access_to_unprotected_subobjects__ = 1

def _get_fake_self(locale=None):
    class fake_self:
        REQUEST = {'HTTP_ACCEPT_LANGUAGE': locale or DEFAULT_LOCALE_STRING}
    return fake_self()

module_security.declarePublic('DateTimeFormatter')
class DateTimeFormatter:
    """Wrapper for DateTime objects that provides some additional stuff"""

    __allow_access_to_unprotected_subobjects__ = 1

    SHORT = 'short'
    MEDIUM = 'medium'
    LONG = 'long'
    FULL = 'full'

    def __init__(self, dt, locale=None):
        if isinstance(dt, datetime):
            self._datetime = DateTime(datetime)
        else:
            self._datetime = dt
        self._locale = locale

    def _get_parts(self):
        return [int(p) for p in self._datetime.parts()[:6]]

    def l_toString(self, format='medium', display_time=True):
        """returns a localized date string of a specified format"""
        if self._datetime is None:
            return ''
        return localdatetime.getFormattedDate(_get_fake_self(self._locale), self._get_parts(), format, display_time=display_time)

def getMonthAbbreviations(locale=None):
    return localdatetime.getMonthAbbreviations(_get_fake_self(locale))
