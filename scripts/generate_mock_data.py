# -*- coding: utf-8 -*-
"""
Mock数据生成脚本
生成约5000条碳排放相关数据
使用方法: python manage.py shell < scripts/generate_mock_data.py
或: python manage.py generate_mock_data (需要注册management command)
"""
import os
import sys
import django
import random
import numpy as np
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carbon_emission.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile, OperationLog
from emissions.models import EmissionSource, Region, Industry, EmissionRecord
from prediction.models import PredictionResult
from alerts.models import ThresholdConfig, AlertRecord

# 设置随机种子保证可重复
random.seed(42)
np.random.seed(42)


def create_users():
    """创建用户（2管理员 + 8普通用户）"""
    print("正在创建用户...")

    # 管理员
    admins = [
        {'username': 'admin', 'password': 'admin123', 'email': 'admin@carbon.com',
         'is_staff': True, 'first_name': '系统', 'last_name': '管理员'},
        {'username': 'manager', 'password': 'manager123', 'email': 'manager@carbon.com',
         'is_staff': True, 'first_name': '数据', 'last_name': '管理员'},
    ]

    # 普通用户
    normal_users = [
        {'username': 'zhangsan', 'password': 'user123', 'email': 'zhangsan@example.com',
         'first_name': '三', 'last_name': '张'},
        {'username': 'lisi', 'password': 'user123', 'email': 'lisi@example.com',
         'first_name': '四', 'last_name': '李'},
        {'username': 'wangwu', 'password': 'user123', 'email': 'wangwu@example.com',
         'first_name': '五', 'last_name': '王'},
        {'username': 'zhaoliu', 'password': 'user123', 'email': 'zhaoliu@example.com',
         'first_name': '六', 'last_name': '赵'},
        {'username': 'sunqi', 'password': 'user123', 'email': 'sunqi@example.com',
         'first_name': '七', 'last_name': '孙'},
        {'username': 'zhouba', 'password': 'user123', 'email': 'zhouba@example.com',
         'first_name': '八', 'last_name': '周'},
        {'username': 'wujiu', 'password': 'user123', 'email': 'wujiu@example.com',
         'first_name': '九', 'last_name': '吴'},
        {'username': 'zhengshi', 'password': 'user123', 'email': 'zhengshi@example.com',
         'first_name': '十', 'last_name': '郑'},
    ]

    orgs = ['北京环境研究院', '清华大学', '中国科学院', '国家发改委',
            '生态环境部', '中国碳排放交易所', '绿色发展基金会', '环境工程公司']

    all_users = admins + normal_users
    count = 0
    for i, u_data in enumerate(all_users):
        is_staff = u_data.pop('is_staff', False)
        password = u_data.pop('password')
        user, created = User.objects.get_or_create(
            username=u_data['username'],
            defaults={**u_data, 'is_staff': is_staff}
        )
        if created:
            user.set_password(password)
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=f'138{random.randint(10000000, 99999999)}',
                organization=orgs[i % len(orgs)],
            )
            count += 1

    print(f"  创建了 {count} 个用户 (管理员: admin/admin123, 普通用户: zhangsan/user123)")
    return count


def create_emission_sources():
    """创建排放源分类"""
    print("正在创建排放源...")
    sources_data = [
        {'name': '能源活动', 'code': 'ENERGY', 'description': '化石燃料燃烧和逃逸排放', 'order': 1},
        {'name': '工业生产', 'code': 'INDUSTRY', 'description': '工业过程中的化学反应排放', 'order': 2},
        {'name': '农业活动', 'code': 'AGRICULTURE', 'description': '农业生产过程中的温室气体排放', 'order': 3},
        {'name': '土地利用变化', 'code': 'LAND_USE', 'description': '森林砍伐、土地转换等导致的排放', 'order': 4},
    ]
    sources = {}
    for s_data in sources_data:
        source, _ = EmissionSource.objects.get_or_create(
            code=s_data['code'], defaults=s_data
        )
        sources[source.code] = source

    print(f"  创建了 {len(sources)} 个排放源")
    return sources


