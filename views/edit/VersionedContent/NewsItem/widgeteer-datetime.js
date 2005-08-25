window.widgeteer_datetime = new function() {
    /* a date/time widget for widgeteer */
    this.DateTimeWidget = function() {
        /* a simple compound date/time field */
        this.date_seperator = '/';
        this.time_seperator = ':';
    };

    this.DateTimeWidget.prototype = new widgeteer.Widget;

    this.DateTimeWidget.prototype.initialize = function(input) {
        this.input = input;
        var parsed = this.parseDateTime(input.value);
        
        var containerdiv = document.createElement('div');
        containerdiv.style.whiteSpace = 'nowrap';
        containerdiv.className = 'datetimewidget-datetimediv';

        var dateel = document.createElement('span');
        dateel.style.whiteSpace = 'nowrap';
        dateel.className = 'datetimewidget-dateel';
        containerdiv.appendChild(dateel);
        
        var dayinput = document.createElement('input');
        this.dayinput = dayinput;
        dayinput.setAttribute('maxlen', '2');
        dayinput.setAttribute('size', '2');
        dayinput.value = parsed[2];
        dateel.appendChild(dayinput);

        dateel.appendChild(document.createTextNode(this.date_seperator));

        var monthinput = document.createElement('input');
        this.monthinput = monthinput;
        monthinput.setAttribute('maxlen', '2');
        monthinput.setAttribute('size', '2');
        monthinput.value = parsed[1];
        dateel.appendChild(monthinput);

        dateel.appendChild(document.createTextNode(this.date_seperator));

        var yearinput = document.createElement('input');
        this.yearinput = yearinput;
        yearinput.setAttribute('maxlen', '4');
        yearinput.setAttribute('size', '4');
        yearinput.value = parsed[0];
        dateel.appendChild(yearinput);

        containerdiv.appendChild(document.createTextNode('\xa0'));

        var hourel = document.createElement('span');
        hourel.style.whiteSpace = 'nowrap';
        hourel.className = 'datetimewidget-hourel';
        containerdiv.appendChild(hourel);

        var hourinput = document.createElement('input');
        this.hourinput = hourinput;
        hourinput.setAttribute('maxlen', '2');
        hourinput.setAttribute('size', '2');
        hourinput.value = parsed[3];
        hourel.appendChild(hourinput);

        hourel.appendChild(document.createTextNode(this.time_seperator));

        var mininput = document.createElement('input');
        this.mininput = mininput;
        mininput.setAttribute('maxlen', '2');
        mininput.setAttribute('size', '2');
        mininput.value = parsed[4];
        hourel.appendChild(mininput);

        input.parentNode.insertBefore(containerdiv, input);
        input.style.display = 'none';
    };

    // mapping from reg to field locations ([y, m, d, h, m, s], s is optional)
    regs = {
        '^(\\d{4})\\\/(\\d{1,2})\\\/(\\d{1,2}) (\\d{1,2}):(\\d{2}):(\\d{2})': 
            [1, 2, 3, 4, 5, 6],
        '^(\\d{4})\\\/(\d{1,2})\\\/(\\d{1,2}) (\\d{1,2})\\:(\\d{2})':
            [1, 2, 3, 4, 5]
        }
    this.DateTimeWidget.prototype.parseDateTime = function(datetime) {
        /* parse a datetime into seperate fields

            returns a list [year, month, day, hour, minute, seconds] if
            the datetime is understood, false if not
        */
        for (var reg in regs) {
            var locations = regs[reg];
            var regobj = new RegExp(reg, 'g');
            var match = regobj.exec(datetime);
            if (match) {
                ret = [
                    match[locations[0]],
                    match[locations[1]],
                    match[locations[2]],
                    match[locations[3]],
                    match[locations[4]]
                ];
                if (locations.length > 5) {
                    ret.push(match[locations[6]]);
                };
                return ret;
            };
        };
    };

    this.DateTimeWidget.prototype.value = function() {
        var ret = this.yearinput.value + '/' + this.monthinput.value + '/' +
                    this.dayinput.value + ' ' + this.hourinput.value + ':' +
                    this.mininput.value;
        return ret;
    };

    // register the widget
    widgeteer.widget_registry.register('datetime', this.DateTimeWidget);
}();
