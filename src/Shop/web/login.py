### login.py
### This module contains user registration and session functionalities.
### (c) 2011 The Webshop Team



### necessary libraries ###
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import *
from django.template import Context, RequestContext, loader
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from myadmin import *
from utils import *
import os.path
from models import *
from forms import *
import datetime, hashlib, os



##
# Render a simple registration form (sign up)
def signup(request):
    t = loader.get_template('signup.html')
    form = RegisterForm()
    categories = Category.objects.all()
    context = RequestContext(request,
    {
        'form'       : form,
        'categories' : categories,
    })
    return HttpResponse(t.render(context))


##
# Render a simple login form (sign in)
def signin(request):
    t = loader.get_template('signin.html')
    categories = Category.objects.all()
    context = RequestContext(request, { 
        'categories' : categories,
    })
    return HttpResponse(t.render(context))


##
# Perform the actual login.
#
# This function checks the user and password against the users in the database
# and tries to log in. If successful, the user is redirected to the home page,
# otherwise an error is displayed.
def tryLogin(request):
    # authenticate the user
    username = request.POST.get('user')
    password = request.POST.get('pass')
    user = authenticate(username=username, password=password)

    # on sign-in go to front-page, otherwise go back to sign-in form
    if user is not None:
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        t = loader.get_template('signin.html')
        categories = Category.objects.all()
        context = RequestContext(request, {
            'login_failed' : True,
            'categories'   : categories,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Close the session for an user and go to the front page.
def signout(request):
    if is_auth(request):
        logout(request)
        return HttpResponseRedirect('/')  


##
# Add a new user.
def register(request):
    t = loader.get_template('signin.html')
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)

        # server-side validation
        if form.is_valid():
            # check if the user already exists in the database
            try:
                check_username = User.objects.get(username=request.POST.get('user'))
            except:
                check_username = None
            try:
                check_email = User.objects.get(email=request.POST.get('email'))
            except:
                check_email = None

            # if the username or email already exist, go back to the sign-up
            # form and remember the entered data
            if check_username is not None or check_email is not None:
                t = loader.get_template('signup.html')
                context = RequestContext(request, {
                    'username'       : request.POST.get('user'),
                    'fname'          : request.POST.get('fname'),
                    'sname'          : request.POST.get('sname'),
                    'email'          : request.POST.get('email'),
                    'email2'         : request.POST.get('email2'),
                    'passwd'         : request.POST.get('passwd'),
                    'pass2'          : request.POST.get('pass2'),
                    'user_exists'    : True,
                    'form'           : form
                })
                context.update(csrf(request))
                return HttpResponse(t.render(context))

            # save all the data from the POST into the database
            u  = User.objects.create_user(
                request.POST.get('user'),
                request.POST.get('email'),
                request.POST.get('passwd')
            )
            up = UserProfile.objects.create(user_id=u.id)
            u.is_staff   = False
            u.first_name = request.POST.get('fname')
            u.last_name  = request.POST.get('sname')
            u.save()
            up.save()

            # save also avatar picture, if available
            handleUploadedPic('users', request.FILES.get('picture'), u.id)

            # redirect the user to the login page with a welcome
            context = RequestContext(request, {
                'user'       : request.POST.get('user'),
                'registered' : True,
            })
            context.update(csrf(request))
            return HttpResponse(t.render(context))


##
# Render the user profile page.
def editProfile(request):
    if is_auth(request):
        t = loader.get_template('profile.html')
        form = ProfileForm(request.POST, request.FILES)

        # obtain the data from the user and display his/her profile
        u = User.objects.get(id=request.user.id)
        no_items = u.get_profile().products_in_cart

        # load unknown avatar if no profile picture
        pic = 'web/static/images/users/' + str(u.id)
        if not os.path.exists(pic):
            pic = 'static/images/users/new_user.png'
        else:
            pic = 'static/images/users/' + str(u.id)

        # set the rest of the data
        context = RequestContext(request, {
            'picture'          : pic,
            'user'             : u.username,
            'fname'            : u.first_name,
            'sname'            : u.last_name,
            'email'            : u.email,
            'products_in_cart' : no_items,
            'address'          : u.get_profile().postal_address,
            'postal_code'      : u.get_profile().postal_code,
            'city'             : u.get_profile().postal_city,
            'country'          : u.get_profile().postal_country,
            'form'             : form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Save the user's profile.
def saveProfile(request):
    if is_auth(request) and request.method == 'POST':
        t = loader.get_template('profile.html')

        # save all the data from the POST into the database
        up = UserProfile.objects.get(user=request.user.id)
        u = User.objects.get(id=request.user.id)
        u.first_name = request.POST.get('fname')
        u.last_name  = request.POST.get('sname')
        up.postal_address = request.POST.get('address')
        up.postal_code    = request.POST.get('postal_code')
        up.postal_city    = request.POST.get('city')
        up.postal_country = request.POST.get('country')

        # if pass and pass2 match, save them as the new password
        pwd = request.POST.get('passwd', None)
        if pwd != '' and pwd != None and (pwd == request.POST.get('pass2')):
            u.set_password(pwd)

        # save the avatar picture, if available
        handleUploadedPic('users', request.FILES.get('picture'), str(u.id))

        # commit to the database
        u.save()
        up.save()

        # display profile again
        form = ProfileForm(request.POST, request.FILES)
        context = RequestContext(request, {
            'picture'        : '/static/images/users/' + str(u.id),
            'user'           : u.username,
            'fname'          : u.first_name,
            'sname'          : u.last_name,
            'email'          : u.email,
            'address'        : u.get_profile().postal_address,
            'postal_code'    : u.get_profile().postal_code,
            'city'           : u.get_profile().postal_city,
            'country'        : u.get_profile().postal_country,
            'form'           : form,
            'saved'          : True,
        })

        # redirect the user to the home page (already logged-in)
        context.update(csrf(request))
        return HttpResponse(t.render(context))
  

##
# Show a dummy page telling that your password has been sent to your email.
def forgot_password(request):
        t = loader.get_template('forgot_password.html')
        form = PassForm()
        context = RequestContext(request, {
            'form' : form,
        })
        context.update(csrf(request))
        return HttpResponse(t.render(context))


##
# Simulate sending a new password (password recovery).
def sendPassword(request):
    if request.method == 'POST':
        form = PassForm(request.POST)
        # check the existence of the user by registered email
        if form.is_valid():
            u = User.objects.get(email=request.POST.get('email', ''))
            if u is not None:
                t = loader.get_template('forgot_password.html')
                context = RequestContext(request, {
                    'email'         : u.email,
                    'password_sent' : True,
                })
                return HttpResponse(t.render(context))

        # if the form is not valid, immediately give an error
        t = loader.get_template('forgot_password.html')
        form = PassForm(request.POST)
        context = RequestContext(request, {
            'form'         : form,
            'doesnt_exist' : True,
        })
        return HttpResponse(t.render(context))
