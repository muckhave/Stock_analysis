# filepath: c:\Users\muckh\Documents\python\stock_analysis\stock_analysis\backtest_app\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # ルート URL をバックテストページに設定
    path("settings/", views.settings_page, name="settings_page"),
    path("index/", views.index, name="index"),  # バックテストページ
    path("update_stock_data/", views.update_stock_data, name="update_stock_data"),  # 最新データ更新ページ
]