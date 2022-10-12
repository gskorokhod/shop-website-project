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

        if (char_id === "") {
            char_id = null;
        }

        let charact = name_input.find('option:selected').text();

        let ch_name = '';
        if (char_id === null) {
            ch_name = form.find('input[name="newCharType"]').val();
            charact = ch_name;
        } else {
            ch_name = charact;
        }

        let val_input = form.find('input[name="charValue"]');
        let value = val_input.val();

        let table = $(this).closest('.characteristics-section').find('.characteristics-table');
        let tbody = table.find('tbody')

        let in_string = char_id + "#" + value + "#" + ch_name;
        console.log(in_string);

        tbody.append("<tr>\n" +
"                       <td>" + ch_name + "</td>\n" +
"                       <td>" + value + "</td>\n" +
"                       <td class=\"text-center\">\n" +
"                           <button type=\"button\" class=\"btn btn-outline-danger item-list-delete\">\n" +
"                               <i class=\"fa fa-trash\"></i>\n" +
"                           </button>\n" +
"                       </td>\n" +
"                       <input type=\"hidden\" name=\"characteristic[]\" value=\"" + in_string + "\">\n" +
"                     </tr>");
    });
})