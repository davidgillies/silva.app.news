from calendar import day_abbr, month_name, Calendar, January

class HTMLCalendar(Calendar):
    """
    This calendar returns complete HTML pages.
    """

    # CSS classes for the day <td>s
    cssclasses = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    serial_format = '%d%02d%02d'

    def __init__(self, first_weekday=0, prev_link=None, next_link=None,
            current_day=None, today=None):
        super(HTMLCalendar, self).__init__(first_weekday)
        self.prev_link = prev_link
        self.next_link = next_link
        self.current_day = current_day
        self.today = today
        self.__hooks = {}
        self.__set_serial()

    def __set_serial(self):
        self.current_day_serial = self.current_day and \
            self.__get_serial(self.current_day.year,
                self.current_day.month, self.current_day.day) or None
        self.today_serial = self.today and self.__get_serial(self.today.year,
            self.today.month, self.today.day) or None

    def register_day_hook(self, formatable_date, hook):
        key = formatable_date.strftime('%Y%m%d')
        hooks = self.__hooks.get(key, list())
        hooks.append(hook)
        self.__hooks[key] = hooks

    def __get_hooks(self, year, month, day):
        hooks = self.__hooks.get(self.__get_serial(year, month, day), list())
        global_hook = self.__hooks.get('*', None)
        if global_hook:
            hooks.append(global_hook)
        return hooks

    def __get_serial(self, year, month, day):
        return self.serial_format % (year, month, day,)

    def __get_classes(self, year, month, day):
        classes = []
        serial = self.__get_serial(year, month, day)
        if serial == self.current_day_serial:
            classes.append('calendar_current')
        if serial == self.today_serial:
            classes.append('calendar_today')
        return " ".join(classes)

    def formatday(self, day, weekday, week, year, month):
        """
        Return a day as a table cell.
        """
        classes = self.__get_classes(year, month, day)
        if day == 0:
            return '<td class="noday">&nbsp;</td>' # day outside month
        else:
            hooks = self.__get_hooks(year, month, day)
            if hooks:
                hook_rendering = ""
                for hook in hooks:
                    hook_rendering += hook(year, month, day)
                return '<td class="%s %s event">%s</td>' % \
                    (self.cssclasses[weekday], classes, hook_rendering,)
            return '<td class="%s %s">%d</td>' % (
                self.cssclasses[weekday], classes, day,)

    def formatweek(self, week, year, month):
        """
        Return a complete week as a table row.
        """
        s = ''.join(self.formatday(d, wd, week, year, month) for (d, wd) in week)
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
        return '<tr><th>%s</th><th colspan="5" class="month">%s</th>' \
            '<th>%s</th></tr>' % (self.prev_link or "", s, self.next_link or "",)

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


