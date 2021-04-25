$(document).ready(function () {
    $('.categories-list, .characteristics-table').on('click', '.item-list-delete', function () {
        let row = $(this).closest('tr');
        let list_item = $(this).closest('.list-group-item');

        if (list_item.length > 0) {
            list_item.remove();
        } else if (row.length > 0) {
            row.remove();
        }
    })

    $('.category-add').on('click', function () {
        let form = $(this).closest('.category-form');
        let name_input = form.find('select[name="categ"]');
        let categ = name_input.find('option:selected').text();

        let list = $(this).closest('.category-section').find('.categories-list');
        list.append("<li class=\"list-group-item\">\n" +
"                       <div class=\"d-flex flex-row justify-content-between\">\n" +
"                           <span class=\"align-self-center\">" + categ + "</span>\n" +
"                           <button type=\"button\" class=\"btn btn-outline-danger item-list-delete\">\n" +
"                               <i class=\"fa fa-trash\"></i>\n" +
"                           </button>\n" +
"                       </div>\n" +
"                       <input type=\"hidden\" name=\"category[]\" value=" + name_input.val() + ">\n" +
"                    </li>");
    });

    $('.characteristic-add').on('click', function () {
        let form = $(this).closest('.characteristics-form');
        let name_input = form.find('select[name="charType"]');
        let char_id = name_input.val();
        let char = name_input.find('option:selected').text();

        let val_input = form.find('input[name="charValue"]');
        let value = val_input.val();

        let table = $(this).closest('.characteristics-section').find('.characteristics-table');
        let tbody = table.find('tbody')

        tbody.append("<tr>\n" +
"                       <td>" + char + "</td>\n" +
"                       <td>" + value + "</td>\n" +
"                       <td class=\"text-center\">\n" +
"                           <button type=\"button\" class=\"btn btn-outline-danger item-list-delete\">\n" +
"                               <i class=\"fa fa-trash\"></i>\n" +
"                           </button>\n" +
"                       </td>\n" +
"                       <input type=\"hidden\" name=\"characteristic[]\" value=" + char_id + "#" + value + ">\n" +
"                     </tr>");
    });
})