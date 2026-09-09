# Brief de arte — Tema visual próprio do CapivaraOS (frente D)

**Objetivo:** dar ao Marsh **formas próprias** (decoração de janela + tema do
Plasma), aposentando o WhiteSur (clone de macOS). A **cor** já é nossa (fatia D1:
esquema `CapivaraOS.colors`, paleta verde); falta a **forma**. Este documento é o
que o design precisa produzir; quando os SVGs chegarem, o wiring no build é
trivial (ver "Como eu ligo" no fim).

Enquanto a arte não vem, **o WhiteSur segue no ar** — nada quebra.

---

## 1. Direção visual (o que é "CapivaraOS")

- **Dark, limpo, moderno.** Base nos neutros escuros da paleta (verde-quase-preto),
  com o **verde da marca** como único acento vivo.
- **NÃO é macOS.** Proibido copiar elementos do WhiteSur/Apple: **sem** os três
  "botõezinhos coloridos de semáforo" (vermelho/amarelo/verde) no canto da janela,
  sem dock com reflexo/vidro estilo macOS, sem ícone de "Preferências" à la Apple.
- **NÃO é Breeze genérico.** Deve ter personalidade: cantos suavemente
  arredondados (não "bolha"), contornos sutis, um toque de sofisticação de
  "estação de desenvolvimento". Distinto tanto do macOS quanto do KDE padrão.
- **Referência de humor:** Pantanal/Cerrado à noite — fundo escuro terroso-esverdeado,
  vida (o verde) pontuando. Sério, mas acolhedor.

## 2. Paleta (tokens — usar EXATAMENTE estes, iguais ao D1)

| Token | Hex | RGB | Uso |
|-------|-----|-----|-----|
| ground | `#12160F` | 18,22,15 | fundo mais profundo (campos, listas, área de conteúdo) |
| surface | `#1E231A` | 30,35,26 | fundo de janela / diálogo |
| surface-alt | `#282E23` | 40,46,35 | faixas alternadas, cabeçalhos, barra de título inativa |
| **accent** | **`#15B22C`** | **21,178,44** | seleção, foco, botão primário, realce, barra de progresso |
| accent-dark | `#0E7A1E` | 14,122,30 | pressionado / hover escuro do accent |
| accent-light | `#46C95B` | 70,201,91 | hover claro / brilho do accent |
| text | `#FCFCFC` | 252,252,252 | texto principal |
| text-muted | `#A1A9B1` | 161,169,177 | texto secundário / desabilitado |
| negative | `#DA4453` | 218,68,83 | erro/fechar-perigo |
| neutral | `#F67400` | 246,116,0 | aviso |
| positive | `#27AE60` | 39,174,96 | sucesso |
| link | `#1D99F3` | 29,153,243 | links (mantido azul por semântica) |

**Raio de canto sugerido:** janela ~8px, botões/menus/campos ~6px, tooltip ~8px.
**Barra de título:** altura ~36–40px. Os SVGs devem ser vetor plano (sem PNG
embutido), para escalarem bem em HiDPI.

## 3. Entregável A — Decoração de janela (Aurorae)

Pasta final: `/usr/share/aurorae/themes/CapivaraOS/`. Arquivos:

- `metadata.desktop` **e** `metadata.json` — nome/id do tema (eu ajusto os ids).
- `CapivaraOSrc` — config da decoração (valores que o design define; eu transcrevo):
  - tamanho da borda, `TitleAlignment` (esq/centro), altura do título,
    espaçamento e tamanho dos botões, padding.
- `decoration.svg` — **o quadro da janela** como SVG com a convenção Aurorae:
  elementos nomeados para as 9 regiões (`decoration`, `decoration-top`,
  `decoration-bottom`, `decoration-left`, `decoration-right`, cantos) + retângulos
  `hint-*` marcando margens/insets e a área do texto do título. Precisa dos
  estados **ativo** e **inativo** (janela focada vs. não). Barra de título em
  `surface`/`surface-alt`, texto em `text`, contorno sutil.
- Botões (um SVG cada, com **estados** como sub-imagens nomeadas: `active`,
  `inactive`, `hover`, `pressed`, `deactivated`):
  `close.svg`, `maximize.svg`, `restore.svg`, `minimize.svg`,
  `keepabove.svg`, `keepbelow.svg`, `alldesktops.svg` (e opcionais `shade`,
  `help`, `menu`). **Glifos monocromáticos** (linha/ícone), não círculos
  coloridos. Hover/pressed usam o **accent** (ex.: fechar pode usar `negative` no
  hover; os demais, `accent`).
- (Opcional) variantes de escala `CapivaraOS_x1.25/1.5/1.75/2.0` com o mesmo
  `decoration.svg` reescalado — o WhiteSur faz isso; podemos começar só com x1.

## 4. Entregável B — Tema do Plasma (painéis, diálogos, plasmoides)

