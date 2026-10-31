#!/usr/bin/env python3
"""Gera a HQ e sua transcrição estática a partir do roteiro público em JSON."""
from pathlib import Path
from html import escape
import argparse
import json
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PUBLIC = 'https://plano-d-comunidade.aldenirmed.chatgpt.site'
e = lambda value: escape(str(value), quote=True)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data', type=Path, default=DIST / 'dados/hq-origem.json')
args = parser.parse_args()
data = json.loads(args.data.read_text(encoding='utf-8'))
pages = data['pages']
assert len(pages) == 8, 'A edição de origem deve conter oito páginas.'
assert [p['number'] for p in pages] == list(range(1, 9)), 'Paginação inválida.'
assert all(len(p['panels']) == 3 for p in pages), 'Cada página deve conter três quadros.'
for page in pages:
    assert re.fullmatch(r'#[0-9a-fA-F]{6}', page['accent']), 'Cor inválida.'
    if 'art' in page:
        art = page['art']
        assert isinstance(art['width'], (int, float)) and art['width'] > 0, 'Largura da arte inválida.'
        assert isinstance(art['height'], (int, float)) and art['height'] > 0, 'Altura da arte inválida.'
        assert len(art['panels']) == 3, 'A arte deve declarar três faixas de quadros.'
        for frame in art['panels']:
            assert isinstance(frame['y'], (int, float)) and frame['y'] >= 0, 'Posição de quadro inválida.'
            assert isinstance(frame['height'], (int, float)) and frame['height'] > 0, 'Altura de quadro inválida.'
            assert frame['y'] + frame['height'] <= art['height'], 'Quadro ultrapassa a altura da arte.'
    for panel in page['panels']:
        assert all(isinstance(panel[k], str) and panel[k].strip() for k in ('narration', 'speaker', 'dialogue', 'scene', 'alt')), 'Quadro incompleto.'

title = e(data['title'])
subtitle = e(data['subtitle'])
author = e(data['credits']['idealization'])
cover_title = 'Quando cinco<br>luzes <em>se encontram.</em>' if data['title'] == 'Quando cinco luzes se encontram' else title
characters = json.loads((DIST / 'dados/cavaleiros.json').read_text(encoding='utf-8'))
character_links = ''.join(f'<a href="../cavaleiros/{e(c["id"])}.html" style="--aura:{e(c["color"])}">{e(c["name"])}</a>' for c in characters)
color_marks = ''.join(f'<span style="--aura:{e(c["color"])}"></span>' for c in characters)

PDF_NAME = 'quando-cinco-luzes-se-encontram.pdf'
share_message = f'🔥📖 Conheça a HQ de origem dos cinco cavaleiros do PLANO D: 8 páginas e 24 quadros sobre fé em Deus, inclusão neurodivergente e cuidado socioambiental.\n\nLeia gratuitamente, sem login:\n{PUBLIC}/hq/\n\nNa página você também pode baixar o PDF e ler a versão em texto.'
share_url = 'https://wa.me/?text=' + quote(share_message, safe='')
resources = f'''<aside class="hq-resources" aria-labelledby="hq-resources-title"><div><p class="eyebrow">LEVE A HISTÓRIA COM VOCÊ</p><h2 id="hq-resources-title">Para guardar e compartilhar.</h2><p>Baixe a HQ ou convide alguém para conhecer os cinco cavaleiros.</p></div><div class="hq-resource-actions"><a class="button button-secondary" href="{PDF_NAME}" download="PLANO-D-HQ-origem.pdf">Baixar HQ em PDF ↓</a><a class="button button-primary" href="{e(share_url)}" target="_blank" rel="noopener noreferrer">Compartilhar HQ no WhatsApp ↗</a></div><p class="hq-resource-note">PDF com 10 folhas: capa, oito páginas ilustradas e créditos. A mensagem do WhatsApp fica pronta; você escolhe para quem enviar.</p></aside>'''


header = '''<a class="skip-link" href="#conteudo">Ir para o conteúdo</a>
<header class="site-header hq-header"><div class="hq-wrap header-inner">
  <a class="hq-wordmark" href="../index.html" aria-label="PLANO D, início"><strong>PLANO D</strong><span>REAVERSO · 360 X</span></a>
  <a class="hq-back" href="../index.html#cavaleiros">← Voltar ao Plano D</a>
</div></header>'''
credits = f'''<footer class="hq-wrap hq-credits"><p>Idealização: {author}. Roteiro e ilustrações desenvolvidos com assistência de inteligência artificial.<br>Ficção do Reaverso · PLANO D · Edição 01, outubro de 2026. Personagens e poderes são imaginários.</p><a href="../direitos.html">Direitos e créditos</a></footer>'''

