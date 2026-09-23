# Mapa das trocas — paleta verde (FEAT-91, frente B)

> **ATUALIZAÇÃO 2026-09-22 (Marsh 2.x, alpha43, PROD-131):** o dono achou "muito
> verde" e pediu para reverter **só cores/accent** ao azul padrão (Breeze Dark).
> Feito: `ColorScheme=BreezeDark` + **sem** `AccentColor` verde no `/etc/skel`
> kdeglobals, nos `defaults` do Look-and-Feel `org.capivaraos.desktop` e no
> `/etc/xdg` (%posttrans, `AccentColor --delete`). O splash do Plymouth voltou ao
> spinner **branco** + fundo azul-escuro (igual Pup/Snout). O esquema
> `CapivaraOS.colors` **segue instalado e selecionável** (só não é mais o padrão).
> **Mantidos verdes** (nesta 1ª rodada): tema Plasma/painel (item 16),
> decoração Aurorae (item 13) e Konsole (item 14).
>
> **ATUALIZAÇÃO 2026-09-23 (alpha44, 2ª rodada):** ainda "muito verde" → revertido
> também o **tema Plasma/painel** (item 16): `plasmarc [Theme] name` CapivaraOS →
> `default` (Breeze) no skel, nos `defaults` do LnF e no `/etc/xdg`. O desktoptheme
> `CapivaraOS` segue instalado/selecionável. **Ainda verdes:** decoração Aurorae
> (item 13) e Konsole (item 14). REVERTIDOS no Marsh: itens 1, 2, 10, 16 e a parte
> de `ColorScheme` do 12/15.

Build de **avaliação** que troca o *accent* do desktop para o verde da marca
**#15B22C** (RGB **21,178,44**). Objetivo: testar em VM/instalação real se o
verde funciona como cor de acento do sistema, mantendo o restante do visual
(neutros escuros + formato "macOS" do WhiteSur) intacto.

Escopo desta mudança = **só o accent**. Foi de propósito: é a troca de maior
impacto visual e menor risco (dados declarativos, sem mexer no `plasmashell` em
runtime). Neutros/cores de apoio da paleta ficam para quando o WhiteSur for
aposentado (frente D). Nada aqui muta a sessão durante o 1º boot.

## Como reverter (1 comando)

Tudo entrou num **único commit**. Para desfazer por completo:

```
git revert <sha-do-commit-da-paleta-verde>
```

Ou, para descartar antes de commitar/publicar: `git checkout -- <arquivos abaixo>`.

## Pontos exatos que foram tocados

