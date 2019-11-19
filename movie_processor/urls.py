from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('login', views.login_page, name='login'),
    path('register', views.register_page, name = "register"),
    path('search', views.search_result,name='search'),
    path('search_ajax', views.search_ajax, name='search_ajax'),
    path('profile/<int:id>', views.profile_page, name='profile'),
    path('movie/<int:movie_id>', views.movie_page, name = "movie"),
    path('confirm-registration/<slug:username>/<slug:token>',
        views.confirm_action, name='confirm'),
    path('logout',views.logout_action, name='logout'),

    path('refresh/<int:movie_id>',views.refresh, name = 'refresh'),
    path('add_post', views.add_post, name='add_post'),
    path('add_comment', views.add_comment, name='add_comment'),
    path('rate_movie/<int:movie_id>',views.rate_movie, name = "rate_movie"),
    path('auto_search', views.auto_search, name='auto_search'),
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('updatepic', views.update_picture, name='updatepic'),
]