def document_head(page_title, description, path, with_script=False):
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="theme-color" content="#080d18">
  <title>{e(page_title)} · PLANO D</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{PUBLIC}/{path}">
  <meta property="og:type" content="article"><meta property="og:title" content="{e(page_title)} · PLANO D">
  <meta property="og:description" content="{e(description)}"><meta property="og:url" content="{PUBLIC}/{path}">
  <meta property="og:image" content="{PUBLIC}/assets/cavaleiros-plano-d.webp">
  <meta property="og:image:alt" content="Os cinco cavaleiros cósmicos do Plano D, com auras ciano, verde, laranja, violeta e dourada.">
  <link rel="icon" href="../assets/marca.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../styles.css"><link rel="stylesheet" href="../hq.css">
  {'<script src="../hq.js" defer></script>' if with_script else ''}
</head>'''

page_articles = []
transcript_articles = []
for page in pages:
    number = page['number']
    artwork = f'../assets/hq/pagina-{number:02d}.webp'
    art = page.get('art', {'width': 1024, 'height': 1536, 'panels': [{'y': i * 512, 'height': 512} for i in range(3)]})
    frames = []
    transcript_frames = []
    for index, panel in enumerate(page['panels']):
        count = (number - 1) * 3 + index + 1
        region = art['panels'][index]
        ratio = art['width'] / region['height']
        image_height = 100 * art['height'] / region['height']
        image_top = -100 * region['y'] / region['height']
        panel_class = 'comic-panel panel-wide' if ratio > 3 else 'comic-panel'
        panel_style = f'--panel-ratio:{art["width"]}/{region["height"]};--image-height:{image_height:.8f}%;--image-top:{image_top:.8f}%'
        frames.append(f'''<figure class="{panel_class}" aria-labelledby="quadro-{count}-label">
  <div class="panel-visual" style="{panel_style}"><img src="{artwork}" width="{art['width']}" height="{art['height']}" alt="{e(panel['alt'])}" loading="lazy" decoding="async"></div>
  <figcaption class="panel-caption"><span class="panel-count" id="quadro-{count}-label">Quadro {count:02d} / 24</span>
    <p class="panel-narration">{e(panel['narration'])}</p>
    <blockquote class="panel-dialogue"><span class="panel-speaker">{e(panel['speaker'])}</span><p>“{e(panel['dialogue'])}”</p></blockquote>
  </figcaption>
</figure>''')
        transcript_frames.append(f'''<section class="transcript-panel" aria-labelledby="texto-quadro-{count}">
  <h3 id="texto-quadro-{count}">Quadro {count:02d}</h3>
  <p class="transcript-description"><strong>Descrição da cena:</strong> {e(panel['alt'])}</p>
  <p><strong>Narração:</strong> {e(panel['narration'])}</p>
  <p class="transcript-dialogue"><strong>{e(panel['speaker'])}:</strong> “{e(panel['dialogue'])}”</p>
</section>''')
    page_articles.append(f'''<article class="comic-page" id="pagina-{number}" data-title="{e(page['title'])}" style="--page-aura:{e(page['accent'])}" aria-labelledby="pagina-{number}-titulo">
  <header class="comic-page-header"><div><p class="eyebrow">Página {number:02d} / 08</p><h3 id="pagina-{number}-titulo" tabindex="-1">{e(page['title'])}</h3></div><a class="comic-page-art-link" href="{artwork}" target="_blank" rel="noopener noreferrer" aria-label="Abrir a arte completa da página {number} em nova aba">Ver arte<br>completa ↗</a></header>
  <div class="comic-panels">{''.join(frames)}</div>
</article>''')
    transcript_articles.append(f'''<section class="transcript-page" id="pagina-{number}" aria-labelledby="texto-pagina-{number}">
  <h2 id="texto-pagina-{number}">{number:02d}. {e(page['title'])}</h2>
  {''.join(transcript_frames)}