| # | Arquivo | O que mudou | Antes | Depois |
|---|---------|-------------|-------|--------|
| 1 | `kickstart/capivaraos-post-theme.ks` | Bloco novo logo após aplicar o `ColorScheme` do WhiteSur: grava `AccentColor` e `accentColorFromWallpaper` no `kdeglobals` de `/root` e `/etc/skel` (sistema instalado) | *(sem accent — usava o azul do WhiteSur)* | `[General] AccentColor=21,178,44` + `accentColorFromWallpaper=false` |
| 2 | `rpm/capivaraos-branding.spec` — `/etc/skel/.config/kdeglobals` (heredoc) | Duas chaves novas em `[General]` (baseline da live antes do post-theme) | `[General]`<br>`ColorScheme=BreezeDark` | idem + `AccentColor=21,178,44`<br>`accentColorFromWallpaper=false` |
| 3 | `rpm/capivaraos-branding.spec` — `Release:` | Bump de versão | `0.22.alpha22` | `0.23.alpha23` |
| 4 | `rpm/capivaraos-branding.spec` — os-release/issue/kcm | Rótulo do preview (×N) | `(alpha22, preview)` | `(alpha23, preview)` |
| 5 | `rpm/capivaraos-branding.spec` — `%changelog` | Entrada nova documentando a paleta | — | entrada `0.23.alpha23` |
| 6 | `build-all.sh` | Nome da ISO + `--volid` | `...alpha22...` | `...alpha23...` |
| 7 | `docs/REVERT-CORES-VERDE.md` | Este mapa | — | novo |
| 8 | `rpm/...spec` — geração do spinner do Plymouth (frente C) | Cor do arco do spinner | `-stroke white` | `-stroke '#15B22C'` |
| 9 | `rpm/...spec` — `capivaraos.script` do Plymouth (frente C) | Cor de fundo do splash | `SetBackground*Color(0.07, 0.09, 0.13)` (azul-escuro) | `(0.071, 0.086, 0.059)` (#12160F, verde-quase-preto) |
| 10 | `rpm/...spec` — `%posttrans`, após o wallpaper do login (frente C) | Grava o accent verde no `kdeglobals` fallback do sistema (via `kwriteconfig`, merge) que o greeter `plasmalogin` lê | *(greeter usava o accent azul padrão do Breeze)* | `/etc/xdg/kdeglobals` → `[General] AccentColor=21,178,44` + `accentColorFromWallpaper=false` |
| 11 | `rpm/...spec` — `capivaraos.script` do Plymouth (frente C, Path C) | ~~Capivara "andando no lugar" (gingado da logo)~~ **REVERTIDO no alpha27** — a logo do boot voltou a ser estática, por decisão de design | logo estática | **logo estática** (animação removida) |
| 12 | `branding/color-schemes/CapivaraOS.colors` (novo) + `rpm/build-rpm.sh` + `rpm/...spec` (`%install`/`%files`/`/etc/skel kdeglobals`) + `kickstart/capivaraos-post-theme.ks` (frente **D**, D1, alpha28) | Esquema de cores **próprio** do CapivaraOS (paleta verde) no lugar do esquema do WhiteSur; `kdeglobals ColorScheme` passa a `CapivaraOS` | `ColorScheme=<WhiteSur*>` | `ColorScheme=CapivaraOS` (arquivo `.colors` empacotado; formas WhiteSur mantidas) |
| 13 | `branding/aurorae/CapivaraOS/*` (novo) + `rpm/build-rpm.sh` + `rpm/...spec` (`%install`/`%files`) + `kickstart/capivaraos-post-theme.ks` (frente **D**, D3, alpha29-30, botões always-color alpha32) | **Decoração de janela própria** (Aurorae): titlebar da paleta, cantos arredondados, botões círculos coloridos da marca; `kwinrc` `library=org.kde.kwin.aurorae.v2` + `theme=__aurorae__svg__CapivaraOS` + `ButtonsOnLeft=XIA`. **alpha32:** `inactive-center` dos 4 botões passou de cinza `#4A5040` para a cor da marca — os círculos ficam SEMPRE coloridos (em foco e fora de foco); glifo só no hover; `deactivated` (ação indisponível) segue cinza | `theme=__aurorae__svg__<WhiteSur*>` (e sem carregar por falta do `.v2`) | decoração CapivaraOS carregando, botões sempre coloridos (tema Plasma/painel do WhiteSur mantido) |
| 14 | `branding/konsole/*` (novo) + `rpm/build-rpm.sh` + `rpm/...spec` (`%install`/`%files`/`/etc/skel konsolerc`) (frente **D**, alpha30) | **Konsole** com identidade CapivaraOS (esquema de cores verde + perfil padrão) | *(Konsole no tema Breeze padrão)* | esquema `CapivaraOS` + perfil padrão `CapivaraOS.profile` |
| 15 | `rpm/...spec` — `%posttrans`, bloco `/etc/xdg` (frente **D**, alpha31; +plasmarc alpha33) | Identidade como **padrão do sistema** (`/etc/xdg`, lido por todos os usuários — corrige a sessão LIVE que não herda `/etc/skel`): `ColorScheme`, decoração Aurorae, perfil do Konsole e (alpha33) o **tema Plasma** | *(só o accent estava em `/etc/xdg`)* | `/etc/xdg/kdeglobals` (+ColorScheme=CapivaraOS), `/etc/xdg/kwinrc` (decoração `.v2`+tema+botões), `/etc/xdg/konsolerc` (DefaultProfile), `/etc/xdg/plasmarc` (`[Theme] name=CapivaraOS`) |
| 16 | `branding/plasma/CapivaraOS/*` (novo) + `rpm/build-rpm.sh` + `rpm/...spec` (`%install`/`%files`/`/etc/skel plasmarc`/`/etc/xdg plasmarc`) + `kickstart/capivaraos-post-theme.ks` (frente **D**, D4, alpha33; prova 2 alpha34) | **Tema Plasma próprio** (desktoptheme): formas próprias do painel/menus/diálogos/dica (nine-patch FrameSvg, paleta verde, cantos r=6) + arquivo `colors` que recolore os widgets herdados do Breeze na nossa paleta; `plasmarc [Theme] name=CapivaraOS`. **Prova 2 (alpha34):** +`widgets/listitem.svg` (realce de menu: selecionado verde sólido), +`widgets/lineedit.svg` (campo + anel de foco verde), +`widgets/button.svg` (normal/hover/foco/pressionado) | `name=<WhiteSur*>` (tema Plasma do WhiteSur) | tema Plasma CapivaraOS carregando (GTK do WhiteSur mantido até D5) |

Para reverter **só a cor** e manter o rótulo alpha23, basta desfazer os itens
**1 e 2** (as duas linhas de `AccentColor`/`accentColorFromWallpaper`).

## O que NÃO foi tocado (e por quê)

- **Cockpit / instalador Anaconda WebUI** (`branding.css`), **quadrado do greeter**
  e **`ANSI_COLOR` do os-release** (`0;32`): **já eram verdes** (#15B22C /
  #46c95b / #0e7a1e). Nenhuma mudança necessária.
- **Tema GTK (WhiteSur), decoração Aurorae, tema Plasma (desktop theme):**
  intactos. O accent verde do KDE **não** recolore o accent embutido no tema GTK
  do WhiteSur — isso só muda quando aposentarmos o WhiteSur (frente D). Se, após
  avaliar, decidirmos ir além do accent (neutros próprios, GTK verde), aí sim
  entra a frente D com esquema de cores/`.colors` próprio e tema GTK próprio.
- **Wallpapers, Plymouth:** sem relação com o accent; inalterados.

## O que você deve ver no teste (alpha23)

Verde da marca em: itens de menu realçados, texto selecionado, borda de campo em
foco, caixas de seleção / botões de rádio / interruptores, barras de progresso,
alças de slider e indicadores de ocupado. Janelas e painéis continuam com o
formato e os cinzas do WhiteSur.

## Frente C — boot/login

- **Boot (Plymouth):** FEITO no alpha24 (itens 8 e 9). Spinner verde + fundo escuro
  da paleta; logo branca mantida.
- **Capivara com movimento:** foi tentada no alpha26 (Path C, gingado por código) e
  **REVERTIDA no alpha27** por decisão de design — a logo do boot/desligamento é
  **estática**. Fica registrado, caso um dia se retome: **Path A** = walk-cycle real
  (~6–12 quadros desenhados da capivara andando, PNG com alfa, ciclados como o
  spinner); **Path B** = logo em camadas (patas separadas) animadas por rotação no
  script. Ambos dependem de **arte** — hoje só há rasters chapados
  (`branding/icons/capivaraos-logo.png` 700×700).
- **Login (accent do formulário):** FEITO no alpha25 (item 10). Confirmado o
  mecanismo em VM: o greeter do `plasma-login-manager` roda como o usuário
  `plasmalogin` (home `/var/lib/plasmalogin`) e lê a aparência de um `kdeglobals`
  (o `.kcfg` do greeter aponta para `kdeglobals`; o accent do Plasma 6 vem de
  `[General] AccentColor`). Como o usuário `plasmalogin` não tem `AccentColor`
  próprio, prevalece o fallback do sistema `/etc/xdg/kdeglobals` — onde gravamos
  as duas chaves via `kwriteconfig` (merge). Seguro: valor não-reconhecido não
  faz efeito e **nunca** dá login preto (o preto do BUG-43 era o wallpaper
  apontando para diretório removido, não o accent). Reversível pelo item 10.

## Frente D — aposentar o WhiteSur (em fatias)

As **4 superfícies** da identidade — (1) tema **GTK**, (2) **esquema de cores**,
(3) decoração **Aurorae**, (4) **tema Plasma** — hoje são **100% próprias**
(pacote `capivaraos-branding`). O WhiteSur foi **aposentado** no alpha35 (D5): o
antigo `kickstart/capivaraos-post-theme.ks`, que clonava 2 repos
(WhiteSur-gtk-theme + WhiteSur-kde), foi **removido** e o build não depende mais
de rede/terceiros para o tema. Ícones (Breeze Dark) e Look&Feel já eram Breeze.

- **D1 — Esquema de cores próprio:** FEITO no alpha28 (item 12). Novo
  `branding/color-schemes/CapivaraOS.colors` (derivado do Breeze Dark do KDE,
  LGPL-2.0-or-later; neutros da paleta + accent verde), empacotado pelo
  `capivaraos-branding`; `kdeglobals ColorScheme=CapivaraOS`. Aposenta a
  dependência do **esquema de cores** do WhiteSur. **Formas** do WhiteSur
  (Aurorae + tema Plasma) seguem por ora.
- **D2 — base das FORMAS: DECIDIDO = bespoke** (tema próprio, não Breeze genérico).
  Brief de arte escrito em **`docs/BRIEF-TEMA-CAPIVARAOS.md`** (decoração Aurorae +
  tema Plasma, com paleta e lista exata de SVGs). Formas do WhiteSur **mantidas até
  a arte chegar** (não-destrutivo).
- **D3 — decoração Aurorae própria:** FUNCIONANDO em VM a partir do alpha30. Arte
  original em `branding/aurorae/CapivaraOS/` (código SVG, não ilustração), validada
  em janelas reais (titlebar arredondada + círculos coloridos da marca). Correção
  do alpha30: a library do kwinrc precisa ser `org.kde.kwin.aurorae.v2` (com `.v2`)
  — sem isso o Plasma 6 caía no Breeze; e botões à esquerda (ButtonsOnLeft=XIA)
  estilo macOS. Tema Plasma/painel do WhiteSur mantido (D4).
- **D4 — tema Plasma próprio:** FEITO (prova 1 alpha33, prova 2 alpha34). Novo
  `branding/plasma/CapivaraOS/` (desktoptheme): fundo do painel/menus/diálogos/
  dica (prova 1) + widgets `button`/`lineedit`/`listitem` (prova 2 — realce de
  item **verde sólido**, anel de foco verde, estados de botão) em nine-patch
  FrameSvg na paleta. O que não redesenhamos cai no Breeze recolorido pela nossa
  paleta (arquivo `colors` do tema). Selecionado via `plasmarc name=CapivaraOS`
  (skel + `/etc/xdg`). Aposenta o **tema Plasma** do WhiteSur.
- **D5 — tema GTK próprio + REMOÇÃO DO WHITESUR:** FEITO no alpha35 (item 17).
  Apps GTK/libadwaita usam **Adwaita-dark nativo + accent verde** (`branding/gtk/`
  → `gtk.css` com `accent_bg_color`/`theme_selected_bg_color` #15B22C, em skel e
  `/etc/xdg`). Com isso as 4 superfícies são próprias: **removidos** os 2
  `git clone` do WhiteSur e todo o `capivaraos-post-theme.ks`, mais as deps de
  build só-WhiteSur (sassc/optipng/gtk-murrine-engine/gtk2-engines/ImageMagick).
  **Fecha o FEAT-91.**

### Item 17 — tema GTK próprio + aposentadoria do WhiteSur (alpha35, FEAT-91 D5)
- **`branding/gtk/{gtk.css,settings.ini,gtkrc-2.0}`** (NOVOS): Adwaita-dark +
  accent verde #15B22C. Instalados pelo RPM em `/etc/skel/.config/gtk-{3,4}.0` e
  `/etc/xdg/gtk-{3,4}.0` (este p/ a sessão LIVE) + `/etc/skel/.gtkrc-2.0`.
- **`kdeglobals [Icons] Theme=breeze-dark`** movido do post-script para o RPM
  (skel + `/etc/xdg`) — único ajuste que o kickstart ainda fazia sozinho.
- **`kickstart/capivaraos-post-theme.ks`**: REMOVIDO (junto com o `%include` e as
  deps de build só-WhiteSur na `capivaraos-marsh.ks`).
- **Reverter:** improvável (é a identidade final). Para voltar ao WhiteSur seria
  preciso restaurar o post-script do histórico do git. O accent GTK isolado:
  apagar `branding/gtk/gtk.css` volta ao Adwaita-dark neutro.

Build: `./build-all.sh`