def create_regions():
    """创建31个省级行政区"""
    print("正在创建地区...")
    regions_data = [
        ('北京市', 'BJ'), ('天津市', 'TJ'), ('河北省', 'HE'), ('山西省', 'SX'),
        ('内蒙古自治区', 'NM'), ('辽宁省', 'LN'), ('吉林省', 'JL'), ('黑龙江省', 'HL'),
        ('上海市', 'SH'), ('江苏省', 'JS'), ('浙江省', 'ZJ'), ('安徽省', 'AH'),
        ('福建省', 'FJ'), ('江西省', 'JX'), ('山东省', 'SD'), ('河南省', 'HA'),
        ('湖北省', 'HB'), ('湖南省', 'HN'), ('广东省', 'GD'), ('广西壮族自治区', 'GX'),
        ('海南省', 'HI'), ('重庆市', 'CQ'), ('四川省', 'SC'), ('贵州省', 'GZ'),
        ('云南省', 'YN'), ('西藏自治区', 'XZ'), ('陕西省', 'SN'), ('甘肃省', 'GS'),
        ('青海省', 'QH'), ('宁夏回族自治区', 'NX'), ('新疆维吾尔自治区', 'XJ'),
    ]
    regions = {}
    for name, code in regions_data:
        region, _ = Region.objects.get_or_create(code=code, defaults={'name': name})
        regions[code] = region

    print(f"  创建了 {len(regions)} 个地区")
    return regions


def create_industries(sources):
    """创建行业分类（每个排放源5个子行业）"""
    print("正在创建行业...")
    industries_data = {
        'ENERGY': [
            ('电力和热力生产', 'E01'), ('石油加工', 'E02'), ('煤炭开采', 'E03'),
            ('天然气开采', 'E04'), ('交通运输', 'E05'),
        ],
        'INDUSTRY': [
            ('钢铁冶炼', 'I01'), ('水泥生产', 'I02'), ('化学工业', 'I03'),
            ('有色金属冶炼', 'I04'), ('建材制造', 'I05'),
        ],
        'AGRICULTURE': [
            ('畜牧养殖', 'A01'), ('水稻种植', 'A02'), ('农田施肥', 'A03'),
            ('农业机械', 'A04'), ('秸秆焚烧', 'A05'),
        ],
        'LAND_USE': [
            ('森林砍伐', 'L01'), ('草地退化', 'L02'), ('湿地减少', 'L03'),
            ('城市扩张', 'L04'), ('荒漠化', 'L05'),
        ],
    }

    industries = {}
    for source_code, ind_list in industries_data.items():
        for name, code in ind_list:
            industry, _ = Industry.objects.get_or_create(
                code=code,
                defaults={'name': name, 'source': sources[source_code]}
            )
            industries[code] = industry

    print(f"  创建了 {len(industries)} 个行业")
    return industries


