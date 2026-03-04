# -*- coding: utf-8 -*-
"""预测模块 - 路由配置"""
from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.prediction_index, name='index'),
    path('run/', views.run_prediction, name='run'),
    path('history/', views.prediction_history, name='history'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('api/history-data/', views.api_history_data, name='api_history_data'),
    # 管理后台 - 模型管理
    path('admin-panel/models/', views.admin_model_manage, name='admin_model_manage'),
]