</section>''')

options = ''.join(f'<option value="{p["number"]}">{p["number"]:02d} · {e(p["title"].split(" · ")[0])}</option>' for p in pages)
description = 'Uma HQ em oito páginas sobre a origem de Nexo, Raiz, Brasa, Prisma e Lúmen: fé em Deus, inclusão neurodivergente e cuidado com a vida.'
html = document_head(data['title'], description, 'hq/', with_script=True) + f'''
<body class="hq-page">
{header}
<main id="conteudo">
  <div class="hq-wrap">
    <section class="hq-cover" aria-labelledby="hq-title">
      <div class="hq-cover-copy"><p class="eyebrow">HQ 01 · A origem dos cinco cavaleiros</p>
        <h1 id="hq-title">{cover_title}</h1>
        <p class="hq-deck">{e(data['premise'])}</p>
        <div class="hq-cover-actions"><a class="button button-primary" href="#pagina-1">Começar a leitura <span aria-hidden="true">↓</span></a><a class="text-link" href="texto.html">Versão em texto</a><a class="text-link" href="{PDF_NAME}" download="PLANO-D-HQ-origem.pdf">Baixar PDF ↓</a></div>
        <p class="hq-cover-meta">8 páginas · 24 quadros · leia no seu ritmo</p>
        <div class="hq-constellation" aria-hidden="true">{color_marks}</div>
      </div>
      <figure class="hq-cover-art"><img src="../assets/cavaleiros-plano-d.webp" width="1536" height="1024" alt="Nexo, Raiz, Brasa, Prisma e Lúmen, os cinco cavaleiros cósmicos, em suas motocicletas diante da Terra." fetchpriority="high"><figcaption>REAVERSO · PLANO D · CINCO CAMINHOS, UM ENCONTRO</figcaption></figure>
    </section>
    <aside class="hq-intro-note" aria-label="Sobre esta história"><p>Uma aventura de ficção sobre aprender a ouvir, repartir recursos e transformar fé em cuidado. A comunidade participa das escolhas desde o começo.</p><a class="text-link" href="#apos-a-historia">Conheça os cavaleiros ↓</a></aside>
    {resources}
    <section class="hq-reader" id="leitor" aria-labelledby="reader-title">
      <div class="reader-heading"><h2 id="reader-title">A história começa aqui.</h2><p>De cima para baixo, um quadro de cada vez.</p></div>
      <div class="reader-tools" id="reader-tools" hidden>
        <div class="reader-tool-row">
          <nav class="reader-navigation" aria-label="Páginas da HQ">
            <button type="button" data-previous aria-label="Página anterior">← Anterior</button>
            <label class="sr-only" for="page-select">Escolha uma página</label><select id="page-select">{options}</select>
            <button type="button" data-next aria-label="Próxima página">Próxima →</button>
          </nav>
          <div class="reader-options" role="group" aria-label="Opções de leitura"><button type="button" id="reading-mode" aria-pressed="false">Leitura contínua</button><button type="button" id="text-size" aria-pressed="false">Texto amplo</button></div>
        </div>
        <div class="reader-feedback"><progress id="reader-progress" max="8" value="1" aria-label="Página 1 de 8"></progress><p id="reader-status" role="status" aria-live="polite" aria-atomic="true"></p></div>
      </div>
      <div class="comic-pages">{''.join(page_articles)}</div>
      <nav class="reader-bottom" id="reader-bottom" aria-label="Continuar a HQ" hidden><button type="button" data-previous aria-label="Página anterior">← Anterior</button><p class="subtle" id="reader-bottom-status">1 / 8</p><button type="button" data-next aria-label="Próxima página">Próxima →</button></nav>
    </section>
    <section class="hq-afterword" id="apos-a-historia" aria-label="Depois da história">
      <div><p class="eyebrow">Cinco caminhos, um propósito</p><h2>Há mais por trás<br>de cada luz.</h2><p>Conheça as histórias, os poderes imaginários e os compromissos de Nexo, Raiz, Brasa, Prisma e Lúmen.</p><nav class="hq-character-links" aria-label="Fichas dos cavaleiros">{character_links}</nav></div>
      <div><p class="eyebrow">Um gesto possível</p><h2>Leve o cuidado<br>para perto.</h2><p>Pergunte de que ajuda alguém precisa, ofereça diferentes formas de participar ou conheça uma causa socioambiental. Cada pessoa escolhe como e quando contribuir.</p><a class="button button-secondary" href="../index.html#doacoes">Conhecer causas do Plano D ↗</a></div>
    </section>
  </div>
</main>
{credits}
</body></html>
'''

index = ''.join(f'<li><a href="#pagina-{p["number"]}">{e(p["title"])}</a></li>' for p in pages)
transcript = document_head(f'{data["title"]} · Versão em texto', 'Leitura integral e descrições das cenas da HQ de origem dos cinco cavaleiros do Plano D.', 'hq/texto.html') + f'''
<body class="hq-page">
{header}
<main id="conteudo" class="hq-wrap">
  <article class="hq-transcript">
    <p class="eyebrow">HQ 01 · Versão em texto</p><h1>{title}</h1>
    <p class="transcript-intro">{subtitle}. Aqui você encontra todas as narrações, falas e descrições das cenas, na mesma ordem da HQ ilustrada.</p>
    <div class="hq-resource-actions"><a class="button button-primary" href="index.html">Abrir a HQ ilustrada →</a><a class="button button-secondary" href="{PDF_NAME}" download="PLANO-D-HQ-origem.pdf">Baixar HQ em PDF ↓</a></div>
    <nav class="transcript-index" aria-label="Índice da história"><ol>{index}</ol></nav>
    {''.join(transcript_articles)}
    <div class="transcript-return"><a class="text-link" href="index.html">← Voltar à HQ ilustrada</a></div>
  </article>
</main>
{credits}
</body></html>
'''

output = DIST / 'hq'
output.mkdir(exist_ok=True)
(output / 'index.html').write_text(html, encoding='utf-8')
(output / 'texto.html').write_text(transcript, encoding='utf-8')
# Compatibilidade com links do rascunho anterior; a URL canônica continua /hq/.
(output / 'origem.html').write_text(html, encoding='utf-8')
print('HQ gerada: 8 páginas, 24 quadros e versão integral em texto.')
