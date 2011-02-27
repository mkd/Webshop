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
                maxlength: 30,
                required:  true
            },
            
            sname:
            {
                maxlength: 30,
                required:  true
            },
            
            address:
            {
                maxlength: 160,
                required:  true
            },
            
            postal_code:
            {
                maxlength: 5,
                required:  true
            },
            
            city:
            {
                maxlength: 20,
                required:  true
            },
            
            country:
            {
                maxlength: 20,
                required:  true
            },
            
            password:
            {
                maxlength: 128,
                required:  true
            },
            
            password_again:
            {
                maxlength: 128,
                equalTo: '#id_passwd',
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

            passwd2:
            {
                required:  true
                equalTo: '#passwd'
            },

            email:
            {
                maxlength:  32,
                required:   true,
                email:		true
            },

            email2:
            {
                maxlength:  32,
                required:   true,
                email:		true,
                equalTo: '#email'
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
                required:	true,
                number: 	true,
                min: 		0
            },

            stock_count:
            {
                required:	true,
                number: 	true,
                min: 		0
            },
        }
    });
    
 // client-side validation for the signin form
    $("#signin_form").validate({
        rules:
        {
        	username:
            {
                maxlength: 32,
                required:  true
            },
            
            password:
            {
                maxlength: 	128,
                required:	true
            },
        }
    })
    });
});
