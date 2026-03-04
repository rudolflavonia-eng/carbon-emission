"""Fix: Add page break before 目录, and check Abstract page break logic"""
from docx import Document
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document(r'E:\2026next\碳排放\基于Django的碳排放分析及预测可视化平台的设计与实现_排版后.docx')

for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if text == '目录':
        pPr = para._element.find(qn('w:pPr'))
        if pPr is not None:
            pb = pPr.find(qn('w:pageBreakBefore'))
            if pb is None:
                pPr.append(parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>'))
                print(f'Added page break before "目录" at para {i}')

doc.save(r'E:\2026next\碳排放\基于Django的碳排放分析及预测可视化平台的设计与实现_排版后.docx')
print('Done.')
