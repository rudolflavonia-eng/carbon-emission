# -*- coding: utf-8 -*-
"""用户模块 - 路由配置"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 首页入口 - 根据角色自动分流
    path('', views.index, name='index'),
    # 登录/登出
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # 用户前台
    path('dashboard/', views.dashboard, name='dashboard'),
    # 个人中心
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    # 管理后台
    path('admin-panel/', views.admin_index, name='admin_index'),
    path('admin-panel/users/', views.admin_user_list, name='admin_user_list'),
    path('admin-panel/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin-panel/users/<int:pk>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin-panel/users/<int:pk>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-panel/logs/', views.admin_logs, name='admin_logs'),
]
