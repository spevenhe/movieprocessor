from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from datetime import datetime
from datetime import timezone as zone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import json
from django.utils import timezone,dateparse
from django.contrib import messages

from django.db import transaction
from django.db.models import Q 
from django.core import serializers
from django.core.paginator import Paginator
from movie_processor.models import *
from movie_processor.forms import * 
from django.utils.translation import ugettext

import difflib



try:
    import requests
except:
    import os
    os.system('pip install requests')
    import requests
from requests.exceptions import RequestException
try:
    import lxml
except:
    import os
    os.system('pip install lxml')
    import lxml
try:
    import bs4
except:
    import os
    os.system('pip install bs4')
    import bs4    
from bs4 import BeautifulSoup
import csv
import re
import random

# access restriction
from django.contrib.auth.decorators import login_required

# Used to generate a one-time-use token to verify a user's email address
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail
import numpy as np
def home_page(request):
    context = {}
    context['if_home'] = True
    return render(request,'movie_processor/home.html',context)

def login_page(request):
    context = {}

    if User.objects.filter(id=request.user.id).exists():
        return redirect(reverse('profile',args=[request.user.id]))

    if request.method == 'GET':
        context['login_form'] = LoginForm()
        return render(request, 'movie_processor/login.html', context)
    
    form = LoginForm(request.POST)
    context['login_form'] = form

    if not form.is_valid():
        return render(request, 'movie_processor/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    if not new_user.is_active:
        return render(request, 'movie_processor/login.html', context)

    login(request, new_user)
    return redirect(reverse('profile', args=[request.user.id]))

@transaction.atomic
def register_page(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'movie_processor/register.html', context)

    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'movie_processor/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'])

    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()
    movieFan = MovieFans(user = new_user)
    movieFan.save()
    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
Please click the link below to verify your email address and
complete the registration of your account:

  http://{host}{path}
