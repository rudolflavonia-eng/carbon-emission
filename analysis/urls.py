# -*- coding: utf-8 -*-
"""分析模块 - 路由配置"""
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # 用户前台 - 分析页面
    path('trend/', views.trend_analysis, name='trend'),
    path('structure/', views.structure_analysis, name='structure'),
    path('factors/', views.factor_analysis, name='factors'),
    # API接口
    path('api/trend-data/', views.api_trend_data, name='api_trend_data'),
    path('api/structure-data/', views.api_structure_data, name='api_structure_data'),
    path('api/factor-data/', views.api_factor_data, name='api_factor_data'),
    path('api/correlation/', views.api_correlation, name='api_correlation'),
]
