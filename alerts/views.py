# -*- coding: utf-8 -*-
"""预警模块 - 视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Q
from .models import ThresholdConfig, AlertRecord
from emissions.models import EmissionSource, Region, Industry
from users.models import OperationLog


def is_admin(user):
    return user.is_staff


@login_required
def alert_list(request):
    """用户前台 - 预警列表"""
    alerts = AlertRecord.objects.select_related(
        'emission_record__region', 'emission_record__industry',
        'emission_record__source', 'threshold'
    ).all()

    level = request.GET.get('level', '')
    if level:
        alerts = alerts.filter(alert_level=level)

    status = request.GET.get('status', '')
    if status == 'unread':
        alerts = alerts.filter(is_read=False)
    elif status == 'resolved':
        alerts = alerts.filter(is_resolved=True)

    paginator = Paginator(alerts, 15)
    page = request.GET.get('page', 1)
    alerts = paginator.get_page(page)

    context = {
        'alerts': alerts,
        'level': level,
        'status': status,
        'unread_count': AlertRecord.objects.filter(is_read=False).count(),
    }
    return render(request, 'front/alert_list.html', context)


@login_required
def mark_as_read(request, pk):
    """标记预警为已读"""
    alert = get_object_or_404(AlertRecord, pk=pk)
    alert.is_read = True
    alert.save()
    return JsonResponse({'code': 0, 'msg': '已标记为已读'})


# ==================== API 接口 ====================

@login_required
def api_alert_stats(request):
    """API - 预警统计"""
    stats = AlertRecord.objects.aggregate(
        total=Count('id'),
        unread=Count('id', filter=Q(is_read=False)),
        yellow=Count('id', filter=Q(alert_level='yellow')),
        orange=Count('id', filter=Q(alert_level='orange')),
        red=Count('id', filter=Q(alert_level='red')),
    )
    return JsonResponse({'code': 0, 'data': stats})


@login_required
def api_recent_alerts(request):
    """API - 最近预警"""
    alerts = AlertRecord.objects.select_related(
        'emission_record__region', 'emission_record__source'
    ).order_by('-created_at')[:10]

    result = []
    for a in alerts:
        result.append({
            'id': a.id,
            'level': a.alert_level,
            'message': a.alert_message,
            'value': a.emission_value,
            'threshold': a.threshold_value,
            'is_read': a.is_read,
            'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse({'code': 0, 'data': result})


# ==================== 管理后台视图 ====================

@login_required
@user_passes_test(is_admin)
def admin_threshold_list(request):
    """管理后台 - 阈值配置列表"""
    thresholds = ThresholdConfig.objects.select_related(
        'region', 'industry', 'source', 'updated_by'
    ).all()

    paginator = Paginator(thresholds, 15)
    page = request.GET.get('page', 1)
    thresholds = paginator.get_page(page)

    context = {'thresholds': thresholds}
    return render(request, 'admin_panel/threshold_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_threshold_create(request):
    """管理后台 - 新增阈值配置"""
    if request.method == 'POST':
        tc = ThresholdConfig(
            name=request.POST['name'],
            region_id=request.POST.get('region') or None,
            industry_id=request.POST.get('industry') or None,
            source_id=request.POST.get('source') or None,
            method=request.POST['method'],
            mean_value=float(request.POST.get('mean_value', 0)) or None,
            std_value=float(request.POST.get('std_value', 0)) or None,
            upper_limit=float(request.POST['upper_limit']),
            warning_level=request.POST['warning_level'],
            updated_by=request.user,
        )
        tc.save()
        OperationLog.objects.create(
            user=request.user, action='create', target='阈值配置',
            detail=f'新增阈值配置: {tc.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, '阈值配置创建成功')
        return redirect('alerts:admin_threshold_list')

    context = {
        'regions': Region.objects.all(),
        'industries': Industry.objects.all(),
        'sources': EmissionSource.objects.all(),
        'action': '新增',
    }
    return render(request, 'admin_panel/threshold_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_threshold_edit(request, pk):
    """管理后台 - 编辑阈值配置"""
    tc = get_object_or_404(ThresholdConfig, pk=pk)

    if request.method == 'POST':
        tc.name = request.POST['name']
        tc.region_id = request.POST.get('region') or None
        tc.industry_id = request.POST.get('industry') or None
        tc.source_id = request.POST.get('source') or None
        tc.method = request.POST['method']
        tc.mean_value = float(request.POST.get('mean_value', 0)) or None
        tc.std_value = float(request.POST.get('std_value', 0)) or None
        tc.upper_limit = float(request.POST['upper_limit'])
        tc.warning_level = request.POST['warning_level']
        tc.updated_by = request.user
        tc.save()

        OperationLog.objects.create(
            user=request.user, action='update', target='阈值配置',
            detail=f'修改阈值配置: {tc.name}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, '阈值配置更新成功')
        return redirect('alerts:admin_threshold_list')

    context = {
        'threshold': tc,
        'regions': Region.objects.all(),
        'industries': Industry.objects.all(),
        'sources': EmissionSource.objects.all(),
        'action': '编辑',
    }
    return render(request, 'admin_panel/threshold_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_threshold_delete(request, pk):
    """管理后台 - 删除阈值配置"""
    tc = get_object_or_404(ThresholdConfig, pk=pk)
    OperationLog.objects.create(
        user=request.user, action='delete', target='阈值配置',
        detail=f'删除阈值配置: {tc.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    tc.delete()
    messages.success(request, '阈值配置已删除')
    return redirect('alerts:admin_threshold_list')
