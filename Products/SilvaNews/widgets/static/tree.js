(function ($) {

    function load_trees(event) {
        var $trees = $(this).find(".tree-widget-jstree");

        $trees.each(function () {
            var $tree = $(this);
            var $input = $tree.siblings('input.tree-input');

            $tree.jstree({
                "plugins" : ["html_data", "checkbox"]
            });

            $tree.delegate('a', 'click', function() {
                var values = [];

                $.each($tree.jstree('get_checked'), function() {
                    values.push($(this).attr('id'));
                });
                $input.val(values.join('|'));
            });
        });
    };

    $('form').live('load-smiform', load_trees);
    $(document).ready(load_trees);

})(jQuery);
