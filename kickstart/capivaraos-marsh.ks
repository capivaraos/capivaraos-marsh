#version=DEVEL
# =============================================================================
# CapivaraOS Marsh - Fedora 44 (KDE Plasma) - kickstart principal
# =============================================================================
#
# Baseado no kickstart oficial do Fedora KDE Live (vendorizado em
# upstream/), com a identidade visual, idioma e seleção de pacotes do
# CapivaraOS Marsh (originalmente construído sobre Debian 13/trixie com
# live-build). Ver PACKAGES.md para o mapeamento completo Debian -> Fedora.
#
# Uso (ver README.md para detalhes; ./build-all.sh automatiza tudo isto):
#   cd kickstart && python3 ks-flatten.py capivaraos-marsh.ks > /var/tmp/capivaraos-marsh-flat.ks
#   livemedia-creator --ks=/var/tmp/capivaraos-marsh-flat.ks \
#       --no-virt --resultdir=/var/tmp/capivaraos-marsh-result \
#       --project="CapivaraOS Marsh" --make-iso --iso-only \
#       --iso-name=CapivaraOS-Marsh-1.2.2-x86_64.iso \
#       --volid="CapivaraOS Marsh 1.2.2" --variant="CapivaraOS Marsh" \
#       --releasever=44
#
# NOTA: o anaconda resolve "%include caminho.ks" em relação ao seu próprio
# cwd (não ao diretório deste arquivo), por isso o ks-flatten.py acima é
# necessário — ver kickstart/ks-flatten.py.

%include upstream/fedora-live-kde-base.ks

# ── Repositório local com o RPM capivaraos-branding ─────────────────────────
# Gerado por ../build-all.sh (rpm/build-rpm.sh + createrepo_c) em
# /var/tmp/capivaraos-repo. Ajuste o caminho se mover o repositório local.
repo --name=capivaraos-local --baseurl=file:///var/tmp/capivaraos-repo

# ── RPM Fusion (free + nonfree) — codecs de mídia + base para GPU ────────────
# Habilitado na linha 2.x ("estação de dev"): resolve H.264/H.265/AAC/MP3 etc.
# de fábrica (sem isto o VLC/navegador tropeçam em conteúdo patenteado) e dá a
# base para a aceleração de GPU da IA local (akmod-nvidia). Os pacotes
# rpmfusion-*-release (em %packages) deixam estes repos habilitados no SISTEMA
# INSTALADO, para receber updates de codec pós-instalação. Ver FEAT-88.
repo --name=rpmfusion-free --baseurl=https://download1.rpmfusion.org/free/fedora/releases/$releasever/Everything/$basearch/os/
repo --name=rpmfusion-free-updates --baseurl=https://download1.rpmfusion.org/free/fedora/updates/$releasever/$basearch/
repo --name=rpmfusion-nonfree --baseurl=https://download1.rpmfusion.org/nonfree/fedora/releases/$releasever/Everything/$basearch/os/
repo --name=rpmfusion-nonfree-updates --baseurl=https://download1.rpmfusion.org/nonfree/fedora/updates/$releasever/$basearch/

# ── IDIOMA / TECLADO / FUSO (sobrescreve os defaults en_US do fedora-live-base) ─
# Equivalente ao "locales=pt_BR.UTF-8 keyboard-layouts=br" do live-build
# Debian. glibc-all-langpacks (incluso via fedora-live-base) já traz todos os
# locales prontos, então pt_BR e en_US ficam disponíveis para troca em
# Configurações do Sistema > Idiomas sem precisar gerar locales.
lang pt_BR.UTF-8
keyboard --xlayouts='br-abnt2' --vckeymap=br-abnt2
timezone America/Sao_Paulo --utc
network --hostname=capivaraos

# =============================================================================
# PACOTES — ver PACKAGES.md para o mapeamento Debian -> Fedora
# =============================================================================
%packages

# ── Identidade visual: usamos nosso próprio pacote de branding em vez do
# branding padrão do Fedora KDE (wallpapers, plymouth, sddm, os-release,
# tema "Sobre o Sistema" do Fedora). Ver rpm/capivaraos-branding.spec.
-fedora-release-kde-desktop
capivaraos-branding

