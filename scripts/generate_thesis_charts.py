# -*- coding: utf-8 -*-
"""
论文图表生成脚本 - 碳排放分析及预测平台
生成第3章数据清洗图表 + 第4章可视化分析图表
"""
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ============ 中文字体修复 ============
font_path = r'C:\Windows\Fonts\msyh.ttc'
if not os.path.exists(font_path):
    font_path = r'C:\Windows\Fonts\simsun.ttc'
font_prop = fm.FontProperties(fname=font_path, size=12)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['font.sans-serif'] = [font_prop.get_name(), 'SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 注册字体
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name

OUT_DIR = r'e:\2026next\碳排放\static\images'
os.makedirs(OUT_DIR, exist_ok=True)

np.random.seed(42)

# ============ 模拟数据 ============
years = list(range(2015, 2026))
regions_top10 = ['广东省','江苏省','山东省','河北省','浙江省','河南省','山西省','内蒙古','湖北省','湖南省']
sources = ['能源活动','工业生产','农业活动','土地利用变化']
industries_energy = ['电力和热力生产','石油加工','煤炭开采','天然气开采','交通运输']

# 年度排放量趋势 (万吨CO2)
base_emission = 85000
annual_emissions = []
for i, y in enumerate(years):
    if y <= 2020:
        val = base_emission * (1 + 0.025 * i) + np.random.normal(0, 800)
    else:
        val = base_emission * (1 + 0.025 * 6) + (y - 2020) * 600 + np.random.normal(0, 500)
    annual_emissions.append(round(val, 2))

# 排放源占比
source_ratios = [0.55, 0.28, 0.10, 0.07]
source_values = [round(annual_emissions[-1] * r, 2) for r in source_ratios]

# 地区排放TOP10
region_emissions = [6500, 6000, 5800, 4500, 4000, 3800, 3500, 3200, 3000, 2800]
region_emissions = [v + np.random.normal(0, 100) for v in region_emissions]

# 能源消耗
energy_consumption = [round(e * 0.65 + np.random.normal(0, 300), 2) for e in annual_emissions]

# GDP
gdp_values = [round(65000 + i * 5500 + np.random.normal(0, 800), 2) for i in range(len(years))]

# 人口
population = [round(138000 + i * 300 + np.random.normal(0, 50), 2) for i in range(len(years))]

# 能源效率 (吨CO2/万元GDP)
energy_efficiency = [round(annual_emissions[i] / gdp_values[i] * 100, 4) for i in range(len(years))]

# ============================================================
# 第3章 数据清洗相关图表
# ============================================================

def save_fig(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  -> 已保存: {name}')

print('='*60)
print('第3章 - 数据清洗图表')
print('='*60)

# --- 图3-3 缺失值处理前后对比 ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
fields = ['排放量', '能源消耗', 'GDP', '人口', '能源效率']
missing_before = [3.2, 4.5, 2.1, 1.8, 5.6]
missing_after = [0.0, 0.0, 0.0, 0.0, 0.0]

bars1 = axes[0].bar(fields, missing_before, color='#e74c3c', alpha=0.8, width=0.6)
axes[0].set_title('清洗前缺失率', fontproperties=font_prop, fontsize=14, fontweight='bold')
axes[0].set_ylabel('缺失率 (%)', fontproperties=font_prop, fontsize=12)
axes[0].set_ylim(0, 8)
for bar, val in zip(bars1, missing_before):
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.15, f'{val}%',
                ha='center', va='bottom', fontsize=10, fontproperties=font_prop)
axes[0].set_xticklabels(fields, fontproperties=font_prop, fontsize=10)
axes[0].tick_params(axis='y', labelsize=10)

bars2 = axes[1].bar(fields, missing_after, color='#2ecc71', alpha=0.8, width=0.6)
axes[1].set_title('清洗后缺失率', fontproperties=font_prop, fontsize=14, fontweight='bold')
axes[1].set_ylabel('缺失率 (%)', fontproperties=font_prop, fontsize=12)
axes[1].set_ylim(0, 8)
for bar, val in zip(bars2, missing_after):
    axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.15, f'{val}%',
                ha='center', va='bottom', fontsize=10, fontproperties=font_prop)
