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
    
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        
        errors = False
        name_error = ""
        mail_error = ""
        check_email = ""
        message_error = ""
        
        # check if the user already exists in the database
        try:
            check_username = User.objects.get(username=request.POST.get('user'))
            errors = True
            name_error = "Username already exist in the system!"
            print "name error"
        except:
            check_username = None
            
        try:
            check_email = User.objects.get(email=request.POST.get('email'))
            errors = True
            mail_error = "Mail already exist in the system! \n"
            
        except:
            if request.POST.get('email') != request.POST.get('email2'):    
                errors = True
                mail_error = "The mails does not match."
            check_email = None
        
        if request.POST.get('passwd') != request.POST.get('passwd2'):    
            errors = True
            message_error = "The password does not match."

        # if the username or email already exist, go back to the sign-up
        # form and remember the entered data
        if errors:
            t = loader.get_template('signup.html')
            login_form = LoginForm()
            print message_error
            context = RequestContext(request, {
                'username'       : request.POST.get('user'),
                'fname'          : request.POST.get('fname'),
                'sname'          : request.POST.get('sname'),
                'email'          : request.POST.get('email'),
                'email2'         : request.POST.get('email2'),
                'passwd'         : request.POST.get('passwd'),
                'pass2'          : request.POST.get('passwd2'),
                'user_exists'    : True,
                'form'           : form,
                'login_form'     : login_form,
                'name_error'     : name_error,
                'mail_error'     : mail_error,
                'check_email'    : check_email,
                'message_error'  : message_error,
                })
            context.update(csrf(request))
            return HttpResponse(t.render(context))
            
        else:

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
            
            t = loader.get_template('signin.html')
            login_form = LoginForm()
            
            categories = Category.objects.all()
            # redirect the user to the login page with a welcome
            context = RequestContext(request, {
                'user'       : request.POST.get('user'),
                'categories'  : categories,
                'login_form': login_form,
                'registered' : True,
            })
            context.update(csrf(request))
            return HttpResponse(t.render(context))
    
    else:
        t = loader.get_template('signup.html')
        form = RegisterForm()
        login_form = LoginForm()
        categories = Category.objects.all()
        context = RequestContext(request,
        {
            'form'       : form,
            'categories' : categories,
            'login_form' : login_form,
        })
        return HttpResponse(t.render(context))


##
# Render a simple login form (sign in)
# If receie data from POST validate the data an login the user.
# If not orif the user is invalid the render the form again.
def signin(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # get the clean data from the POST
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # try to validate the user against the DB
            user = authenticate(username=username, password=password)
            if user is not None:
                # login the user and redirect to the front page.
                login(request, user)
                return HttpResponseRedirect('/')
    
    # if the input values are not correct, or direct access to this page    
    t = loader.get_template('signin.html')
    categories = Category.objects.all()
    login_form = LoginForm()
    context = RequestContext(request, { 
        'categories' : categories,
        'login_form': login_form
    })

    # render the login page.
    return HttpResponse(t.render(context))


##
# Close the session for an user and go to the front page.
def signout(request):
    if is_auth(request):
        logout(request)
        return HttpResponseRedirect('/')  

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
