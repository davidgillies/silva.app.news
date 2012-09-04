(function ($) {

    function create_trees() {
        var $trees = $(this).find(".field-tree-widget");

        $trees.each(function () {
            var $tree = $(this);
            var $input = $tree.siblings('input.field-tree');
            var readonly = $input.attr('readonly') != undefined;
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

            $tree.delegate('jstree')

            if (!readonly) {
                $tree.delegate('a', 'click', function() {
                    $nodeElement = $(this).closest('li');
                    if ($nodeElement.length != 1) {
                        return;
                    }

                    var id = $nodeElement.attr('id');
                    var values = $input.val().split('|');

                    if ($tree.jstree('is_checked', $nodeElement)) {
                        if ($.inArray(values, id) < 0) {
                            values.push(id);
                        }
                    } else {
                        var ids = $nodeElement.find('li').map(function(){
                            return $(this).attr('id')
                        });
                        ids.push(id);
                        values = $.grep(values, function(val){
                            return $.inArray(val, ids) < 0;
                        });
                    }

                    $input.val(values.join('|'));
                    $input.change();
                });
            }
        });
    };

    $('.form-fields-container').live('loadwidget-smiform', function(event) {
        $(this).invoke(create_trees);
        event.stopPropagation();
    });

    $(document).ready(create_trees);

})(jQuery);
