$(document).ready(function () {
    $('.nav-tabs').on('click', function () {
        $(this).children('button').each(function () {
            console.log(this);
            if ($(this).hasClass('active')) {
                $(this).addClass('bg-success').addClass('text-light');
            } else {
                $(this).removeClass('bg-success').removeClass('text-light');
            }
        })
    })
});