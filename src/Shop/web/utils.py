### utils.py
###
### Misc utilities.


### necessary libraries ###
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User


##
# Check if the user is logged  in, or redirect to another page otherwise.
#
# @param r URL to which redirect in case of not being staff.
def only_signed(request, r = '/'):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(r)


##
# Check if the user is staff, or redirect to another page otherwise.
#
# @param r URL to which redirect in case of not being staff.
def only_staff(request, r = '/'):
    only_signed(request)
    if not request.user.is_staff:
        return HttpResponseRedirect(r)


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
    fo = open('web/static/images/' + d + '/' + n, 'wb+')
    for chunk in f.chunks():
        fo.write(chunk)
    fo.close()
