"""thesis_utils.py - Utility functions for thesis formatting"""
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
from docx.shared import Pt, Cm, Emu, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
import copy

def ensure_rpr(run):
    """Ensure run has rPr and rFonts elements"""
    rPr = run._element.find(qn('w:rPr'))
    if rPr is None:
        rPr = parse_xml(f'<w:rPr {nsdecls("w")}><w:rFonts {nsdecls("w")}/></w:rPr>')
        run._element.insert(0, rPr)
    else:
        if rPr.find(qn('w:rFonts')) is None:
            rPr.insert(0, parse_xml(f'<w:rFonts {nsdecls("w")}/>'))
    return rPr

def set_run_font(run, cn=None, en=None, sz=None, b=None):
    """Set run font: cn=中文字体, en=西文字体, sz=磅值, b=加粗"""
    ensure_rpr(run)
    rPr = run._element.rPr
    rFonts = rPr.find(qn('w:rFonts'))
    
    if cn:
        rFonts.set(qn('w:eastAsia'), cn)
    if en:
        rFonts.set(qn('w:ascii'), en)
        rFonts.set(qn('w:hAnsi'), en)
        run.font.name = en
    if sz is not None:
        run.font.size = Pt(sz)
    if b is not None:
        run.font.bold = b

def fmt_all_runs(para, cn=None, en=None, sz=None, b=None):
    """Format all runs in a paragraph"""
    for run in para.runs:
        set_run_font(run, cn=cn, en=en, sz=sz, b=b)

def ensure_ppr(para):
    """Ensure paragraph has pPr element"""
    pPr = para._element.find(qn('w:pPr'))
    if pPr is None:
        pPr = parse_xml(f'<w:pPr {nsdecls("w")}/>')
        para._element.insert(0, pPr)
    return pPr

def set_paragraph_fmt(para, align=None, line_spacing=None, line_rule='exact',
                       space_before=None, space_after=None,
                       first_indent_chars=None, first_indent_pt=None,
                       before_lines=None, after_lines=None):
    """Set paragraph formatting"""
    pf = para.paragraph_format
    
    if align is not None:
        pf.alignment = align
    
    # Line spacing
    if line_spacing is not None:
        pPr = ensure_ppr(para)
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = parse_xml(f'<w:spacing {nsdecls("w")}/>')
            pPr.append(spacing)
        if line_rule == 'exact':
            spacing.set(qn('w:line'), str(int(line_spacing * 20)))  # twips
            spacing.set(qn('w:lineRule'), 'exact')
        elif line_rule == 'auto':
            spacing.set(qn('w:line'), str(int(line_spacing * 240)))  # 240 = single
            spacing.set(qn('w:lineRule'), 'auto')
    
    # Space before/after (in lines using beforeLines/afterLines)
    if before_lines is not None or after_lines is not None:
        pPr = ensure_ppr(para)
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = parse_xml(f'<w:spacing {nsdecls("w")}/>')
            pPr.append(spacing)
        if before_lines is not None:
            spacing.set(qn('w:beforeLines'), str(int(before_lines * 100)))
            spacing.set(qn('w:before'), str(int(before_lines * 312)))  # approx
        if after_lines is not None:
            spacing.set(qn('w:afterLines'), str(int(after_lines * 100)))
            spacing.set(qn('w:after'), str(int(after_lines * 312)))
    
    if space_before is not None:
        pPr = ensure_ppr(para)
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = parse_xml(f'<w:spacing {nsdecls("w")}/>')
            pPr.append(spacing)
        spacing.set(qn('w:before'), str(space_before))
        # Remove beforeLines if set
        if spacing.get(qn('w:beforeLines')):
            del spacing.attrib[qn('w:beforeLines')]
    
    if space_after is not None:
        pPr = ensure_ppr(para)
        spacing = pPr.find(qn('w:spacing'))
        if spacing is None:
            spacing = parse_xml(f'<w:spacing {nsdecls("w")}/>')
            pPr.append(spacing)
        spacing.set(qn('w:after'), str(space_after))
        if spacing.get(qn('w:afterLines')):
            del spacing.attrib[qn('w:afterLines')]
    
    # First line indent
    if first_indent_chars is not None:
        pPr = ensure_ppr(para)
        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = parse_xml(f'<w:ind {nsdecls("w")}/>')
            pPr.append(ind)
        ind.set(qn('w:firstLineChars'), str(first_indent_chars))
        ind.set(qn('w:firstLine'), str(int(first_indent_chars * 12 / 100 * 20)))  # approx
    
    if first_indent_pt is not None:
        pPr = ensure_ppr(para)
        ind = pPr.find(qn('w:ind'))
        if ind is None:
            ind = parse_xml(f'<w:ind {nsdecls("w")}/>')
            pPr.append(ind)
        ind.set(qn('w:firstLine'), str(int(first_indent_pt * 20)))
        # Remove chars if set
        if ind.get(qn('w:firstLineChars')):
            del ind.attrib[qn('w:firstLineChars')]

def clear_indent(para):
    """Clear all indentation"""
    pPr = ensure_ppr(para)
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = parse_xml(f'<w:ind {nsdecls("w")}/>')
        pPr.append(ind)
    ind.set(qn('w:firstLine'), '0')
    ind.set(qn('w:firstLineChars'), '0')
    # Remove hanging
    for attr in ['w:hanging', 'w:left', 'w:right']:
        if ind.get(qn(attr)):
            del ind.attrib[qn(attr)]

def add_code_border(para, fill='F2F2F2', border_color='BFBFBF'):
    """Add code-style background shading and border to paragraph"""
    pPr = ensure_ppr(para)
    
    # Remove existing shd and pBdr
    for old in pPr.findall(qn('w:shd')):
        pPr.remove(old)
    for old in pPr.findall(qn('w:pBdr')):
        pPr.remove(old)
    
    # Add shading
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>')
    pPr.append(shd)
    
    # Add borders
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="1" w:color="{border_color}"/>'
        f'<w:left w:val="single" w:sz="4" w:space="4" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="1" w:color="{border_color}"/>'
        f'<w:right w:val="single" w:sz="4" w:space="4" w:color="{border_color}"/>'
        f'</w:pBdr>')
    pPr.append(pBdr)

def set_hanging_indent(para, hanging=420, left=420):
    """Set hanging indent"""
    pPr = ensure_ppr(para)
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = parse_xml(f'<w:ind {nsdecls("w")}/>')
        pPr.append(ind)
    ind.set(qn('w:hanging'), str(hanging))
    ind.set(qn('w:left'), str(left))
    # Remove firstLine if set
    if ind.get(qn('w:firstLine')):
        del ind.attrib[qn('w:firstLine')]
    if ind.get(qn('w:firstLineChars')):
        del ind.attrib[qn('w:firstLineChars')]

def add_page_break_before(para):
    """Add page break before paragraph"""
    pPr = ensure_ppr(para)
    existing = pPr.find(qn('w:pageBreakBefore'))
    if existing is None:
        pb = parse_xml(f'<w:pageBreakBefore {nsdecls("w")}/>')
        pPr.append(pb)

def set_keep_next(para):
    """Set keepNext and keepLines"""
    pPr = ensure_ppr(para)
    if pPr.find(qn('w:keepNext')) is None:
        pPr.append(parse_xml(f'<w:keepNext {nsdecls("w")}/>'))
    if pPr.find(qn('w:keepLines')) is None:
        pPr.append(parse_xml(f'<w:keepLines {nsdecls("w")}/>'))
