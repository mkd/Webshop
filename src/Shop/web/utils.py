### utils.py
### Misc utilities to be used in Webshop.
### (c) 2011 The Webshop Team

### necessary libraries ###
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


##
# Check if the request is made through POST, otherwise redirect.
def is_post(request):
    if request.method == 'POST':
        return True
    else:
        return False


##
# Check if the user is logged  in, or redirect to another page otherwise.
def is_auth(request):
    if request.user.is_authenticated():
        return True
    else:
        return False


##
# Check if the user is staff, or redirect to another page otherwise.
#
# @param r URL to which redirect in case of not being staff.
def is_staff(request):
    if is_auth(request) and request.user.is_staff:
        return True
    else:
        return False


# Handle an uploaded file.
#
# This function does not only save a file but also do other checks (e.g. picture
# size and resolution). TODO: this is not yet implemented!
#
# @param d Directory where to store the picture.
# @param f File to be handled.
# @param n Name of the file.
def handleUploadedPic(d, f, n):
    # if no file uploaded, don't change the picture
    if f is None:
        return

    # if a file is provided, then save it where it belongs
    fo = open('static/images/' + d + '/' + n, 'wb+')
    for chunk in f.chunks():
        fo.write(chunk)
    fo.close()
