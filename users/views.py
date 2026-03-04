# -*- coding: utf-8 -*-
"""用户模块 - 视图"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from .models import UserProfile, OperationLog
from emissions.models import EmissionRecord, EmissionSource, Region
from alerts.models import AlertRecord


def is_admin(user):
    return user.is_staff


def index(request):
    """首页入口 - 角色自动分流"""
    if not request.user.is_authenticated:
        return redirect('users:login')
    if request.user.is_staff:
        return redirect('users:admin_index')
    return redirect('users:dashboard')


def user_login(request):
    """统一登录页"""
    if request.user.is_authenticated:
        return redirect('users:index')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # 记录登录日志
            OperationLog.objects.create(
                user=user, action='login', target='系统',
                detail=f'用户 {user.username} 登录系统',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            # 角色分流
            if user.is_staff:
                return redirect('users:admin_index')
            return redirect('users:dashboard')
        else:
            messages.error(request, '用户名或密码错误')

    return render(request, 'registration/login.html')


@login_required
def user_logout(request):
    """登出"""
    OperationLog.objects.create(
        user=request.user, action='logout', target='系统',
        detail=f'用户 {request.user.username} 登出系统',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    logout(request)
    return redirect('users:login')


@login_required
def dashboard(request):
    """用户前台 - 仪表盘首页"""
    # 统计数据
    total_emission = EmissionRecord.objects.aggregate(total=Sum('emission_amount'))['total'] or 0
    latest_year = EmissionRecord.objects.order_by('-year').values_list('year', flat=True).first() or 2025
    latest_emission = EmissionRecord.objects.filter(year=latest_year).aggregate(
        total=Sum('emission_amount'))['total'] or 0
    prev_emission = EmissionRecord.objects.filter(year=latest_year - 1).aggregate(
        total=Sum('emission_amount'))['total'] or 1
    change_rate = ((latest_emission - prev_emission) / prev_emission * 100) if prev_emission else 0

    # 排放源统计
    source_count = EmissionSource.objects.count()
    region_count = Region.objects.count()
    record_count = EmissionRecord.objects.count()

    # 最新预警
    recent_alerts = AlertRecord.objects.select_related(
        'emission_record', 'threshold'
    ).order_by('-created_at')[:5]
    unread_alerts = AlertRecord.objects.filter(is_read=False).count()

    context = {
        'total_emission': round(total_emission, 2),
        'latest_year': latest_year,
        'latest_emission': round(latest_emission, 2),
        'change_rate': round(change_rate, 2),
        'source_count': source_count,
        'region_count': region_count,
        'record_count': record_count,
        'recent_alerts': recent_alerts,
        'unread_alerts': unread_alerts,
    }
    return render(request, 'front/dashboard.html', context)


@login_required
def profile(request):
    """个人中心"""
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        organization = request.POST.get('organization', '')

        request.user.email = email
        request.user.save()

        user_profile.phone = phone
        user_profile.organization = organization
        if 'avatar' in request.FILES:
            user_profile.avatar = request.FILES['avatar']
        user_profile.save()
        messages.success(request, '资料更新成功')
        return redirect('users:profile')

    context = {'user_profile': user_profile}
    if request.user.is_staff:
        return render(request, 'admin_panel/profile.html', context)
    return render(request, 'front/profile.html', context)


@login_required
def change_password(request):
    """修改密码"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(old_password):
            messages.error(request, '原密码错误')
        elif new_password != confirm_password:
            messages.error(request, '两次输入的新密码不一致')
        elif len(new_password) < 6:
            messages.error(request, '新密码长度不能少于6位')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, '密码修改成功')

    return redirect('users:profile')


# ==================== 管理后台视图 ====================

@login_required
@user_passes_test(is_admin)
def admin_index(request):
    """管理后台 - 首页"""
    context = {
        'user_count': User.objects.count(),
        'record_count': EmissionRecord.objects.count(),
        'alert_count': AlertRecord.objects.filter(is_resolved=False).count(),
        'source_count': EmissionSource.objects.count(),
        'region_count': Region.objects.count(),
        'recent_logs': OperationLog.objects.select_related('user')[:10],
        'recent_alerts': AlertRecord.objects.select_related(
            'emission_record', 'threshold'
        ).order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/index.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    """管理后台 - 用户列表"""
    users = User.objects.all().order_by('-date_joined')
    keyword = request.GET.get('keyword', '')
    if keyword:
        users = users.filter(username__icontains=keyword)

    paginator = Paginator(users, 15)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)
    return render(request, 'admin_panel/user_list.html', {'users': users, 'keyword': keyword})


@login_required
@user_passes_test(is_admin)
def admin_user_create(request):
    """管理后台 - 新增用户"""
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')
        is_staff = request.POST.get('is_staff') == 'on'
        phone = request.POST.get('phone', '')
        organization = request.POST.get('organization', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
        else:
            user = User.objects.create_user(
                username=username, password=password,
                email=email, is_staff=is_staff
            )
            UserProfile.objects.create(
                user=user, phone=phone, organization=organization
            )
            OperationLog.objects.create(
                user=request.user, action='create', target='用户管理',
                detail=f'新增用户: {username}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, '用户创建成功')
            return redirect('users:admin_user_list')

    return render(request, 'admin_panel/user_form.html', {'action': '新增'})


@login_required
@user_passes_test(is_admin)
def admin_user_edit(request, pk):
    """管理后台 - 编辑用户"""
    user = get_object_or_404(User, pk=pk)
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user.email = request.POST.get('email', '')
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.is_active = request.POST.get('is_active') == 'on'
        user.save()

        user_profile.phone = request.POST.get('phone', '')
        user_profile.organization = request.POST.get('organization', '')
        user_profile.save()

        new_password = request.POST.get('new_password', '')
        if new_password:
            user.set_password(new_password)
            user.save()

        OperationLog.objects.create(
            user=request.user, action='update', target='用户管理',
            detail=f'修改用户: {user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, '用户信息更新成功')
        return redirect('users:admin_user_list')

    context = {
        'edit_user': user,
        'user_profile': user_profile,
        'action': '编辑',
    }
    return render(request, 'admin_panel/user_form.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_delete(request, pk):
    """管理后台 - 删除用户"""
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, '不能删除当前登录用户')
    else:
        OperationLog.objects.create(
            user=request.user, action='delete', target='用户管理',
            detail=f'删除用户: {user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        user.delete()
        messages.success(request, '用户已删除')
    return redirect('users:admin_user_list')


@login_required
@user_passes_test(is_admin)
def admin_logs(request):
    """管理后台 - 操作日志"""
    logs = OperationLog.objects.select_related('user').all()

    action = request.GET.get('action', '')
    if action:
        logs = logs.filter(action=action)

    keyword = request.GET.get('keyword', '')
    if keyword:
        logs = logs.filter(detail__icontains=keyword)

    paginator = Paginator(logs, 20)
    page = request.GET.get('page', 1)
    logs = paginator.get_page(page)

    context = {
        'logs': logs,
        'action': action,
        'keyword': keyword,
        'action_choices': OperationLog.ACTION_CHOICES,
    }
    return render(request, 'admin_panel/logs.html', context)
