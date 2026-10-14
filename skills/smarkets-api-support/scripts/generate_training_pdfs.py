#!/usr/bin/env python3
"""Generate clean PDFs from Smarkets API documentation markdown files.

Handles:
- Markdown headers (H1-H4), bold, italic, inline code, links
- Tables with header rows, alternating row colours, proper column widths
- Confluence macros: {info}, {tip}, {warning}, {error} with optional :title=
- Code blocks (```...```)
- Blockquotes
- Ordered/unordered lists
- Internal anchor links (#section) rendered as plain text (not hyperlinks)
- Title page + page numbers + footer

Usage:
  cd ~/smarkets-api-support/training && python3 ~/.hermes/skills/process/smarkets-api-support/scripts/generate_training_pdfs.py

Requirements: reportlab (pip install reportlab)

Known gotchas (fixed in this version):
- ReportLab Canvas uses setFillColor(), NOT setColour() — the latter raises AttributeError
- Internal markdown anchor links (#section-name) must be stripped to plain text,
  NOT rendered as <a href="#..."> — ReportLab tries to resolve them as PDF
  destinations and raises ValueError on save
- getSampleStyleSheet() is the correct function name (camelCase), not get_sample_styles()
"""

import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# Colors
DARK_BLUE = HexColor('#1a365d')
LIGHT_BLUE = HexColor('#3182ce')
GREY = HexColor('#4a5568')
TABLE_HEADER_BG = HexColor('#2d3748')
TABLE_ROW_ALT = HexColor('#f7fafc')
CODE_BG = HexColor('#edf2f7')
INFO_BG = HexColor('#ebf8ff'); INFO_BORDER = HexColor('#3182ce')
WARN_BG = HexColor('#fffaf0'); WARN_BORDER = HexColor('#dd6b20')
ERR_BG = HexColor('#fed7d7'); ERR_BORDER = HexColor('#c53030')
TIP_BG = HexColor('#f0fff4'); TIP_BORDER = HexColor('#38a169')

