# filepath: c:\Users\muckh\Documents\python\stock_analysis\stock_analysis\backtest_app\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]