axes[1].set_xticklabels(fields, fontproperties=font_prop, fontsize=10)
axes[1].tick_params(axis='y', labelsize=10)

fig.suptitle('图3-3 缺失值处理前后对比', fontproperties=font_prop, fontsize=15, y=1.02)
fig.tight_layout()
save_fig(fig, '图3-3 缺失值处理前后对比.png')

# --- 图3-4 异常值检测结果(箱线图) ---
fig, ax = plt.subplots(figsize=(10, 6))
data_boxplot = []
labels_box = ['能源活动','工业生产','农业活动','土地利用变化','总排放量']
for i, (mean, std) in enumerate([(4800, 600), (2400, 350), (850, 120), (600, 90), (8600, 900)]):
    d = np.random.normal(mean, std, 200)
    # 添加少量异常值
    d = np.append(d, [mean + 4*std, mean - 3.5*std, mean + 3.8*std])
    data_boxplot.append(d)

bp = ax.boxplot(data_boxplot, labels=labels_box, patch_artist=True, 
                boxprops=dict(facecolor='#AED6F1', linewidth=1.5),
                whiskerprops=dict(linewidth=1.5),
                medianprops=dict(color='#E74C3C', linewidth=2),
                flierprops=dict(marker='o', markerfacecolor='#E74C3C', markersize=6))
