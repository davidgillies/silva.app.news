window.widgeteer_datetime = new function() {
    /* a date/time widget for widgeteer */
    this.DateTimeWidget = function() {
    };

    this.DateTimeWidget.prototype = new widgeteer.Widget;

    this.DateTimeWidget.prototype.initialize = function(input) {
        this.input = input;
        
        var containerdiv = document.createElement('div');
        containerdiv.style.whiteSpace = 'nowrap';
	containerdiv.style.textAlign = 'right'; //So IE understands...
        containerdiv.className = 'datetimewidget-datetimediv';

	var rand = Math.floor(Math.random()*100000);
	var display = document.createElement('span');
	display.setAttribute('id', 'display' + rand);
	display.innerHTML = 'no date set';
	containerdiv.appendChild(display);
	containerdiv.appendChild(document.createTextNode('\xa0'));

	var calendar = document.createElement('button');
	calendar.setAttribute('id', 'calendar' + rand);
	calendar.className = 'kupu-button kupu-link-reference calendar-button';
	calendar.setAttribute('title', 'set date');
	calendar.appendChild(document.createTextNode(' '));
	containerdiv.appendChild(calendar);

        input.parentNode.insertBefore(containerdiv, input);
	input.setAttribute('id', input.getAttribute('name') + rand);
	input.style.display = 'none'; //So IE understands...
	var theid = input.getAttribute('id');

        /* initialize the calendar later, as it isn't in the DOM yet */
	setTimeout(function() {Calendar.setup({inputField : theid,
                              		       ifFormat : "%Y/%m/%d %H:%M",
					       displayArea : 'display' + rand,
					       daFormat : "%A, %B %d, %Y %I:%M %P",
					       showsTime : true,  
					       timeFormat:  "12",  
					       button : 'calendar' + rand,
					       weekNumbers: false})},1000);

	if (input.value == "") { //No date has been set
		return;
	}

	//Because we can't easily get the nice format...
	var date = Date.parseDate(input.value, "%Y/%m/%d %H:%M");

	var DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
	var MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
	var hour = date.getHours();
	if (hour == 0 || hour == 12) {
		hour = 12;
	}
	else if (hour < 12) {
		if (hour < 10) {
			hour = "0" + hour;
		}
	}
	else {
	        if (hour < 22) {
	                hour = "0" + (hour - 12);
	        }
		else {
			hour -= 12;
		}
	}
	display.innerHTML = DAYS[date.getDay()] + ", " + MONTHS[date.getMonth()] + " " + date.getDate() + ", " + date.getFullYear() + " " + hour + ":" + (date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes()) + " " + (date.getHours() < 12 ? "am" : "pm");
    };

    this.DateTimeWidget.prototype.value = function() {
        return this.input.value; //The value is set automatically from the jscalendar
    };

    // register the widget
    widgeteer.widget_registry.register('datetime', this.DateTimeWidget);
}();
