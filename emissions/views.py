# -*- coding: utf-8 -*-
"""排放数据模块 - 视图"""
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Sum, Avg, Count, Q
from .models import EmissionRecord, EmissionSource, Region, Industry
from users.models import OperationLog


def is_admin(user):
    return user.is_staff


# ==================== 管理后台视图 ====================

@login_required
@user_passes_test(is_admin)
def admin_emission_list(request):
    """管理后台 - 排放数据列表"""
    records = EmissionRecord.objects.select_related('region', 'industry', 'source').all()

    # 筛选
    year = request.GET.get('year', '')
    region_id = request.GET.get('region', '')
    source_id = request.GET.get('source', '')
    keyword = request.GET.get('keyword', '')

    if year:
        records = records.filter(year=int(year))
    if region_id:
        records = records.filter(region_id=int(region_id))
    if source_id:
        records = records.filter(source_id=int(source_id))
    if keyword:
        records = records.filter(
            Q(industry__name__icontains=keyword) | Q(region__name__icontains=keyword)
        )

    paginator = Paginator(records, 20)
    page = request.GET.get('page', 1)
    records = paginator.get_page(page)

    context = {
        'records': records,
        'regions': Region.objects.all(),
        'sources': EmissionSource.objects.all(),
        'years': list(range(2025, 2014, -1)),
        'filter_year': year,
        'filter_region': region_id,
        'filter_source': source_id,
        'keyword': keyword,
    }
    return render(request, 'admin_panel/emission_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_emission_create(request):
    """管理后台 - 新增排放记录"""
    if request.method == 'POST':
        record = EmissionRecord(
            year=int(request.POST['year']),
            quarter=int(request.POST['quarter']),
            region_id=int(request.POST['region']),
            industry_id=int(request.POST['industry']),
            source_id=int(request.POST['source']),
            emission_amount=float(request.POST['emission_amount']),
            energy_consumption=float(request.POST.get('energy_consumption', 0)),
            gdp=float(request.POST.get('gdp', 0)),
            population=float(request.POST.get('population', 0)),
            energy_efficiency=float(request.POST.get('energy_efficiency', 0)),
        )
        record.save()
        OperationLog.objects.create(
            user=request.user, action='create', target='排放数据',
            detail=f'新增排放记录: {record}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, '排放记录创建成功')
        return redirect('emissions:admin_emission_list')

    context = {
        'regions': Region.objects.all(),
        'industries': Industry.objects.select_related('source').all(),
        'sources': EmissionSource.objects.all(),
        'years': list(range(2025, 2014, -1)),
        'action': '新增',
    }
    return render(request, 'admin_panel/emission_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_emission_edit(request, pk):
    """管理后台 - 编辑排放记录"""
    record = get_object_or_404(EmissionRecord, pk=pk)

    if request.method == 'POST':
        record.year = int(request.POST['year'])
        record.quarter = int(request.POST['quarter'])
        record.region_id = int(request.POST['region'])
        record.industry_id = int(request.POST['industry'])
        record.source_id = int(request.POST['source'])
        record.emission_amount = float(request.POST['emission_amount'])
        record.energy_consumption = float(request.POST.get('energy_consumption', 0))
        record.gdp = float(request.POST.get('gdp', 0))
        record.population = float(request.POST.get('population', 0))
        record.energy_efficiency = float(request.POST.get('energy_efficiency', 0))
        record.save()
        OperationLog.objects.create(
            user=request.user, action='update', target='排放数据',
            detail=f'修改排放记录: {record}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, '排放记录更新成功')
        return redirect('emissions:admin_emission_list')

    context = {
        'record': record,
        'regions': Region.objects.all(),
        'industries': Industry.objects.select_related('source').all(),
        'sources': EmissionSource.objects.all(),
        'years': list(range(2025, 2014, -1)),
        'action': '编辑',
    }
    return render(request, 'admin_panel/emission_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_emission_delete(request, pk):
    """管理后台 - 删除排放记录"""
    record = get_object_or_404(EmissionRecord, pk=pk)
    OperationLog.objects.create(
        user=request.user, action='delete', target='排放数据',
        detail=f'删除排放记录: {record}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    record.delete()
    messages.success(request, '排放记录已删除')
    return redirect('emissions:admin_emission_list')


@login_required
@user_passes_test(is_admin)
def admin_emission_import(request):
    """管理后台 - CSV批量导入"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded = csv_file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        count = 0
        for row in reader:
            try:
                region = Region.objects.get(name=row['地区'])
                industry = Industry.objects.get(name=row['行业'])
                source = EmissionSource.objects.get(name=row['排放源'])

                EmissionRecord.objects.create(
                    year=int(row['年份']),
                    quarter=int(row['季度']),
                    region=region,
                    industry=industry,
                    source=source,
                    emission_amount=float(row['排放量']),
                    energy_consumption=float(row.get('能源消耗', 0)),
                    gdp=float(row.get('GDP', 0)),
                    population=float(row.get('人口', 0)),
                    energy_efficiency=float(row.get('能源效率', 0)),
                )
                count += 1
            except Exception as e:
                continue

        OperationLog.objects.create(
            user=request.user, action='import', target='排放数据',
            detail=f'批量导入 {count} 条排放记录',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'成功导入 {count} 条记录')

    return redirect('emissions:admin_emission_list')


@login_required
@user_passes_test(is_admin)
def admin_emission_export(request):
    """管理后台 - CSV导出"""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="emission_data.csv"'
    response.write('\ufeff')  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow(['年份', '季度', '地区', '行业', '排放源', '排放量(万吨CO2)',
                     '能源消耗(万吨标准煤)', 'GDP(亿元)', '人口(万人)', '能源效率'])

    records = EmissionRecord.objects.select_related('region', 'industry', 'source').all()
    for r in records:
        writer.writerow([
            r.year, r.quarter, r.region.name, r.industry.name, r.source.name,
            r.emission_amount, r.energy_consumption, r.gdp, r.population, r.energy_efficiency
        ])

    return response


@login_required
@user_passes_test(is_admin)
def admin_source_list(request):
    """管理后台 - 排放源管理"""
    sources = EmissionSource.objects.prefetch_related('industries').all()
    context = {'sources': sources}
    return render(request, 'admin_panel/source_list.html', context)


# ==================== API 接口 ====================

@login_required
def api_emission_summary(request):
    """API - 排放数据概览"""
    year = request.GET.get('year')
    data = EmissionRecord.objects.all()
    if year:
        data = data.filter(year=int(year))

    summary = data.aggregate(
        total_emission=Sum('emission_amount'),
        avg_emission=Avg('emission_amount'),
        record_count=Count('id'),
    )
    return JsonResponse({'code': 0, 'data': summary})


@login_required
def api_emission_by_region(request):
    """API - 按地区统计"""
    year = request.GET.get('year')
    data = EmissionRecord.objects.all()
    if year:
        data = data.filter(year=int(year))

    result = data.values('region__name').annotate(
        total=Sum('emission_amount')
    ).order_by('-total')

    return JsonResponse({
        'code': 0,
        'data': {
            'names': [r['region__name'] for r in result],
            'values': [round(r['total'], 2) for r in result],
        }
    })


@login_required
def api_emission_by_industry(request):
    """API - 按行业统计"""
    year = request.GET.get('year')
    data = EmissionRecord.objects.all()
    if year:
        data = data.filter(year=int(year))

    result = data.values('industry__name').annotate(
        total=Sum('emission_amount')
    ).order_by('-total')

    return JsonResponse({
        'code': 0,
        'data': {
            'names': [r['industry__name'] for r in result],
            'values': [round(r['total'], 2) for r in result],
        }
    })


@login_required
def api_emission_by_source(request):
    """API - 按排放源统计"""
    year = request.GET.get('year')
    data = EmissionRecord.objects.all()
    if year:
        data = data.filter(year=int(year))

    result = data.values('source__name').annotate(
        total=Sum('emission_amount')
    ).order_by('-total')

    return JsonResponse({
        'code': 0,
        'data': {
            'names': [r['source__name'] for r in result],
            'values': [round(r['total'], 2) for r in result],
        }
    })