def create_emission_records(sources, regions, industries):
    """创建排放记录数据（约4800条）"""
    print("正在生成排放数据...")

    # 各省份基准排放量（反映经济规模差异）
    province_base = {
        'GD': 6.5, 'JS': 6.0, 'SD': 5.8, 'ZJ': 4.5, 'HA': 4.0,
        'HE': 4.5, 'SX': 3.8, 'HB': 3.5, 'HN': 3.2, 'AH': 3.0,
        'SC': 3.0, 'FJ': 2.8, 'BJ': 2.5, 'SH': 2.5, 'LN': 3.0,
        'NM': 3.5, 'JX': 2.2, 'CQ': 2.0, 'GX': 1.8, 'YN': 1.8,
        'GZ': 1.5, 'JL': 1.8, 'HL': 2.0, 'TJ': 1.5, 'SN': 2.0,
        'GS': 1.2, 'XJ': 1.5, 'NX': 0.8, 'QH': 0.5, 'HI': 0.4, 'XZ': 0.2,
    }

    # 各排放源的排放占比
    source_ratio = {'ENERGY': 0.55, 'INDUSTRY': 0.28, 'AGRICULTURE': 0.10, 'LAND_USE': 0.07}

    # 各行业在本排放源内的占比
    industry_ratios = {
        'E01': 0.40, 'E02': 0.20, 'E03': 0.15, 'E04': 0.10, 'E05': 0.15,
        'I01': 0.30, 'I02': 0.25, 'I03': 0.20, 'I04': 0.15, 'I05': 0.10,
        'A01': 0.30, 'A02': 0.25, 'A03': 0.20, 'A04': 0.15, 'A05': 0.10,
        'L01': 0.35, 'L02': 0.20, 'L03': 0.15, 'L04': 0.20, 'L05': 0.10,
    }

    # 季节因子（取暖季排放高）
    quarter_factors = {1: 1.15, 2: 0.90, 3: 0.85, 4: 1.10}

    # 年度增长趋势（模拟碳达峰趋势）
    year_trend = {}
    for y in range(2015, 2026):
        if y <= 2020:
            year_trend[y] = 1.0 + (y - 2015) * 0.025  # 年增2.5%
        else:
            year_trend[y] = year_trend[2020] + (y - 2020) * 0.008  # 增速放缓

    records = []
    count = 0

    # 选择部分省份×行业组合（不是全排列，控制在~4800条）
    # 31省 × 4季度 × 11年 = 1364（每省每年每季度一条汇总太少）
    # 按排放源和行业展开: 选择重点组合

    for region_code, region in regions.items():
        base = province_base.get(region_code, 1.0)

        for year in range(2015, 2026):
            for quarter in range(1, 5):
                # 每个省份每个季度，随机选3-4个行业生成记录
                selected_industries = random.sample(list(industries.items()),
                                                     random.randint(3, 5))

                for ind_code, industry in selected_industries:
                    source_code = ind_code[0]
                    source_map = {'E': 'ENERGY', 'I': 'INDUSTRY',
                                  'A': 'AGRICULTURE', 'L': 'LAND_USE'}
                    s_code = source_map[source_code]
                    source = sources[s_code]

                    # 计算排放量
                    s_ratio = source_ratio[s_code]
                    i_ratio = industry_ratios[ind_code]
                    base_emission = base * s_ratio * i_ratio * 100  # 基准（万吨）
                    yearly_factor = year_trend[year]
                    q_factor = quarter_factors[quarter]
                    noise = np.random.normal(1.0, 0.05)

                    emission = base_emission * yearly_factor * q_factor * noise
                    emission = max(emission, 0.01)

                    # GDP和人口等关联数据
                    gdp_base = base * 1000 * yearly_factor  # 亿元
                    pop_base = base * 800  # 万人
                    energy_cons = emission * 0.65  # 万吨标准煤
                    energy_eff = emission / gdp_base * 4 if gdp_base > 0 else 0

                    records.append(EmissionRecord(
                        year=year,
                        quarter=quarter,
                        region=region,
                        industry=industry,
                        source=source,
                        emission_amount=round(emission, 2),
                        energy_consumption=round(energy_cons + np.random.normal(0, energy_cons * 0.03), 2),
                        gdp=round(gdp_base * q_factor / 4 + np.random.normal(0, gdp_base * 0.02), 2),
                        population=round(pop_base + np.random.normal(0, pop_base * 0.005), 2),
                        energy_efficiency=round(energy_eff + np.random.normal(0, 0.01), 4),
                    ))
                    count += 1

                    # 批量插入（每1000条一批）
                    if len(records) >= 1000:
                        EmissionRecord.objects.bulk_create(records)
                        records = []

    # 插入剩余记录
    if records:
        EmissionRecord.objects.bulk_create(records)

    total = EmissionRecord.objects.count()
    print(f"  生成了 {total} 条排放记录")
    return total


def create_prediction_results(sources, regions):
    """创建预测结果（约100条）"""
    print("正在生成预测数据...")
    admin_user = User.objects.filter(is_staff=True).first()

    results = []
    model_types = ['lstm', 'cnn', 'cnn_lstm']

    for region_code in random.sample(list(regions.keys()), 10):
        region = regions[region_code]
        for year in [2026, 2027, 2028]:
            for mt in model_types:
                base_pred = random.uniform(500, 5000)
                results.append(PredictionResult(
                    target_year=year,
                    target_quarter=0,
                    region=region,
                    source=random.choice(list(sources.values())),
                    predicted_amount=round(base_pred, 2),
                    model_type=mt,
                    confidence=round(random.uniform(0.85, 0.98), 2),
                    mae=round(random.uniform(30, 200), 2),
                    rmse=round(random.uniform(50, 300), 2),
                    r2_score=round(random.uniform(0.82, 0.98), 4),
                    created_by=admin_user,
                ))

    PredictionResult.objects.bulk_create(results)
    print(f"  生成了 {len(results)} 条预测结果")
    return len(results)


def create_threshold_configs(sources, regions):
    """创建阈值配置（约40条）"""
    print("正在生成阈值配置...")
    admin_user = User.objects.filter(is_staff=True).first()

    configs = []
    # 按排放源配置
    for source in sources.values():
        for level, limit_factor in [('yellow', 1.5), ('orange', 2.0), ('red', 3.0)]:
            base_limit = random.uniform(800, 3000) * limit_factor
            configs.append(ThresholdConfig(
                name=f'{source.name}-{level}预警',
                source=source,
                method='standard',
                upper_limit=round(base_limit, 2),
                warning_level=level,
                updated_by=admin_user,
            ))

    # 按重点省份配置（正态分布法）
    key_provinces = ['GD', 'JS', 'SD', 'ZJ', 'HE', 'SX', 'HA', 'HB']
    for code in key_provinces:
        if code in regions:
            region = regions[code]
            mean_val = random.uniform(1000, 4000)
            std_val = mean_val * 0.15
            configs.append(ThresholdConfig(
                name=f'{region.name}-综合预警',
                region=region,
                method='normal',
                mean_value=round(mean_val, 2),
                std_value=round(std_val, 2),
                upper_limit=round(mean_val + 2 * std_val, 2),
                warning_level='orange',
                updated_by=admin_user,
            ))

    ThresholdConfig.objects.bulk_create(configs)
    print(f"  生成了 {len(configs)} 条阈值配置")
    return len(configs)


