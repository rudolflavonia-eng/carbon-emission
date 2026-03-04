# -*- coding: utf-8 -*-
"""预警模块 - 路由配置"""
from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # 用户前台
    path('', views.alert_list, name='list'),
    path('<int:pk>/read/', views.mark_as_read, name='mark_read'),
    # API
    path('api/stats/', views.api_alert_stats, name='api_stats'),
    path('api/recent/', views.api_recent_alerts, name='api_recent'),
    # 管理后台 - 阈值配置
    path('admin-panel/thresholds/', views.admin_threshold_list, name='admin_threshold_list'),
    path('admin-panel/thresholds/create/', views.admin_threshold_create, name='admin_threshold_create'),
    path('admin-panel/thresholds/<int:pk>/edit/', views.admin_threshold_edit, name='admin_threshold_edit'),
    path('admin-panel/thresholds/<int:pk>/delete/', views.admin_threshold_delete, name='admin_threshold_delete'),
]
