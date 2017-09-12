"""playundercover URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^register/', views.register, name='register'),
    url('^api/v1/', include('social_django.urls', namespace='social')),
    url(r'^authentication/', views.authentication, name='authentication'),
    url(r'^process-register/', views.process_register, name='process_register'),
    url(r'^quickplay/', views.quickplay, name='quickplay'),
    url(r'^register-players/', views.register_players, name='register_players'),
    url(r'^register_players_new_word/', views.register_players_new_word, name='register_players_new_word'),
    url(r'^turn-reveal/', views.turn_reveal_single, name='turn_reveal'),
    url(r'^player-elim/', views.player_elim, name='player_elim'),
    url(r'^replay/', views.replay, name='replay'),
    url(r'^name-list/', views.name_list, name='name_list'),
    url(r'^process-name-list/', views.process_name_list, name='process_name_list'),
    url(r'^process-pair-feedback/', views.process_pair_feedback, name='process_pair_feedback'),
]
