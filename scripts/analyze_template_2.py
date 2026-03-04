"""Round 2: Analyze template paragraph styles and formatting"""
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

doc = Document(r'E:\2026next\碳排放\论文1.docx')

print('=== PARAGRAPH ANALYSIS ===')
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if not text:
        continue
    
    style_name = para.style.name if para.style else 'None'
    alignment = para.alignment
    pf = para.paragraph_format
    line_spacing = pf.line_spacing
    line_rule = pf.line_spacing_rule
    space_before = pf.space_before
    space_after = pf.space_after
    first_indent = pf.first_line_indent
    
    # Extract run-level formatting from XML
    run_info = []
    for run in para.runs:
        rPr = run._element.find(qn('w:rPr'))
        cn_font = en_font = sz = bold = None
        if rPr is not None:
            rFonts = rPr.find(qn('w:rFonts'))
            if rFonts is not None:
                cn_font = rFonts.get(qn('w:eastAsia'))
                en_font = rFonts.get(qn('w:ascii'))
            szEl = rPr.find(qn('w:sz'))
            if szEl is not None:
                sz = szEl.get(qn('w:val'))
            bEl = rPr.find(qn('w:b'))
            if bEl is not None:
                bval = bEl.get(qn('w:val'))
                bold = bval != '0' if bval else True
        run_info.append({
            'text': run.text[:20],
            'cn': cn_font, 'en': en_font,
            'sz': sz, 'bold': bold
        })
    
    # Truncate display
    display_text = text[:50] + ('...' if len(text)>50 else '')
    
    print(f'\nPara {i}: [{style_name}] "{display_text}"')
    print(f'  align={alignment} line_spacing={line_spacing} rule={line_rule}')
    print(f'  space_before={space_before} space_after={space_after} first_indent={first_indent}')
    for j, ri in enumerate(run_info[:3]):
        print(f'  run{j}: cn={ri["cn"]} en={ri["en"]} sz={ri["sz"]} bold={ri["bold"]} text="{ri["text"]}"')
    
    # Also check pPr XML for details
    pPr = para._element.find(qn('w:pPr'))
    if pPr is not None:
        spacing = pPr.find(qn('w:spacing'))
        if spacing is not None:
            line_val = spacing.get(qn('w:line'))
            line_rule_val = spacing.get(qn('w:lineRule'))
            before_val = spacing.get(qn('w:before'))
            after_val = spacing.get(qn('w:after'))
            print(f'  XML spacing: line={line_val} rule={line_rule_val} before={before_val} after={after_val}')
        ind = pPr.find(qn('w:ind'))
        if ind is not None:
            fl = ind.get(qn('w:firstLine'))
            flc = ind.get(qn('w:firstLineChars'))
            hanging = ind.get(qn('w:hanging'))
            left = ind.get(qn('w:left'))
            print(f'  XML indent: firstLine={fl} firstLineChars={flc} hanging={hanging} left={left}')
