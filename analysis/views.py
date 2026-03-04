# -*- coding: utf-8 -*-
"""分析模块 - 视图"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Avg, F
from emissions.models import EmissionRecord, EmissionSource, Region, Industry
import json


@login_required
def trend_analysis(request):
    """排放趋势分析页面"""
    context = {
        'sources': EmissionSource.objects.all(),
        'regions': Region.objects.all(),
        'years': list(range(2015, 2026)),
    }
    return render(request, 'front/trend_analysis.html', context)


@login_required
def structure_analysis(request):
    """排放结构分析页面"""
    context = {
        'sources': EmissionSource.objects.all(),
        'regions': Region.objects.all(),
        'years': list(range(2015, 2026)),
    }
    return render(request, 'front/structure_analysis.html', context)


@login_required
def factor_analysis(request):
    """影响因素分析页面"""
    context = {
        'regions': Region.objects.all(),
        'years': list(range(2015, 2026)),
    }
    return render(request, 'front/factor_analysis.html', context)


# ==================== API 接口 ====================

@login_required
def api_trend_data(request):
    """API - 排放趋势数据"""
    source_id = request.GET.get('source')
    region_id = request.GET.get('region')
    start_year = int(request.GET.get('start_year', 2015))
    end_year = int(request.GET.get('end_year', 2025))
    granularity = request.GET.get('granularity', 'year')  # year 或 quarter

    data = EmissionRecord.objects.filter(year__gte=start_year, year__lte=end_year)
    if source_id:
        data = data.filter(source_id=int(source_id))
    if region_id:
        data = data.filter(region_id=int(region_id))

    if granularity == 'quarter':
        result = data.values('year', 'quarter').annotate(
            total=Sum('emission_amount')
        ).order_by('year', 'quarter')
        labels = [f"{r['year']}Q{r['quarter']}" for r in result]
    else:
        result = data.values('year').annotate(
            total=Sum('emission_amount')
        ).order_by('year')
        labels = [str(r['year']) for r in result]

    values = [round(r['total'], 2) for r in result]

    # 按排放源分组趋势
    source_trends = {}
    for src in EmissionSource.objects.all():
        src_data = data.filter(source=src)
        if granularity == 'quarter':
            src_result = src_data.values('year', 'quarter').annotate(
                total=Sum('emission_amount')
            ).order_by('year', 'quarter')
        else:
            src_result = src_data.values('year').annotate(
                total=Sum('emission_amount')
            ).order_by('year')
        source_trends[src.name] = [round(r['total'], 2) for r in src_result]

    return JsonResponse({
        'code': 0,
        'data': {
            'labels': labels,
            'values': values,
            'source_trends': source_trends,
        }
    })


@login_required
def api_structure_data(request):
    """API - 排放结构数据"""
    year = int(request.GET.get('year', 2025))
    dimension = request.GET.get('dimension', 'source')  # source, industry, region

    data = EmissionRecord.objects.filter(year=year)

    if dimension == 'source':
        result = data.values('source__name').annotate(
            total=Sum('emission_amount')
        ).order_by('-total')
        names = [r['source__name'] for r in result]
    elif dimension == 'industry':
        result = data.values('industry__name').annotate(
            total=Sum('emission_amount')
        ).order_by('-total')[:15]
        names = [r['industry__name'] for r in result]
    else:
        result = data.values('region__name').annotate(
            total=Sum('emission_amount')
        ).order_by('-total')
        names = [r['region__name'] for r in result]

    values = [round(r['total'], 2) for r in result]
    total = sum(values)
    percentages = [round(v / total * 100, 1) if total > 0 else 0 for v in values]

    return JsonResponse({
        'code': 0,
        'data': {
            'names': names,
            'values': values,
            'percentages': percentages,
            'total': round(total, 2),
        }
    })


@login_required
def api_factor_data(request):
    """API - 影响因素数据"""
    region_id = request.GET.get('region')
    start_year = int(request.GET.get('start_year', 2015))
    end_year = int(request.GET.get('end_year', 2025))

    data = EmissionRecord.objects.filter(year__gte=start_year, year__lte=end_year)
    if region_id:
        data = data.filter(region_id=int(region_id))

    yearly = data.values('year').annotate(
        total_emission=Sum('emission_amount'),
        total_gdp=Sum('gdp'),
        total_population=Sum('population'),
        avg_efficiency=Avg('energy_efficiency'),
        total_energy=Sum('energy_consumption'),
    ).order_by('year')

    result = {
        'years': [r['year'] for r in yearly],
        'emissions': [round(r['total_emission'], 2) for r in yearly],
        'gdp': [round(r['total_gdp'], 2) for r in yearly],
        'population': [round(r['total_population'], 2) for r in yearly],
        'energy_efficiency': [round(r['avg_efficiency'], 4) for r in yearly],
        'energy_consumption': [round(r['total_energy'], 2) for r in yearly],
    }

    return JsonResponse({'code': 0, 'data': result})


@login_required
def api_correlation(request):
    """API - 相关性分析"""
    region_id = request.GET.get('region')
    data = EmissionRecord.objects.all()
    if region_id:
        data = data.filter(region_id=int(region_id))

    yearly = data.values('year').annotate(
        emission=Sum('emission_amount'),
        gdp=Sum('gdp'),
        population=Sum('population'),
        efficiency=Avg('energy_efficiency'),
    ).order_by('year')

    yearly_list = list(yearly)

    if len(yearly_list) < 3:
        return JsonResponse({'code': 0, 'data': {'correlations': {}}})

    import numpy as np
    emissions = np.array([r['emission'] for r in yearly_list])
    gdp = np.array([r['gdp'] for r in yearly_list])
    population = np.array([r['population'] for r in yearly_list])
    efficiency = np.array([r['efficiency'] for r in yearly_list])

    def safe_corr(a, b):
        if np.std(a) == 0 or np.std(b) == 0:
            return 0
        return float(np.corrcoef(a, b)[0, 1])

    correlations = {
        'GDP': round(safe_corr(emissions, gdp), 4),
        '人口': round(safe_corr(emissions, population), 4),
        '能源效率': round(safe_corr(emissions, efficiency), 4),
    }

    return JsonResponse({'code': 0, 'data': {'correlations': correlations}})