""".format(host=request.get_host(), 
           path=reverse('confirm', args=(new_user.username, token)))


    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_processor.settings")
    send_mail(subject="Verify your email address",
              message= email_body,
            #   from_email="movieprocessor@gmail.com",
              from_email="movieprocessor@gmail.com",
              recipient_list=[new_user.email])
    
    context['email'] = form.cleaned_data['email']
    return render(request, 'movie_processor/needs-confirmation.html', context)


@transaction.atomic
def confirm_action(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    return render(request, 'movie_processor/confirmed.html', {})


def search_result(request):
    if request.method == 'GET':
        return render(request, 'movie_processor/home.html', {})
    context = {}
    movie_name = Movie.objects.all().filter(Q(name__icontains = request.POST['search_content']) | Q(director__icontains = request.POST['search_content'])| Q(movie_type__icontains = request.POST['search_content']))
    number = len(movie_name)
    if(number == 0):
        context['not_found'] = 'This movie is not found.'
        return render(request, 'movie_processor/search.html', context)
    # TODO: enable page list
    pages = Paginator(movie_name, 10)
    context['movie_name'] = pages.get_page(1)
    context['search_content'] = request.POST['search_content']

    page_list = []
    for i in range(pages.num_pages):
        page_list.append(i+1)
    context['total_page'] = page_list
    return render(request, 'movie_processor/search.html', context)

# TODO: Try to get into database using ajax. return movie lists and search keywords
def search_ajax(request):
    page_number = request.POST.get('page')
    key_word = request.POST.get('search_content')
    
    movie_type = Movie.objects.all().filter(Q(name__icontains = request.POST['search_content']) | Q(director__icontains = request.POST['search_content'])| Q(movie_type__icontains = request.POST['search_content']))
    pages = Paginator(movie_type, 10)
    total_page = pages.num_pages
    movie_type = pages.get_page(page_number)

    response_text = serializers.serialize('json', movie_type)
    json_text = json.loads(response_text)
    json_text.append({'page_number':total_page})
    json_text.append({'current_page':page_number})
    json_text.append({'search_content':key_word})
    response_text = json.dumps(json_text)
    return HttpResponse(response_text, content_type='application/json')

def auto_search(request):
    key_word = request.GET.get('search_name')
    movie_name = Movie.objects.all().filter(Q(name__icontains = key_word) | Q(director__icontains = key_word)| Q(movie_type__icontains = key_word))
    movie_name = Paginator(movie_name, 6).get_page(1)
    response_text = serializers.serialize('json', movie_name)
    return HttpResponse(response_text, content_type='application/json')

@login_required
def profile_page(request, id):
    context = {}

    try:
        if request.user.id != id:
            context['status'] = False
        else:
            context['status'] = True
        movie_fan = MovieFans.objects.get(id=id) 
        context['movie_fan'] = movie_fan 
        context['form'] = profileForm()  
        context['posts'] = Post.objects.filter(user=movie_fan.user)

        movie_history_split = movie_fan.rating_history.split(',')[:-1]
        history_list = []
        history_dict = {}

        for history_obj in movie_history_split:
            history_obj_split = history_obj.split(':')
            history_list.append(history_obj_split[0])
            history_dict[history_obj_split[0]] = history_obj_split[1]

        fav_list = []
        for key in history_dict.keys():
            if(int(history_dict[key]) >= 9):
                fav_list.append(key)

        context['rate_history'] = Movie.objects.filter(id__in = history_list)
        context['favorite_movies'] = Movie.objects.filter(id__in = fav_list)
        return render(request, 'movie_processor/profile.html', context)
    except:
        context['not_exist'] = True
        
        return render(request, 'movie_processor/profile.html', context)

@login_required
def update_picture(request):
    user=User.objects.get(id=request.user.id)
    new_fan = MovieFans.objects.get(user=user)
    form = profileForm(request.POST, request.FILES, instance=new_fan)
    if not form.is_valid():
        messages.warning(request, 'You must choose a picture.')
    elif 'content_type' not in dir (form.cleaned_data['profile_picture']):
        url=reverse('profile',kwargs={'id':user.id})
        return redirect(url)
    else:
        pic = form.cleaned_data['profile_picture']
        new_fan.profile_picture = pic
        new_fan.content_type = form.cleaned_data['profile_picture'].content_type
        new_fan.save()

    url=reverse('profile',kwargs={'id':user.id})
    return redirect(url)    

def get_photo(request, id):
    movie_fan = get_object_or_404(MovieFans, id=id)
    if not movie_fan.profile_picture:
        return Http404
    return HttpResponse(movie_fan.profile_picture, content_type=movie_fan.content_type)

def movie_page(request,movie_id):
    context = {}
    language_message = ugettext('you language')
    context['language_message'] = language_message
    movie = Movie.objects.get(id = movie_id)
    if( request.user.id != None):
        MovieFan = MovieFans.objects.get(user = request.user)
        context['isRated'] = MovieFan.isMovieRated(str(movie_id)) 
        if(context['isRated'] == True):
            context['ratedScore'] = MovieFan.get_rated_movie(str(movie_id))
    context['movie'] = movie

    context['recommand_movie'] = get_recommand_movies(movie)

    if (len(Product.objects.all().filter(movie = movie.name))==0):
        try:
            url = "https://www.amazon.com/s?k=moviename+movie"
            url = re.sub("moviename", movie.name, url)
            url = re.sub(" ", "+", url)
            user_agent={"user-agent":"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)"}
            user_agents =['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Beamrise/17.2.0.9 Chrome/17.0.939.0 Safari/535.8','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7','Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)','Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50','Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50','Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11','Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11']
            i=random.randint(0,7)
            user_agent['user-agent']=user_agents[i]
            response = requests.get(url, headers = user_agent)
            html = response.text
            soup = BeautifulSoup(html,'lxml')
            items = range(5)
            for item in items:
                new_goods = Product(product_picture=soup.select('img.s-image')[item]["src"],
                    name=soup.select('a span.a-size-medium')[item].string,
                    link="https://www.amazon.com" + str(soup.select('h5 a.a-link-normal')[item]["href"]),
                    movie=movie.name,
                   
                )
                new_goods.save()
        except:
            context['error_message'] = ugettext("Amzon block the product request")
            return render(request,'movie_processor/error.html',context)

    goods = Product.objects.all().filter(movie = movie.name)
    context['goods'] = goods

    if not request.user.is_authenticated:
       context['status'] = False
    else:
        context['status'] = True

    return render(request,'movie_processor/movie.html',context)

def get_recommand_movies(movie):
    movie_type = movie.movie_type
    movie_director = movie.director
    same_director_movie = Movie.objects.filter(director = movie_director).exclude(name = movie.name)
    number = len(same_director_movie)
    topThreeMovie = {}
    if(number!=0):
        for movietemp in same_director_movie:
            topThreeMovie[str(movietemp.id)] = movietemp.id
            if(len(topThreeMovie) >= 4):
                break

    all_movie_type = Movie.objects.all().exclude(id = movie.id).values_list('movie_type','id')
    topThree = {}
    for name in all_movie_type:
        temp = difflib.SequenceMatcher(lambda x: x==",", movie_type, name[0]).quick_ratio()
        movie_id = name[1]
        topThree[str(movie_id)] = temp

    topThree = sorted(topThree.items(),key = lambda item:item[1],reverse = True)
    for top in topThree:
        movie_same_type = Movie.objects.get(id = top[0])
        topThreeMovie[top[0]] = movie_same_type
        if(len(topThreeMovie) >= 5):
            break
    five_re_movie = Movie.objects.filter(id__in = topThreeMovie.keys())
    return five_re_movie



def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def refresh(request,movie_id):
    lastupdatetime = request.POST.get('last_refresh')
    if (lastupdatetime==None):
        movie = Movie.objects.get(id = movie_id)
        newposts=Post.objects.all().filter(movie = movie)
        current_time=datetime.now(zone.utc).astimezone().isoformat()

        newcomments=Comment.objects.all().filter(movie = movie)
        comment_text=serializers.serialize('json', newcomments)
        response_text=serializers.serialize('json', newposts)
        
        json_text=json.loads(response_text)
        json_comment_text=json.loads(comment_text)
         
        json_text.append({'comments':json_comment_text})
        json_text.append({'movie_id':movie_id})
        json_text.append({'lastupdatetime':current_time})

        if not request.user.is_authenticated:
            json_text.append({'status':False})
        else:
            json_text.append({'status':True})

        response_text = json.dumps(json_text)
        return HttpResponse(response_text, content_type='application/json')
  
    try:
        lastupdatetime = dateparse.parse_datetime(lastupdatetime)
        current_time=datetime.now(zone.utc).astimezone().isoformat()
        movie = Movie.objects.get(id = movie_id)
        newposts=Post.objects.all().filter(movie = movie).exclude(post_time__lt = lastupdatetime)

        newcomments=Comment.objects.all().filter(movie = movie).exclude(comment_time__lt = lastupdatetime)
        comment_text=serializers.serialize('json', newcomments)

        response_text=serializers.serialize('json', newposts)

        json_comment_text=json.loads(comment_text)
        json_text=json.loads(response_text)
        
        json_text.append({'comments':json_comment_text})
        json_text.append({'movie_id':movie_id})
        json_text.append({'lastupdatetime':current_time})

        response_text = json.dumps(json_text)
        
        if not request.user.is_authenticated:
            json_text.append({'status':False})
        else:
            json_text.append({'status':True})

        response_text = json.dumps(json_text)

        return HttpResponse(response_text, content_type='application/json')
    except:
        raise Http404

def add_post(request):
    if request.method != 'POST':
        raise Http404

    if not 'post' in request.POST or not request.POST['post']:
        message = ugettext('You must enter an post to add.')
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    movie = Movie.objects.get(id = request.POST['id'])
    new_post = Post(user=request.user,
                    text=request.POST['post'],
                    post_time=timezone.now(),
                    username=request.user.username,
                    movie=movie,
            )
    new_post.save()
    posts = Post.objects.all().filter(movie=movie).order_by('-post_time')
    response_text = serializers.serialize('json', posts)
    return HttpResponse(response_text, content_type='application/json')

def rate_movie(request, movie_id):
    context = {}
    movie = Movie.objects.get(id = movie_id)
    
    
    try:
        number = int(request.POST['rating'])
        score =float(movie.score) 
        ratings_number = int(movie.ratings_number)
        movie.score = str(np.round((score*ratings_number+number*ratings_number)/2/ratings_number,1))
        movie.ratings_number = str(ratings_number+1)
        movie.save()

        context['movie'] = movie
        if( request.user.id != None):
            MovieFan = MovieFans.objects.get(user = request.user)
            MovieFan.add_rated_movie(str(movie_id),str(number))
            MovieFan.save()
            context['isRated'] = MovieFan.isMovieRated(str(movie_id)) 
            if(context['isRated'] == True):
                context['ratedScore'] = MovieFan.get_rated_movie(str(movie_id))
    except:
        raise Http404
 #   context['recommand_movie'] = get_recommand_movies(movie)
    return redirect(reverse('movie', args=[movie_id]))

def logout_action(request):
  logout(request)
  return redirect(reverse('home'))

def add_comment(request):
    if request.method != 'POST':
        raise Http404

    if not 'comment' in request.POST or not request.POST['comment']:
        message = 'You must enter an comment to add.'
        json_error = '{ "error": "'+message+'" }'
        return HttpResponse(json_error, content_type='application/json')

    movie = Movie.objects.get(id = request.POST['movie_id'])
    new_comment = Comment(user=request.user,
                    text=request.POST['comment'],
                    comment_time=timezone.now(),
                    username=request.user.username,
                    post_id=request.POST['post_id'],
                    movie=movie,
            )
    new_comment.save()
    comments = Comment.objects.all().filter(movie=movie).order_by('-comment_time')
    response_text = serializers.serialize('json', comments)
    return HttpResponse(response_text, content_type='application/json')