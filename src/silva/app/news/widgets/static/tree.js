(function ($) {

    $(document).on('loadwidget-smiform', '.form-fields-container', function(event, data) {
        var $trees = $(this).find(".field-tree-widget");

        $trees.each(function () {
            var $tree = $(this);
            var $input = $tree.siblings('input.field-tree');
            var readonly = $input.attr('readonly') !== undefined;
            var plugins = ["html_data", "ui"];

            if (!readonly) {
                plugins.push("checkbox");
            }

            $tree.jstree({
                core: {
                    animation: 100
                },
                plugins: plugins
            });

            if (!readonly) {
                $tree.on('click', 'a', function() {
                    var values = [];

                    $.each($tree.jstree('get_checked'), function() {
                        values.push($(this).attr('id'));
                    });
                    $input.val(values.join('|'));
                    $input.change();
                });
            };
        });
        event.stopPropagation();
    });


})(jQuery);
