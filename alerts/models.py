# -*- coding: utf-8 -*-
"""预警模型"""
from django.db import models
from django.contrib.auth.models import User
from emissions.models import Region, Industry, EmissionSource, EmissionRecord


class ThresholdConfig(models.Model):
    """阈值配置"""
    METHOD_CHOICES = [
        ('normal', '正态分布法'),
        ('standard', '参考排放标准'),
    ]
    LEVEL_CHOICES = [
        ('yellow', '黄色预警'),
        ('orange', '橙色预警'),
        ('red', '红色预警'),
    ]

    name = models.CharField(max_length=100, verbose_name='配置名称')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='地区')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name='行业')
    source = models.ForeignKey(EmissionSource, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='排放源')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='阈值方法')
    mean_value = models.FloatField(null=True, blank=True, verbose_name='均值(μ)')
    std_value = models.FloatField(null=True, blank=True, verbose_name='标准差(σ)')
    upper_limit = models.FloatField(verbose_name='预警上限(万吨CO2)')
    warning_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='yellow',
                                     verbose_name='预警级别')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='更新人')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '阈值配置'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} - {self.get_warning_level_display()}'


class AlertRecord(models.Model):
    """预警记录"""
    LEVEL_CHOICES = [
        ('yellow', '黄色预警'),
        ('orange', '橙色预警'),
        ('red', '红色预警'),
    ]

    emission_record = models.ForeignKey(EmissionRecord, on_delete=models.CASCADE,
                                        related_name='alerts', verbose_name='排放记录')
    threshold = models.ForeignKey(ThresholdConfig, on_delete=models.SET_NULL, null=True,
                                  verbose_name='触发阈值')
    alert_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, verbose_name='预警级别')
    alert_message = models.TextField(verbose_name='预警信息')
    emission_value = models.FloatField(verbose_name='排放值(万吨CO2)')
    threshold_value = models.FloatField(verbose_name='阈值(万吨CO2)')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    is_resolved = models.BooleanField(default=False, verbose_name='是否已处理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '预警记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_alert_level_display()} - {self.alert_message[:50]}'
