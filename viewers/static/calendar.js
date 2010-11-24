(function($) {
  $(document).ready(function(event){

    $('#calendar').fullCalendar({
      header: {
        left: 'prev,next today',
        center: 'title',
        right: 'month,agendaWeek,agendaDay'
      },
      events: $("a#events-location").attr('href'),
      eventRender: function(event, element) {
        $(element).qtip({
          content: {
            title: event.title,
            ajax: {
              url: event.url + '/tooltip.html',
              type: 'GET',
              data: {}
            }
          },
          style: {
            classes: 'ui-tooltip-dark'
          },
          position: {
            at: 'top right'
          }
        });
      }
    });
  });
})(jQuery);
