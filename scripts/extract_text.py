"""Extract full text from docx for review"""
from docx import Document
from docx.oxml.ns import qn
import re

doc = Document(r'E:\2026next\碳排放\基于Django的碳排放分析及预测可视化平台的设计与实现_排版后.docx')

with open(r'E:\2026next\碳排放\scripts\thesis_text.txt', 'w', encoding='utf-8') as f:
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        style = para.style.name
        if not text:
            continue
        # Skip code
        pPr = para._element.find(qn('w:pPr'))
        has_shd = False
        if pPr is not None:
            has_shd = pPr.find(qn('w:shd')) is not None
        if has_shd:
            if i < 200 or i > 560:  # only skip inner code, show first/last
                continue
            else:
                continue
        if style.startswith('toc'):
            continue
        f.write(f'[{i}][{style}] {text}\n\n')

print('Extracted to thesis_text.txt')
