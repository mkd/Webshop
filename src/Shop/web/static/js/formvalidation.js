/*
 * formvalidation.js
 *
 * Here are all the rules to validate various forms in the website.
 */
$(document).ready(function()
{
    // hide and show image field when clicking on the icon
    $('#id_picture').hide()

    $('#picture_enabler').click(function()
    {
        $('#id_picture').toggle()
    })

    // client-side validation for the profile form
    $("#submit").click(function()
    {
    $("#profile_form").validate({
        rules:
        {
            fname:
            {
                maxlength: 16,
                required:  true
            },
            
            sname:
            {
                maxlength: 16,
                required:  true
            },

            email:
            {
                maxlength: 32,
                required:  true
            },
        }
    });


    // client-side validation for the registration form
    $("#register_form").validate({
        rules:
        {
            fname:
            {
                maxlength: 16,
                required:  true
            },
            
            sname:
            {
                maxlength: 16,
                required:  true
            },

            user:
            {
                required:  true
            },

            passwd:
            {
                required:  true
            },

            pass2:
            {
                required:  true
            },

            email:
            {
                maxlength: 32,
                required:  true
            },

            email2:
            {
                maxlength: 32,
                required:  true
            },
        }
    });


    // client-side validation for the product form
    $("#add_product_form").validate({
        rules:
        {
            name:
            {
                maxlength: 32,
                required:  true
            },
            
            desc:
            {
                maxlength: 512,
            },

            price:
            {
                required:  true
            },

            units:
            {
                required:  true
            },
        }
    });
    });
});
