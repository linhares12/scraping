from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('atualiza', views.atualiza_precos, name='atualiza_precos')
]