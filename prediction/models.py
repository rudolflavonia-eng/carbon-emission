# -*- coding: utf-8 -*-
"""预测模型"""
from django.db import models
from django.contrib.auth.models import User
from emissions.models import Region, Industry, EmissionSource


class PredictionResult(models.Model):
    """预测结果"""
    MODEL_CHOICES = [
        ('lstm', 'LSTM'),
        ('cnn', 'CNN'),
        ('cnn_lstm', 'CNN-LSTM混合'),
    ]

    target_year = models.IntegerField(verbose_name='预测年份')
    target_quarter = models.IntegerField(verbose_name='预测季度')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='地区')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, null=True, blank=True,
                                 verbose_name='行业')
    source = models.ForeignKey(EmissionSource, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='排放源')
    predicted_amount = models.FloatField(verbose_name='预测排放量(万吨CO2)')
    actual_amount = models.FloatField(null=True, blank=True, verbose_name='实际排放量(万吨CO2)')
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES, default='cnn_lstm',
                                  verbose_name='模型类型')
    confidence = models.FloatField(default=0.95, verbose_name='置信度')
    mae = models.FloatField(null=True, blank=True, verbose_name='MAE')
    rmse = models.FloatField(null=True, blank=True, verbose_name='RMSE')
    r2_score = models.FloatField(null=True, blank=True, verbose_name='R2分数')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '预测结果'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.target_year}Q{self.target_quarter} 预测: {self.predicted_amount}万吨'
