# -*- coding: utf-8 -*-
"""碳排放分析及预测平台 - 主路由配置"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    # 用户认证
    path('', include('users.urls')),
    # 排放数据
    path('emissions/', include('emissions.urls')),
    # 数据分析
    path('analysis/', include('analysis.urls')),
    # 智能预测
    path('prediction/', include('prediction.urls')),
    # 预警中心
    path('alerts/', include('alerts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
