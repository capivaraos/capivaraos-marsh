# Mapa das trocas — paleta verde (FEAT-91, frente B)

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
| 15 | `rpm/...spec` — `%posttrans`, bloco `/etc/xdg` (frente **D**, alpha31) | Identidade como **padrão do sistema** (`/etc/xdg`, lido por todos os usuários — corrige a sessão LIVE que não herda `/etc/skel`): `ColorScheme`, decoração Aurorae e perfil do Konsole | *(só o accent estava em `/etc/xdg`)* | `/etc/xdg/kdeglobals` (+ColorScheme=CapivaraOS), `/etc/xdg/kwinrc` (decoração `.v2`+tema+botões), `/etc/xdg/konsolerc` (DefaultProfile) |

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

Onde o WhiteSur entra hoje: `kickstart/capivaraos-post-theme.ks` clona 2 repos
(WhiteSur-gtk-theme + WhiteSur-kde) e aplica **4 superfícies** — (1) tema **GTK**,
(2) **esquema de cores**, (3) decoração **Aurorae**, (4) **tema Plasma**. Ícones e
Look&Feel já são Breeze.

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
- **D4 — tema Plasma próprio:** aguardando arte (ver brief).
- **D5 — tema GTK** (Adwaita accent verde recomendado) + remover os 2 `git clone`
  do WhiteSur do build: entra junto com D3/D4.

Build: `./build-all.sh`
