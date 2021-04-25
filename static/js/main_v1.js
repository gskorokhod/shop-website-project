const delay = (function () {
    let timer = 0;
    return function (callback, ms) {
        clearTimeout(timer);
        timer = setTimeout(callback, ms);
    };
})();


$(document).ready(function () {
    $('.goods-buy-form').submit(function (e) {
        e.preventDefault();
        $.ajax({
            url: '/api/v1/cart',
            type: 'post',
            data: $(this).serialize(),
            success: function (data) {
                let n_items = data['cart'].length
                $('#cart-items-number').text(n_items)
            }
        })
    });

    $('.quantity-minus').on('click', function () {
        let elem = $(this).closest('.quantity-box').find('.quantity-input');
        let num_value = Math.max(parseInt(elem.val()) - 1, 1);
        elem.val(num_value);
    });

    $('.quantity-plus').on('click', function () {
        let parent_form = $(this).closest('.quantity-box')
        let max_n_goods = parent_form.find('input[name="max_n_goods"]').val();

        let elem = $(this).closest('.quantity-box').find('.quantity-input');

        let num_value = Math.min(parseInt(elem.val()) + 1, parseInt(max_n_goods));
        elem.val(num_value);
    });

    $('#open-sidebar-categories').on('click', function () {
        $('#sidebar-categories').toggleClass('collapse');
        $(this).removeClass('d-md-block').hide();
    });

    $('#close-sidebar-categories').on('click', function () {
        $('#sidebar-categories').toggleClass('collapse');
        $('#open-sidebar-categories').addClass('d-md-block').show()
    });

    $('.collapse-toggle').on('click', function () {
        $(this).children('i').each(function () {
            if ($(this).hasClass('fa-caret-down')) {
                $(this).removeClass('fa-caret-down');
                $(this).addClass('fa-caret-up');
            } else {
                if ($(this).hasClass('fa-caret-up')) {
                    $(this).removeClass('fa-caret-up');
                    $(this).addClass('fa-caret-down');
                }
            }
        })
    });
});