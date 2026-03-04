"""Round 2b: Analyze template style definitions"""
from docx import Document
from docx.oxml.ns import qn

doc = Document(r'E:\2026next\碳排放\论文1.docx')

print('=== STYLE DEFINITIONS ===')
for style in doc.styles:
    if style.type is not None and style.type.name == 'PARAGRAPH':
        pPr = style.element.find(qn('w:pPr'))
        rPr_style = style.element.find(qn('w:rPr'))
        
        info = f'Style: "{style.name}" (id={style.style_id})'
        if style.base_style:
            info += f' base="{style.base_style.name}"'
        
        if pPr is not None:
            jc = pPr.find(qn('w:jc'))
            spacing = pPr.find(qn('w:spacing'))
            ind = pPr.find(qn('w:ind'))
            outlineLvl = pPr.find(qn('w:outlineLvl'))
            if jc is not None: info += f' align={jc.get(qn("w:val"))}'
            if spacing is not None:
                info += f' spacing(line={spacing.get(qn("w:line"))},rule={spacing.get(qn("w:lineRule"))},before={spacing.get(qn("w:before"))},after={spacing.get(qn("w:after"))})'
            if ind is not None:
                info += f' ind(fl={ind.get(qn("w:firstLine"))},flc={ind.get(qn("w:firstLineChars"))},hang={ind.get(qn("w:hanging"))},left={ind.get(qn("w:left"))})'
            if outlineLvl is not None:
                info += f' outlineLvl={outlineLvl.get(qn("w:val"))}'
        
        if rPr_style is not None:
            rFonts = rPr_style.find(qn('w:rFonts'))
            sz = rPr_style.find(qn('w:sz'))
            b = rPr_style.find(qn('w:b'))
            if rFonts is not None:
                cn = rFonts.get(qn('w:eastAsia'))
                en = rFonts.get(qn('w:ascii'))
                info += f' font(cn={cn},en={en})'
            if sz is not None:
                info += f' sz={sz.get(qn("w:val"))}'
            if b is not None:
                bval = b.get(qn('w:val'))
                info += f' bold={bval if bval else "true"}'
        
        print(info)

# Also get first 30 paragraphs to see structure
print('\n=== FIRST 30 PARAGRAPHS ===')
for i, para in enumerate(doc.paragraphs[:30]):
    text = para.text.strip()[:60]
    style_name = para.style.name if para.style else 'None'
    alignment = para.alignment
    
    run_info = []
    for run in para.runs[:2]:
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
        run_info.append(f'cn={cn_font} en={en_font} sz={sz} b={bold}')
    
    pPr = para._element.find(qn('w:pPr'))
    xml_info = ''
    if pPr is not None:
        spacing = pPr.find(qn('w:spacing'))
        ind = pPr.find(qn('w:ind'))
        if spacing is not None:
            xml_info += f' spacing(line={spacing.get(qn("w:line"))},rule={spacing.get(qn("w:lineRule"))},before={spacing.get(qn("w:before"))},after={spacing.get(qn("w:after"))})'
        if ind is not None:
            xml_info += f' ind(fl={ind.get(qn("w:firstLine"))})'
    
    print(f'{i}: [{style_name}] align={alignment} "{text}"')
    for ri in run_info:
        print(f'   {ri}')
    if xml_info:
        print(f'   {xml_info}')
