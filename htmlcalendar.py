import sys
import datetime
import locale as _locale

from calendar import day_abbr, month_name, Calendar

class HTMLCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes for the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def __init__(self, *args, **kw):
        super(HTMLCalendar, self).__init__(*args, **kw)
        self.__hooks = {}

    def register_day_hook(self, formatable_date, hook):
        key = formatable_date.strftime('%Y%m%d')
        hooks = self.__hooks.get(key, list())
        hooks.append(hook)
        self.__hooks[key] = hooks

    def __get_hooks(self, year, month, day):
        hooks = self.__hooks.get('%d%02d%02d' % (year, month, day,), list())
        global_hook = self.__hooks.get('*', None)
        if global_hook:
            hooks.append(global_hook)
        return hooks

    def formatday(self, day, weekday, theweek, theyear, themonth):
        """
        Return a day as a table cell.
        """
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            hooks = self.__get_hooks(theyear, themonth, day)
            if hooks:
                hook_rendering = ""
                for hook in hooks:
                    hook_rendering += hook(theyear, themonth, day)
                return '<td class="%s event">%s</td>' % \
                    (self.cssclasses[weekday], hook_rendering,)
            return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweek(self, theweek, theyear, themonth):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, theweek, theyear, themonth) for (d, wd) in theweek)
        return '<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return '<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="7" class="month">%s</th></tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="month">')
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week, theyear, themonth))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        """
        Return a formatted year as a table of tables.
        """
        v = []
        a = v.append
        width = max(width, 1)
        a('<table border="0" cellpadding="0" cellspacing="0" class="year">')
        a('\n')
        a('<tr><th colspan="%d" class="year">%s</th></tr>' % (width, theyear))
        for i in range(January, January+12, width):
            # months in this row
            months = range(i, min(i+width, 13))
            a('<tr>')
            for m in months:
                a('<td>')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>')
            a('</tr>')
        a('</table>')
        return ''.join(v)


