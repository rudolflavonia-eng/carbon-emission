"""Step 0: Backup original and create working copy"""
import shutil

src = r'E:\2026next\碳排放\基于Django的碳排放分析及预测可视化平台的设计与实现.docx'
dst = r'E:\2026next\碳排放\基于Django的碳排放分析及预测可视化平台的设计与实现_排版后.docx'
shutil.copy2(src, dst)
print(f'Copied to: {dst}')
