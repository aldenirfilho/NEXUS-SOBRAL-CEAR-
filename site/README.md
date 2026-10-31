# PLANO D · Site

Site estático de comunidade, cuidado e propósito para Sobral, com biblioteca de 24 leituras e seis temas.

## Uso local

Execute `python3 -m http.server 4173 --directory dist` e abra `http://127.0.0.1:4173`.
Não há instalação de dependências nem etapa de compilação.

## Conteúdo e manutenção

- `dist/index.html`, `styles.css` e `app.js`: interface e interação.
- `dist/dados/catalogo.json`: projeção pública da edição 0.3.0 do acervo bíblico.
- `dist/dados/procedencia.json`: procedência do catálogo, separada da versão do site.
- `dist/biblioteca.html`: alternativa de leitura sem JavaScript.
- `dist/direitos.html`: autoria, fontes, direitos e privacidade.
- `.openai/hosting.json`: identidade do site e diretório publicado.

Os textos completos abrem o site de origem. A busca é local. Favoritos usam o armazenamento deste navegador; não há contas, telemetria ou coleta de relatos.

A revisão teológica independente da origem permanece pendente. Alterações editoriais exigem conferência humana; publicação técnica não equivale a essa revisão.

## Compartilhamento e doações

A página inclui QR estático do endereço público, download em PNG e link de WhatsApp com mensagem revisável. O link não envia mensagens automaticamente.

O diretório de doações aponta para canais oficiais de Associação Caatinga, Projeto Tamar, SOS Mata Atlântica, APAE Fortaleza, Instituto Verdeluz, UNICEF, MSF, Cáritas Brasileira, Pastoral da Criança e Gerando Falcões. QR codes abrem os sites das instituições; não são códigos de pagamento. Chaves Pix só aparecem quando conferidas em fonte oficial. Não há intermediação financeira nem promessa de parceria. As fontes e a data de consulta estão em `dist/dados/doacoes.json`; a atualização é manual.

A APAE Fortaleza publica expressamente seu CNPJ como chave Pix; o valor copiável usa os mesmos dígitos sem pontuação. Para o Instituto Verdeluz, não foi reproduzida chave fixa sem confirmação atual: o cartão distingue o canal geral de contribuição e o canal Asaas com Pix, que exibia doação única de R$ 30 na consulta de 20/10/2026. Relatórios vinculados não foram auditados. O site não publica registros pessoais de doação.

## Identidade aeroespacial e causas ambientais

A interface usa uma identidade aeroespacial escura com guardião conceitual original, preservando fé, liberdade de consciência e cuidado. Caatinga e SOS Mata Atlântica exibem Pix publicado em suas páginas oficiais. O Projeto Tamar é apresentado com suas formas oficiais de apoio e transparência; não foi inventada chave Pix nem convertido seu CNPJ em chave de pagamento. O diretório reúne dez instituições e oportunidades de apoio.


### Cinco cavaleiros do universo PLANO D

Arte de ficção criada com a ferramenta integrada de geração de imagens, em 20/10/2026, a pedido do idealizador. A versão PNG original está em `dist/assets/cavaleiros-plano-d.png`; a versão WebP usada na hero preserva a composição 1536×1024 e reduz o peso para 481.518 bytes. A página apresenta Nexo, Raiz, Brasa, Prisma e Lúmen como alegorias dos valores do projeto, com crédito da arte e distinção do texto bíblico. O arquivo SVG anterior permanece preservado.


### Fichas dos cinco cavaleiros

As cinco páginas em `dist/cavaleiros/` oferecem retrato individual, história, três poderes ficcionais, missão, gesto na vida real e links para o diretório de causas. São HTML estático e funcionam sem JavaScript. Os dados ficam em `dist/dados/cavaleiros.json`; após editar o conteúdo, execute `python3 scripts/gerar-fichas.py` para atualizar as páginas e os cartões da página inicial. Os retratos usados no site ficam em `dist/assets/cavaleiros/`, em WebP; os PNGs originais e prompts foram preservados na pasta de entrega `artes-cavaleiros-fichas/` do workspace. Não há coleta de dados, envio de mensagem nem doação automática nas fichas.


### HQ 01 — Quando cinco luzes se encontram

Edição de 22/10/2026. Oito páginas e 24 quadros contam as origens, o encontro e a primeira missão de Nexo, Raiz, Brasa, Prisma e Lúmen. A HQ usa as identidades já registradas em `dist/dados/cavaleiros.json`; a máquina da Cobiça, a oferta das chaves e o pacto final são novos elementos ficcionais desta edição.

- Leitor: `dist/hq/index.html`; versão integral em texto: `dist/hq/texto.html`.
- Roteiro editável: `dist/dados/hq-origem.json`.
- Artes: `dist/assets/hq/pagina-01.webp` a `pagina-08.webp`.
- Interface: `dist/hq.css` e `dist/hq.js`.
- Regenerar após editar o roteiro: `python3 scripts/gerar-hq.py`.
- As falas são HTML ampliável, com descrições por quadro; sem JavaScript, todas as páginas ficam legíveis. A interface permite uma página por vez, leitura contínua, salto de página e texto amplo. Não usa dados pessoais, armazenamento ou telemetria.
- Fontes do cânone, prompts e registro das artes: `ARTE-HQ.md`.

Endereço da HQ: https://plano-d-comunidade.aldenirmed.chatgpt.site/hq/


### Continuação da HQ — download e compartilhamento

A edição de oito páginas e 24 quadros foi preservada. O leitor em `dist/hq/index.html` e a versão em texto oferecem download de `dist/hq/quando-cinco-luzes-se-encontram.pdf`. O PDF contém dez folhas (capa, oito páginas com arte e texto selecionável e créditos). O botão do WhatsApp apenas abre a mensagem com o link público, para revisão e envio pelo visitante.

O gerador `scripts/gerar-hq.py` também produz `dist/hq/origem.html` como endereço compatível, com a mesma HQ e URL canônica `/hq/`. Para atualizar o PDF, execute `python3 scripts/gerar-hq-pdf.py`; para atualizar as páginas, execute `python3 scripts/gerar-hq.py`. As imagens, os 24 quadros, as fichas, a biblioteca e os dados de doações não são alterados por esta continuação.
