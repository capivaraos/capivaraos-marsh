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
- **Login (accent do formulário):** FEITO no alpha25 (item 10). Confirmado o
  mecanismo em VM: o greeter do `plasma-login-manager` roda como o usuário
  `plasmalogin` (home `/var/lib/plasmalogin`) e lê a aparência de um `kdeglobals`
  (o `.kcfg` do greeter aponta para `kdeglobals`; o accent do Plasma 6 vem de
  `[General] AccentColor`). Como o usuário `plasmalogin` não tem `AccentColor`
  próprio, prevalece o fallback do sistema `/etc/xdg/kdeglobals` — onde gravamos
  as duas chaves via `kwriteconfig` (merge). Seguro: valor não-reconhecido não
  faz efeito e **nunca** dá login preto (o preto do BUG-43 era o wallpaper
  apontando para diretório removido, não o accent). Reversível pelo item 10.

Build: `./build-all.sh`
