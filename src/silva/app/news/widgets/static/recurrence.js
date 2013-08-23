(function($, infrae) {

    function parse_recurrence_data(value) {
        var items = value.split(';');
        var data = {};
        $.each(items || [], function(index, item) {
            var pair = item.split('=');
            data[pair[0]] = pair[1];
        });
        return data;
    };

    // -------------- DAILY RECURRENCE ---------------------------------------

    $.widget('ui.dailyrecurrence', {
        options: {
            interval: 1,
            mainDivId: 'ui-dailyrecurrence-main'
        },

        destroy: function() {
            $.Widget.prototype.destroy.apply(this, arguments);
        },

        freq: function() {
            var freq = "FREQ=DAILY";
            if (this.options.interval && !isNaN(this.options.interval))
                freq += ";INTERVAL=" + this.options.interval;
            return freq;
        },

        _create: function() {
            var self = this;
            this.element.bind('freqsync', function(){ self.reset.apply(self); });
            this._build();
            this._attachEvents();
        },

        _build: function() {
            var dom = $('<div id="' + this.options.mainDivId + '" />');
            var base = dom;
            base.addClass(
                'ui-dailyrecurrence ui-widget ui-widget-content ' +
                    'ui-helper-clearfix ui-corner-all');
            var every = $('<div>every<input size="3" type="text" ' +
                          'name="interval"/> day(s)</div>');
            every.appendTo(base);
            base.appendTo(this.element);
            this.interval_input = $(every.find('input'));
            this.interval_input.val(this.options.interval);
        },

        _attachEvents: function() {
            var handler = this;
            this.interval_input.change(function(event){
                handler._setOption('interval', handler.interval_input.val());
                handler._freq_change();
            });
        },

        _freq_change: function(event) {
            this._trigger('freqchange', event, {freq: this.freq()});
        },

        reset: function(value) {
            this._freq_change();
        },

        update: function(data) {
            if (data['FREQ'] != 'DAILY')
                return;

            if (data['INTERVAL'])
                this.options.interval = data['INTERVAL'];

            this._freq_change();
            this._setState();
        },

        _setState: function() {
            this.interval_input.val(this.options.interval);
        }

    });

    $.extend($.ui.dailyrecurrence, {
        getter: ["freq", "reset"],
        setter: "update"
    });


    // --------------------------- WEEKLY RECURRENCE --------------------------

    $.widget("ui.weeklyrecurrence", {

        weekDays: ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'],

        options: {
            interval: 1,
            days: [],
            debug: false,
            firstDay: 3,
            dayNames: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            mainDivId: 'ui-weeklyrecurrence-main'
        },

        destroy: function() {
            $.Widget.prototype.destroy.apply(this, arguments);
        },

        _create: function() {
            var self = this;
            this.element.bind('freqsync', function(){ self.reset.apply(self); });
            this._build();
        },

        _build: function() {
            var content = $(this._generateDom());
            this.element.empty().append(content);
        },

        freq: function() {
            var freq = "FREQ=WEEKLY";
            var days = this.options.days;
            if (this.options.interval)
                freq += ";INTERVAL=" + this.options.interval;
            if (days.length == 0)
                return freq;
            freq += ";BYDAY=" + days.join(',');
            return freq;
        },

        reset: function(value) {
            this._freq_change();
        },

        update: function(data) {
            if (data['FREQ'] != 'WEEKLY') {
                data = {};
                return;
            }

            this.options.interval = data['INTERVAL'] || 1;
            if (data['BYDAY']) {
                this.options.days = data['BYDAY'].split(',');
            } else {
                this.options.days = [];
            }

            this._freq_change();
            this._setState();
        },

        dayChanged: function(event, element) {
            element = $(element);
            element.toggleClass('ui-state-active');
            var value = element.data('ui-wr:daynum');
            var days = this.options.days || [];
            if (element.hasClass('ui-state-active')) {
                if ($.inArray(value, days) == -1) {
                    this._setOption('days', days.concat([value]));
                }
            } else {
                var pos = $.inArray(value, days);
                if (pos != -1) {
                    days.splice(pos, 1);
                }
            }
            this._freq_change(event);
        },

        intervalChanged: function(event, input) {
            this._setOption('interval', input.val());
            this._freq_change(event);
        },

        _freq_change: function(event) {
            this._trigger('freqchange', event, {freq: this.freq()});
        },

        _setState: function() {
            this.interval_input.val(this.options.interval);
            var days_elements = this.element.find('a.ui-state-default');
            var self = this;
            $.each(days_elements, function(index, element){
                var el = $(element);
                var day = el.data('ui-wr:daynum');
                if ($.inArray(day, self.options.days) != -1) {
                    el.addClass('ui-state-active');
                } else {
                    el.removeClass('ui-state-active');
                }
            });
        },

        _createDayElement: function(value, name) {
            var handler = this;
            var dom = $('<td><a href="#" class="ui-state-default">' +
                        name + '</a></td>');
            var el = $(dom[0]).find('a');
            el.data('ui-wr:daynum', WEEKDAYS[value]);
            el.click(function(event) {
                var el = $(this);
                handler.dayChanged.apply(handler, [event, el]);
                return false;
            });
            if ($.inArray(WEEKDAYS[value], this.options.days) != -1)
                el.addClass('ui-state-active');
            return dom;
        },

        _createInput: function() {
            var handler = this;
            var dom = $(
                '<div class="ui-weeklyrecurrence-every">every<input size="2" value="' +
                    this.options.interval + '" type="text" /> weeks on</div>');
            var input = $(dom.find('input'));
            this.interval_input = input;
            input.change(function(event) {
                var input = $(this);
                handler.intervalChanged.apply(handler, [event, input]);
            });
            return dom;
        },

        _generateDom: function() {
            var dom = $("<div id=\"" + this.options.mainDivId + "\" />");
            $(dom[0]).addClass('ui-weeklyrecurrence ui-widget ui-widget-content' +
                               ' ui-helper-clearfix ui-corner-all');
            this._createInput(this.options.interval).appendTo(dom);
            var table = $('<table>');
            var tbody = $('<tbody>');
            var tr = $('<tr>');

            for (var i=0; i < 7; i++) {
                // the value is the offset from firstDay
                var index = (i + this.options.firstDay) % 7;
                var day = this.options.dayNames[index];
                var td = this._createDayElement(index, day);
                td.appendTo(tr);
            }
            tr.appendTo(tbody);
            tbody.appendTo(table);
            table.appendTo(dom);
            return dom;
        }

    });

    $.extend($.ui.weeklyrecurrence, {
        getter: ["freq", "reset"],
        setter: "update"
    });

    // -------------- MONTHLY RECURRENCE --------------------------------------

    var WEEKDAYS = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];

    $.widget("ui.monthlyrecurrence", {

        options: {
            interval: 1,
            mode: 'each',
            days: [],
            debug: false,
            firstDay: 0,
            weekEndDay: 6,
            dayNames: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            mainDivId: 'ui-monthlyrecurrence-main'
        },

        destroy: function() {
            $.Widget.prototype.destroy.apply(this, arguments);
        },

        _create: function() {
            var self = this;
            this.element.bind('freqsync', function(){ self.reset.apply(self); });
            this._build();
            this._attachEvents();
        },

        freq: function() {
            if (this.options.mode == 'each')
                return this._getFreqEach();
            return this._getFreqOnthe();
        },

        mode: function() {
            return this.options.mode;
        },

        days: function() {
            return this.options.days;
        },

        _freq_change: function(event) {
            this._trigger('freqchange', event, {freq: this.freq()});
        },

        _getFreqEach: function() {
            var days = this.options.days || [];
            var freq = "FREQ=MONTHLY";
            if (this.options.interval && !isNaN(this.options.interval))
                freq += ";INTERVAL=" + this.options.interval;
            if (days.length > 0)
                freq += ";BYMONTHDAY=" + days.join(',');
            return freq;
        },

        _getFreqOnthe: function() {
            var pos = this.options.pos;
            var on = this.options.on;
            var freq = "FREQ=MONTHLY";
            if (this.options.interval && !isNaN(this.options.interval))
                freq += ";INTERVAL=" + this.options.interval;
            if (this.options.pos && this.options.on) {
                freq += ";BYSETPOS=" + this.options.pos;
                freq += ";BYDAY=" + this.options.on;
            }
            return freq;
        },

        _getDay: function(daylike) {
            var pos = $.inArray(daylike, WEEKDAYS);
            if (pos != -1)
                return daylike;
            var binding = {
                day: function(){ return "1"; },
                weekendday: function(){
                    return WEEKDAYS[this.options.weekEndDay]; },
                weekday: function() {
                    return WEEKDAYS[this.options.firstDay]; }
            };
            return binding[daylike].apply(this);
        },

        reset: function(value) {
            this._freq_change();
        },

        update: function(data) {
            if (data['FREQ'] != 'MONTHLY') {
                data = {};
                return;
            }

            this._set_each_mode();
            this.options.interval = data['INTERVAL'] || "1";

            if (data['BYDAY']) {
                this.options.on = data['BYDAY'];
                this._set_onthe_mode();
            }

            if (data['BYSETPOS']) {
                this.options.pos = data['BYSETPOS'];
            }

            if (data['BYMONTHDAY']) {
                this.options.days = data['BYMONTHDAY'].split(',');
            }

            this._freq_change();
            this._setState();
        },

        _set_each_mode: function() {
            this.select_pos.attr('disabled', true);
            this.select_on.attr('disabled', true);
            this.days_table.removeClass('disabled');
            this._setOption('mode', 'each');
        },

        _set_onthe_mode: function() {
            this.select_pos.attr('disabled', false);
            this.select_on.attr('disabled', false);
            this.days_table.addClass('disabled');
            this._setOption('mode', 'onthe');
        },

        radioEachChanged: function(event){
            this._set_each_mode();
            this._freq_change(event);
        },

        radioOntheChanged: function(event){
            this._set_onthe_mode();
            this.posChanged();
            this._freq_change(event);
        },

        dayChanged: function(event, target, value) {
            var days = this.options.days;
            value = String(value);
            var pos = $.inArray(value, days);
            if (pos == -1) {
                this._setOption('days', days.concat([value]));
                target.addClass('ui-state-active');
            } else {
                days.splice(pos, 1);
                target.removeClass('ui-state-active');
            }
            this._freq_change(event);
        },

        posChanged: function(event) {
            this._setOption('on', this.select_on.val());
            this._setOption('pos', this.select_pos.val());
            this._freq_change(event);
        },

        intervalChanged: function(event) {
            this._setOption('interval', this.interval_input.val());
            this._freq_change(event);
        },

        _attachEvents: function() {
            var handler = this;

            this.radio_each.change(function(event) {
                if (event.target.checked)
                    handler.radioEachChanged.apply(handler, [event, $(this)]);
            });

            this.radio_onthe.change(function(event) {
                if (event.target.checked)
                    handler.radioOntheChanged.apply(handler, [event, $(this)]);
            });

            this.days_table.click(function(event) {
                if (handler.options.mode == 'onthe')
                    return;
                var target = $(event.target);
                if (target.data('ui-mr:day')) {
                    var value = target.data('ui-mr:day');
                    handler.dayChanged.apply(handler, [event, target, value]);
                }
            });

            this.select_pos.change(function(event){
                handler.posChanged.apply(handler, [event, $(this)]);
            });
            this.select_on.change(function(event){
                handler.posChanged.apply(handler, [event, $(this)]);
            });
            this.interval_input.change(function(event){
                handler.intervalChanged.apply(handler, [event, $(this)]);
            });
        },

        _setState: function() {
            var self = this;
            this.radio_each.attr('checked', this.options.mode == 'each');
            this.radio_onthe.attr('checked', this.options.mode != 'each');
            this.interval_input.val(this.options.interval);
            $.each(this.days_table.find('td.ui-mr-day'), function(index, element){
                var el = $(element);
                var day = String(el.data("ui-mr:day"));
                if ($.inArray(day, self.options.days) != -1) {
                    el.addClass('ui-state-active');
                } else {
                    el.removeClass('ui-state-active');
                }
            });
            $.each(this.select_on.attr('options') || [], function(index, element) {
                var opt = $(element);
                opt.attr('selected', opt.val() == self.options.on);
            });
            $.each(this.select_pos.attr('options') || [], function(index, element) {
                var opt = $(element);
                opt.attr('selected', opt.val() == self.options.pos);
            });
        },

        _build: function() {
            var dom = $("<div id=\"" + this.options.mainDivId + "\" />");
            var base = dom;
            base.addClass(
                'ui-monthlyrecurrence ui-widget ui-widget-content' +
                    ' ui-helper-clearfix ui-corner-all');
            var every = $('<div>every<input size="3" type="text"' +
                          ' name="interval"/> month(s)</div>');
            var radio_each = $('<div><input checked="true"' +
                               ' type="radio" name="ui-mr-radio" />each</div>');
            var each_days = $('<div class="ui-mr-days" />');
            this._buildEachGrid(each_days);
            var radio_onthe =
                $('<div><input type="radio" name="ui-mr-radio" />on the</div>');
            var onthe_part = $('<div class="ui-mr-days" />');
            this._buildOnthe(onthe_part);
            every.appendTo(base);
            radio_each.appendTo(base);
            each_days.appendTo(base);
            radio_onthe.appendTo(base);
            onthe_part.appendTo(base);
            base.appendTo(this.element);

            this.radio_each = $(radio_each.find('input'));
            this.radio_onthe = $(radio_onthe.find('input'));
            this.interval_input = $(every.find('input'));
            this.interval_input.val(this.options.interval);
        },

        _buildEachGrid: function(root) {
            root = $(root);
            var table = $('<table><tr/><table/>');
            var base = $(table.find('tr'));
            table = $(table[0]);

            for(var i=0; i < 31; i++) {
                if (i % 6 == 0) {
                    var tr = $("<tr/>");
                    tr.appendTo(table);
                    base = tr;
                }
                var value = i + 1;
                var td = $('<td class="ui-mr-day ui-state-default">' +
                           value + '</td>');
                td.data('ui-mr:day', String(value));
                td.appendTo(base);
            }
            table.appendTo(root);
            this.days_table = table;
        },

        _buildOnthe: function(root) {
            root = $(root);
            var select_pos = $('<select name="first" />');
            var options = $('<option value="1">first</option>' +
                            '<option value="2">second</options>' +
                            '<option value="3">third</option>' +
                            '<option value="4">fourth</option>' +
                            '<option value="-1">last</option>');
            options.appendTo(select_pos);
            select_pos.appendTo(root);
            options = $('<option value="SU">Sunday</option>' +
                        '<option value="MO">Monday</option>' +
                        '<option value="TU">Tuesday</option>' +
                        '<option value="WE">Wednesday</option>' +
                        '<option value="TH">Thursday</option>' +
                        '<option value="FR">Friday</option>' +
                        '<option value="SA">Saturday</option>' +
                        '<option value="day">day</option>' +
                        '<option value="weekday">weekday</option>' +
                        '<option value="weekendday">weekend day</option>');
            var select_on = $('<select name="on" />');
            options.appendTo(select_on);
            select_on.appendTo(root);

            this.select_pos = select_pos;
            this.select_on = select_on;
            var disabled = (this.options.mode != 'onthe');
            this.select_pos.attr('disabled', disabled);
            this.select_on.attr('disabled', disabled);
        }
    });

    $.extend($.ui.monthlyrecurrence, {
        getter: ["freq", "reset"],
        setter: "update"
    });

    // ------------------------ YEARLY RECURRENCE -----------------------------

    $.widget('ui.yearlyrecurrence', {
        options: {
            interval: 1,
            monthes: [],
            mode: null,
            on: null,
            pos: null,
            mainDivId: 'ui-yearlyrecurrence-main',
            monthNames: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec']
        },

        _create: function() {
            var self = this;
            this.element.bind('freqsync', function(){ self.reset.apply(self); });
            this._build();
            this._attachEvents();
        },

        _build: function(){
            var dom = $("<div id=\"" + this.options.mainDivId + "\" />");
            dom.addClass(
                'ui-monthlyrecurrence ui-widget ui-widget-content' +
                    ' ui-helper-clearfix ui-corner-all');
            var every = $('<div>every<input size="3" type="text" ' +
                          'name="interval"/> year(s)</div>');

            var table = $('<table><tr/><table/>');
            var base = $(table.find('tr'));

            for (var i=0; i < 12; i++) {
                if (i % 3 == 0) {
                    var tr = $("<tr/>");
                    tr.appendTo(table);
                    base = tr;
                }
                var value = this.options.monthNames[i];
                var td = $('<td class="ui-yr-month ui-state-default">' +
                           value + '</td>');
                td.data('ui-yr:month', String(i + 1));
                td.appendTo(base);
            }

            every.appendTo(dom);
            table.appendTo(dom);
            this.every_input = $(every.find('input'));
            this.every_input.val(this.options.interval);
            this.monthes_table = table;

            var radio_onthe =
                $('<div><input type="checkbox" name="ui-mr-radio" />on the</div>');
            radio_onthe.appendTo(dom);
            this.radio_onthe = $(radio_onthe.find('input'));
            this._buildOnthe(dom);
            dom.appendTo(this.element);
        },

        _buildOnthe: function(root) {
            root = $(root);
            var select_pos = $('<select name="first" />');
            var options = $('<option value="1">first</option>' +
                            '<option value="2">second</options>' +
                            '<option value="3">third</option>' +
                            '<option value="4">fourth</option>' +
                            '<option value="-1">last</option>');
            options.appendTo(select_pos);
            select_pos.appendTo(root);
            options = $('<option value="SU">Sunday</option>' +
                        '<option value="MO">Monday</option>' +
                        '<option value="TU">Tuesday</option>' +
                        '<option value="WE">Wednesday</option>' +
                        '<option value="TH">Thursday</option>' +
                        '<option value="FR">Friday</option>' +
                        '<option value="SA">Saturday</option>' +
                        '<option value="day">day</option>' +
                        '<option value="weekday">weekday</option>' +
                        '<option value="weekendday">weekend day</option>');
            var select_on = $('<select name="on" />');
            options.appendTo(select_on);
            select_on.appendTo(root);

            this.select_pos = select_pos;
            this.select_on = select_on;
            var disabled = (this.options.mode != 'onthe');
            this.select_pos.attr('disabled', disabled);
            this.select_on.attr('disabled', disabled);
        },

        _attachEvents: function() {
            var handler = this;
            this.monthes_table.click(function(event){
                var target = $(event.target);
                if(target.data('ui-yr:month')) {
                    var value = target.data('ui-yr:month');
                    handler.monthChanged.apply(handler, [event, target, value]);
                }
            });
            this.radio_onthe.change(function(event){
                handler.posChanged.apply(handler, [event]);
            });
            this.select_pos.change(function(event){
                handler.posChanged.apply(handler, [event]);
            });
            this.select_on.change(function(event){
                handler.posChanged.apply(handler, [event]);
            });
            this.every_input.change(function(event){
                handler.everyChanged.apply(handler, [event]);
            });
        },

        everyChanged: function(event) {
            this.options.interval = this.every_input.val();
            this._freq_change(event);
        },

        posChanged: function(event) {
            this.options.mode = (this.radio_onthe.attr('checked') && 'onthe' || null);
            this.options.on = this.select_on.val();
            this.options.pos = this.select_pos.val();

            var disabled = (this.options.mode != 'onthe');
            this.select_on.attr('disabled', disabled);
            this.select_pos.attr('disabled', disabled);
            this._freq_change(event);
        },

        monthChanged: function(event, target, value) {
            var monthes = this.options.monthes;
            value = String(value);
            var pos = $.inArray(value, monthes);
            if (pos == -1) {
                this.options.monthes = monthes.concat([value]);
                target.addClass('ui-state-active');
            } else {
                monthes.splice(pos, 1);
                target.removeClass('ui-state-active');
            }
            this._freq_change(event);
        },

        freq: function() {
            var freq = 'FREQ=YEARLY';
            if (this.options.interval && !isNaN(this.options.interval))
                freq += ';INTERVAL=' + this.options.interval;
            if (this.options.monthes.length == 0)
                return freq;
            freq += ';BYMONTH=' + this.options.monthes.join(',');
            if (this.options.mode == 'onthe'){
                if (this.options.on && this.options.pos) {
                    freq += ';BYDAY=' + this.options.on;
                    freq += ';BYSETPOS=' + this.options.pos;
                }
            }
            return freq;
        },

        _freq_change: function(event) {
            this._trigger('freqchange', event, {freq: this.freq()});
        },

        reset: function(value) {
            this._freq_change();
        },

        update: function(data) {
            if (data['FREQ'] != 'YEARLY')
                return;
            if (data['INTERVAL'])
                this.options.interval = data['INTERVAL'];
            if (data['BYMONTH']) {
                this.options.monthes = data['BYMONTH'].split(',');
            }
            if (data['BYDAY']) {
                this.options.on = data['BYDAY'];
                this.options.mode = 'onthe';
            }
            if (data['BYSETPOS']) {
                this.options.pos = data['BYSETPOS'];
                this.options.mode = 'onthe';
            }
            this._setState();
        },

        _setState: function() {
            this.radio_onthe.attr('checked', this.options.mode == 'onthe');
            this.select_on.val(this.options.on);
            this.select_pos.val(this.options.pos);
            this.every_input.val(this.options.interval);

            var monthes = this.monthes_table.find('td.ui-yr-month');
            var self = this;
            $.each(monthes, function(index, element){
                var el = $(element);
                var month = String(el.data("ui-yr:month"));
                if ($.inArray(month, self.options.monthes) != -1) {
                    el.addClass('ui-state-active');
                } else {
                    el.removeClass('ui-state-active');
                }
            });
            $.each(this.select_on.attr('options') || [], function(index, element) {
                var opt = $(element);
                opt.attr('selected', opt.val() == self.options.on);
            });
            $.each(this.select_pos.attr('options') || [], function(index, element) {
                var opt = $(element);
                opt.attr('selected', opt.val() == self.options.pos);
            });
        }
    });

    $.extend($.ui.yearlyrecurrence, {
        getter: ["freq", "reset"],
        setter: "update"
    });

    // --- translation and humanize support ----------------------------

    var humanize_translations = {
        monthNames: ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October',
                     'November', 'December'],
        dayNames: {
            'MO': 'Monday',
            'TU': 'Tuesday',
            'WE': 'Wednesday',
            'TH': 'Thursday',
            'FR': 'Friday',
            'SA': 'Saturday',
            'SU': 'Sunday',
            'day': 'day',
            'weekendday': 'weekend day',
            'weekday': 'week day'
        },

        DAILY: ['each day', 'every %s day'],
        WEEKLY: ['each week', 'every %s week'],
        MONTHLY: ['each month', 'every %s month'],
        YEARLY: ['each year', 'every %s year'],

        BYDAY: 'on %s',
        BYMONTHDAY: 'on the %s',
        BYSETPOS: {
            '1': 'on the first',
            '2': 'on the second',
            '3': 'on the third',
            '4': 'on the fourth',
            '-1': 'on last'
        },
        BYMONTH: 'in %s',
        listterm: 'and',
        notset: 'no recurence set.'
    };

    function daySort(x, y) {
        var ref = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];
        return $.inArray(x, ref) - $.inArray(y, ref);
    };

    function sortInt(x, y) {
        return x - y;
    };

    function format(string, param) {
        return string.replace('%s', String(param));
    };

    function pluralize(data, count) {
        if (isNaN(count))
            return data[0];

        var c = parseInt(count);

        if (c > 1)
            return format(data[1], c);
        else
            return data[0];
    };

    function humanJoin(list, term) {
        var result = list[0];
        var i = 1;
        for (i; i < list.length - 1; i++) {
            result += ', ' + list[i];
        }
        if (list.length != 1)
            result += ' ' + term + ' ' + list[list.length - 1];
        return result;
    };

    function joinDayNames(list, translations) {
        return humanJoin(
            $.map(list.sort(daySort), function(x, i){
                return translations['dayNames'][x];
            }),
            translations['listterm']);
    };

    function joinDayNumbers(list, translations) {
        return humanJoin(list.sort(sortInt),
                         translations['listterm']);
    };

    function joinMonthNumbers(list, translations) {
        return humanJoin(
            $.map(list.sort(sortInt), function(x, i){
                return translations.monthNames[x - 1];
            }),
            translations['listterm']);
    };

    function humanize(data, translations) {
        if (data['FREQ'] === undefined)
            return translations['notset'];

        var sentence = pluralize(translations[data['FREQ']], data['INTERVAL']);

        if (data['BYMONTH']) {
            sentence += ' ' + format(translations['BYMONTH'],
                                     joinMonthNumbers(data['BYMONTH'].split(','),
                                                      translations));
        }

        if (data['BYSETPOS']) {
            sentence += ' ' + translations['BYSETPOS'][data['BYSETPOS']];

            if (data['BYDAY'])
                sentence += ' ' + joinDayNames(data['BYDAY'].split(','),
                                               translations);

            if (data['BYMONTHDAY'])
                sentence += ' ' + joinDayNumbers(data['BYMONTHDAY'].split(','),
                                                 translations);

            return sentence;
        }

        if (data['BYDAY'])
            sentence += ' ' + format(translations['BYDAY'],
                                     joinDayNames(data['BYDAY'].split(','),
                                                  translations));

        if (data['BYMONTHDAY'])
            sentence += ' ' + format(
                translations['BYMONTHDAY'], joinDayNumbers(
                    data['BYMONTHDAY'].split(','),
                    translations));

        return sentence;
    };

    // ------------------------------------------------------------------------


    $('.recurrence-popup-button').live('click', function() {
        var widget = $(this).closest('.recurrence-widget');
        var input = widget.find('input.recurrence-data');

        function updateInputWidget() {
            var value = widget.data('recurrence-value');
            input.val(value);
            widget.find('.recurrence-sentence').text(
                humanize(parse_recurrence_data(value),
                         humanize_translations));
        }

        var $popup = $("#" + widget.attr('id') + '-popup').clone();
        // initialize widget value from input value
        widget.data('recurrence-value', String(input.val()));
        $popup.find('.sentence-val').text(
            humanize(parse_recurrence_data(String(input.val())),
                     humanize_translations));
        updateInputWidget();

        var select = $popup.find('select');

        var daily = $popup.find("div.daily-widget");
        var weekly = $popup.find("div.weekly-widget");
        var monthly = $popup.find("div.monthly-widget");
        var yearly = $popup.find("div.yearly-widget");

        // create widgets
        daily.dailyrecurrence();
        weekly.weeklyrecurrence();
        monthly.monthlyrecurrence();
        yearly.yearlyrecurrence();

        function updateWidgets(event){
            daily.dailyrecurrence('update', parse_recurrence_data(data));
            weekly.weeklyrecurrence('update', parse_recurrence_data(data));
            monthly.monthlyrecurrence('update', parse_recurrence_data(data));
            yearly.yearlyrecurrence('update', parse_recurrence_data(data));
        };

        var handler = function(event, data){
            widget.data('recurrence-value', data['freq']);
            var sentence = humanize(parse_recurrence_data(String(data['freq'])),
                                    humanize_translations);
            $popup.find('.sentence-val').text(sentence);
        };

        daily.bind('dailyrecurrencefreqchange', handler);
        weekly.bind('weeklyrecurrencefreqchange', handler);
        monthly.bind('monthlyrecurrencefreqchange', handler);
        yearly.bind('yearlyrecurrencefreqchange', handler);

        select.change(function(event){
            var widget_class = String(select.val());
            $.each($popup.find('.widget'), function(index, element){
                $(element).hide();
            });
            if (widget_class != ''){
                var el = $popup.find('div.' + widget_class);
                el.show();
                el.trigger($.Event('freqsync'));
            }
        });

        $.each($popup.find('.widget'), function(index, element){
            $(element).hide();
        });

        // set field current state
        var data = parse_recurrence_data(widget.data('recurrence-value'));
        switch(data['FREQ']){
        case 'DAILY':
            daily.dailyrecurrence('update', data);
            select.val('daily-widget');
            daily.show();
            break;
        case 'WEEKLY':
            weekly.weeklyrecurrence('update', data);
            select.val('weekly-widget');
            weekly.show();
            break;
        case 'MONTHLY':
            monthly.monthlyrecurrence('update', data);
            select.val('monthly-widget');
            monthly.show();
            break;
        case 'YEARLY':
            yearly.yearlyrecurrence('update', data);
            select.val('yearly-widget');
            yearly.show();
            break;
        default:
            select.val('');
        };

        $popup.dialog({
            autoOpen: false,
            modal: false,
            width: 300,
            height: 375,
            buttons: {
                'Cancel': function() {
                    $(this).dialog('close');
                },
                'Clear': function() {
                    widget.data('recurrence-value', '');
                    updateInputWidget();
                    $(this).dialog('close');
                },
                'Ok': function() {
                    updateInputWidget();
                    $(this).dialog('close');
                }
            }
        });
        $popup.bind('dialogclose', function() {
            $popup.remove();
        });
        infrae.ui.ShowDialog($popup);
    });

    $(document).on('loadwidget-smiform', '.form-fields-container', function(event, data) {
        $(this).find('.recurrence-widget').each(function() {
            var $widget = $(this);
            var $input = $widget.find('input.recurrence-data');
            var value = String($input.val());
            $widget.find('.recurrence-sentence').text(
                humanize(parse_recurrence_data(value),
                         humanize_translations));
        });
        event.stopPropagation();
    });

})(jQuery, infrae);
