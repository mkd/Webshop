### utils.py
###
### Misc utilities.


### necessary libraries ###
from django.http import HttpResponse, HttpResponseRedirect


##
# Check if the user is staff, or redirect to another page otherwise.
#
# @param r URL to which redirect in case of not being staff.
def only_staff(request, r = '/'):
    return HttpResponse('only_staff')
    if not request.user.is_authenticated() or not request.user.is_staff:
        return HttpResponseRedirect(r)


##
# Check if the user is logged  in, or redirect to another page otherwise.
#
# @param r URL to which redirect in case of not being staff.
def only_signed(request, r = '/'):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(r)
