(function($) {

// -------------- MONTHLY RECURRENCE --------------------------------------

  WEEKDAYS = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];

  $.widget("ui.monthlyrecurrence", {

    _init: function() {
      this._build();
      this._attachEvents();
    },

    freq: function() {
      if (this._getData('mode') == 'each')
        return this._getFreqEach();
      return this._getFreqOnthe();
    },

    mode: function() {
      return this._getData('mode');
    },

    days: function() {
      return this._getData('days');
    },

    _freq_change: function(event) {
      this._trigger('freqchange', event, {
        freq: this.freq()
      })
    },

    _getFreqEach: function() {
      var days = this._getData('days') || []
      if (days.length == 0)
        return '';
      var freq = "FREQ=MONTHLY;"
      freq += "INTERVAL=" + this._getData('interval') + ';';
      freq += "BYMONTHDAY=" + days.join(',') + ';';
      return freq;
    },

    _getFreqOnthe: function() {
      var pos = this._getData('pos');
      var on = this._getData('on');
      var freq = "FREQ=MONTHLY"
      freq += ";INTERVAL=" + this._getData('interval');
      freq += ";BYSETPOS=" + pos;
      freq += ";BYDAY=" + this.__getDay(on);
      return freq;
    },

    __getDay: function(daylike) {
      var pos = $.inArray(daylike, WEEKDAYS);
      if (pos != -1)
        return daylike;
      var binding = {
         day: function(){ return "1" },
         weekendday: function(){
            return WEEKDAYS[this.options.weekEndDay] },
         weekday: function() {
            return WEEKDAYS[this.options.firstDay] }
      }
      return binding[daylike].apply(this);
    },

    update: function(value) {
      var items = value.split(';');
      var data = {};
      $.each(items, function(index, item) {
        var pair = item.split('=');
        data[pair[0]] = pair[1]
      });

      if (data['FREQ'] != 'MONTHLY') {
        data = {};
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
      this._setData('mode', 'each');
    },

    _set_onthe_mode: function() {
      this.select_pos.attr('disabled', false);
      this.select_on.attr('disabled', false);
      this.days_table.addClass('disabled');
      this._setData('mode', 'onthe');
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
      var days = this._getData('days')
      value = String(value);
      var pos = $.inArray(value, days)
      if (pos == -1) {
        this._setData('days', days.concat([value]));
        target.addClass('ui-state-active');
      } else {
        days.splice(pos, 1);
        target.removeClass('ui-state-active');
      }
      this._freq_change(event);
    },

    posChanged: function(event) {
      this._setData('on', this.select_on.val());
      this._setData('pos', this.select_pos.val());
      this._freq_change(event);
    },

    intervalChanged: function(event) {
      this._setData('interval', this.interval_input.val())
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
        if (target.attr('tagName') == 'TD') {
          var value = target.data('ui-mr:day');
          handler.dayChanged.apply(handler, [event, target, value]);
        }
      });

      this.select_pos.change(function(event){
        handler.posChanged.apply(handler, [event, $(this)])
      });
      this.select_on.change(function(event){
        handler.posChanged.apply(handler, [event, $(this)])
      });
      this.interval_input.change(function(event){
        handler.intervalChanged.apply(handler, [event, $(this)])
      })
    },

    _setState: function() {
      var self = this;
      this.radio_each.attr('checked', this.options.mode == 'each');
      this.radio_onthe.attr('checked', this.options.mode != 'each');
      this.interval_input.val(this.options.interval);
      $.each(this.days_table.find('td.ui-mr-day'),
          function(index, element){
        var el = $(element);
        day = String(el.data("ui-mr:day"));
        if ($.inArray(day, self.options.days) != -1) {
          el.addClass('ui-state-active');
        } else {
          el.removeClass('ui-state-active');
        }
      });
      $.each(this.select_on.attr('options'), function(index, element) {
        var opt = $(element)
        if (opt.val() == self.options.on) {
          opt.attr('selected', true);
        } else {
          opt.attr('selected', false);
        }
      });
      $.each(this.select_pos.attr('options'), function(index, element) {
        var opt = $(element);
        if (opt.val() == self.options.pos) {
          opt.attr('selected', true);
        } else {
          opt.attr('selected', false);
        }
      });
    },

    _build: function() {
      var dom = $("<div id=\"" + this.options.mainDivId + "\" />");
      var base = dom;
      base.addClass(
        'ui-monthlyrecurrence ui-widget ui-widget-content' +
        ' ui-helper-clearfix ui-corner-all');
      every = $('<div>every<input size="3" type="text"' +
        ' name="interval"/> month(s)</div>');
      radio_each = $('<div><input checked="true"' +
        ' type="radio" name="ui-mr-radio" />each</div>');
      each_days = $('<div class="ui-mr-days" />');
      this._buildEachGrid(each_days);
      radio_onthe =
        $('<div><input type="radio" name="ui-mr-radio" />on the</div>');
      onthe_part = $('<div class="ui-mr-days" />')
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
      this.interval_input.val(this._getData('interval'));
    },

    _buildEachGrid: function(root) {
      var root = $(root);
      var table = $('<table><tr/><table/>');
      var base = $(table.find('tr'));
      table = $(table[0]);

      for(i=0; i < 31; i++) {
        if (i % 6 == 0) {
          tr = $("<tr/>");
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
      var root = $(root);
      var select_pos = $('<select name="first" />');
      var options = $('<option value="1">first</option>' +
        '<option value="2">second</options>' +
        '<option value="3">third</option>' +
        '<option value="4">fourth</option>' +
        '<option value="-1">last</option>')
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
        '<option value="weekendday">weekend day</option>')
      var select_on = $('<select name="on" />');
      options.appendTo(select_on);
      select_on.appendTo(root);

      this.select_pos = select_pos;
      this.select_on = select_on;
      disabled = (this._getData('mode') != 'onthe')
      this.select_pos.attr('disabled', disabled);
      this.select_on.attr('disabled', disabled);
    }
  });

  $.extend($.ui.monthlyrecurrence, {
    getter: "freq",
    defaults: {
      interval: 2,
      mode: 'each',
      days: [],
      debug: false,
      firstDay: 3,
      weekEndDay: 6,
      dayNames: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      mainDivId: 'ui-monthlyrecurrence-main',
    }
  });

// --------------------------- WEEKLY RECURRENCE --------------------------

  $.widget("ui.weeklyrecurrence", {

    weekDays: ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'],

    _init: function() {
      this._build();
    },

    _build: function() {
      var content = $(this._generateDom())
      this.element.empty().append(content);
    },

    freq: function() {
      var days = this._getData('days');
      if (days.length == 0)
        return '';
      var freq = "FREQ=WEEKLY";
      freq += ";INTERVAL=" + this._getData('interval');
      freq += ";BYDAY=" + days.join(',');
      return freq;
    },

    update: function(value) {
      var items = value.split(';');
      var data = {};
      $.each(items, function(index, item) {
        var pair = item.split('=');
        data[pair[0]] = pair[1];
      });

      if (data['FREQ'] != 'WEEKLY') {
        data = {}
      }

      this.options.interval = data['INTERNAL'] || 1;
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
      value = element.data('ui-wr:daynum');
      days = this._getData('days') || []
      if (element.hasClass('ui-state-active')) {
        if ($.inArray(value, days) == -1) {
          this._setData('days', days.concat([value]));
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
      this._setData('interval', input.val());
      this._freq_change(event);
    },

    _freq_change: function(event) {
      this._trigger('freqchange', event, {freq: this.freq()})
    },

    _setState: function() {
      this.interval_input.val(this.options.interval);
      days_elements = this.element.find('a.ui-state-default');
      var self = this;
      $.each(days_elements, function(index, element){
        var el = $(element);
        day = el.data('ui-wr:daynum');
        if ($.inArray(day, self._getData('days')) != -1) {
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
      if ($.inArray(WEEKDAYS[value], this._getData('days')) != -1)
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
        var input = $(this)
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

      for (i=0; i < 7; i++) {
        // the value is the offset from firstDay
        var index = (i + this.options.firstDay) % 7;
        var day = this.options.dayNames[index];
        var td = this._createDayElement(index, day);
        td.appendTo(tr);
      }
      tr.appendTo(tbody);
      tbody.appendTo(table);
      table.appendTo(dom)
      return dom;
    }

  });

  $.extend($.ui.weeklyrecurrence, {
    getter: "freq",
    setter: "update",
    defaults: {
      interval: 2,
      days: [],
      debug: false,
      firstDay: 3,
      dayNames: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      mainDivId: 'ui-weeklyrecurrence-main',
    }
  });

  $(document).ready(function(){
    var widgets = $('.recurrence-widget');
    $.each(widgets, function(index, w){
      var widget = $(w);
      var weekly = $(widget.find("div.weekly-widget"));
      var monthly = $(widget.find("div.monthly-widget"));
      var wlink = $(widget.find("a.weekly-link"));
      var mlink = $(widget.find("a.monthly-link"));
      var input = $(widget.find("input.recurrence-data"));
      weekly.weeklyrecurrence();
      monthly.monthlyrecurrence();
      weekly.bind('weeklyrecurrencefreqchange', function(event, data){
        input.val(data['freq']);
      });
      monthly.bind('monthlyrecurrencefreqchange', function(event, data){
        input.val(data['freq']);
      });
      wlink.click(function(event){
        weekly.weeklyrecurrence('update', input.val());
        monthly.css('display', 'none');
        weekly.css('display', 'block');
      });
      mlink.click(function(event){
        monthly.monthlyrecurrence('update', input.val());
        weekly.css('display', 'none');
        monthly.css('display', 'block');
      });
    })
  })

})(jQuery);
