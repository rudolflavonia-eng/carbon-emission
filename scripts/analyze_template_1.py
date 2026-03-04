"""Round 1: Analyze template page settings"""
from docx import Document
from docx.oxml.ns import qn

doc = Document(r'E:\2026next\碳排放\论文1.docx')

print('=== PAGE SETTINGS ===')
for i, sec in enumerate(doc.sections):
    print(f'Section {i}:')
    w = sec.page_width
    h = sec.page_height
    print(f'  Page size: {w/914400:.1f}x{h/914400:.1f} inches')
    if sec.top_margin: print(f'  top={sec.top_margin.cm:.2f}cm')
    if sec.bottom_margin: print(f'  bottom={sec.bottom_margin.cm:.2f}cm')
    if sec.left_margin: print(f'  left={sec.left_margin.cm:.2f}cm')
    if sec.right_margin: print(f'  right={sec.right_margin.cm:.2f}cm')
    if sec.header_distance: print(f'  header_dist={sec.header_distance.cm:.2f}cm')
    if sec.footer_distance: print(f'  footer_dist={sec.footer_distance.cm:.2f}cm')
    print(f'  Different first page: {sec.different_first_page_header_footer}')
    
    sectPr = sec._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is not None:
        fmt = pgNumType.get(qn('w:fmt'))
        start = pgNumType.get(qn('w:start'))
        print(f'  Page number: fmt={fmt}, start={start}')
    
    st = sectPr.find(qn('w:type'))
    if st is not None:
        val = st.get(qn('w:val'))
        print(f'  Section type: {val}')

# Check even/odd headers setting
from lxml import etree
settings_part = doc.settings.element
evenOdd = settings_part.find(qn('w:evenAndOddHeaders'))
print(f'\nEven/Odd headers enabled: {evenOdd is not None}')