def escape_xml(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text

def convert_inline(text):
    text = escape_xml(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="8.5" color="#4a5568">\1</font>', text)
    def replace_link(m):
        t, url = m.group(1), m.group(2)
        if url.startswith('#'): return t  # strip internal anchors
        return f'<a href="{url}">{t}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_link, text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    return text

def build_table(rows, styles):
    if not rows: return Spacer(1, 4)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=10)
    hdr_style = ParagraphStyle('HdrCell', parent=cell_style, fontName='Helvetica-Bold', textColor=white)
    data = []
    for ri, row in enumerate(rows):
        s = hdr_style if ri == 0 else cell_style
        fr = [Paragraph(convert_inline(c), s) for c in row]
        while len(fr) < max(len(r) for r in rows): fr.append(Paragraph('', cell_style))
        data.append(fr)
    max_cols = max(len(r) for r in data)
    t = Table(data, colWidths=[170*mm/max_cols]*max_cols, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_BG),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, HexColor('#cbd5e0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, TABLE_ROW_ALT]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    return t

def md_to_flowables(md_text):
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=18, textColor=DARK_BLUE, spaceAfter=12, spaceBefore=18, fontName='Helvetica-Bold')
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=DARK_BLUE, spaceAfter=8, spaceBefore=14, fontName='Helvetica-Bold')
    h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, textColor=LIGHT_BLUE, spaceAfter=6, spaceBefore=10, fontName='Helvetica-Bold')
    body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, leading=13, spaceAfter=4)
    code_s = ParagraphStyle('Code', fontSize=8.5, leading=11, textColor=GREY, backColor=CODE_BG, fontName='Courier', leftIndent=10, rightIndent=10, spaceBefore=4, spaceAfter=4)
    quote_s = ParagraphStyle('Quote', parent=body, leftIndent=15, rightIndent=15, textColor=GREY, fontName='Helvetica-Oblique')

    flow = []
    lines = md_text.split('\n')
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s:
            if in_table and table_rows:
                flow.append(build_table(table_rows, styles)); table_rows = []; in_table = False
            i += 1; continue

        if s.startswith('|') and s.endswith('|'):
            if i+1 < len(lines) and re.match(r'^\|[\s\-:]+\|', lines[i+1].strip()):
                if not in_table: in_table = True; table_rows = []
                table_rows.append([c.strip() for c in s.split('|')[1:-1]])
                i += 2; continue
            elif in_table:
                cells = [c.strip() for c in s.split('|')[1:-1]]
                while len(cells) < len(table_rows[0]): cells.append('')
                table_rows.append(cells); i += 1; continue

        if in_table and table_rows:
            flow.append(build_table(table_rows, styles)); table_rows = []; in_table = False

        if s in ('---', '***'):
            flow.append(Spacer(1, 6)); i += 1; continue

        if s.startswith('```'):
            cl = []; i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                cl.append(lines[i]); i += 1
            i += 1
            flow.append(Paragraph('<br/>'.join(escape_xml('  '+l) for l in cl), code_s)); continue

        macro = re.match(r'^\{(info|warning|error|tip)(?::title=([^}]+))?\}', s)
        if macro:
            mt, mtitle = macro.group(1), macro.group(2)
            ml = []; i += 1
            while i < len(lines) and lines[i].strip() != f'{{{mt}}}':
                ml.append(lines[i]); i += 1
            i += 1
            bg, brd = {'info':(INFO_BG,INFO_BORDER),'warning':(WARN_BG,WARN_BORDER),'error':(ERR_BG,ERR_BORDER),'tip':(TIP_BG,TIP_BORDER)}.get(mt, (HexColor('#f7fafc'), GREY))
            ms = ParagraphStyle(f'M_{mt}', parent=body, backColor=bg, borderColor=brd, borderWidth=1, borderPadding=6, leftIndent=5, rightIndent=5, spaceBefore=6, spaceAfter=6)
            th = f'<b>{escape_xml(mtitle)}</b><br/>' if mtitle else ''
            flow.append(Paragraph(th + convert_inline(' '.join(ml).strip()), ms)); continue

        if s.startswith('# '): flow.append(Paragraph(convert_inline(s[2:]), h1)); i += 1; continue
        if s.startswith('## '): flow.append(Paragraph(convert_inline(s[3:]), h2)); i += 1; continue
        if s.startswith('### '): flow.append(Paragraph(convert_inline(s[4:]), h3)); i += 1; continue
        if s.startswith('#### '): flow.append(Paragraph(convert_inline(s[5:]), h3)); i += 1; continue
        if s.startswith('> '): flow.append(Paragraph(convert_inline(s[2:]), quote_s)); i += 1; continue
        if s.startswith('- ') or s.startswith('* '):
            ls = ParagraphStyle('LI', parent=body, leftIndent=15, spaceAfter=2)
            flow.append(Paragraph(f'• {convert_inline(s[2:])}', ls)); i += 1; continue
        nm = re.match(r'^(\d+)\.\s+(.*)', s)
        if nm:
            ls = ParagraphStyle('NI', parent=body, leftIndent=20, spaceAfter=2)
            flow.append(Paragraph(f'{nm.group(1)}. {convert_inline(nm.group(2))}', ls)); i += 1; continue
        t = convert_inline(s)
        if t: flow.append(Paragraph(t, body))
        i += 1

    if in_table and table_rows: flow.append(build_table(table_rows, styles))
    return flow

def add_page_num(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 10*mm, f'Page {canvas.getPageNumber()}')
    canvas.drawString(20*mm, 10*mm, 'Smarkets API Support')
    canvas.drawRightString(A4[0]-20*mm, 10*mm, 'Confidential — Internal Use')
    canvas.restoreState()

def generate_pdf(md_path, pdf_path, title):
    with open(md_path) as f: md = f.read()
    doc = SimpleDocTemplate(pdf_path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=18*mm, bottomMargin=18*mm, title=title, author='Smarkets API Support Team')
    ts = ParagraphStyle('Title', fontSize=24, textColor=DARK_BLUE, alignment=TA_CENTER, spaceAfter=10, fontName='Helvetica-Bold')
    ss = ParagraphStyle('Sub', fontSize=11, textColor=GREY, alignment=TA_CENTER, spaceAfter=4)
    flow = [Spacer(1, 60*mm), Paragraph(title, ts), Spacer(1, 8*mm), Paragraph('Smarkets API Support Team', ss), Paragraph('June 2026', ss), PageBreak()]
    flow.extend(md_to_flowables(md))
    doc.build(flow, onFirstPage=lambda c,d: None, onLaterPages=add_page_num)
    sz = os.path.getsize(pdf_path)/1024
    print(f'OK: {pdf_path} ({sz:.0f} KB)')

if __name__ == '__main__':
    base = os.path.expanduser('~/smarkets-api-support/training')
    generate_pdf(f'{base}/confluence_draft_v2.md', f'{base}/confluence_draft_v2.pdf', 'Smarkets API Support — Agent Knowledge Base')
    generate_pdf(f'{base}/customer_faq.md', f'{base}/customer_faq.pdf', 'Smarkets API — Frequently Asked Questions')
