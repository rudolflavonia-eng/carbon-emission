# -*- coding: utf-8 -*-
"""碳排放数据模型"""
from django.db import models


class EmissionSource(models.Model):
    """排放源分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name='排放源名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='编码')
    description = models.TextField(blank=True, default='', verbose_name='描述')
    order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        verbose_name = '排放源'
        verbose_name_plural = verbose_name
        ordering = ['order']

    def __str__(self):
        return self.name


class Region(models.Model):
    """地区"""
    name = models.CharField(max_length=50, verbose_name='地区名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='地区编码')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='children', verbose_name='上级地区')

    class Meta:
        verbose_name = '地区'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return self.name


class Industry(models.Model):
    """行业分类"""
    name = models.CharField(max_length=100, verbose_name='行业名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='行业编码')
    source = models.ForeignKey(EmissionSource, on_delete=models.CASCADE,
                               related_name='industries', verbose_name='所属排放源')
    description = models.TextField(blank=True, default='', verbose_name='描述')

    class Meta:
        verbose_name = '行业'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self):
        return self.name


class EmissionRecord(models.Model):
    """排放记录 - 核心数据表"""
    QUARTER_CHOICES = [
        (1, '第一季度'),
        (2, '第二季度'),
        (3, '第三季度'),
        (4, '第四季度'),
    ]

    year = models.IntegerField(verbose_name='年份')
    quarter = models.IntegerField(choices=QUARTER_CHOICES, verbose_name='季度')
    region = models.ForeignKey(Region, on_delete=models.CASCADE,
                               related_name='emission_records', verbose_name='地区')
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE,
                                 related_name='emission_records', verbose_name='行业')
    source = models.ForeignKey(EmissionSource, on_delete=models.CASCADE,
                               related_name='emission_records', verbose_name='排放源')
    emission_amount = models.FloatField(verbose_name='排放量(万吨CO2)')
    energy_consumption = models.FloatField(default=0, verbose_name='能源消耗(万吨标准煤)')
    gdp = models.FloatField(default=0, verbose_name='GDP(亿元)')
    population = models.FloatField(default=0, verbose_name='人口(万人)')
    energy_efficiency = models.FloatField(default=0, verbose_name='能源效率(吨CO2/万元GDP)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '排放记录'
        verbose_name_plural = verbose_name
        ordering = ['-year', '-quarter']
        indexes = [
            models.Index(fields=['year', 'quarter']),
            models.Index(fields=['region', 'year']),
            models.Index(fields=['industry', 'year']),
            models.Index(fields=['source', 'year']),
        ]

    def __str__(self):
        return f'{self.year}Q{self.quarter} {self.region} {self.industry} {self.emission_amount}万吨'
