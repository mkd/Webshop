/*
 * admin.js
 *
 * Added functionality for the admin pages.
 */
$(document).ready(function()
{
    // submit forms when clicking on admin buttons
    $('#bt_delete_products').click(function()
    {
        if (confirm('Do you want to delete the selected products?'))
            $('#admin_products').submit()
    })

    $('#lb_delete_products').click(function()
    {
        if (confirm('Do you want to delete the selected products?'))
            $('#admin_products').submit()
    })
})
