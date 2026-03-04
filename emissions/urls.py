# -*- coding: utf-8 -*-
"""排放数据模块 - 路由配置"""
from django.urls import path
from . import views

app_name = 'emissions'

urlpatterns = [
    # 管理后台 - 排放数据管理
    path('admin-panel/data/', views.admin_emission_list, name='admin_emission_list'),
    path('admin-panel/data/create/', views.admin_emission_create, name='admin_emission_create'),
    path('admin-panel/data/<int:pk>/edit/', views.admin_emission_edit, name='admin_emission_edit'),
    path('admin-panel/data/<int:pk>/delete/', views.admin_emission_delete, name='admin_emission_delete'),
    path('admin-panel/data/import/', views.admin_emission_import, name='admin_emission_import'),
    path('admin-panel/data/export/', views.admin_emission_export, name='admin_emission_export'),
    # 管理后台 - 排放源管理
    path('admin-panel/sources/', views.admin_source_list, name='admin_source_list'),
    # API接口 - 提供给图表使用
    path('api/summary/', views.api_emission_summary, name='api_emission_summary'),
    path('api/by-region/', views.api_emission_by_region, name='api_emission_by_region'),
    path('api/by-industry/', views.api_emission_by_industry, name='api_emission_by_industry'),
    path('api/by-source/', views.api_emission_by_source, name='api_emission_by_source'),
]