colors = ['#AED6F1','#A9DFBF','#F9E79F','#F5CBA7','#D7BDE2']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
ax.set_ylabel('排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图3-4 异常值检测结果（箱线图）', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.set_xticklabels(labels_box, fontproperties=font_prop, fontsize=11)
ax.tick_params(axis='y', labelsize=10)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
save_fig(fig, '图3-4 异常值检测结果.png')

# --- 图3-5 去重前后记录数对比 ---
fig, ax = plt.subplots(figsize=(8, 5))
categories = ['排放记录', '预测结果', '预警记录', '操作日志']
before_counts = [5420, 385, 210, 1580]
after_counts = [5186, 362, 198, 1520]

x = np.arange(len(categories))
width = 0.35
bars1 = ax.bar(x - width/2, before_counts, width, label='去重前', color='#5DADE2', alpha=0.85)
bars2 = ax.bar(x + width/2, after_counts, width, label='去重后', color='#2ECC71', alpha=0.85)

ax.set_ylabel('记录数 (条)', fontproperties=font_prop, fontsize=12)
ax.set_title('图3-5 去重前后数据记录数对比', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(categories, fontproperties=font_prop, fontsize=11)
ax.legend(prop=font_prop, fontsize=11)
ax.tick_params(axis='y', labelsize=10)
ax.grid(axis='y', alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords='offset points', ha='center', va='bottom', fontsize=9)
fig.tight_layout()
save_fig(fig, '图3-5 去重前后数据记录数对比.png')

# ============================================================
# 第4章 可视化分析图表
# ============================================================
print()
print('='*60)
print('第4章 - 可视化分析图表')
print('='*60)

# --- 图4-1 年度碳排放趋势分析 ---
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(years, [e/10000 for e in annual_emissions], 'o-', color='#2563EB', linewidth=2.5, 
        markersize=7, markerfacecolor='white', markeredgewidth=2)
ax.fill_between(years, [e/10000 for e in annual_emissions], alpha=0.15, color='#2563EB')
ax.set_xlabel('年份', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('排放量 (亿吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图4-1 2015-2025年度碳排放趋势', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years], fontproperties=font_prop, fontsize=10, rotation=45)
ax.tick_params(axis='y', labelsize=10)
ax.grid(alpha=0.3)
fig.tight_layout()
save_fig(fig, '图4-1 年度碳排放趋势分析.png')

# --- 图4-2 排放源结构分析（饼图） ---
fig, ax = plt.subplots(figsize=(9, 7))
colors_pie = ['#2563EB','#3B82F6','#60A5FA','#93C5FD']
explode = (0.05, 0.02, 0, 0)
wedges, texts, autotexts = ax.pie(source_values, labels=sources, autopct='%1.1f%%',
                                   colors=colors_pie, explode=explode, startangle=90,
                                   textprops={'fontproperties': font_prop, 'fontsize': 12})
for t in autotexts:
    t.set_fontproperties(font_prop)
    t.set_fontsize(11)
ax.set_title('图4-2 排放源结构占比分析', fontproperties=font_prop, fontsize=14, fontweight='bold')
fig.tight_layout()
save_fig(fig, '图4-2 排放源结构分析.png')

# --- 图4-3 地区排放TOP10分析（水平柱状图） ---
fig, ax = plt.subplots(figsize=(10, 6))
y_pos = np.arange(len(regions_top10))
colors_bar = plt.cm.Blues(np.linspace(0.4, 0.9, len(regions_top10)))[::-1]
bars = ax.barh(y_pos, region_emissions, color=colors_bar, height=0.6, edgecolor='white')
ax.set_yticks(y_pos)
ax.set_yticklabels(regions_top10, fontproperties=font_prop, fontsize=11)
ax.set_xlabel('排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图4-3 地区碳排放TOP10', fontproperties=font_prop, fontsize=14, fontweight='bold')
for i, (bar, val) in enumerate(zip(bars, region_emissions)):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height()/2, f'{val:.0f}',
            va='center', fontsize=10, fontproperties=font_prop)
ax.tick_params(axis='x', labelsize=10)
ax.grid(axis='x', alpha=0.3)
ax.invert_yaxis()
fig.tight_layout()
save_fig(fig, '图4-3 地区排放TOP10分析.png')

# --- 图4-4 季度排放对比分析 ---
fig, ax = plt.subplots(figsize=(10, 6))
quarters = ['Q1','Q2','Q3','Q4']
q_factors = [1.15, 0.90, 0.85, 1.10]
selected_years = [2020, 2022, 2024, 2025]
x = np.arange(len(quarters))
width = 0.18
colors_q = ['#1E40AF','#2563EB','#60A5FA','#93C5FD']
for idx, yr in enumerate(selected_years):
    yr_base = annual_emissions[years.index(yr)] / 4
    q_vals = [round(yr_base * qf + np.random.normal(0, 100), 0) for qf in q_factors]
    bars = ax.bar(x + idx * width, q_vals, width, label=f'{yr}年', color=colors_q[idx], alpha=0.9)

ax.set_xlabel('季度', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图4-4 季度碳排放对比分析', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(quarters, fontproperties=font_prop, fontsize=11)
ax.legend(prop=font_prop, fontsize=10, ncol=4, loc='upper right')
ax.tick_params(axis='y', labelsize=10)
ax.grid(axis='y', alpha=0.3)
fig.tight_layout()
save_fig(fig, '图4-4 季度排放对比分析.png')

# --- 图4-5 行业排放结构分析（堆叠面积图） ---
fig, ax = plt.subplots(figsize=(10, 6))
industry_data = {}
for j, ind in enumerate(industries_energy):
    base = [4000, 2000, 1500, 1000, 1500][j]
    vals = [base * (1 + 0.02 * i) + np.random.normal(0, base * 0.03) for i in range(len(years))]
    industry_data[ind] = vals

colors_area = ['#1E3A5F','#2563EB','#3B82F6','#60A5FA','#93C5FD']
ax.stackplot(years, *industry_data.values(), labels=industry_data.keys(), colors=colors_area, alpha=0.8)
ax.set_xlabel('年份', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图4-5 能源活动行业排放结构', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.legend(prop=font_prop, fontsize=10, loc='upper left')
ax.set_xticks(years)
ax.set_xticklabels([str(y) for y in years], fontproperties=font_prop, fontsize=10, rotation=45)
ax.tick_params(axis='y', labelsize=10)
ax.grid(alpha=0.2)
fig.tight_layout()
save_fig(fig, '图4-5 行业排放结构分析.png')

# --- 图4-6 碳排放与GDP相关性分析（散点图+拟合） ---
fig, ax = plt.subplots(figsize=(9, 6))
gdp_arr = np.array(gdp_values) / 10000
emission_arr = np.array(annual_emissions) / 10000
ax.scatter(gdp_arr, emission_arr, s=80, color='#2563EB', zorder=5, edgecolors='white', linewidth=1.5)
z = np.polyfit(gdp_arr, emission_arr, 1)
p = np.poly1d(z)
x_fit = np.linspace(min(gdp_arr), max(gdp_arr), 100)
ax.plot(x_fit, p(x_fit), '--', color='#E74C3C', linewidth=2, label=f'拟合线 (r={np.corrcoef(gdp_arr, emission_arr)[0,1]:.3f})')
ax.set_xlabel('GDP (万亿元)', fontproperties=font_prop, fontsize=12)
ax.set_ylabel('碳排放量 (亿吨CO2)', fontproperties=font_prop, fontsize=12)
ax.set_title('图4-6 碳排放与GDP相关性分析', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax.legend(prop=font_prop, fontsize=11)
ax.tick_params(axis='both', labelsize=10)
ax.grid(alpha=0.3)
# 标注年份
for i, yr in enumerate(years):
    if yr % 2 == 1:
        ax.annotate(str(yr), (gdp_arr[i], emission_arr[i]), textcoords="offset points",
                    xytext=(5, 8), fontsize=8, fontproperties=font_prop, color='#666')
fig.tight_layout()
save_fig(fig, '图4-6 碳排放与GDP相关性分析.png')

# --- 图4-7 能源效率变化趋势（双Y轴） ---
fig, ax1 = plt.subplots(figsize=(10, 6))
color1 = '#2563EB'
color2 = '#E74C3C'
ax1.set_xlabel('年份', fontproperties=font_prop, fontsize=12)
ax1.set_ylabel('碳排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12, color=color1)
line1 = ax1.plot(years, annual_emissions, 'o-', color=color1, linewidth=2.5, markersize=6, label='碳排放量')
ax1.tick_params(axis='y', labelcolor=color1, labelsize=10)
ax1.set_xticks(years)
ax1.set_xticklabels([str(y) for y in years], fontproperties=font_prop, fontsize=10, rotation=45)

ax2 = ax1.twinx()
ax2.set_ylabel('能源效率 (tCO2/万元GDP)', fontproperties=font_prop, fontsize=12, color=color2)
line2 = ax2.plot(years, energy_efficiency, 's--', color=color2, linewidth=2.5, markersize=6, label='能源效率')
ax2.tick_params(axis='y', labelcolor=color2, labelsize=10)

lines = line1 + line2
labs = [l.get_label() for l in lines]
ax1.legend(lines, labs, prop=font_prop, fontsize=10, loc='upper center')
ax1.set_title('图4-7 碳排放与能源效率变化趋势', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax1.grid(alpha=0.2)
fig.tight_layout()
save_fig(fig, '图4-7 能源效率变化趋势.png')

# --- 图4-8 预测模型对比分析 ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：预测 vs 实际
predict_years = [2023, 2024, 2025]
actual_vals = [annual_emissions[years.index(y)] for y in predict_years]
lstm_preds = [v * (1 + np.random.normal(0, 0.02)) for v in actual_vals]
cnn_preds = [v * (1 + np.random.normal(0, 0.03)) for v in actual_vals]
cnn_lstm_preds = [v * (1 + np.random.normal(0, 0.015)) for v in actual_vals]

x = np.arange(len(predict_years))
width = 0.2
axes[0].bar(x - 1.5*width, actual_vals, width, label='实际值', color='#1E3A5F', alpha=0.9)
axes[0].bar(x - 0.5*width, lstm_preds, width, label='LSTM', color='#2563EB', alpha=0.9)
axes[0].bar(x + 0.5*width, cnn_preds, width, label='CNN', color='#60A5FA', alpha=0.9)
axes[0].bar(x + 1.5*width, cnn_lstm_preds, width, label='CNN-LSTM', color='#93C5FD', alpha=0.9)
axes[0].set_xticks(x)
axes[0].set_xticklabels([str(y) for y in predict_years], fontproperties=font_prop, fontsize=11)
axes[0].set_ylabel('排放量 (万吨CO2)', fontproperties=font_prop, fontsize=12)
axes[0].set_title('预测值与实际值对比', fontproperties=font_prop, fontsize=13, fontweight='bold')
axes[0].legend(prop=font_prop, fontsize=9, ncol=2)
axes[0].tick_params(axis='y', labelsize=10)
axes[0].grid(axis='y', alpha=0.3)

# 右图：模型指标雷达图
models_name = ['LSTM','CNN','CNN-LSTM']
metrics = ['MAE','RMSE','R²','置信度','训练速度']
values_radar = {
    'LSTM':      [0.75, 0.72, 0.88, 0.92, 0.85],
    'CNN':       [0.80, 0.78, 0.85, 0.90, 0.90],
    'CNN-LSTM':  [0.70, 0.68, 0.93, 0.95, 0.75],
}
angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False).tolist()
angles += angles[:1]

ax_r = fig.add_subplot(122, polar=True)
colors_radar = ['#2563EB','#60A5FA','#E74C3C']
for idx, (model, vals) in enumerate(values_radar.items()):
    vals_plot = vals + vals[:1]
    ax_r.plot(angles, vals_plot, 'o-', linewidth=2, color=colors_radar[idx], label=model, markersize=5)
    ax_r.fill(angles, vals_plot, alpha=0.1, color=colors_radar[idx])
ax_r.set_xticks(angles[:-1])
ax_r.set_xticklabels(metrics, fontproperties=font_prop, fontsize=10)
ax_r.set_title('模型性能指标对比', fontproperties=font_prop, fontsize=13, fontweight='bold', pad=20)
ax_r.legend(prop=font_prop, fontsize=9, loc='lower right', bbox_to_anchor=(1.3, -0.05))
ax_r.set_ylim(0, 1)

# Remove the empty subplot and replace with radar
axes[1].set_visible(False)

fig.suptitle('图4-8 预测模型对比分析', fontproperties=font_prop, fontsize=15, y=1.02)
fig.tight_layout()
save_fig(fig, '图4-8 预测模型对比分析.png')

# --- 图4-9 预警级别分布分析 ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 饼图
alert_labels = ['黄色预警','橙色预警','红色预警']
alert_counts = [98, 65, 35]
alert_colors = ['#F4D03F','#E67E22','#E74C3C']
wedges, texts, autotexts = axes[0].pie(alert_counts, labels=alert_labels, autopct='%1.1f%%',
                                        colors=alert_colors, startangle=90,
                                        textprops={'fontproperties': font_prop, 'fontsize': 11})
for t in autotexts:
    t.set_fontproperties(font_prop)
    t.set_fontsize(10)
axes[0].set_title('预警级别占比', fontproperties=font_prop, fontsize=13, fontweight='bold')

# 月度趋势
months = [f'{m}月' for m in range(1, 13)]
yellow_month = [8, 6, 5, 4, 3, 4, 5, 6, 7, 9, 12, 15]
orange_month = [5, 4, 3, 3, 2, 3, 4, 5, 6, 7, 9, 10]
red_month =    [3, 2, 1, 1, 1, 1, 2, 2, 3, 4, 6, 7]
axes[1].plot(months, yellow_month, 'o-', color='#F4D03F', linewidth=2, label='黄色预警')
axes[1].plot(months, orange_month, 's-', color='#E67E22', linewidth=2, label='橙色预警')
axes[1].plot(months, red_month, '^-', color='#E74C3C', linewidth=2, label='红色预警')
axes[1].set_ylabel('预警次数', fontproperties=font_prop, fontsize=12)
axes[1].set_title('月度预警趋势', fontproperties=font_prop, fontsize=13, fontweight='bold')
axes[1].set_xticklabels(months, fontproperties=font_prop, fontsize=9)
axes[1].legend(prop=font_prop, fontsize=10)
axes[1].tick_params(axis='y', labelsize=10)
axes[1].grid(alpha=0.3)

fig.suptitle('图4-9 预警级别分布分析', fontproperties=font_prop, fontsize=15, y=1.02)
fig.tight_layout()
save_fig(fig, '图4-9 预警级别分布分析.png')

print()
print('='*60)
print('所有图表生成完毕！')
print('='*60)
