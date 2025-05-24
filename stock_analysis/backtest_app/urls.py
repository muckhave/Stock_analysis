# filepath: c:\Users\muckh\Documents\python\stock_analysis\stock_analysis\backtest_app\urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 既存の URL パターン
    path('', views.index, name='index'),  # ルート URL をバックテストページに設定
    path('settings/', views.settings_page, name='settings_page'),
    path('update_stock_data/', views.update_stock_data, name='update_stock_data'),  # 最新データ更新ページ

    # 新しいデータログページの URL パターン
    path('data_log/', views.data_log, name='data_log'),
]