Pasta final: `/usr/share/plasma/desktoptheme/CapivaraOS/`. Arquivos:

- `metadata.json` — nome/id (eu ajusto).
- `colors` — pode simplesmente **referenciar o esquema do sistema** (nossa paleta
  já vem do `CapivaraOS.colors`); ou repetir os tokens acima.
- SVGs (convenção Plasma "nine-patch": elementos nomeados `center/left/right/top/
  bottom/topleft/...` + retângulos `hint-*margin`). **Prioridade** (os que mais
  definem o visual — começar por estes):
  1. `widgets/panel-background.svgz` — **fundo do painel** (a "cara" da barra).
  2. `widgets/background.svgz` + `dialogs/background.svgz` — fundo de plasmoides/menus/diálogos.
  3. `widgets/tooltip.svgz` — balões de dica.
  4. `widgets/button.svgz`, `widgets/lineedit.svg` — botões e campos.
  5. `widgets/listitem.svg`, `widgets/viewitem.svg` — itens de lista (hover/seleção em accent).
  6. `widgets/tabbar.svgz`, `widgets/slider.svg`, `widgets/scrollbar.svgz`,
     `widgets/switch.svgz`, `widgets/radiobutton.svgz`, `widgets/checkmarks.svgz`.
  7. Resto (completar depois): `clock.svg`, `calendar.svg`, `arrows.svgz`,
     `line.svgz`, `frame.svgz`, `plasmoidheading.svgz`, `busywidget.svg`,
     `bar_meter_*.svg`, `pager.svg`, `notes.svg`, `toolbar.svg`,
     `configuration-icons.svg`, `action-overlays.svg`, `actionbutton.svg`,
     `translucentbackground.svg`, `containment-controls.svg`.
- `icons/` (opcional) — ícones monocromáticos da bandeja próprios.

> Dica de esforço: os itens **1–4** já entregam ~80% da percepção. Podemos lançar
> uma primeira versão só com eles (o Plasma cai no tema Breeze para o que faltar).

## 5. Entregável C (opcional/leve) — GTK

Autoria de tema GTK completo é caro. **Recomendação:** em vez de tema autoral,
usar **Adwaita com accent verde** (GTK3/4 já suportam accent) ou um recolor leve —
suficiente para os apps GTK combinarem com o Plasma. Bespoke de GTK só se sobrar
fôlego de design.

## 6. Restrições (importantes)

- **Licença:** arte **original** (ou base com licença compatível — GPL/LGPL/CC-BY).
  Cada arquivo com cabeçalho **SPDX** (autor + licença). **Nada** derivado do
  WhiteSur/Apple ou de assets proprietários.
- **Formato:** SVG vetor plano; `.svgz` = apenas o `.svg` comprimido com gzip
  (`gzip -9 arquivo.svg > arquivo.svgz`) — o design entrega `.svg`, eu comprimo.
- **Contraste/acessibilidade:** texto sobre `surface` e sobre `accent` deve passar
  em contraste (accent #15B22C com texto branco = OK para rótulos de botão).

## 7. Decisão a reboque — LAYOUT do painel

Hoje o layout é `macos-layout.js` (barra no topo + dock embaixo, estilo macOS).
Com formas próprias, faz sentido decidir: **manter** esse layout (topo+dock) ou
**migrar** para um painel único (mais "KDE/estação de dev"). Não é arte de tema,
mas afeta a percepção — decidir junto com o design. *(Fica registrado; não bloqueia
os SVGs acima.)*

## 8. Como eu ligo a arte no build (para referência)

1. Os SVGs entram no pacote `capivaraos-branding` em
   `/usr/share/aurorae/themes/CapivaraOS/` e `/usr/share/plasma/desktoptheme/CapivaraOS/`.
2. No `kickstart/capivaraos-post-theme.ks`: troco a detecção do WhiteSur por
   nomes fixos — `kwinrc` → `org.kde.kdecoration2 theme=__aurorae__svg__CapivaraOS`
   e `library=org.kde.kwin.aurorae`; `plasmarc` → `[Theme] name=CapivaraOS`.
3. **Removo os 2 `git clone`** do WhiteSur (seções 1–2 do post-theme) e as
   limpezas relacionadas → build mais rápido, sem dependência de terceiros.
4. Mapa de revert atualizado; versão nova; teste em VM.

## 9. Critérios de aceite (teste em VM)

- Barra de título, botões, painel, menus, diálogos e tooltips mostram as **formas
  CapivaraOS** na **paleta verde**, coerentes entre si.
- **Nenhum** vestígio de macOS (sem semáforo, sem dock estilo Apple).
- Sem regressão de legibilidade/contraste; HiDPI OK.
- Screenshots de janela ativa/inativa, painel e um menu aberto.

---

*Superfícies cobertas por este brief: decoração (Aurorae) + tema Plasma [+ GTK
opcional]. A cor (esquema `CapivaraOS.colors`) já está pronta na fatia D1.*
