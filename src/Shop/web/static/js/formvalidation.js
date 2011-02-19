/*
 * formvalidation.js
 *
 * Here are all the rules to validate various forms in the website.
 */
$(document).ready(function()
{
  $("#submit").click(function()
  {
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

            pass:
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
  });
});