# Tema Plymouth do CapivaraOS (capivaraos.script) é um tema "script": precisa
# do plugin script.so do plymouth para ser renderizado. Sem este pacote,
# /usr/lib64/plymouth/script.so não existe e o plymouthd cai num
# renderizador genérico (spinner simples em fundo preto, sem logo/texto),
# mesmo com plymouthd.conf apontando Theme=capivaraos corretamente.
plymouth-plugin-script

# Plasma Welcome genérico (sem branding Fedora) no lugar da variante
# plasma-welcome-fedora trazida por fedora-kde-common.ks
-plasma-welcome-fedora
plasma-welcome

# Estilo QQC2 do Breeze (100% QML). Usado APENAS pelo plasma-welcome, via o
# wrapper criado em capivaraos-post-branding.ks. Motivo: o ToolButton do
# qqc2-desktop-style (estilo padrao) desenha o rotulo do botao tambem no
# background, pelo QStyle; como o ApplicationIcon.qml do plasma-welcome
# substitui o contentItem por icone+titulo, o texto "Instalar CapivaraOS"
# aparecia DUAS vezes na tela de boas-vindas do live — a segunda por tras da
# capivara. O ToolButton do org.kde.breeze nao pinta rotulo no background.
qqc2-breeze-style

# Fedora Media Writer não é necessário e tem branding/conteúdo padrão do Fedora
-mediawriter

# ===== SISTEMA BASE (idioma) =====
langpacks-pt_BR
glibc-langpack-pt

# ===== OFFICE: tradução pt-BR do LibreOffice =====
libreoffice-langpack-pt-BR
libreoffice-help-pt-BR
libreoffice-kf6

# ===== INTERNET =====
# Thunderbird -> OPCIONAL/onboarding na linha 2.x (dev jovem usa webmail). FEAT-89.

# ===== MIDIA =====
vlc
# GIMP -> OPCIONAL/onboarding na linha 2.x (nichado num foco dev). FEAT-89.
# gwenview já incluso via @kde-media / @kde-apps

# ===== CODECS (RPM Fusion) — ver FEAT-88 =====
# Deixa os repos RPM Fusion habilitados no sistema instalado (traz as chaves
# GPG e os .repo → updates de codec pós-instalação):
rpmfusion-free-release
rpmfusion-nonfree-release
# Codecs completos de mídia (H.264/H.265/AAC/MP3/…). libavcodec-freeworld
# adiciona codecs ao ffmpeg-free do Fedora SEM trocar o pacote (coexiste):
gstreamer1-plugins-bad-freeworld
gstreamer1-plugins-ugly
gstreamer1-libav
libavcodec-freeworld

# ===== UTILITARIOS =====
gparted
htop
fastfetch
curl
wget
zip
unzip
rsync
# ark, kate, okular já inclusos via @kde-apps

# ===== DESENVOLVIMENTO =====
git
nano
vim-enhanced
@development-tools

# ===== ESTACAO DE DEV (linha 2.x) — pacotes do Fedora oficial. FEAT-89 =====
# NOTA: VSCodium, mise, starship e lazygit vêm de repos externos e sao
# instalados no %post (capivaraos-post-devstation.ks) com chave GPG explicita.
# Semgrep (pipx), extensao Continue (Open VSX) e Flathub tambem ficam no %post.
#
# -- Seguranca shift-left (SAST/segredos/deps) --
gitleaks
pre-commit
trivy
# -- IA local (runtime; modelo de codigo baixado sob demanda no onboarding) --
ollama
# -- Ambiente de desenvolvimento --
gh
podman
distrobox
# -- Gerenciador de senhas (pegada de seguranca) --
keepassxc
# -- Snapshots "atualize sem medo" (Btrfs nativo do Fedora) --
btrfs-assistant
snapper

# ===== FONTES =====
liberation-fonts
dejavu-fonts-all
google-noto-sans-fonts
google-noto-serif-fonts
google-noto-emoji-fonts

# ===== IMPRESSAO =====
cups
system-config-printer

# ===== TEMA MACOS (WHITESUR) — dependências para o post-script de tema =====
sassc
optipng
gtk-murrine-engine
gtk2-engines
ImageMagick

%end

# =============================================================================
# Post-scripts específicos do CapivaraOS
# =============================================================================
%include capivaraos-post-branding.ks
%include capivaraos-post-theme.ks
