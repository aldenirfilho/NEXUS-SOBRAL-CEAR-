#!/usr/bin/env python3
"""Cria o PDF da HQ canônica: capa, oito pranchas e créditos.

Uso: python3 scripts/gerar-hq-pdf.py [--font-dir PASTA]
Requer reportlab e Pillow. Descobre Arial ou DejaVu no sistema, sem copiar
fontes para o repositório. Todos os caminhos editoriais são relativos à raiz.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
import os
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageFont
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SOURCE = DIST / 'dados' / 'hq-origem.json'
OUTPUT = DIST / 'hq' / 'quando-cinco-luzes-se-encontram.pdf'
SITE = 'https://plano-d-comunidade.aldenirmed.chatgpt.site/'
HQ_URL = SITE + 'hq/'
PAGE_W, PAGE_H = landscape(A4)
MARGIN = 35
INK = colors.HexColor('#172033')
MUTED = colors.HexColor('#526174')
LINE = colors.HexColor('#d5dce5')
NIGHT = colors.HexColor('#080d18')
CYAN = colors.HexColor('#67e8f9')
AMBER = colors.HexColor('#ffd166')


def register_fonts(explicit_dir: str | None) -> str:
    """Usa fontes instaladas; --font-dir permite a mesma execução noutro SO."""
    pairs = [('DejaVuSans.ttf', 'DejaVuSans-Bold.ttf'),
             ('Arial.ttf', 'Arial Bold.ttf'), ('arial.ttf', 'arialbd.ttf')]
    roots = []
    if explicit_dir:
        roots.append(Path(explicit_dir).expanduser())
    if os.environ.get('PLANO_D_FONT_DIR'):
        roots.append(Path(os.environ['PLANO_D_FONT_DIR']).expanduser())
    fs_root = Path(os.path.abspath(os.sep))
    roots += [fs_root / 'System' / 'Library' / 'Fonts' / 'Supplemental',
              fs_root / 'Library' / 'Fonts',
              fs_root / 'usr' / 'share' / 'fonts' / 'truetype' / 'dejavu',
              fs_root / 'usr' / 'local' / 'share' / 'fonts',
              Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts']
    selected = None
    for root in roots:
        for regular, bold in pairs:
            if (root / regular).is_file() and (root / bold).is_file():
                selected = (root / regular, root / bold)
                break
        if selected:
            break
    if not selected:
        for regular, bold in pairs:
            try:
                r = Path(ImageFont.truetype(regular, 12).path)
                b = Path(ImageFont.truetype(bold, 12).path)
                if r.is_file() and b.is_file():
                    selected = (r, b)
                    break
            except OSError:
                continue
    if not selected:
        raise SystemExit('Instale Arial ou DejaVu Sans, ou informe --font-dir.')
    pdfmetrics.registerFont(TTFont('PD-Regular', str(selected[0])))
    pdfmetrics.registerFont(TTFont('PD-Bold', str(selected[1])))
    pdfmetrics.registerFontFamily('PD', normal='PD-Regular', bold='PD-Bold',
                                italic='PD-Regular', boldItalic='PD-Bold')
    return selected[0].stem


def safe(value: object) -> str:
    # Mantém acentos e troca apenas hífens tipográficos por hífen ASCII.
    value = str(value).translate(str.maketrans({'\u2010': '-', '\u2011': '-',
                                             '\u2012': '-', '\u2013': '-',
                                             '\u2014': '-', '\u2212': '-'}))
    return escape(value)


def style(name: str, size: float, leading: float, color=INK,
          bold=False) -> ParagraphStyle:
    return ParagraphStyle(name, fontName='PD-Bold' if bold else 'PD-Regular',
                          fontSize=size, leading=leading, textColor=color,
                          alignment=TA_LEFT, spaceAfter=0, allowWidows=0,
                          allowOrphans=0)


def paragraph(c, text, x, top, width, st, minimum=None):
    p = Paragraph(text, st)
    _, h = p.wrap(width, PAGE_H)
    if minimum is not None and top - h < minimum - .1:
        raise ValueError(f'Texto não cabe na página: {text[:80]}')
    p.drawOn(c, x, top - h)
    return top - h


def image_reader(path: Path, quality: int):
    """Prepara JPEG em memória; preserva toda a arte, sem recorte."""
    with Image.open(path) as original:
        im = original.convert('RGB')
        original_size = im.size
        memory = BytesIO()
        im.save(memory, format='JPEG', quality=quality, optimize=True,
                progressive=False, subsampling=2)
    memory.seek(0)
    return ImageReader(memory), original_size


def footer(c, number: int, label: str, dark=False):
    color = colors.HexColor('#b6c5da') if dark else MUTED
    c.setStrokeColor(colors.HexColor('#354762') if dark else LINE)
    c.setLineWidth(.6)
    c.line(MARGIN, 34, PAGE_W - MARGIN, 34)
    c.setFillColor(color)
    c.setFont('PD-Regular', 8)
    c.drawString(MARGIN, 21, label)
    c.drawRightString(PAGE_W - MARGIN, 21, f'FOLHA {number:02d} / 10')


def cover(c, story, pictures):
    c.setFillColor(NIGHT)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(CYAN)
    c.rect(MARGIN, PAGE_H - 48, 82, 4, fill=1, stroke=0)
    paragraph(c, safe(story['universe']).upper(), MARGIN, PAGE_H - 67,
              425, style('cover-kicker', 10, 14, CYAN, True))
    top = paragraph(c, safe(story['title']), MARGIN, PAGE_H - 113,
                    402, style('cover-title', 38, 41, colors.white, True))
    top = paragraph(c, safe(story['subtitle']), MARGIN, top - 20,
                    399, style('cover-sub', 16, 21, colors.HexColor('#d4deed')))
    top = paragraph(c, safe(story['premise']), MARGIN, top - 24,
                    400, style('cover-premise', 11.5, 17, colors.HexColor('#b6c5da')))
    top = paragraph(c, '<b>8 pranchas ilustradas · 24 quadros</b><br/>'
                    'Este PDF tem 10 folhas: capa, 8 pranchas e créditos.',
                    MARGIN, top - 25, 400,
                    style('cover-format', 11.3, 17, AMBER))
    paragraph(c, 'Idealização: ' + safe(story['credits']['idealization']),
              MARGIN, top - 24, 408, style('cover-author', 10.5, 15, colors.white))
    paragraph(c, f'<link href="{HQ_URL}" color="#67e8f9"><u>Ler a HQ no site público do PLANO D</u></link>',
              MARGIN, 91, 407, style('cover-link', 10.5, 15, CYAN))
    x, y, h = 490, 72, 454
    reader, (iw, ih) = pictures[-1]
    w = h * iw / ih
    c.setFillColor(colors.HexColor('#17253a'))
    c.roundRect(x - 6, y - 6, w + 12, h + 12, 4, fill=1, stroke=0)
    c.drawImage(reader, x, y, w, h, preserveAspectRatio=True, mask='auto')
    footer(c, 1, 'HQ 01 · Origem dos cavaleiros · Conteúdo ficcional', dark=True)
    c.showPage()


def story_page(c, page, picture):
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    accent = colors.HexColor(page['accent'])
    # A tonalidade escura acompanha os títulos; a cor original fica na regra.
    c.setFillColor(accent)
    c.rect(MARGIN, PAGE_H - 42, 55, 3, fill=1, stroke=0)
    paragraph(c, f'PLANO D · HQ 01 · PRANCHA {page["number"]:02d} / 08',
              MARGIN + 68, PAGE_H - 35, PAGE_W - 2*MARGIN - 68,
              style('page-kicker', 8.5, 12, MUTED, True))
    paragraph(c, safe(page['title']), MARGIN, PAGE_H - 61,
              PAGE_W - 2*MARGIN, style('page-title', 23, 27, INK, True))
    image_top, image_bottom = PAGE_H - 108, 52
    image_h = image_top - image_bottom
    reader, (iw, ih) = picture
    image_w = image_h * iw / ih
    c.drawImage(reader, MARGIN, image_bottom, image_w, image_h,
                preserveAspectRatio=True, mask='auto')
    c.setStrokeColor(LINE)
    c.setLineWidth(.5)
    c.rect(MARGIN, image_bottom, image_w, image_h, fill=0, stroke=1)
    text_x = MARGIN + image_w + 27
    text_w = PAGE_W - MARGIN - text_x
    block_gap = 12
    block_h = (image_h - block_gap*2)/3
    for position, panel in enumerate(page['panels']):
        number = (page['number']-1)*3 + position + 1
        block_top = image_top - position*(block_h + block_gap)
        block_bottom = block_top - block_h
        c.setStrokeColor(LINE)
        c.setLineWidth(.6)
        if position:
            c.line(text_x, block_top + 6, text_x + text_w, block_top + 6)
        top = paragraph(c, f'QUADRO {number:02d}', text_x, block_top,
                        text_w, style('panel-number', 9, 12, INK, True))
        top = paragraph(c, safe(panel['narration']), text_x, top - 7,
                        text_w, style('narration', 11.2, 14.5), block_bottom + 7)
        quote = '<b>' + safe(panel['speaker']) + ':</b> “' + safe(panel['dialogue']) + '”'
        paragraph(c, quote, text_x + 11, top - 10, text_w - 11,
                  style('dialogue', 11.1, 14.5), block_bottom + 2)
        c.setStrokeColor(colors.HexColor('#73839a'))
        c.setLineWidth(1.3)
        c.line(text_x + 2, top - 8, text_x + 2, block_bottom + 3)
    first, last = (page['number']-1)*3 + 1, page['number']*3
    footer(c, page['number'] + 1,
           f'Leitura: quadros {first:02d}-{last:02d}, de cima para baixo. Arte integral à esquerda.')
    c.showPage()


def credits_page(c, story):
    c.setFillColor(colors.white)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    paragraph(c, 'CRÉDITOS · LEITURA · PROPÓSITO', MARGIN, PAGE_H - 42,
              730, style('credit-kicker', 9, 13, MUTED, True))
    paragraph(c, 'A história continua no cuidado.', MARGIN, PAGE_H - 75,
              740, style('credit-title', 29, 34, INK, True))
    gutter = 42
    col_w = (PAGE_W - 2*MARGIN - gutter)/2
    left, right, top = MARGIN, MARGIN + col_w + gutter, PAGE_H - 135
    top = paragraph(c, 'Idealização', left, top, col_w,
                    style('credit-heading', 14, 18, INK, True))
    top = paragraph(c, safe(story['credits']['idealization']), left, top - 7,
                    col_w, style('credit-body', 11, 15))
    top = paragraph(c, 'Desenvolvimento e arte', left, top - 23, col_w,
                    style('credit-heading2', 14, 18, INK, True))
    top = paragraph(c, safe(story['credits']['story_and_art']), left, top - 7,
                    col_w, style('credit-ai', 11, 15))
    top = paragraph(c, 'Ficção e liberdade de consciência', left, top - 23,
                    col_w, style('credit-heading3', 14, 18, INK, True))
    top = paragraph(c, 'Os personagens, poderes, a máquina da Cobiça e os acontecimentos são ficcionais. '
                    'A fé em Deus inspira gestos de cuidado, com respeito a outras crenças e ao direito de não crer. '
                    'A inclusão neurodivergente envolve autonomia, apoio, comunicação e escolhas; '
                    'não há promessa de cura nem poderes clínicos atribuídos às pessoas.',
                    left, top - 8, col_w, style('credit-fiction', 11, 15), 57)
    rtop = paragraph(c, 'Uma HQ, oito pranchas, dez folhas', right, PAGE_H - 135,
                     col_w, style('reading-heading', 14, 18, INK, True))
    rtop = paragraph(c, 'A obra ilustrada tem 8 páginas e 24 quadros. Esta edição PDF acrescenta capa e créditos, '
                     'totalizando 10 folhas A4 em orientação horizontal. Cada prancha é reproduzida inteira à esquerda, '
                     'com narração e falas selecionáveis à direita. Leia os três quadros de cada prancha de cima para baixo.',
                     right, rtop - 8, col_w, style('reading-body', 11, 15))
    rtop = paragraph(c, 'Da ficção à vida real', right, rtop - 22, col_w,
                     style('real-heading', 14, 18, INK, True))
    rtop = paragraph(c, 'O PLANO D reúne reflexões e canais oficiais de apoio a causas socioambientais. '
                     'Qualquer contribuição é voluntária e realizada diretamente pelos canais da instituição. '
                     'As instituições reais são independentes desta narrativa; a HQ não afirma parceria, '
                     'campanha conjunta, recebimento de valores ou certificação de resultados.',
                     right, rtop - 8, col_w, style('real-body', 11, 15))
    links = [('Ler a HQ no site público', HQ_URL),
             ('Conhecer o PLANO D', SITE),
             ('Direitos e créditos do projeto', SITE + 'direitos.html')]
    for label, href in links:
        rtop = paragraph(c, f'<link href="{href}" color="#165c74"><u>{label}</u></link>',
                         right, rtop - 16, col_w, style('credit-link', 11, 15), 54)
    footer(c, 10, f'Edição {story["edition"]} · Roteiro canônico: {story["date"]} · PLANO D / 360X')
    c.showPage()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font-dir')
    parser.add_argument('--jpeg-quality', type=int, default=78,
                        help='Qualidade das ilustrações JPEG em memória (65-95; padrão 78).')
    args = parser.parse_args()
    if not 65 <= args.jpeg_quality <= 95:
        parser.error('--jpeg-quality deve ficar entre 65 e 95.')
    # JPEG binário evita a expansão ASCII85 sem alterar a arte ou o texto.
    rl_config.useA85 = 0
    font_family = register_fonts(args.font_dir)
    story = json.loads(SOURCE.read_text())
    if len(story['pages']) != 8 or any(len(p['panels']) != 3 for p in story['pages']):
        raise ValueError('Esta edição exige oito pranchas canônicas de três quadros.')
    if [p['number'] for p in story['pages']] != list(range(1, 9)):
        raise ValueError('Numeração canônica das pranchas inválida.')
    pictures = [image_reader(DIST / 'assets' / 'hq' / f'pagina-{n:02d}.webp',
                             args.jpeg_quality)
                for n in range(1, 9)]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H),
                      pageCompression=1)
    c.setTitle(story['title'] + ' - HQ de origem dos cavaleiros do Plano D')
    c.setAuthor(story['credits']['idealization'])
    c.setSubject('HQ ficcional: fé, inclusão neurodivergente e cuidado socioambiental')
    c.setCreator('PLANO D - scripts/gerar-hq-pdf.py')
    cover(c, story, pictures)
    for page, picture in zip(story['pages'], pictures):
        story_page(c, page, picture)
    credits_page(c, story)
    c.save()
    if OUTPUT.stat().st_size > 8*1024*1024:
        raise ValueError('PDF ultrapassou a meta de 8 MiB; revisar preparação das imagens.')
    print(json.dumps({'path': str(OUTPUT), 'pages': 10, 'panels': 24,
                      'bytes': OUTPUT.stat().st_size,
                      'embedded_font': font_family,
                      'jpeg_quality': args.jpeg_quality}, ensure_ascii=False))


if __name__ == '__main__':
    main()
