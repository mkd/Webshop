/*
 * admin.js
 *
 * Added functionality for the admin pages.
 */
$(document).ready(function()
{
    // delete products
    $('#bt_delete_products').click(function()
    {
        if (confirm('Do you want to delete the selected products?'))
            $('#admin_products').submit()
    });

    $('#lb_delete_products').click(function()
    {
        if (confirm('Do you want to delete the selected products?'))
            $('#admin_products').submit()
    });

    // cancel orders
    $('#bt_cancel_orders').click(function()
    {
        if (confirm('Do you want to cancel the selected orders?'))
            $('#admin_orders').submit()
    });

    $('#lb_cancel_orders').click(function()
    {
        if (confirm('Do you want to cancel the selected orders?'))
            $('#admin_orders').submit()
    });
});
