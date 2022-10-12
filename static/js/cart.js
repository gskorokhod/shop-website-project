const update_cart = function () {
    let total_price = 0;
    let total_amt = 0;

    $('.cart-table tbody tr').each(function () {
        let price = parseInt($(this).find('.cart-price').text());
        let amt = parseInt($(this).find('.quantity-box').find('.quantity-input').val());

        total_price += price * amt;
        total_amt += amt;
    });

    $('.cart-form').find('.cart-total').text(total_price)
    $('.cart-form').find('.cart-amount').text(total_amt)
};


$(document).ready(function () {
    $('.cart-delete').on('click', function (e) {
        e.preventDefault();

        let trow = $(this).closest('tr');
        let ind = trow.index();
        let query = '/api/v1/cart/' + ind;

        $.ajax({
            url: query,
            method: 'delete',
            type: 'delete',
            success: function (response) {
                console.log(response);
                trow.remove();
                update_cart();
            }
        });
    });

    $('.cart-update').on('click', function (e) {
        e.preventDefault();

        let ind = $(this).closest('tr').index();
        let amt = $(this).closest('.quantity-box').find('.quantity-input').val();
        let query = '/api/v1/cart/' + ind + '?amount=' + amt;
        $.ajax({
            url: query,
            type: 'post',
            success: function () {
                update_cart();
            }
        });
    });

    $('.cart-clear').on('click', function (e) {
        e.preventDefault();

        $.ajax({
            url: '/api/v1/cart',
            type: 'delete',
            success: function () {
                window.location.replace('/cart')
            }
        });
    });
});