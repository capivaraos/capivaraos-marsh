# Identidade visual do Marsh ao alternar claro/escuro (KDE Plasma)

Como manter a identidade do CapivaraOS (bolinhas coloridas das janelas + ícone do
lançador adaptável) ao usar o Marsh no modo **claro** ou **escuro**.

## O que é a nossa identidade (e de onde vem)

O visual do Marsh é o **Tema Global "CapivaraOS"** (`org.capivaraos.desktop`), que é o
**padrão de fábrica** e reúne:

- **Decoração de janela "CapivaraOS"** (Aurorae): as **bolinhas coloridas** estilo macOS
  (vermelho/amarelo/verde) à esquerda da barra de título.
- **Ícone do lançador** (kickoff no dock): um SVG **simbólico adaptável** — o Plasma o
  recolore pelo tema automaticamente (escuro no claro, claro no escuro). Sempre visível.
- Esquema de cores, tema Plasma, ícones, perfil do Konsole.

Num **install novo**, tudo isso já vem ligado (gravado em `/etc/xdg`, lido por todos os
usuários).

## O jeito CERTO de alternar claro ↔ escuro

Use **Configurações do Sistema → Aparência e estilo → Cores** e escolha o esquema
**"Breeze Light"** ou **"Breeze Dark"**.

A página **Cores** troca **só o esquema de cores** — **não** mexe na decoração da janela
nem no ícone. Então as **bolinhas coloridas continuam** e o ícone do lançador se adapta
sozinho. É assim que você tem a nossa identidade tanto no claro quanto no escuro.

## O que EVITA (e por quê)

**Não** use o seletor de **Tema Global** (Aparência → Tema Global, ou as miniaturas
"Breeze" / "Breeze Dark" em "Configurações rápidas") para alternar claro/escuro.

Esses são os **temas de fábrica do KDE** — aplicá-los **substitui** a nossa decoração
pela lisa (× ∨ ∧ sem cor) e sobrescreve o nosso padrão no seu perfil (`~/.config`). O
"Breeze Dark" de fábrica **não é** o nosso tema; ele não traz as bolinhas coloridas.

> O ícone do lançador **continua visível** mesmo assim (ele é adaptável), mas as
> **bolinhas** voltam a ser as lisas do Breeze.

## Como RESTAURAR as bolinhas coloridas

Se você já aplicou um tema de fábrica e perdeu as bolinhas:

- **Configurações do Sistema → Aparência e estilo → Decorações de janela** → selecione
  **"CapivaraOS"** → **Aplicar**. (Isso traz só a decoração, sem mexer nas cores.)
- **Ou** reaplique o **Tema Global "CapivaraOS"** (Aparência → Tema Global) — isso
  restaura a decoração **e** o resto do nosso padrão de uma vez.

## Resumo

| Quero… | Faça |
|---|---|
| Alternar claro/escuro mantendo a identidade | **Cores** → Breeze Light / Breeze Dark |
| Trazer as bolinhas coloridas de volta | **Decorações de janela** → "CapivaraOS" |
| Voltar tudo ao nosso padrão | Tema Global → **"CapivaraOS"** |
| (evitar) | Aplicar o Tema Global **"Breeze"/"Breeze Dark"** de fábrica p/ claro/escuro |