def create_alert_records():
    """创建预警记录（约50条）"""
    print("正在生成预警记录...")

    thresholds = list(ThresholdConfig.objects.all())
    records = list(EmissionRecord.objects.order_by('-emission_amount')[:100])

    alerts = []
    for i in range(min(50, len(records))):
        record = records[i]
        threshold = random.choice(thresholds)

        level_map = {'yellow': '黄色', 'orange': '橙色', 'red': '红色'}
        level = random.choice(['yellow', 'orange', 'red'])

        alerts.append(AlertRecord(
            emission_record=record,
            threshold=threshold,
            alert_level=level,
            alert_message=f'{record.region.name}{record.year}年Q{record.quarter}{record.industry.name}'
                         f'排放量({record.emission_amount}万吨)超过{level_map[level]}预警阈值({threshold.upper_limit}万吨)',
            emission_value=record.emission_amount,
            threshold_value=threshold.upper_limit,
            is_read=random.choice([True, False]),
            is_resolved=random.choice([True, False, False]),
        ))

    AlertRecord.objects.bulk_create(alerts)
    print(f"  生成了 {len(alerts)} 条预警记录")
    return len(alerts)


def create_operation_logs():
    """创建操作日志"""
    print("正在生成操作日志...")
    users = list(User.objects.all())

    logs = []
    actions = ['login', 'create', 'update', 'delete', 'export', 'predict']
    targets = ['排放数据', '用户管理', '阈值配置', '智能预测', '系统']

    for _ in range(30):
        user = random.choice(users)
        action = random.choice(actions)
        target = random.choice(targets)
        logs.append(OperationLog(
            user=user,
            action=action,
            target=target,
            detail=f'{user.username} 执行了 {action} 操作于 {target}',
            ip_address=f'192.168.1.{random.randint(1, 254)}',
        ))

    OperationLog.objects.bulk_create(logs)
    print(f"  生成了 {len(logs)} 条操作日志")
    return len(logs)


def main():
    """主函数"""
    print("=" * 60)
    print("碳排放分析及预测平台 - Mock数据生成")
    print("=" * 60)

    # 清空已有数据
    print("\n清空已有数据...")
    AlertRecord.objects.all().delete()
    ThresholdConfig.objects.all().delete()
    PredictionResult.objects.all().delete()
    EmissionRecord.objects.all().delete()
    Industry.objects.all().delete()
    EmissionSource.objects.all().delete()
    Region.objects.all().delete()
    OperationLog.objects.all().delete()
    UserProfile.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # 生成数据
    print("\n开始生成数据...")
    create_users()
    sources = create_emission_sources()
    regions = create_regions()
    industries = create_industries(sources)
    create_emission_records(sources, regions, industries)
    create_prediction_results(sources, regions)
    create_threshold_configs(sources, regions)
    create_alert_records()
    create_operation_logs()

    # 统计
    print("\n" + "=" * 60)
    print("数据生成完成！统计信息：")
    print(f"  用户: {User.objects.count()} 个")
    print(f"  排放源: {EmissionSource.objects.count()} 个")
    print(f"  地区: {Region.objects.count()} 个")
    print(f"  行业: {Industry.objects.count()} 个")
    print(f"  排放记录: {EmissionRecord.objects.count()} 条")
    print(f"  预测结果: {PredictionResult.objects.count()} 条")
    print(f"  阈值配置: {ThresholdConfig.objects.count()} 条")
    print(f"  预警记录: {AlertRecord.objects.count()} 条")
    print(f"  操作日志: {OperationLog.objects.count()} 条")
    total = (User.objects.count() + EmissionSource.objects.count() +
             Region.objects.count() + Industry.objects.count() +
             EmissionRecord.objects.count() + PredictionResult.objects.count() +
             ThresholdConfig.objects.count() + AlertRecord.objects.count() +
             OperationLog.objects.count())
    print(f"\n  总计: {total} 条记录")
    print("=" * 60)
    print("\n登录信息:")
    print("  管理员: admin / admin123")
    print("  普通用户: zhangsan / user123")


if __name__ == '__main__':
    main()
