from django.urls import path
from . import views

urlpatterns = [
    path('participant/add', views.create_view, name='add participant'),
    path('participant/list', views.list, name='list participants'),
    path('p/<str:playerName>', views.getPlayerRanking, name='player ranking in json'),
    path('r/<str:playerName>', views.currentRanking, name='player ranking page'),
    path('c/<str:playerName>', views.changeRanking, name='change ranking item for player'),
    path('result', views.results, name='result'),
    path('resultpage', views.resultPage, name='resultPage'),
]