from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sendmessage', views.messageform, name='messageform'),
    path('history', views.history, name='history')
]
