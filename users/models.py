# -*- coding: utf-8 -*-
"""用户模型 - 扩展Django自带User"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户扩展资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField(max_length=20, blank=True, default='', verbose_name='手机号')
    organization = models.CharField(max_length=100, blank=True, default='', verbose_name='所属机构')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username} 的资料'


class OperationLog(models.Model):
    """操作日志"""
    ACTION_CHOICES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('create', '新增'),
        ('update', '修改'),
        ('delete', '删除'),
        ('import', '导入'),
        ('export', '导出'),
        ('predict', '预测'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作用户')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    target = models.CharField(max_length=100, verbose_name='操作对象')
    detail = models.TextField(blank=True, default='', verbose_name='操作详情')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.get_action_display()} - {self.target}'
