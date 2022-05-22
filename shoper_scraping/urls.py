from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('atualizar', views.atualiza_precos, name='atualiza_precos'),
    path('exportar/assortment', views.assortment, name='assortment'),
    path('exportar/seller', views.seller, name='seller')
]