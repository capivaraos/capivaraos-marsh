# capivaraos-branding — identidade visual do CapivaraOS Marsh (Fedora)
#
# Reimplementa em formato RPM o que os hooks do live-build faziam no
# CapivaraOS Marsh (Debian):
#   - 0010-wallpaper.hook.chroot  -> wallpapers, pacotes de wallpaper KDE,
#                                     script de aplicação no primeiro login
#   - 0020-desktop.hook.chroot    -> os-release, issue, plymouth, ícones
#                                     "Sobre o sistema", avatar, layout macOS
#
# A identidade visual (cores, Aurorae, tema Plasma e GTK) e 100% propria e vive
# NESTE pacote — nao ha mais tema de terceiros. O antigo kickstart/
# capivaraos-post-theme.ks (que baixava o WhiteSur por git clone) foi aposentado
# na frente D, D5 (FEAT-91): o build nao depende mais de rede para o tema.

Name:           capivaraos-branding
Version:        2.0.0
# Sufixo ".marsh": as tres spins constroem um pacote com este MESMO Name e
# compartilham ~/rpmbuild, entao sem ele duas spins na mesma Version-Release
# geram nomes de arquivo identicos -- ja causou dois incidentes (ver BUG-30).
# Com o sufixo a colisao e impossivel por construcao.
Release:        0.50.alpha50%{?dist}.marsh
Summary:        Identidade visual, wallpapers e tema padrão do CapivaraOS Marsh

License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark AND OFL-1.1
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick
# /usr/bin/convert
Requires:       plymouth
Requires:       sddm
Requires:       kde-settings

# Fornecemos nosso próprio /etc/os-release, ícones "Sobre o Sistema" e
# wallpapers padrão do Fedora KDE.
Conflicts:      fedora-release-kde-desktop
Conflicts:      fedora-logos

%description
Pacote de identidade visual do CapivaraOS Marsh: wallpapers exclusivos da
marca, conjunto de ícones
"capivaraos-logo", "capivaraos-full-logo" e "capivaraos-head", tema Plymouth
de boot, tela de login SDDM, /etc/os-release, /etc/issue, configuração padrão do Plasma
(Breeze Dark + wallpaper CapivaraOS) e o layout de painéis estilo macOS
(menu global no topo + dock inferior).

%prep
%setup -q

%build
set -e

# ── 1. Ícones hicolor "capivaraos-logo" (apenas a capivara, sem texto) ──────
# Fonte: icons/capivaraos-logo.png (1536x1024)
mkdir -p build/icons
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert icons/capivaraos-logo.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png"
done

# ── 2. Ícones hicolor "capivaraos-full-logo" (capivara + texto "CapivaraOS") ─
# Usado pelo KCM "Sobre este Sistema" (LOGO= em /etc/os-release).
# Fonte: backgrounds/CapivaraOS_Logo.png (1536x1024) ajustada para canvas
# quadrado transparente antes do resize, evitando distorção.
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert backgrounds/CapivaraOS_Logo.png -background none -gravity center \
        -extent 1536x1536 -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png"
done

# ── 2b. Ícone "capivaraos-head" (só a cabeça) — SIMBÓLICO/ADAPTÁVEL ──────────
# Ícone do lançador de aplicativos (kickoff) no dock, no lugar do logo do KDE.
# Agora é um SVG MONOCROMÁTICO simbólico (classe ColorScheme-Text), que o Plasma
# RECOLORE pelo tema: ESCURO no tema claro, CLARO no escuro — visível nos dois.
# Antes era PNG branco, que sumia no Breeze claro (painel claro). Fonte vetorial:
# icons/capivaraos-head.svg (traçada da silhueta com potrace; cor padrão CLARA
# #eff0f1 como rede de segurança: se o Plasma não recolorir, fica claro = visível
# no nosso painel escuro padrão, sem regressão). Instalado como 'scalable' em
# %install — o scalable serve todos os tamanhos no hicolor. O PNG
# icons/capivaraos-head.png continua existindo como FONTE do avatar (abaixo).

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
convert icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): capivara BRANCA sobre fundo AZUL-MARINHO ────────
# Decisao do dono (2026-09-23, de-green): avatar do usuario/greeter = fundo navy
# #1E2F4E (o azul-marinho da logo do CapivaraOS) + capivara branca, no lugar do
# verde. Recorta so a capivara da arte-mestre, pinta de branco (colorize
# preservando o alfa) e poe sobre quadrado navy. Exibido em circulo pelo greeter
# -> o quadrado navy preenche. Sem o texto "CapivaraOS" (seria cortado no circulo)
# -- mesmo estilo "so capivara" do avatar anterior, so trocando verde por navy.
convert backgrounds/CapivaraOS_Logo.png -crop 1536x600+0+0 +repage -trim +repage \
    -colorspace sRGB -fill white -colorize 100% \
    -gravity center -background '#1E2F4E' -extent 1700x1700 \
    -resize 256x256 build/pixmaps/capivaraos-face.png

# ── 5. Logo BRANCA para o splash do Plymouth (boot/desligamento) ────────────
mkdir -p build/plymouth
convert backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -resize 320x320 build/plymouth/logo.png

# ── 5b. Logo BRANCA (nome+capivara) para a sidebar do instalador (FEAT-104) ──
# Mesmo truque do Plymouth: colorize 100% branco preservando o alfa. -trim tira
# a moldura transparente; largura 200 cabe na sidebar do Anaconda (~230px).
mkdir -p build/anaconda
convert backgrounds/CapivaraOS_Logo.png -fill white -colorize 100% \
    -trim +repage -resize 200x build/anaconda/sidebar-logo.png

# ── 5c. Logo (cabeca da capivara) para o branding do Cockpit / Anaconda WebUI ─
# Em Fedora 44 o instalador grafico REAL da ISO live e o Anaconda WebUI
# (Cockpit/PatternFly), NAO o GTK -- por isso o custom_stylesheet GTK abaixo nao
# pinta a tela (fica azul). O Cockpit escolhe a pasta
# /usr/share/cockpit/branding/<ID do os-release> (cai p/ ID_LIKE=fedora se nao
# existir), entao criamos "capivaraos". A cabeca (215x215, quadrada) preenche a
# caixa da .logo; a silhueta larga da logo completa ficaria achatada. Mesmo
# mecanismo ja usado em Pup/Snout.
mkdir -p build/cockpit
# BRANCA: o Anaconda WebUI aplica na .logo um filter:invert(1) grayscale(1)
# brightness(2.5) + mix-blend-mode:screen (feito para a logo SVG do Fedora). Uma
# silhueta branca vira preta e some no screen; por isso anulamos esse filtro no
# branding.css (bloco do Cockpit no %install) E entregamos a logo ja em branco,
# para ela aparecer no header verde.
convert icons/capivaraos-head.png -colorspace sRGB -fill white -colorize 100% \
    -resize 256x256 build/cockpit/logo.png
convert build/cockpit/logo.png -resize 32x32 build/cockpit/favicon.ico

# ── Wallpaper padrao do sistema (default.jxl) = luar ────────────────────────
# O /usr/share/backgrounds/default.jxl (desktop-backgrounds-compat) e o "mapa 3D"
# que o Plasma usa como fundo da TELA DE BLOQUEIO (e fallback de varios lugares).
# Geramos a versao JXL do luar para sobrescreve-lo no %posttrans, deixando o
# wallpaper padrao do sistema com a marca. (magick tem suporte a escrever JXL.)
mkdir -p build/backgrounds
convert backgrounds/capivaraos-wp-moonlight.png build/backgrounds/capivaraos-default.jxl

# ── Fundo do greeter do SDDM em Full HD (1920x1080) ─────────────────────────
# A arte-fonte do luar e 4K (3840x2160). O plasma-login-greeter roda ANTES do
# login e inicializa o proprio contexto GL; em VMs/GL degradado (ex.: ZINK sem
# Vulkan) uma textura 3840 de largura estoura o GL_MAX_TEXTURE_SIZE do driver e
# o fundo sai PRETO (a UI, com texturas pequenas, ainda aparece). A tela de
# bloqueio funciona por rodar DENTRO da sessao, com GL ja inicializado. Damos ao
# greeter uma versao 1920x1080, que cabe no limite mesmo com GL fraco.
convert backgrounds/capivaraos-wp-moonlight.png -resize 1920x1080 \
    build/backgrounds/capivaraos-sddm-1080.png

# Spinner BRANCO padrao (arco girando) exibido logo abaixo da logo no splash --
# igual ao Pup e ao Snout. Decisao do dono (2026-09-22, "muito verde"): a rodinha
# volta ao branco (antes era verde #15B22C). A logo ja era branca.
# Geramos 30 quadros, cada um girado 12°, e o script do Plymouth os cicla.
mkdir -p build/plymouth/spinner
convert -size 64x64 xc:none -stroke white -strokewidth 5 \
    -fill none -draw "stroke-linecap round arc 12,12 52,52 0,300" \
    build/plymouth/spinner-base.png
for i in $(seq 0 29); do
    ANG=$(( i * 12 ))
    convert build/plymouth/spinner-base.png -background none \
        -distort SRT ${ANG} +repage "build/plymouth/spinner/${i}.png"
done

# ── 6. Pacotes de wallpaper no formato KDE (aparecem no seletor do Plasma) ──
# Cada wallpaper "capivaraos-*" do live-build vira um pacote
# /usr/share/wallpapers/<id>/{metadata.json,contents/images/*.png}
mkdir -p build/wallpapers

create_kde_wallpaper_pkg() {
    local ID="$1" NAME="$2" FILE="$3" AUTHOR="${4:-CapivaraOS}" LICENSE="${5:-LicenseRef-CapivaraOS-Trademark}"
    local DIR="build/wallpapers/${ID}/contents/images"
    mkdir -p "$DIR"
    cp "$FILE" "${DIR}/1920x1080.png"
    convert "$FILE" -resize 400x250 "${DIR}/400x250.png" 2>/dev/null || \
        cp "$FILE" "${DIR}/400x250.png"
    cat > "build/wallpapers/${ID}/metadata.json" << METAEOF
{
    "KPlugin": {
        "Authors": [{"Name": "${AUTHOR}"}],
        "Id": "${ID}",
        "License": "${LICENSE}",
        "Name": "${NAME}",
        "Version": "%{version}",
        "Website": "https://capivaraos.org"
    },
    "X-KDE-PluginInfo-Name": "${ID}"
}
METAEOF
}

# Wallpapers EXCLUSIVOS da marca CapivaraOS (linha 2.x, FEAT-105). Todos usam o
# LICENSE default da funcao (LicenseRef-CapivaraOS-Trademark) -- arte propria,
# NAO CC. As antigas (7 de cor solida + 6 fotos CC do Wikimedia) foram removidas:
# o conjunto do Marsh 2.x passa a ser exatamente estes 9. As 3 cenas (luar/por-do-
# sol/dev) levam a logo branca padronizada no canto; as abstratas ja trazem a
# marca no proprio desenho; o "serie2" e o hero de marca da linha 2.0.
create_kde_wallpaper_pkg "capivaraos-luar"       "CapivaraOS Luar"       backgrounds/capivaraos-wp-moonlight.png
create_kde_wallpaper_pkg "capivaraos-por-do-sol" "CapivaraOS Pôr do Sol" backgrounds/capivaraos-wp-sunset.png
create_kde_wallpaper_pkg "capivaraos-dev"        "CapivaraOS Dev"        backgrounds/capivaraos-wp-dev.png
create_kde_wallpaper_pkg "capivaraos-abstrato-1" "CapivaraOS Abstrato 1" backgrounds/capivaraos-wp-abstract-1.png
create_kde_wallpaper_pkg "capivaraos-abstrato-2" "CapivaraOS Abstrato 2" backgrounds/capivaraos-wp-abstract-2.png
create_kde_wallpaper_pkg "capivaraos-abstrato-3" "CapivaraOS Abstrato 3" backgrounds/capivaraos-wp-abstract-3.png
create_kde_wallpaper_pkg "capivaraos-abstrato-4" "CapivaraOS Abstrato 4" backgrounds/capivaraos-wp-abstract-4.png
create_kde_wallpaper_pkg "capivaraos-comics"     "CapivaraOS Comics"     backgrounds/capivaraos-wp-comics.png
# Hero da Série 2 (capivara + "2" de circuito + "CapivaraOS"). Asset comum as 3
# spins, criado no Pup 2.x e propagado (ver project_brand_assets_2x). 3840x2160.
create_kde_wallpaper_pkg "capivaraos-serie2"     "CapivaraOS Série 2"    backgrounds/capivaraos-wp-serie2.png

%install
set -e
# O wallpaper padrao (luar) mora APENAS dentro do pacote KDE, nao mais como
# arquivo solto em backgrounds/ -- ver a nota no bloco de wallpapers abaixo.
# DEFAULT_WP_PKG: diretorio do pacote (forma canonica do org.kde.image, casa o
# item "CapivaraOS Luar" no seletor). DEFAULT_WP_IMG: arquivo de imagem dentro
# do pacote (para consumidores que querem um caminho de arquivo: SDDM, script).
DEFAULT_WP_PKG=%{_datadir}/wallpapers/capivaraos-luar
DEFAULT_WP_IMG=%{_datadir}/wallpapers/capivaraos-luar/contents/images/1920x1080.png

# ── FiraCode Nerd Font Mono (Regular+Bold) — fonte de codigo com iconos para
#    terminal/starship/lazygit (linha 2.x, FEAT-89). Licenca OFL. O trigger de
#    arquivo do fontconfig do Fedora reconstroi o cache ao instalar em
#    %{_datadir}/fonts, entao nao precisa de fc-cache manual. ─────────────────
install -d %{buildroot}%{_datadir}/fonts/capivaraos-firacode-nerd
install -m0644 fonts/FiraCodeNerdFontMono-Regular.ttf fonts/FiraCodeNerdFontMono-Bold.ttf \
    %{buildroot}%{_datadir}/fonts/capivaraos-firacode-nerd/

# ── Wallpapers ──────────────────────────────────────────────────────────────
# Os 9 wallpapers da marca sao instalados APENAS como pacotes KDE (bloco
# "Pacotes de wallpaper KDE" abaixo), em %{_datadir}/wallpapers/capivaraos-*/.
# NAO instalamos mais os arquivos soltos em %{_datadir}/backgrounds/capivaraos/:
# (1) o seletor do Plasma lista TANTO os pacotes KDE (com nome bonito, ex.
#     "CapivaraOS Luar") QUANTO os arquivos soltos (pelo nome do arquivo, ex.
#     "capivaraos-wp-moonlight") -> cada wallpaper aparecia DUPLICADO no seletor.
# (2) o arquivo solto era uma copia identica da imagem que ja vai dentro do
#     pacote (contents/images/1920x1080.png) -> ~69 MB duplicados no sistema.
# Eliminando os soltos, cada wallpaper aparece 1x (o pacote) e some a duplicata,
# mantendo os 9 do CapivaraOS + os wallpapers padrao do KDE. Login/bloqueio/
# desktop/SDDM apontam para a imagem DENTRO do pacote (DEFAULT_WP_PKG/IMG).
# A arte-mestre backgrounds/CapivaraOS_Logo.png nunca foi wallpaper (e a fonte
# 1536x1024 dos icones/plymouth) e continua fora do sistema instalado.

# ── Pixmaps ──────────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/pixmaps
install -m 0644 icons/capivaraos.png %{buildroot}%{_datadir}/pixmaps/capivaraos.png
install -m 0644 icons/capivaraos-logo.png %{buildroot}%{_datadir}/pixmaps/capivaraos-logo.png
install -m 0644 build/pixmaps/capivaraos-white.png %{buildroot}%{_datadir}/pixmaps/capivaraos-white.png

# ── Icones hicolor ───────────────────────────────────────────────────────────
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    install -d %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-full-logo.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# Ícone do lançador (kickoff) = SVG SIMBÓLICO adaptável, instalado só em 'scalable'
# (o scalable serve todos os tamanhos no hicolor; o Plasma recolore pelo tema).
# Substitui os PNGs brancos da cabeça. Ver a nota em %build (seção 2b).
install -d %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -m 0644 icons/capivaraos-head.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/capivaraos-head.svg

# ── Pacotes de wallpaper KDE ─────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/wallpapers
cp -r build/wallpapers/* %{buildroot}%{_datadir}/wallpapers/
find %{buildroot}%{_datadir}/wallpapers -type f -exec chmod 0644 {} \;
find %{buildroot}%{_datadir}/wallpapers -type d -exec chmod 0755 {} \;

# ── Esquema de cores próprio do CapivaraOS (FEAT-91 frente D, D1) ────────────
# Paleta verde da marca (accent #15B22C + neutros escuros ~#12160F). Substitui de
# vez o esquema de cores do WhiteSur. Selecionado em kdeglobals
# (ColorScheme=CapivaraOS) pelo /etc/skel abaixo e pelo /etc/xdg (%posttrans, p/
# a sessao LIVE). Ver docs/REVERT-CORES-VERDE.md.
install -d %{buildroot}%{_datadir}/color-schemes
install -m 0644 color-schemes/CapivaraOS.colors \
    %{buildroot}%{_datadir}/color-schemes/CapivaraOS.colors

# ── Decoração de janela própria (Aurorae) do CapivaraOS (FEAT-91 frente D, D3) ─
# Titlebar da paleta + cantos arredondados + botões círculos coloridos da marca.
# Selecionada via /etc/xdg/kwinrc (theme=__aurorae__svg__CapivaraOS, %posttrans).
# Ver docs/BRIEF-TEMA-CAPIVARAOS.md.
install -d %{buildroot}%{_datadir}/aurorae/themes/CapivaraOS
install -m 0644 aurorae/CapivaraOS/* \
    %{buildroot}%{_datadir}/aurorae/themes/CapivaraOS/

# ── Tema Plasma próprio (desktoptheme) do CapivaraOS (FEAT-91 frente D, D4) ────
# Formas próprias do Plasma: fundo do painel (a "cara" da barra), fundo de
# menus/plasmoides/diálogos e balão de dica — nine-patch FrameSvg na paleta
# verde. O arquivo "colors" replica o esquema CapivaraOS, então TODO widget que
# não redesenhamos (botão, slider, etc.) cai no Breeze recolorido na NOSSA
# paleta. Selecionado em plasmarc [Theme] name=CapivaraOS pelo /etc/skel abaixo e
# pelo /etc/xdg/plasmarc (%posttrans, p/ a sessao LIVE). Ver docs/BRIEF-TEMA-CAPIVARAOS.md.
install -d %{buildroot}%{_datadir}/plasma/desktoptheme/CapivaraOS
cp -r plasma/CapivaraOS/. %{buildroot}%{_datadir}/plasma/desktoptheme/CapivaraOS/
find %{buildroot}%{_datadir}/plasma/desktoptheme/CapivaraOS -type d -exec chmod 0755 {} \;
find %{buildroot}%{_datadir}/plasma/desktoptheme/CapivaraOS -type f -exec chmod 0644 {} \;

# ── Konsole: esquema de cores + perfil padrão do CapivaraOS (FEAT-91 frente D) ─
# Terminal na paleta verde da marca (identidade "estação de dev"). O perfil usa
# o esquema CapivaraOS e a FiraCode Nerd Font (já instalada por este pacote). O
# perfil padrão é apontado no /etc/skel/.config/konsolerc abaixo.
install -d %{buildroot}%{_datadir}/konsole
install -m 0644 konsole/CapivaraOS.colorscheme \
    %{buildroot}%{_datadir}/konsole/CapivaraOS.colorscheme
install -m 0644 konsole/CapivaraOS.profile \
    %{buildroot}%{_datadir}/konsole/CapivaraOS.profile

# ── Config GTK: Adwaita-dark + accent verde da marca (FEAT-91 frente D, D5) ────
# Apps GTK/libadwaita usam o tema NATIVO Adwaita-dark (in-box) com o verde da
# marca (#15B22C) injetado como accent (gtk.css), casando com o accent do Plasma.
# Isso APOSENTA o tema GTK do WhiteSur, que antes era baixado por git no
# capivaraos-post-theme.ks — agora nao ha mais dependencia de rede/terceiros no
# tema. Gravado em /etc/skel (usuarios novos = sistema instalado) E em /etc/xdg
# (padrao do sistema, lido na sessao LIVE, que nao herda /etc/skel de forma
# confiavel — mesmo motivo do bloco /etc/xdg do %posttrans).
for GDIR in %{buildroot}%{_sysconfdir}/skel/.config %{buildroot}%{_sysconfdir}/xdg; do
    install -d "$GDIR/gtk-3.0" "$GDIR/gtk-4.0"
    install -m 0644 gtk/settings.ini "$GDIR/gtk-3.0/settings.ini"
    install -m 0644 gtk/settings.ini "$GDIR/gtk-4.0/settings.ini"
    install -m 0644 gtk/gtk.css      "$GDIR/gtk-3.0/gtk.css"
    install -m 0644 gtk/gtk.css      "$GDIR/gtk-4.0/gtk.css"
done
# GTK2 legado (poucos apps): so no skel do usuario.
install -d %{buildroot}%{_sysconfdir}/skel
install -m 0644 gtk/gtkrc-2.0 %{buildroot}%{_sysconfdir}/skel/.gtkrc-2.0

# ── Logo próprio do fastfetch (FEAT-136 / FEAT-50) ────────────────────────────
# O fastfetch mostra o logo ASCII do Fedora (escolhido por ID_LIKE do os-release).
# Trocamos pela cabeça de capivara da marca + "CapivaraOS" em verde. A arte vai
# em /usr/share/capivaraos/fastfetch/ (coberta por %{_datadir}/capivaraos/) e o
# config.jsonc (só o LOGO, sem mexer nos módulos) em /etc/skel E /etc/xdg — este
# ultimo p/ valer na sessao LIVE (fastfetch le XDG_CONFIG_DIRS=/etc/xdg).
install -d %{buildroot}%{_datadir}/capivaraos/fastfetch
install -m 0644 fastfetch/capivara.txt %{buildroot}%{_datadir}/capivaraos/fastfetch/capivara.txt
for FDIR in %{buildroot}%{_sysconfdir}/skel/.config %{buildroot}%{_sysconfdir}/xdg; do
    install -d "$FDIR/fastfetch"
    install -m 0644 fastfetch/config.jsonc "$FDIR/fastfetch/config.jsonc"
done

# ── Tema Plymouth ────────────────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos
install -m 0644 build/plymouth/logo.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/logo.png

# Quadros do spinner (arco branco girando)
install -d %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner
install -m 0644 build/plymouth/spinner/*.png \
    %{buildroot}%{_datadir}/plymouth/themes/capivaraos/spinner/

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.plymouth << 'EOF'
[Plymouth Theme]
Name=CapivaraOS
Description=CapivaraOS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/capivaraos
ScriptFile=/usr/share/plymouth/themes/capivaraos/capivaraos.script
EOF

cat > %{buildroot}%{_datadir}/plymouth/themes/capivaraos/capivaraos.script << 'EOF'
# Fundo = azul-escuro neutro (mesmo do Pup e do Snout), no lugar do verde-escuro
# antigo (#12160F). Decisao do dono (2026-09-22, "muito verde").
Window.SetBackgroundTopColor(0.07, 0.09, 0.13);
Window.SetBackgroundBottomColor(0.07, 0.09, 0.13);

# ── Logo branca (acima do spinner) ──────────────────────────────────────────
logo.image = Image("logo.png");
logo.sprite = Sprite(logo.image);
logo.x = Window.GetWidth() / 2 - logo.image.GetWidth() / 2;
logo.y = Window.GetHeight() / 2 - logo.image.GetHeight() / 2 - 80;
logo.sprite.SetPosition(logo.x, logo.y, 1);

# ── Spinner (arco branco girando, logo abaixo da logo) ──────────────────────
spinner_frame_count = 30;
for (i = 0; i < spinner_frame_count; i++)
    spinner_image[i] = Image("spinner/" + i + ".png");

spinner.sprite = Sprite();
spinner.cx = Window.GetWidth() / 2;
spinner.cy = logo.y + logo.image.GetHeight() + 50;
spinner.frame = 0;

# ── Mensagem (abaixo do spinner) ────────────────────────────────────────────
# "updates"/"system-upgrade": modo usado pelo PackageKit/Discover ao reiniciar
# para aplicar atualizacoes offline (systemd system-update.target). Sem essa
# checagem, esse boot mostraria a mesma mensagem de inicializacao normal.
is_updates = (Plymouth.GetMode() == "updates" || Plymouth.GetMode() == "system-upgrade");

if (Plymouth.GetMode() == "shutdown" || Plymouth.GetMode() == "reboot") {
    message_text = "Encerrando o CapivaraOS";
} else if (is_updates) {
    message_text = "Instalando atualizações";
} else {
    message_text = "Inicializando o CapivaraOS";
}

message.image = Image.Text(message_text, 1, 1, 1, 1, "Sans 14");
message.sprite = Sprite(message.image);
message.sprite.SetPosition(Window.GetWidth() / 2 - message.image.GetWidth() / 2,
                            spinner.cy + 70, 1);

# ── Aviso + percentual, somente durante atualizacao offline ────────────────
if (is_updates) {
    warning.image = Image.Text("Não desligue o computador", 0.8, 0.8, 0.8, 1, "Sans 11");
    warning.sprite = Sprite(warning.image);
    warning.sprite.SetPosition(Window.GetWidth() / 2 - warning.image.GetWidth() / 2,
                                spinner.cy + 95, 1);

    # PackageKit/Discover reporta o progresso via "plymouth system-update
    # --progress=N" (N de 0 a 100) enquanto instala os pacotes baixados.
    fun system_update_callback(progress) {
        percent.image = Image.Text(Math.Int(progress) + "%", 1, 1, 1, 1, "Sans 11");
        if (percent.sprite)
            percent.sprite.SetImage(percent.image);
        else
            percent.sprite = Sprite(percent.image);
        percent.sprite.SetPosition(Window.GetWidth() / 2 - percent.image.GetWidth() / 2,
                                    spinner.cy + 118, 1);
    }
    Plymouth.SetSystemUpdateFunction(system_update_callback);
}

fun refresh_callback() {
    spinner.frame++;
    if (spinner.frame >= spinner_frame_count * 3)
        spinner.frame = 0;
    idx = Math.Int(spinner.frame / 3);
    img = spinner_image[idx];
    spinner.sprite.SetImage(img);
    spinner.sprite.SetX(spinner.cx - img.GetWidth() / 2);
    spinner.sprite.SetY(spinner.cy - img.GetHeight() / 2);
}
Plymouth.SetRefreshFunction(refresh_callback);
EOF

# NOTA CapivaraOS: /etc/os-release, /etc/issue, /etc/issue.net e
# /etc/xdg/kcm-about-distrorc NAO sao gerados aqui (em %{buildroot}). Esses
# caminhos tambem pertencem a fedora-release-common e kde-settings, e tê-los
# em %files causa "conflito de arquivo" no dnf durante a transacao de
# instalacao (PayloadInstallationError). Em vez disso, sao escritos
# diretamente no sistema instalado em %posttrans (ver abaixo), que roda
# depois de toda a transacao e garante que nosso conteudo prevaleca.

# ── /etc/skel: wallpaper, tela de bloqueio e tema padrão (Breeze Dark) ──────
install -d %{buildroot}%{_sysconfdir}/skel/.config

cat > %{buildroot}%{_sysconfdir}/skel/.config/plasma-org.kde.plasma.desktop-appletsrc << EOF
[Containments][1][Wallpaper][org.kde.image][General]
Image=${DEFAULT_WP_PKG}
FillMode=2
EOF

# Tela de bloqueio: usa o CAMINHO DE ARQUIVO (nao o diretorio do pacote). O
# desktop (appletsrc acima) usa o diretorio do pacote porque o script
# capivaraos-set-wallpaper o reaplica via plasma-apply-wallpaperimage; a tela de
# bloqueio NAO tem script, entao precisa de um valor que renderize sozinho. Alem
# disso, o default.jxl do sistema tambem e trocado pelo luar no %posttrans (o
# lock cai nele quando nao ha wallpaper proprio) -- cinto e suspensorio.
cat > %{buildroot}%{_sysconfdir}/skel/.config/kscreenlockerrc << EOF
[Greeter][Wallpaper][org.kde.image][General]
Image=${DEFAULT_WP_IMG}
FillMode=2
EOF

# Konsole: perfil padrão = CapivaraOS (esquema de cores verde da marca).
cat > %{buildroot}%{_sysconfdir}/skel/.config/konsolerc << 'EOF'
[Desktop Entry]
DefaultProfile=CapivaraOS.profile
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/kdeglobals << 'EOF'
[General]
# ESQUEMA DE CORES = AZUL PADRAO (Breeze Dark). Decisao do dono (2026-09-22):
# "muito verde" -> o esquema/accent voltam ao azul padrao (botoes, selecao, cor
# de pasta). O esquema verde proprio (CapivaraOS.colors) continua INSTALADO e
# selecionavel em Aparencia > Cores -- so deixa de ser o padrao. O tema Plasma
# (painel/menus), a decoracao Aurorae e o Konsole SEGUEM verdes (escopo do dono:
# so cores/accent). Ver docs/REVERT-CORES-VERDE.md.
ColorScheme=BreezeDark
# Sem AccentColor proprio -> o accent segue o azul padrao do esquema.
# accentColorFromWallpaper=false garante o azul (senao viria do wallpaper, que e
# esverdeado).
accentColorFromWallpaper=false

[KDE]
# Tema Global = o nosso Look-and-Feel org.capivaraos.desktop (PROD-130), para que
# "CapivaraOS" apareca como o tema ATIVO em Aparencia (no lugar de "Breeze Dark").
# O usuario pode trocar para Breeze e voltar quando quiser (nao bloqueia nada).
LookAndFeelPackage=org.capivaraos.desktop
SingleClick=false

[Icons]
# Icones oficiais Breeze Dark do KDE (sem icones estilo Apple do WhiteSur).
Theme=breeze-dark

[KSplash]
Theme=None
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/plasmarc << 'EOF'
[Theme]
# TEMA PLASMA = Breeze padrao (default). Decisao do dono (2026-09-23): tirar o
# verde do painel/menus tambem. O tema Plasma proprio CapivaraOS continua
# INSTALADO em /usr/share/plasma/desktoptheme/CapivaraOS e selecionavel em
# Aparencia > Tema do Plasma -- so deixa de ser o padrao (nao-destrutivo). A
# decoracao de janela (Aurorae) e o Konsole SEGUEM verdes (escopo do dono).
name=default
EOF

# Desativa o assistente de primeiro boot do Plasma (plasma-welcome / tela
# "Bem-vindo ao Plasma Desktop"). O fundo dessa tela é compilado no binário do
# plasma-welcome (não é personalizável para a identidade do CapivaraOS) e a
# tela é disparada pelo módulo KDED, não pelo autostart. Pré-gravar um
# LastSeenVersion alto faz o plasma-welcome considerar que o usuário já viu a
# apresentação, então o OOBE não aparece para novos usuários (sistema
# instalado). Na sessão live o livesys-kde escreve seu próprio plasma-welcomerc
# (LiveEnvironment=true), então este valor só afeta o sistema instalado.
# IMPORTANTE: a chave é "LastSeenVersion" (com L/S/V maiúsculos) -- é o nome
# exato lido pelo kded_plasma_welcome (confirmado via strings do binário). A
# variante "lastSeenVersion" (camelCase) é IGNORADA, e o módulo trata isso
# como "sem versão vista", disparando a tela de boas-vindas mesmo assim.
cat > %{buildroot}%{_sysconfdir}/skel/.config/plasma-welcomerc << 'EOF'
[General]
LastSeenVersion=99.0.0
EOF

# ── Avatar padrão (.face) para novos usuários ────────────────────────────────
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_sysconfdir}/skel/.face
ln -sf .face %{buildroot}%{_sysconfdir}/skel/.face.icon
# Copia legivel-por-todos da face, num caminho do SISTEMA. O ~/.face do skel nao
# basta para o avatar do SDDM: a home e 0700, entao o processo do SDDM (outro
# usuario) nao consegue le-lo -> aparece o icone generico (FEAT-102). O script
# capivaraos-set-avatar (abaixo) registra ESTE arquivo no AccountsService, cujo
# daemon (root) o copia para /var/lib/AccountsService/icons/<user>, que o SDDM le.
install -d %{buildroot}%{_datadir}/capivaraos
install -m 0644 build/pixmaps/capivaraos-face.png %{buildroot}%{_datadir}/capivaraos/capivaraos-face.png
# JXL do luar (usado no %posttrans para sobrescrever o default.jxl do sistema)
install -m 0644 build/backgrounds/capivaraos-default.jxl %{buildroot}%{_datadir}/capivaraos/capivaraos-default.jxl
# Fundo 1920x1080 do greeter do SDDM (evita textura 4K que fica preta em GL fraco)
install -m 0644 build/backgrounds/capivaraos-sddm-1080.png %{buildroot}%{_datadir}/capivaraos/sddm-background.png

# ── Layout estilo macOS: script JS do Plasma + autostarts de aplicação única ─
install -d %{buildroot}%{_datadir}/capivaraos
cat > %{buildroot}%{_datadir}/capivaraos/macos-layout.js << 'EOF'
// Remove quaisquer paineis existentes (layout padrao do Plasma / Look and Feel)
var ids = panelIds;
for (var i = 0; i < ids.length; i++) {
    panelById(ids[i]).remove();
}

// ── Painel superior (menu global estilo macOS) ──────────────────────────────
var topPanel = new Panel();
topPanel.location = "top";
topPanel.height = 28;
// Flutuante + translucido, para combinar com o dock inferior (visual
// "barra flutuante" do macOS, com a mesma transparencia nos dois paineis).
topPanel.floating = true;
topPanel.opacityMode = 2; // Panel.Global.Translucent

topPanel.addWidget("org.kde.plasma.appmenu");
topPanel.addWidget("org.kde.plasma.panelspacer");

// Previsao do tempo (widget proprio, do kdeplasma-addons)
var weather = topPanel.addWidget("org.kde.plasma.weather");
// Aparencia: temperatura ao lado do icone do widget; dica (tooltip) mostra
// temperatura, vento e umidade, mas nao a pressao.
weather.currentConfigGroup = ["Appearance"];
weather.writeConfig("showTemperatureInCompactMode", true);
weather.writeConfig("showTemperatureInBadge", false);
weather.writeConfig("showTemperatureInTooltip", true);
weather.writeConfig("showWindInTooltip", true);
weather.writeConfig("showPressureInTooltip", false);
weather.writeConfig("showHumidityInTooltip", true);

// Bandeja do sistema: mostra volume, redes, layout de teclado, notificacoes
// e o medidor de bateria (FEAT-128); os demais itens ficam recolhidos
// (showAllItems=false) e os mais comuns sao explicitamente ocultados.
// A bateria fica em shownItems (sempre visivel) para aparecer por padrao no
// notebook independentemente do nivel de carga — o "shown when relevant" a
// esconderia quando a carga estivesse cheia/na tomada. Em desktop sem bateria,
// o applet "Energia e bateria" ainda serve de atalho de perfil de energia.
var systray = topPanel.addWidget("org.kde.plasma.systemtray");
systray.currentConfigGroup = ["General"];
systray.writeConfig("showAllItems", false);
// shownItems / hiddenItems sao StringList -> precisam ser ARRAYS JS (idem
// launchers do dock; string com virgulas nao funciona).
systray.writeConfig("shownItems", [
    "org.kde.plasma.battery",
    "org.kde.plasma.volume",
    "org.kde.plasma.networkmanagement",
    "org.kde.plasma.keyboardlayout",
    "org.kde.plasma.notifications"
]);
systray.writeConfig("hiddenItems", [
    "org.kde.plasma.brightness",
    "org.kde.plasma.clipboard",
    "org.kde.plasma.devicenotifier",
    "org.kde.plasma.bluetooth",
    "org.kde.plasma.mediacontroller",
    "org.kde.kscreen",
    "org.kde.plasma.printmanager"
]);

// Encerramento de sessao / bloquear tela
topPanel.addWidget("org.kde.plasma.lock_logout");
// Hora e data
topPanel.addWidget("org.kde.plasma.digitalclock");

// ── Dock inferior estilo macOS ──────────────────────────────────────────────
var dock = new Panel();
dock.location = "bottom";
dock.height = 64;
dock.alignment = "center";
dock.lengthMode = "fit";
// Flutuante + translucido, igual ao painel superior (visual "dock" do
// macOS, com a mesma transparencia em ambos os paineis).
dock.floating = true;
dock.opacityMode = 2; // Panel.Global.Translucent
dock.hiding = "none";

// Lancador de aplicativos (mantido). O icone padrao e o logo do KDE
// ("start-here-kde-symbolic"); trocamos pela cabeca da capivara da nossa
// logo (icone hicolor "capivaraos-head", instalado por este pacote).
var kickoff = dock.addWidget("org.kde.plasma.kickoff");
kickoff.currentConfigGroup = ["General"];
kickoff.writeConfig("icon", "capivaraos-head");

// Aplicativos fixados no dock, na ordem pedida (esquerda -> direita), FEAT-103:
// Configuracoes, Discover, Firefox, Konsole, Dolphin, VLC, Spectacle, KeePassXC,
// KAddressBook, KCalc, LibreOffice. Alpaca (cliente Ollama) NAO entra: o Ollama
// passou a OPCIONAL (instalado pelo onboarding) em 2026-08-21, entao pre-fixar o
// cliente deixaria um icone quebrado no sistema recem-instalado. Spotify tambem
// ficou de fora (descartado). IDs .desktop do Fedora 44: KeePassXC =
// org.keepassxc.KeePassXC; Konsole = org.kde.konsole; KAddressBook =
// org.kde.kaddressbook; KCalc = org.kde.kcalc.
var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
// IMPORTANTE: "launchers" é um StringList — precisa ser um ARRAY JS. Passar
// uma string única com vírgulas faz o Plasma tratar tudo como UM lançador
// inválido (aparece como uma "folha em branco" no dock).
tasks.writeConfig("launchers", [
    "applications:systemsettings.desktop",
    "applications:org.kde.discover.desktop",
    "applications:org.mozilla.firefox.desktop",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.dolphin.desktop",
    "applications:vlc.desktop",
    "applications:org.kde.spectacle.desktop",
    "applications:org.keepassxc.KeePassXC.desktop",
    "applications:org.kde.kaddressbook.desktop",
    "applications:org.kde.kcalc.desktop",
    "applications:libreoffice-writer.desktop"
]);
EOF

# ── Tema Global (Look-and-Feel) proprio: org.capivaraos.desktop (PROD-130) ───
# Empacota a identidade do desktop num Look-and-Feel do KDE para que "CapivaraOS"
# apareca como o Tema Global ATIVO em Ajustes do Sistema > Aparencia (no lugar de
# "Breeze Dark") e o usuario possa experimentar o Breeze e VOLTAR para
# "CapivaraOS" -- marcando "usar o layout da area de trabalho" ele reconstroi
# painel superior + dock. Nao bloqueia nada (e so mais um tema selecionavel).
# REUSA os nomes exatos ja instalados por este pacote e reforcados no %posttrans:
# esquema de cores CapivaraOS, desktoptheme CapivaraOS, decoracao
# __aurorae__svg__CapivaraOS (lib org.kde.kwin.aurorae.v2), icones breeze-dark,
# accent 21,178,44. O layout e o MESMO macos-layout.js (copiado -> fonte unica,
# sem divergencia). Nao se aplica a Snout/Pup (desktops diferentes).
LNF=%{buildroot}%{_datadir}/plasma/look-and-feel/org.capivaraos.desktop
install -d "$LNF/contents/layouts" "$LNF/contents/previews"
cat > "$LNF/metadata.json" << 'LNFMETA'
{
    "KPackageStructure": "Plasma/LookAndFeel",
    "KPlugin": {
        "Authors": [
            {
                "Name": "CapivaraOS Project"
            }
        ],
        "Description": "Tema global do CapivaraOS Marsh (verde-Pantanal, painel + dock)",
        "Id": "org.capivaraos.desktop",
        "License": "GPL-3.0-or-later",
        "Name": "CapivaraOS",
        "Name[pt_BR]": "CapivaraOS",
        "Version": "%{version}",
        "Website": "https://capivaraos.org"
    }
}
LNFMETA
# 'defaults': o que o KCM aplica ao selecionar o tema. Formato [arquivo][grupo].
# Os MESMOS valores dos blocos de skel/%posttrans -- selecionar "CapivaraOS"
# reaplica a nossa identidade; selecionar "Breeze" volta ao padrao do KDE.
cat > "$LNF/contents/defaults" << 'LNFDEF'
[kdeglobals][KDE]
widgetStyle=Breeze

[kdeglobals][General]
ColorScheme=BreezeDark
accentColorFromWallpaper=false

[kdeglobals][Icons]
Theme=breeze-dark

[plasmarc][Theme]
name=default

[kwinrc][org.kde.kdecoration2]
library=org.kde.kwin.aurorae.v2
theme=__aurorae__svg__CapivaraOS
ButtonsOnLeft=XIA
ButtonsOnRight=

[kscreenlockerrc][Greeter]
Theme=org.kde.breeze
LNFDEF
# Layout = MESMO macos-layout.js (fonte unica). Presente aqui, o KCM oferece a
# opcao "usar o layout da area de trabalho" -> reconstroi painel superior + dock.
cp %{buildroot}%{_datadir}/capivaraos/macos-layout.js \
    "$LNF/contents/layouts/org.kde.plasma.desktop-layout.js"
# Preview do cartao do KCM: a cena "Luar" (wallpaper padrao).
convert backgrounds/capivaraos-wp-moonlight.png -resize 400x250^ -gravity center \
    -extent 400x250 "$LNF/contents/previews/preview.png" 2>/dev/null || \
    cp backgrounds/capivaraos-wp-moonlight.png "$LNF/contents/previews/preview.png"
find "$LNF" -type d -exec chmod 0755 {} \;
find "$LNF" -type f -exec chmod 0644 {} \;

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/capivaraos-set-layout << 'EOF'
#!/bin/bash
MARKER="$HOME/.config/.capivaraos-layout-applied"
[ -f "$MARKER" ] && exit 0

for i in $(seq 1 30); do
    pgrep -x plasmashell >/dev/null 2>&1 && break
    sleep 1
done
# Aguarda 12s para o Plasma + Look and Feel terminarem a criacao assincrona
# de todos os paineis padrao. Com 5s, o L&F criava um dock extra apos o
# primeiro evaluateScript, causando duplicidade visual por ~5s ate a segunda
# chamada limpar. Com 12s, aplicamos o layout uma unica vez, ja com todos os
# paineis do L&F presentes, e removemos tudo de uma vez.
sleep 12

QDBUS=""
for CAND in qdbus6 qdbus-qt6 qdbus; do
    command -v "$CAND" >/dev/null 2>&1 && QDBUS="$CAND" && break
done

if [ -n "$QDBUS" ]; then
    "$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
        "$(cat /usr/share/capivaraos/macos-layout.js)" >/dev/null 2>&1 || true
fi

mkdir -p "$HOME/.config"
touch "$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-layout

cat > %{buildroot}%{_bindir}/capivaraos-set-wallpaper << EOF
#!/bin/bash
MARKER="\$HOME/.config/.capivaraos-wallpaper-applied"
[ -f "\$MARKER" ] && exit 0

for i in \$(seq 1 30); do
    pgrep -x plasmashell >/dev/null 2>&1 && break
    sleep 1
done
sleep 2

# Aplica o DIRETORIO do pacote (nao o arquivo): assim o Plasma marca o tile
# "CapivaraOS Luar" como atual. Passar o arquivo (.../1920x1080.png) fazia o
# Plasma criar um tile de imagem avulsa nomeado pela resolucao ("1920x1080"),
# separado e duplicado do pacote.
if command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
    plasma-apply-wallpaperimage "${DEFAULT_WP_PKG}" >/dev/null 2>&1
fi

mkdir -p "\$HOME/.config"
touch "\$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-wallpaper

# ── Avatar do usuario -> capivara (FEAT-102) ────────────────────────────────
# Registra a face da marca no AccountsService no 1o login. O SDDM mostra o icone
# do AccountsService; sem isto o usuario (criado pelo instalador ou o liveuser)
# fica com o boneco generico. SetIconFile e permitido pelo polkit para o proprio
# usuario da sessao ativa; o daemon (root) copia a imagem para
# /var/lib/AccountsService/icons/<user>, legivel pelo SDDM (a home 0700 nao e).
cat > %{buildroot}%{_bindir}/capivaraos-set-avatar << 'EOF'
#!/bin/bash
MARKER="$HOME/.config/.capivaraos-avatar-applied"
[ -f "$MARKER" ] && exit 0

FACE=/usr/share/capivaraos/capivaraos-face.png
[ -f "$FACE" ] || exit 0

USERPATH="/org/freedesktop/Accounts/User$(id -u)"
# Espera o AccountsService responder no barramento do sistema (ate ~30s) e
# tenta registrar a face. SetIconFile e idempotente, entao repetir nao faz mal.
for i in $(seq 1 30); do
    if dbus-send --system --print-reply --dest=org.freedesktop.Accounts \
        "$USERPATH" org.freedesktop.Accounts.User.SetIconFile \
        string:"$FACE" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

mkdir -p "$HOME/.config"
touch "$MARKER"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-set-avatar

install -d %{buildroot}%{_sysconfdir}/xdg/autostart
cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Wallpaper
Exec=/usr/bin/capivaraos-set-wallpaper
NoDisplay=true
X-KDE-autostart-phase=2
OnlyShowIn=KDE;
EOF

cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-layout.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Layout
Exec=/usr/bin/capivaraos-set-layout
NoDisplay=true
X-KDE-autostart-phase=2
OnlyShowIn=KDE;
EOF

cat > %{buildroot}%{_sysconfdir}/xdg/autostart/capivaraos-avatar.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=CapivaraOS Avatar
Exec=/usr/bin/capivaraos-set-avatar
NoDisplay=true
X-KDE-autostart-phase=2
OnlyShowIn=KDE;
EOF

# ── Wallpaper do login (plasma-login-manager) -> luar ───────────────────────
# O gerenciador de login da ISO e o plasma-login-manager (plasmalogin.service),
# NAO o SDDM. O fundo do greeter vem de /usr/lib/plasmalogin/defaults.conf, que
# aponta para Image=file:///usr/share/wallpapers/Fedora/ -- um pacote de wallpaper
# que REMOVEMOS do seletor (FEAT-105); sem o pacote, o login fica PRETO.
# TESTADO: um drop-in em /etc/plasmalogin.conf.d/ NAO surte efeito (o greeter le
# o wallpaper SO do defaults.conf do vendor, nao da cascata do /etc). O que
# funciona (confirmado ao vivo na VM) e reescrever o proprio defaults.conf. Isso
# e feito no %posttrans (instalacao) e reaplicado por %transfiletriggerin quando o
# plasma-login-manager atualizar (ele reescreve o defaults.conf de volta p/
# Fedora). Ver FEAT-108 / BUG-43.
# ── Rotulo da raiz do sistema instalado -> "capivaraos" ─────────────────────
# O instalador (Anaconda/blivet) rotula o volume raiz com o "short product name"
# derivado internamente, que acaba saindo "fedora" (visto no gerenciador de
# arquivos como o rotulo do disco). Isso e interno do Anaconda e nao ha flag de
# build confiavel para muda-lo. Solucao deterministica: um servico de 1o boot no
# sistema INSTALADO reetiqueta a raiz para "capivaraos". Guardas: (1) nao roda na
# sessao live (ConditionKernelCommandLine=!rd.live.image + checagem no script);
# (2) so reetiqueta se o rotulo atual for generico (fedora/anaconda/vazio), nunca
# um rotulo que o usuario tenha escolhido; (3) marcador para rodar so uma vez.
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/capivaraos-relabel-root << 'EOF'
#!/bin/bash
# NAO 'set -e': um erro no relabel nao deve deixar o servico em estado 'failed'
# sem log. Registramos tudo (echo -> journal do systemd, oneshot).
MARK=/var/lib/capivaraos/.root-relabeled
mkdir -p /var/lib/capivaraos
[ -f "$MARK" ] && { echo "relabel: ja executado, saindo"; exit 0; }
# Sessao live: nao mexer (a raiz e o overlay do live)
if grep -qw rd.live.image /proc/cmdline 2>/dev/null; then
    echo "relabel: sessao live (rd.live.image), nao mexo"; exit 0
fi

SRC=$(findmnt -no SOURCE / 2>/dev/null)
FST=$(findmnt -no FSTYPE / 2>/dev/null)
CUR=$(findmnt -no LABEL / 2>/dev/null)
# No btrfs o SOURCE vem como "/dev/sda3[/root]" (com o subvolume). O device real
# (para e2label e para o udevadm) e so a parte antes do "[".
DEV=${SRC%%[*}
echo "relabel: raiz SRC=$SRC DEV=$DEV FST=$FST LABEL_ATUAL='$CUR'"

case "$CUR" in
    capivaraos) echo "relabel: ja e capivaraos"; touch "$MARK"; exit 0 ;;
    fedora|anaconda|localhost-live|"" ) ;;           # generico -> reetiquetar
    *) echo "relabel: rotulo proprio '$CUR', respeitando"; touch "$MARK"; exit 0 ;;
esac

case "$FST" in
    btrfs)          btrfs filesystem label / capivaraos && echo "relabel: btrfs -> capivaraos" ;;
    ext2|ext3|ext4) e2label "$DEV" capivaraos && echo "relabel: $FST -> capivaraos" ;;
    *)              echo "relabel: FST '$FST' nao suportado online, pulando" ;;
esac
# Forca o udev/udisks a reler o rotulo AGORA (senao o Dolphin mostra o "fedora"
# cacheado do momento da montagem, ate o proximo reboot). Emite um evento
# "change" no DEVICE real (sem o sufixo [subvol], que invalidava o comando).
udevadm trigger --settle --action=change "$DEV" 2>/dev/null || true
udevadm settle 2>/dev/null || true
touch "$MARK"
echo "relabel: concluido (rotulo agora: $(findmnt -no LABEL / 2>/dev/null))"
EOF
chmod 0755 %{buildroot}%{_bindir}/capivaraos-relabel-root

install -d %{buildroot}%{_unitdir}
cat > %{buildroot}%{_unitdir}/capivaraos-relabel-root.service << 'EOF'
[Unit]
Description=Reetiqueta a raiz do CapivaraOS (rotulo do disco)
ConditionKernelCommandLine=!rd.live.image
ConditionPathExists=!/var/lib/capivaraos/.root-relabeled
# local-fs.target garante a raiz montada e regravavel. Sem DefaultDependencies=no
# (removido: causava ordenacao cedo demais) para herdar as deps padrao do systemd.
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/usr/bin/capivaraos-relabel-root
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

# ── Snapshots pré-upgrade: config 'root' do snapper no 1º boot (PROD-118) ────
# O capivaraos-upgrade (FEAT-115) só tira o snapshot de segurança ANTES do
# upgrade in-place se a raiz for btrfs E existir a config 'root' do snapper
# (snapper list-configs | grep -qw root). O Marsh instala snapper +
# btrfs-assistant, mas nem o pacote nem o Anaconda criam essa config — então o
# upgrade caía no caminho "sem snapshot" (sem rollback automático). Este
# serviço a cria uma única vez no 1º boot do sistema instalado (idempotente,
# DE-agnóstico). Portado do Snout (PROD-116, commit 5ac5b59). Sem '%' nos
# heredocs (o rpm come '%' no %install mesmo com << 'EOF' -- ver
# reference_rpm_percent_heredoc): o script/unit abaixo não usa nenhum.
install -d %{buildroot}%{_libexecdir}/capivaraos
cat > %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot << 'EOF'
#!/bin/bash
# Cria a config 'root' do snapper se a raiz for btrfs e ainda não existir.
# Idempotente; pensado para rodar uma vez no 1o boot do sistema instalado.
set -e
[ "$(findmnt -no FSTYPE /)" = btrfs ] || exit 0
command -v snapper >/dev/null 2>&1 || exit 0
snapper list-configs 2>/dev/null | grep -qw root && exit 0
snapper -c root create-config /
# Limites conservadores: sem timeline automática (não encher o disco); mantém
# os snapshots numerados (pré/pós de transação e o do capivaraos-upgrade).
snapper -c root set-config TIMELINE_CREATE=no NUMBER_CLEANUP=yes NUMBER_LIMIT=10 NUMBER_LIMIT_IMPORTANT=10 || true
systemctl enable --now snapper-cleanup.timer >/dev/null 2>&1 || true
EOF
chmod 0755 %{buildroot}%{_libexecdir}/capivaraos/snapper-firstboot

cat > %{buildroot}%{_unitdir}/capivaraos-snapper-setup.service << 'EOF'
[Unit]
Description=CapivaraOS: cria a configuracao snapper 'root' no 1o boot (btrfs)
Documentation=https://capivaraos.org
# Pula assim que a config existir (nao roda de novo); e so em raiz btrfs.
ConditionPathExists=!/etc/snapper/configs/root
After=local-fs.target
Before=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/libexec/capivaraos/snapper-firstboot

[Install]
WantedBy=multi-user.target
EOF

# ── Perfil do Anaconda: faz o instalador reconhecer o CapivaraOS (BUG-38) ────
# O Anaconda casa o perfil de instalacao pelo os_id do /etc/os-release. Como o
# nosso ID e "capivaraos" (nao "fedora"), NENHUM perfil casava e o instalador
# caia no default de /etc/anaconda/anaconda.conf, que define efi_dir=default.
# Em UEFI isso faz o gen_grub_cfgstub tentar gravar o stub em
# /boot/efi/EFI/default (inexistente -- shim/grub2-efi instalam em /EFI/fedora)
# -> "gen_grub_cfgstub script failed" e a instalacao FALHA no passo do
# bootloader. So aparece em UEFI real; em VM no modo BIOS/legacy o caminho EFI
# nem roda (por isso nao pegamos antes). Herdando base_profile=fedora, o
# CapivaraOS reusa efi_dir=fedora, esquema BTRFS e demais ajustes do Fedora.
install -d %{buildroot}%{_sysconfdir}/anaconda/profile.d
cat > %{buildroot}%{_sysconfdir}/anaconda/profile.d/capivaraos.conf << 'EOF'
[Profile]
profile_id = capivaraos
base_profile = fedora

[Profile Detection]
os_id = capivaraos

[User Interface]
# Branding visual do instalador (FEAT-104): SOBRESCREVE o custom_stylesheet
# herdado do fedora.conf (fedora.css, que pinta a barra de #51a2da azul). Sem
# esta linha, o instalador do CapivaraOS sairia com o azul do Fedora.
custom_stylesheet = /usr/share/anaconda/pixmaps/capivaraos.css
EOF

# ── Branding visual do Anaconda GTK (FEAT-104): barra azul -> verde da marca +
# logo na sidebar. ATENCAO: em Fedora 44 o instalador da ISO live e o Anaconda
# WebUI (Cockpit), que IGNORA este CSS GTK -- o branding que realmente pinta a
# tela e o do Cockpit (bloco logo abaixo). Este bloco GTK fica como fallback
# caso algum caminho use o frontend GTK. As classes .logo-sidebar / .logo /
# #nav-box replicam o esquema do fedora.css, trocando cor e logo.
install -d %{buildroot}%{_datadir}/anaconda/pixmaps/capivaraos
install -m 0644 build/anaconda/sidebar-logo.png \
    %{buildroot}%{_datadir}/anaconda/pixmaps/capivaraos/sidebar-logo.png
cat > %{buildroot}%{_datadir}/anaconda/pixmaps/capivaraos.css << 'EOF'
/* Branding do instalador CapivaraOS Marsh — verde da marca + logo (FEAT-104) */
@define-color capivaraos_green #15B22C;

/* Barra lateral: verde solido (sem a textura sidebar-bg.png do Fedora) */
.logo-sidebar {
    background-image: none;
    background-color: @capivaraos_green;
    background-repeat: no-repeat;
}

/* Logo (nome + capivara, branca) no topo da sidebar */
.logo {
    background-image: url('/usr/share/anaconda/pixmaps/capivaraos/sidebar-logo.png');
    background-position: 50% 20px;
    background-repeat: no-repeat;
    background-color: transparent;
}

.product-logo {
    background-image: none;
    background-color: transparent;
}

/* Barra SUPERIOR (era azul #51a2da do Fedora) -> verde CapivaraOS */
AnacondaSpokeWindow #nav-box {
    background-color: @capivaraos_green;
    background-image: none;
    color: white;
}
EOF

# ── Branding do Cockpit / Anaconda WebUI (FEAT-104) — o que REALMENTE pinta a
# tela do instalador da ISO live (Fedora 44). O Cockpit carrega
# /usr/share/cockpit/branding/<ID>/branding.css escolhido pelo ID do os-release
# (capivaraos). branding.css sobrescreve as variaveis PatternFly da cor de marca
# (--pf-t--global--color--brand--*) para o verde CapivaraOS, troca a logo do
# topo e o texto do #brand. Mesmo mecanismo do Pup/Snout. Cockpit expande
# ${NAME}/${VARIANT} a partir do os-release em tempo de execucao (heredoc
# aspado de proposito, para nao expandir aqui).
install -d %{buildroot}%{_datadir}/cockpit/branding/capivaraos
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/logo.png
install -m 0644 build/cockpit/logo.png %{buildroot}%{_datadir}/cockpit/branding/capivaraos/apple-touch-icon.png
install -m 0644 build/cockpit/favicon.ico %{buildroot}%{_datadir}/cockpit/branding/capivaraos/favicon.ico
cat > %{buildroot}%{_datadir}/cockpit/branding/capivaraos/branding.css << 'EOF'
/* Branding do instalador CapivaraOS Marsh — Anaconda WebUI (Cockpit) FEAT-104 */
#badge {
    inline-size: 225px;
    block-size: 80px;
    background-image: url("logo.png");
    background-size: contain;
    background-repeat: no-repeat;
}

#brand::before {
    content: "${NAME} <b>${VARIANT}</b>";
}

.anaconda {
    /* Paleta da marca CapivaraOS (verde #15B22C) */
    --brand-default-light: #46c95b;
    --brand-default: #15b22c;
    --brand-default-dark: #0e7a1e;

    .logo {
        background-image: url("logo.png");
        width: 2.5rem;
        height: 2.5rem;
        /* O index.css do WebUI poe filter:invert(1) grayscale(1) brightness(2.5)
           + mix-blend-mode:screen na .logo (para a logo SVG do Fedora). Isso
           inverte nossa capivara branca para preta e o screen a some. Anulamos
           os dois para a nossa logo (ja branca) aparecer como esta. */
        filter: none;
        mix-blend-mode: normal;
    }
}

:not(.pf-v6-theme-dark) .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default);
    --pf-t--global--color--brand--hover: var(--brand-default-dark);
}

.pf-v6-theme-dark .anaconda {
    --pf-t--global--color--brand--default: var(--brand-default-light);
    --pf-t--global--color--brand--hover: var(--brand-default);
}
EOF
# NOTA: Spotify foi DESCARTADO (decisao do usuario 2026-08-20 — nao vale o
# esforco: flatpak de extra-data nao instala no compose e exigia oneshot de 1o
# boot). Cliente de IA fica so o Alpaca (Ollama GUI) no %post. FEAT-103.

%post
# Splash de boot CapivaraOS
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# Reetiquetar a raiz para "capivaraos" no 1o boot do sistema instalado
# (nao roda na live -- ver a unit). Habilitado aqui, no compose, para o
# sistema instalado herdar o servico ligado.
systemctl enable capivaraos-relabel-root.service >/dev/null 2>&1 || true

# Cria a config 'root' do snapper no 1o boot (btrfs) -> habilita o snapshot/
# rollback automático do capivaraos-upgrade. PROD-118. Habilitado aqui (compose)
# para o sistema instalado herdar o serviço ligado, igual ao relabel-root acima.
systemctl enable capivaraos-snapper-setup.service >/dev/null 2>&1 || true

# Pula o OOBE de 1o boot do Plasma (plasma-setup.service: assistente de idioma/
# teclado/usuario com fundo do mapa 3D, que "abre no inicio do KDE"). E
# REDUNDANTE: o Anaconda WebUI ja coletou tudo. A unit tem
# ConditionPathExists=!/etc/plasma-setup-done, entao criamos esse flag (mecanismo
# oficial) -> o assistente nao roda no sistema instalado.
touch %{_sysconfdir}/plasma-setup-done

# ── Tela de login SDDM: ver %posttrans ──────────────────────────────────────
# O fundo/logo do SDDM sao aplicados no %posttrans (nao aqui), porque exige
# editar o theme.conf do tema do sddm-breeze DEPOIS que ele foi instalado na
# transacao. Ate o alpha5 tentavamos via theme.conf.user, mas o binario do SDDM
# (sddm-greeter-qt6) le SO o ConfigFile do metadata (theme.conf) -- nunca um
# ".user" (confirmado: nao ha a string ".user" no binario). Por isso o login
# nunca mudava, em nenhuma versao. Ver o bloco SDDM no %posttrans.

# GRUB_DISTRIBUTOR -> "CapivaraOS" (efetivo apos grub2-mkconfig no sistema
# instalado; a ISO live em si usa o titulo passado ao livemedia-creator)
if [ -f %{_sysconfdir}/default/grub ]; then
    if grep -q '^GRUB_DISTRIBUTOR=' %{_sysconfdir}/default/grub; then
        sed -i 's/^GRUB_DISTRIBUTOR=.*/GRUB_DISTRIBUTOR="CapivaraOS"/' %{_sysconfdir}/default/grub
    else
        echo 'GRUB_DISTRIBUTOR="CapivaraOS"' >> %{_sysconfdir}/default/grub
    fi
fi

gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true

%postun
if [ "$1" -eq 0 ]; then
    gtk-update-icon-cache -f %{_datadir}/icons/hicolor >/dev/null 2>&1 || true
fi

%posttrans
# ── Tela de login SDDM: fundo (luar) + logo (capivara branca) no tema ativo ──
# O SDDM le SO o theme.conf (ConfigFile do metadata) do tema Current; nao ha
# theme.conf.user. Editamos in-place o background/logo do tema DEPOIS que o
# sddm-breeze foi instalado (por isso aqui no %posttrans, nao no %post -- se
# rodasse antes do sddm-breeze na transacao, o theme.conf nem existiria).
# type ja e "image", entao a cor nao importa. As demais chaves sao preservadas.
for T in 01-breeze-fedora breeze; do
    TC=%{_datadir}/sddm/themes/$T/theme.conf
    [ -f "$TC" ] || continue
    sed -i \
        -e "s|^background=.*|background=%{_datadir}/capivaraos/sddm-background.png|" \
        -e "s|^logo=.*|logo=%{_datadir}/pixmaps/capivaraos-white.png|" \
        "$TC"
done

# ── Wallpaper padrao do sistema (tela de bloqueio + fallbacks) -> luar ───────
# O /usr/share/backgrounds/default.jxl (desktop-backgrounds-compat) e o mapa 3D
# que a tela de bloqueio do Plasma mostra. Sobrescrevemos com o luar (JXL). Feito
# no %posttrans (depois do desktop-backgrounds-compat instalar) e reaplicado por
# %transfiletriggerin quando esse pacote atualizar (que reverteria o arquivo).
# IMPORTANTE: default.jxl e um SYMLINK -> ./f45/default/f45-01-day.jxl (idem o
# -dark, -> f45-01-night.jxl) no Fedora 45. Um "cp -f" escreve ATRAVES do link e sobrescreve a
# arte REAL do Fedora (era o que fazia o wallpaper "Fedora Forty-Four" aparecer
# com o luar). "cp --remove-destination" apaga o link antes e grava um arquivo
# real -> os originais do Fedora ficam intactos.
if [ -f %{_datadir}/capivaraos/capivaraos-default.jxl ]; then
    for BG in default.jxl default-dark.jxl; do
        [ -e %{_datadir}/backgrounds/$BG ] && \
            cp --remove-destination %{_datadir}/capivaraos/capivaraos-default.jxl \
                %{_datadir}/backgrounds/$BG
    done
fi

# ── Fundo do login (plasma-login-manager) -> luar ───────────────────────────
# O greeter le o wallpaper de /usr/lib/plasmalogin/defaults.conf (Image/
# PreviewImage sob [Greeter][Wallpaper][org.kde.image][General]). O padrao do
# Fedora aponta p/ .../wallpapers/Fedora/, que removemos -> login PRETO. Um
# drop-in em /etc/plasmalogin.conf.d/ NAO funciona (o greeter nao le a cascata do
# /etc p/ o wallpaper). Reescrevemos as duas chaves no proprio defaults.conf p/ o
# pacote KDE do luar (mantido). Feito aqui no %posttrans (depois que o
# plasma-login-manager instalou o defaults.conf). Confirmado ao vivo. BUG-43.
PLD=%{_prefix}/lib/plasmalogin/defaults.conf
if [ -f "$PLD" ]; then
    sed -i -E \
        's,^(Image|PreviewImage)=.*,\1=file:///usr/share/wallpapers/capivaraos-luar/,' \
        "$PLD"
fi

# ── Accent do login (greeter do plasma-login-manager) — AZUL PADRAO ──────────
# O greeter roda como o usuario "plasmalogin" e le o accent do fallback do
# sistema /etc/xdg/kdeglobals ([General] AccentColor). Decisao do dono (2026-09-22,
# "muito verde"): sem AccentColor proprio -> o greeter usa o azul padrao do
# esquema. REMOVEMOS ativamente qualquer AccentColor verde que uma versao anterior
# tenha gravado no /etc/xdg. Mantemos accentColorFromWallpaper=false para o accent
# NAO vir do wallpaper (esverdeado). Ver docs/REVERT-CORES-VERDE.md.
XDGKG=%{_sysconfdir}/xdg/kdeglobals
install -d %{_sysconfdir}/xdg
kwriteconfig6 --file "$XDGKG" --group General --key AccentColor --delete 2>/dev/null || \
    kwriteconfig5 --file "$XDGKG" --group General --key AccentColor --delete 2>/dev/null || true
kwriteconfig6 --file "$XDGKG" --group General --key accentColorFromWallpaper "false" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKG" --group General --key accentColorFromWallpaper "false" 2>/dev/null || true

# ── Identidade CapivaraOS como PADRAO DO SISTEMA (/etc/xdg) — FEAT-91 frente D ─
# A sessao LIVE (liveuser) NAO herda /etc/skel/.config de forma confiavel (por
# isso wallpaper/layout usam autostart). Provado: no live, ~/.config/kdeglobals
# nao tem ColorScheme=CapivaraOS nem o kwinrc tem a decoracao -- so o accent, que
# ja vinha justamente daqui do /etc/xdg. Entao gravamos o esquema de cores, a
# decoracao de janela e o perfil do Konsole no /etc/xdg (fallback do sistema,
# lido por TODOS os usuarios sem override -- live e instalado). Merge via
# kwriteconfig; reversivel. Ver docs/REVERT-CORES-VERDE.md.
kwriteconfig6 --file "$XDGKG" --group General --key ColorScheme "BreezeDark" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKG" --group General --key ColorScheme "BreezeDark" 2>/dev/null || true
# Tema Global = nosso Look-and-Feel org.capivaraos.desktop (PROD-130). Reforcado
# aqui no /etc/xdg para a sessao LIVE (que nao herda o /etc/skel/.config/kdeglobals)
# mostrar "CapivaraOS" como tema ativo em Aparencia. Reversivel (troca pelo KCM).
kwriteconfig6 --file "$XDGKG" --group KDE --key LookAndFeelPackage "org.capivaraos.desktop" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKG" --group KDE --key LookAndFeelPackage "org.capivaraos.desktop" 2>/dev/null || true
# Icones Breeze Dark (antes fixados no capivaraos-post-theme.ks, agora aposentado).
kwriteconfig6 --file "$XDGKG" --group Icons --key Theme "breeze-dark" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKG" --group Icons --key Theme "breeze-dark" 2>/dev/null || true

XDGKWIN=%{_sysconfdir}/xdg/kwinrc
kwriteconfig6 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key library "org.kde.kwin.aurorae.v2" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key library "org.kde.kwin.aurorae.v2" 2>/dev/null || true
kwriteconfig6 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key theme "__aurorae__svg__CapivaraOS" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key theme "__aurorae__svg__CapivaraOS" 2>/dev/null || true
kwriteconfig6 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key ButtonsOnLeft "XIA" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key ButtonsOnLeft "XIA" 2>/dev/null || true
kwriteconfig6 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key ButtonsOnRight "" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKWIN" --group "org.kde.kdecoration2" --key ButtonsOnRight "" 2>/dev/null || true

XDGKONSOLE=%{_sysconfdir}/xdg/konsolerc
kwriteconfig6 --file "$XDGKONSOLE" --group "Desktop Entry" --key DefaultProfile "CapivaraOS.profile" 2>/dev/null || \
    kwriteconfig5 --file "$XDGKONSOLE" --group "Desktop Entry" --key DefaultProfile "CapivaraOS.profile" 2>/dev/null || true

# Tema Plasma = Breeze padrao (default) tambem no fallback do sistema /etc/xdg
# (a live nao herda /etc/skel/.config/plasmarc). Decisao do dono (2026-09-23):
# sem verde no painel/menus. O desktoptheme CapivaraOS segue instalado/selecionavel.
XDGPLASMA=%{_sysconfdir}/xdg/plasmarc
kwriteconfig6 --file "$XDGPLASMA" --group Theme --key name "default" 2>/dev/null || \
    kwriteconfig5 --file "$XDGPLASMA" --group Theme --key name "default" 2>/dev/null || true

# ── Remove os wallpapers de marca Fedora do seletor do Plasma ────────────────
# O seletor deve listar so os 9 do CapivaraOS + os neutros do KDE
# (plasma-workspace-wallpapers). As entradas "Fedora KDE SIG" saem: a da versao
# (F45 no Fedora 45 -- "Fedora Forty-Five"; deixamos F44 na lista por seguranca
# entre rebases), Fedora e Default. NAO removemos os PACOTES: kde-settings-plasma
# (dono de "Fedora") e essencial e desktop-backgrounds-kde EXIGE
# f45-backgrounds-kde -> excluir no kickstart arrastaria dependencia. Entao
# apagamos so os diretorios do seletor. Reaplicado por %transfiletriggerin em
# %{_datadir}/wallpapers caso um update reinstale-os.
for WP in F44 F45 Fedora Default; do
    rm -rf %{_datadir}/wallpapers/"$WP"
done

# Tema padrao do Plymouth (boot/desligamento): escrito direto aqui, em vez de
# depender so do "plymouth-set-default-theme capivaraos" do %post, porque o
# pacote plymouth grava /etc/plymouth/plymouthd.conf com "Theme=" comentado
# e plymouth-set-default-theme so EDITA uma linha "Theme=" existente -- nao
# descomenta/cria a linha se ela nao existir descomentada. Escrevendo aqui
# (%posttrans, depois de toda a transacao) garantimos que o tema CapivaraOS
# fique ativo quando o dracut gerar a initramfs da ISO live (etapa que roda
# depois, no %post do kickstart).
install -d %{_sysconfdir}/plymouth
cat > %{_sysconfdir}/plymouth/plymouthd.conf << 'EOF'
[Daemon]
Theme=capivaraos
EOF
plymouth-set-default-theme capivaraos >/dev/null 2>&1 || true

# /etc/os-release, /etc/issue, /etc/issue.net (fedora-release-common) e
# /etc/xdg/kcm-about-distrorc (kde-settings): escritos aqui (em vez de
# %files) para evitar conflito de arquivo no dnf durante a transacao.
# %posttrans roda depois de toda a transacao, entao nosso conteudo
# prevalece independente da ordem de instalacao dos pacotes.
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Marsh 2.0.0 (alpha50, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Marsh 2.0.0 (alpha50, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Marsh 2.0.0 (alpha50, preview)"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha50, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha50, preview)
EOF

install -d %{_sysconfdir}/xdg
cat > %{_sysconfdir}/xdg/kcm-about-distrorc << 'EOF'
[General]
LogoPath=capivaraos-full-logo
Variant=Marsh 2.0.0 (alpha50, preview)
Website=https://capivaraos.org
UseOSReleaseVersion=true
EOF

# ── Regenera os titulos GRUB/BLS com o os-release JA branded ────────────────
# No install do Anaconda, o kernel-install roda DURANTE a transacao (antes deste
# %posttrans), gravando o title BLS a partir do os-release do Fedora ->
# "Fedora Linux 44". O Anaconda usa esse title como nome do SO ja instalado, e
# na REINSTALACAO mostra "Reinstalar Fedora"/"Instalado atualmente: Fedora Linux
# 44" mesmo com o /etc/os-release ja como CapivaraOS. O %transfiletriggerin de
# /usr/lib nao cobre este caso: como o %posttrans ja brandou o os-release, a
# guarda dele (NAME="CapivaraOS") faz sair sem regenerar. Entao regeneramos aqui,
# depois do os-release branded -> os titles passam a "CapivaraOS Marsh ...".
for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

# ── Reaplica os-release apos qualquer atualizacao futura do sistema ────────
# Nao declaramos /etc/os-release em %files (evita conflito na transacao da
# ISO), so sobrescrevemos o conteudo. Logo o arquivo continua pertencendo ao
# Fedora no rpmdb, e um "dnf update" que toque o pacote dono reescreve tudo de
# volta para o padrao do Fedora. Se isso acontecer na MESMA transacao em que
# um kernel novo e instalado, o titulo GRUB/BLS desse kernel (que o
# kernel-install gera a partir de NAME/VERSION do os-release) fica gravado
# como "Fedora Linux ... 44 (Forty Four)" -- e fica preso assim para sempre,
# mesmo depois do os-release ser corrigido.
#
# Geografia dos arquivos no Fedora 44 (os dois sao de pacotes DIFERENTES):
#
#   /etc/os-release      -> symlink para ../usr/lib/os-release,
#                           pertence a fedora-release-common
#   /usr/lib/os-release  -> arquivo com o conteudo REAL,
#                           pertence a fedora-release-identity-basic
#
# ATENCAO -- NAO troque o prefixo abaixo por um caminho de arquivo exato
# (ex.: /usr/lib/os-release). Verificado empiricamente em container fedora:44
# (2026-07-17): o %transfiletriggerin casa APENAS com prefixos de DIRETORIO e
# NUNCA com caminhos de arquivo exatos -- um trigger "-- /usr/lib/os-release"
# jamais dispara. (Ja o %filetriggerin casa com caminho exato, mas roda logo
# apos cada pacote, e nao no fim da transacao, o que reintroduz a corrida com
# o kernel-install.) Foi essa a armadilha da 1.1.2, cujo trigger
# "-- /etc/os-release" era codigo morto: nunca disparou uma unica vez.
#
# Por isso vigiamos o diretorio /usr/lib (dirname do arquivo que importa).
# Esse prefixo dispara em quase toda transacao, entao a guarda logo abaixo
# faz o caso comum sair de imediato; so pagamos o kernel-install quando o
# os-release realmente foi revertido.
%transfiletriggerin -- %{_prefix}/lib
# Caso comum: nosso os-release intacto, nada a fazer.
grep -q '^NAME="CapivaraOS"' %{_prefix}/lib/os-release 2>/dev/null && exit 0
cat > %{_sysconfdir}/os-release << 'EOF'
NAME="CapivaraOS"
VERSION="Marsh 2.0.0 (alpha50, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=45
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f45"
PRETTY_NAME="CapivaraOS Marsh 2.0.0 (alpha50, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:45"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=45
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=45
VARIANT="Marsh 2.0.0 (alpha50, preview)"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha50, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha50, preview)
EOF

for kver in $(ls /lib/modules 2>/dev/null); do
    [ -f "/lib/modules/${kver}/vmlinuz" ] && \
        kernel-install add "${kver}" "/lib/modules/${kver}/vmlinuz" >/dev/null 2>&1 || true
done

# Reaplica o fundo/logo do SDDM quando o sddm-breeze (dono do theme.conf do tema)
# for atualizado: o update reescreve o theme.conf com o padrao do Fedora
# (mapa-mundi), revertendo nossa edicao. Este trigger vigia o diretorio dos temas
# do SDDM e reaplica o sed. Prefixo de DIRETORIO (o %transfiletriggerin so casa
# prefixo de diretorio, nunca caminho exato -- ver a nota do os-release acima).
%transfiletriggerin -- %{_datadir}/sddm/themes
for T in 01-breeze-fedora breeze; do
    TC=%{_datadir}/sddm/themes/$T/theme.conf
    [ -f "$TC" ] || continue
    grep -q '^background=%{_datadir}/capivaraos/sddm-background.png$' "$TC" && continue
    sed -i \
        -e "s|^background=.*|background=%{_datadir}/capivaraos/sddm-background.png|" \
        -e "s|^logo=.*|logo=%{_datadir}/pixmaps/capivaraos-white.png|" \
        "$TC"
done

# Reaplica o default.jxl (luar) quando o desktop-backgrounds-compat for
# atualizado (que reescreve o mapa do Fedora por cima). Prefixo de DIRETORIO.
%transfiletriggerin -- %{_datadir}/backgrounds
[ -f %{_datadir}/capivaraos/capivaraos-default.jxl ] || exit 0
for BG in default.jxl default-dark.jxl; do
    [ -e %{_datadir}/backgrounds/$BG ] || continue
    cmp -s %{_datadir}/capivaraos/capivaraos-default.jxl %{_datadir}/backgrounds/$BG && continue
    # --remove-destination: nao escrever ATRAVES do symlink para o f44 do Fedora.
    cp --remove-destination %{_datadir}/capivaraos/capivaraos-default.jxl \
        %{_datadir}/backgrounds/$BG
done

# Mantem os wallpapers de marca Fedora fora do seletor apos updates que
# reinstalem os pacotes donos (f44-backgrounds-kde / kde-settings-plasma /
# desktop-backgrounds-kde). Prefixo de DIRETORIO (o %transfiletriggerin so casa
# prefixo de diretorio, nunca caminho exato).
%transfiletriggerin -- %{_datadir}/wallpapers
for WP in F44 Fedora Default; do
    rm -rf %{_datadir}/wallpapers/"$WP"
done

# Reaplica o fundo do login quando o plasma-login-manager for atualizado (o
# update reescreve /usr/lib/plasmalogin/defaults.conf de volta p/ o wallpaper
# Fedora -> login PRETO). Prefixo de DIRETORIO (%transfiletriggerin so casa
# prefixo de diretorio). BUG-43.
%transfiletriggerin -- %{_prefix}/lib/plasmalogin
PLD=%{_prefix}/lib/plasmalogin/defaults.conf
[ -f "$PLD" ] || exit 0
grep -q '^Image=file:///usr/share/wallpapers/capivaraos-luar/$' "$PLD" && exit 0
sed -i -E \
    's,^(Image|PreviewImage)=.*,\1=file:///usr/share/wallpapers/capivaraos-luar/,' \
    "$PLD"

%files
%license fonts/LICENSE-FiraCode-OFL.txt
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/icons/hicolor/scalable/apps/capivaraos-head.svg
%{_datadir}/wallpapers/capivaraos-*/
%{_datadir}/color-schemes/CapivaraOS.colors
%{_datadir}/aurorae/themes/CapivaraOS/
%{_datadir}/plasma/desktoptheme/CapivaraOS/
%{_datadir}/plasma/look-and-feel/org.capivaraos.desktop/
%{_datadir}/konsole/CapivaraOS.colorscheme
%{_datadir}/konsole/CapivaraOS.profile
%{_datadir}/plymouth/themes/capivaraos/
%{_datadir}/capivaraos/
%{_datadir}/fonts/capivaraos-firacode-nerd/
%{_bindir}/capivaraos-set-layout
%{_bindir}/capivaraos-set-wallpaper
%{_bindir}/capivaraos-set-avatar
%{_bindir}/capivaraos-relabel-root
%{_unitdir}/capivaraos-relabel-root.service
%{_unitdir}/capivaraos-snapper-setup.service
%dir %{_libexecdir}/capivaraos
%{_libexecdir}/capivaraos/snapper-firstboot
%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop
%{_sysconfdir}/xdg/autostart/capivaraos-layout.desktop
%{_sysconfdir}/xdg/autostart/capivaraos-avatar.desktop
%{_sysconfdir}/skel/.config/plasma-org.kde.plasma.desktop-appletsrc
%{_sysconfdir}/skel/.config/kscreenlockerrc
%{_sysconfdir}/skel/.config/kdeglobals
%{_sysconfdir}/skel/.config/konsolerc
%{_sysconfdir}/skel/.config/plasmarc
%{_sysconfdir}/skel/.config/plasma-welcomerc
%{_sysconfdir}/skel/.config/gtk-3.0/
%{_sysconfdir}/skel/.config/gtk-4.0/
%{_sysconfdir}/skel/.gtkrc-2.0
%{_sysconfdir}/xdg/gtk-3.0/
%{_sysconfdir}/xdg/gtk-4.0/
%{_sysconfdir}/skel/.config/fastfetch/
%{_sysconfdir}/xdg/fastfetch/
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%{_sysconfdir}/anaconda/profile.d/capivaraos.conf
%{_datadir}/anaconda/pixmaps/capivaraos.css
%{_datadir}/anaconda/pixmaps/capivaraos/
%{_datadir}/cockpit/branding/capivaraos/

%changelog
* Fri Oct 09 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.50.alpha50
- Rótulo do menu de boot da mídia: "Start CapivaraOS Marsh 45" → "Start CapivaraOS
  Marsh 2 45" (agora mostra a versão do CapivaraOS **2** + a do Fedora **45**). Feito
  via --project="CapivaraOS Marsh 2" no livemedia-creator (grava no COMPOSE), espelhado
  do Pup (8475bfb)/Snout. REMOVIDO também o bloco xorriso pós-build que tentava reescrever
  o grub.cfg — NÃO funciona no F45 (dava sempre "AVISO: não consegui reescrever") e virou
  redundante com o --project. Bump porque a ISO muda; sem mudança no pacote de branding.

* Thu Oct 08 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.49.alpha49
- A ISO passa a incluir o COS Config Center (pacote cos-config 0.11.1, central de
  configuração do CapivaraOS): adicionado ao %packages do kickstart e baixado+verificado
  (assinatura) do canal testing no build-all.sh (PR #7). Bump de versão porque o conteúdo
  da ISO mudou. Rastreio: PROD-141 (inclusão nas ISOs) / PROD-5 (épico do app). Sem
  mudança no pacote de branding em si (só o número de versão).

* Sun Oct 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.48.alpha48
- Ícone do lançador (kickoff no dock) agora é ADAPTÁVEL: virou um SVG simbólico
  monocromático (classe ColorScheme-Text) que o Plasma recolore pelo tema — escuro
  no tema claro, claro no escuro. Antes era PNG branco e sumia no Breeze claro.
  Fonte vetorial icons/capivaraos-head.svg (traçada da silhueta); substitui os PNGs
  hicolor da cabeça. PNG da cabeça segue como fonte do avatar. (Enhancement pedido
  pelo dono; cor padrão clara como rede de segurança p/ o tema escuro default.)

* Tue Sep 29 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.47.alpha47
- Sub-versão de validação do update in-place (FEAT-142): sem mudança funcional além
  do número de versão. Usada para provar, numa VM real, o update contínuo assinado
  da branding (alpha46 → alpha47) pelo canal testing — `dnf update` puxa e valida
  (gpgcheck + repo_gpgcheck), reescreve os-release/BLS no sistema em execução, e a
  versão nova aparece em "Sobre o sistema"/fastfetch. Análogo a uma troca de logo.

* Mon Sep 28 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.46.alpha46
- BLOCKER de boot (PROD-133): a imagem live nascia com um /etc/kernel/cmdline
  "fantasma" (UUID de raiz do ambiente de build + sem rootflags=subvol=root). O
  liveimg copia o rootfs da live pro alvo; o Anaconda escreve as entradas BLS do
  install certas, mas deixava esse arquivo intacto → o 1º update de kernel gerava
  uma entrada BLS com root inexistente/sem subvol → dracut emergency mode. Fix no
  %post do post-branding: remover /etc/kernel/cmdline (e /usr/lib/kernel/cmdline)
  da live → o kernel-install passa a derivar do /proc/cmdline real do sistema
  instalado (comportamento padrão do Fedora live). Só bump de versão neste pacote;
  o conserto é no kickstart. VALIDAR em install limpo + 1 update de kernel.

* Wed Sep 23 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.45.alpha45
- Avatar de usuário (.face / greeter): fundo verde #15B22C → azul-marinho #1E2F4E
  (navy da logo do CapivaraOS), capivara branca mantida. Continuação do de-green
  (decisão do dono). Sem texto (o círculo do greeter cortaria).

* Wed Sep 23 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.44.alpha44
- De-green (2ª rodada, decisão do dono: ainda "muito verde"). Escopo escolhido =
  TAMBÉM o painel/menus: o tema Plasma (desktoptheme) volta ao Breeze padrão
  (`plasmarc [Theme] name` CapivaraOS → default) nos 3 pontos: /etc/skel/plasmarc,
  defaults do Look-and-Feel e /etc/xdg (%posttrans). O desktoptheme CapivaraOS
  segue INSTALADO e selecionável (só não é mais o padrão). Decoração de janela
  (Aurorae) e Konsole SEGUEM verdes (fora do escopo pedido nesta rodada).

* Tue Sep 22 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.43.alpha43
- De-green parcial (decisao do dono: "muito verde"). Escopo = SÓ cores/accent:
  - Esquema de cores/accent volta ao AZUL padrao (Breeze Dark): botoes, selecao e
    cor de pasta. kdeglobals do skel, defaults do Look-and-Feel e o /etc/xdg
    (%posttrans) passam a ColorScheme=BreezeDark e SEM AccentColor verde (accent =
    azul padrao do esquema; greeter idem, via --delete do AccentColor no /etc/xdg).
    O esquema verde CapivaraOS.colors continua INSTALADO e selecionavel (só nao e
    mais o padrao). Tema Plasma (painel/menus), decoracao Aurorae e Konsole SEGUEM
    verdes (fora do escopo pedido).
  - Plymouth: spinner do splash volta ao BRANCO padrao (era verde #15B22C) e o
    fundo ao azul-escuro neutro (0.07,0.09,0.13), igual ao Pup e ao Snout.

* Tue Sep 22 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.42.alpha42
- Look-and-Feel org.capivaraos.desktop alinhado ao hand-off da PROD-130: metadata
  License=GPL-3.0-or-later, Authors "CapivaraOS Project", + Name[pt_BR]; defaults
  ganham [kscreenlockerrc][Greeter] Theme=org.kde.breeze. (Mantidos como melhoria:
  ButtonsOnLeft=XIA no defaults e Version=%%{version}.)

* Tue Sep 22 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.41.alpha41
- Tema Global proprio (PROD-130): novo Look-and-Feel org.capivaraos.desktop em
  /usr/share/plasma/look-and-feel/. Agora "CapivaraOS" aparece como o Tema Global
  ATIVO em Ajustes do Sistema > Aparencia (no lugar de "Breeze Dark"); o usuario
  pode experimentar o Breeze e VOLTAR para "CapivaraOS" (com a opcao de layout,
  reconstroi painel superior + dock). Nao bloqueia nada. metadata.json + contents/
  defaults (reusa os nomes exatos: ColorScheme/desktoptheme CapivaraOS, decoracao
  __aurorae__svg__CapivaraOS lib aurorae.v2, icones breeze-dark, accent 21,178,44)
  + contents/layouts (= macos-layout.js, fonte unica) + preview. LookAndFeelPackage
  do skel e do /etc/xdg apontam para ele. So Marsh (KDE).

* Mon Sep 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.40.alpha40
- REBASE F45 (PROD-113): os-release agora declara Fedora 45 (VERSION_ID/PLATFORM_ID/
  CPE_NAME/REDHAT_*_PRODUCT_VERSION 44->45, nos 2 blocos). O rebase tinha trocado só
  os rótulos alpha e deixado platform:f44. CONSEQUÊNCIA GRAVE: o Anaconda escolhe a
  versão de comandos de kickstart pelo PLATFORM_ID do os-release; com f44 ele montava
  o conjunto do F44 (sem o comando 'stratisfs' que o pyanaconda 45 referencia) ->
  KeyError em pyanaconda/core/kickstart/commands.py -> TODO módulo do backend (Timezone,
  Localization, Network, Security, Runtime, Payloads) falhava ao iniciar -> instalador
  travado eternamente em "Initializing...". Corrigido = instalador volta a subir.
- Limpeza f44->f45 do mesmo rebase: seletor remove também a entrada "F45" do Fedora
  (era só "F44"); comentários do default.jxl/f45-backgrounds-kde atualizados.

* Mon Sep 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.39.alpha39
- Wallpaper "CapivaraOS Série 2" (capivaraos-wp-serie2.png, 3840x2160) somado ao
  conjunto da marca (agora 9 pacotes KDE). Hero da linha 2.0 (capivara + "2" de
  circuito). Asset comum às 3 spins, criado no Pup 2.x e propagado (padrão segue
  o "Luar"). Ver project_brand_assets_2x.

* Sat Sep 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.38.alpha38
- snapper: cria a config 'root' no 1o boot do sistema instalado (PROD-118). Novo
  /usr/libexec/capivaraos/snapper-firstboot + capivaraos-snapper-setup.service
  (oneshot, ConditionPathExists=!/etc/snapper/configs/root, so em raiz btrfs),
  habilitado no %post. Sem isso o capivaraos-upgrade (FEAT-115) caía em "sem
  snapshot" — snapper/btrfs-assistant vêm na ISO, mas ninguém criava a config.
  Portado do Snout (PROD-116, commit 5ac5b59); DE-agnóstico e idempotente.

* Fri Sep 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.37.alpha37
- Primeira build do rebase para Fedora 45 (base do 2.0) — PROD-113. O F45 Beta saiu
  (2026-09-18); build repontado no branch rebase-f45: build-all.sh --releasever=45,
  base fedora-repo.ks -> f45 (fedora-45/updates-released-f45), trava de updates e
  titulo grub em 45. Só rótulo/versão aqui no branding; a base muda no compose.
  F45 = Plasma 6.7 (revalidar Aurorae/tema Plasma/greeter/GTK) + Anaconda 45.
  SMOKE BUILD p/ levantar quebras — NÃO cortar ISO pública do F45 antes do GA.

* Fri Sep 11 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.36.alpha36
- Logo próprio do CapivaraOS no fastfetch (FEAT-136 / FEAT-50): o painel ASCII do
  terminal deixa de mostrar o logo do Fedora (que o fastfetch escolhia por ID_LIKE
  do os-release) e passa a mostrar a cabeça de capivara da marca + "CapivaraOS" em
  VERDE (#15B22C). Arte em /usr/share/capivaraos/fastfetch/capivara.txt (silhueta
  do brand-assets + nome via placeholder $2) e config.jsonc mínimo (só o LOGO, sem
  mexer nos módulos) em /etc/skel/.config/fastfetch/ e /etc/xdg/fastfetch/ (este p/
  valer na sessao LIVE). ASCII funciona em TTY. Só o Marsh (2.x); Pup/Snout/Herd
  ficam p/ o 2.x de cada (FEAT-137/138/PROD-110).

* Sun Sep 06 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.35.alpha35
- Tema GTK proprio (FEAT-91 frente D, D5 -- ULTIMA fatia): apps GTK/libadwaita
  passam a usar o tema NATIVO Adwaita-dark (in-box) com o verde da marca #15B22C
  injetado como accent via gtk.css (accent_bg_color/theme_selected_bg_color),
  casando com o accent do desktop Plasma. Config em /etc/skel/.config/gtk-{3,4}.0
  (settings.ini + gtk.css) e /etc/gtk-2.0 legado (.gtkrc-2.0), e replicada em
  /etc/xdg/gtk-{3,4}.0 para valer na sessao LIVE. Icones Breeze Dark fixados em
  kdeglobals [Icons] Theme (skel + /etc/xdg), antes feito no post-script.
- APOSENTA O WHITESUR: com D1 (cores), D3 (Aurorae), D4 (tema Plasma) e agora D5
  (GTK), as 4 superficies visuais sao 100% proprias. Removidos do build os dois
  "git clone" do WhiteSur (GTK e KDE) e todo o capivaraos-post-theme.ks (agora
  sem funcao -- o RPM cobre colors/aurorae/plasma/gtk em skel e /etc/xdg).
  Removidas do %packages as dependencias que so serviam ao WhiteSur (sassc,
  optipng, gtk-murrine-engine, gtk2-engines, ImageMagick). Build sem rede.
  Fecha o FEAT-91. Ver docs/REVERT-CORES-VERDE.md.

* Sat Sep 05 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.34.alpha34
- Tema Plasma (FEAT-91 frente D, D4 -- prova 2): formas proprias de widget
  adicionadas ao desktoptheme CapivaraOS -- widgets/listitem.svg (realce de
  item de menu/lista: hover accent suave, selecionado VERDE solido #15B22C,
  pressionado #0E7A1E), widgets/lineedit.svg (campo: base escura #12160F +
  borda, anel de foco verde) e widgets/button.svg (botao: normal surface-alt
  #282E23, hover/foco com borda accent, pressionado #0E7A1E). Nine-patch r=6,
  fill EXPLICITO por forma (o QSvg do Plasma nao herda fill do <g> ancestral ao
  desenhar por id -- so o transform; um bug de listitem preto foi pego e
  corrigido na validacao). Empacotamento reaproveita o cp -r do tema (sem
  mudanca em %install/%files). Item 16 (revert map).

* Sat Sep 05 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.33.alpha33
- Tema Plasma proprio (FEAT-91 frente D, D4 -- prova 1): novo desktoptheme
  CapivaraOS em /usr/share/plasma/desktoptheme/CapivaraOS. Formas proprias
  (nine-patch FrameSvg) para o fundo do painel (a "cara" da barra), fundo de
  menus/plasmoides/dialogos e balao de dica, na paleta verde (surface #1E231A,
  borda #2A3122, dica em #12160F; cantos arredondados r=6). O arquivo "colors"
  do tema replica o esquema CapivaraOS, entao TODO widget nao redesenhado (botao,
  slider, etc.) cai no Breeze recolorido pela NOSSA paleta. Selecionado no
  post-theme.ks (plasmarc [Theme] name=CapivaraOS) + /etc/skel/.config/plasmarc
  + /etc/xdg/plasmarc (%posttrans, para valer na sessao LIVE). Aposenta o tema
  Plasma do WhiteSur (3a das 4 superficies; falta so o GTK). Botao/campo/listitem
  proprios ficam para a prova 2. Item 16 (revert map). WhiteSur segue como
  fallback (git clone ainda no build; removido em D5).

* Sat Sep 05 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.32.alpha32
- Decoração Aurorae: os botões da janela (círculos coloridos) agora ficam SEMPRE
  com a cor, tanto na janela em foco quanto fora de foco. Antes o estado de
  janela inativa (inactive-center) era um círculo cinza -> os botões pareciam
  "perder a cor" quando a janela não estava em foco, só reacendendo no hover.
  Agora inactive-center usa a cor da marca (fechar vermelho / minimizar âmbar /
  maximizar/restaurar verde); o glifo (× – + / quadradinho) continua aparecendo
  só no hover, por dentro do círculo colorido. Estado "deactivated" (ação
  indisponível) segue cinza, que é a semântica correta. Item 13 (revert map).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.31.alpha31
- Correção: identidade visual agora aplica também na sessão LIVE. Diagnóstico
  (grep no liveuser): a sessão live NÃO herda /etc/skel/.config -> o esquema de
  cores CapivaraOS e a decoração de janela não estavam sendo aplicados no live
  (só o accent, que já vinha do /etc/xdg). Correção: gravamos ColorScheme=
  CapivaraOS, a decoração Aurorae (library aurorae.v2 + theme + ButtonsOnLeft=XIA)
  e o perfil padrão do Konsole no /etc/xdg (padrão do sistema, lido por todos os
  usuários -- live e instalado), via kwriteconfig no %posttrans. Skel mantido
  como reforço para o sistema instalado. Ver docs/REVERT-CORES-VERDE.md.
- Rótulo do preview alpha30 -> alpha31 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.30.alpha30
- Correção: a decoração de janela própria agora carrega no boot da live (antes
  caía no Breeze). A library correta do kwinrc é org.kde.kwin.aurorae.v2 (com
  .v2) -- sem isso o KWin do Plasma 6 nao carrega o Aurorae. Descoberto lendo o
  valor que o KCM grava. Corrigido no capivaraos-post-theme.ks (FEAT-91 D3).
- Botões da janela à ESQUERDA, estilo macOS (ButtonsOnLeft=XIA / ButtonsOnRight
  vazio), coerente com o layout topo+dock e os círculos coloridos da marca.
- Konsole com identidade CapivaraOS (FEAT-91 frente D): novo esquema de cores
  /usr/share/konsole/CapivaraOS.colorscheme (fundo #12160F + verde da marca +
  ANSI da paleta) e perfil /usr/share/konsole/CapivaraOS.profile (FiraCode Nerd
  Font); perfil padrão apontado em /etc/skel/.config/konsolerc.
- Rótulo do preview alpha29 -> alpha30 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.29.alpha29
- Decoração de janela PRÓPRIA (FEAT-91 frente D, D3 - prova p/ avaliação): novo
  tema Aurorae /usr/share/aurorae/themes/CapivaraOS (arte original GPL-3.0):
  titlebar na cor da paleta, cantos arredondados, botões como círculos coloridos
  da marca (fechar vermelho / minimizar âmbar / maximizar-restaurar verde
  #15B22C, glifo no hover), botões à esquerda (topo/dock). Selecionada no
  capivaraos-post-theme.ks (kwinrc theme=__aurorae__svg__CapivaraOS). O tema
  Plasma (painel) do WhiteSur segue por ora. Prova sujeita a ajuste após teste
  em VM. Ver docs/BRIEF-TEMA-CAPIVARAOS.md.
- Rótulo do preview alpha28 -> alpha29 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.28.alpha28
- Esquema de cores PROPRIO do CapivaraOS (FEAT-91 frente D, fatia D1): novo
  /usr/share/color-schemes/CapivaraOS.colors (derivado do Breeze Dark do KDE,
  LGPL-2.0-or-later, com neutros da paleta ~#12160F e accent/selecao/foco no
  verde da marca #15B22C). kdeglobals passa a ColorScheme=CapivaraOS (/etc/skel
  + reforco no capivaraos-post-theme.ks), aposentando a dependencia do esquema
  de cores do WhiteSur. As FORMAS do WhiteSur (decoracao Aurorae + tema Plasma)
  seguem por ora -- proximas fatias da frente D dependem de design. Reversivel;
  ver docs/REVERT-CORES-VERDE.md.
- Rotulo do preview alpha27 -> alpha28 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.27.alpha27
- Revertida a animacao da capivara no splash do Plymouth (Path C do alpha26): a
  logo do boot/desligamento volta a ser ESTATICA, por decisao de design. Removido
  o gingado do refresh_callback e o contador logo.tick. Boot continua verde
  (spinner #15B22C + fundo #12160F) e o accent do login segue verde. A "capivara
  andando de verdade" (Path A, walk-cycle) segue como ideia futura dependente de
  arte, se um dia for retomada.
- Rotulo do preview alpha26 -> alpha27 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.26.alpha26
- Capivara com movimento no boot/desligamento (FEAT-91 frente C, Path C): a logo
  do splash do Plymouth ganha um gingado sutil de "andar no lugar" -- bob
  vertical + leve sway lateral, animado no refresh_callback via Math.Sin (so
  reposiciona o sprite, sem re-render). NAO e um walk-cycle real (isso exige
  quadros desenhados da capivara andando -- Path A, dependente de arte); e uma
  aproximacao ate a arte existir. Reversivel; ver docs/REVERT-CORES-VERDE.md.
- Rotulo do preview alpha25 -> alpha26 (ISO/os-release).

* Fri Sep 04 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.25.alpha25
- Login coerente com a paleta (FEAT-91 frente C, fatia final): o accent do
  greeter do plasma-login-manager passa ao verde da marca #15B22C. O greeter
  roda como o usuario "plasmalogin" e le a aparencia de um kdeglobals; gravamos
  [General] AccentColor=21,178,44 + accentColorFromWallpaper=false no fallback do
  sistema /etc/xdg/kdeglobals (merge via kwriteconfig, nao apaga outras chaves).
  Estatico/reversivel; seguro (valor nao-reconhecido nao faz efeito e nunca da
  tela preta -- o preto do BUG-43 era o wallpaper, nao o accent).
- Rotulo do preview alpha24 -> alpha25 (ISO/os-release).

* Thu Sep 03 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.24.alpha24
- Boot coerente com a paleta (FEAT-91 frente C): o spinner do Plymouth passa a
  usar o verde da marca #15B22C (era branco) e o fundo do splash passa ao tom
  escuro da paleta (#12160F). Logo continua branca. So arte/cores no tema
  Plymouth; nenhuma mudanca de logica. Login (accent do formulario) fica p/ uma
  proxima fatia, apos confirmar a alavanca do plasma-login-manager em VM (evita
  regressao de login preto -- BUG-43).
- Rotulo do preview alpha23 -> alpha24 (ISO/os-release).

* Thu Sep 03 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.23.alpha23
- Paleta verde CapivaraOS (FEAT-91 frente B, build de avaliacao): aplica o accent
  verde da marca #15B22C (RGB 21,178,44) ao desktop Plasma. AccentColor +
  accentColorFromWallpaper=false em /etc/skel/.config/kdeglobals (baseline) e
  reforcado no sistema instalado pelo capivaraos-post-theme.ks sobre o esquema de
  cores do WhiteSur. Recolore selecao/foco/realce/controles em todo o desktop,
  mantendo os neutros e o formato "macOS" do WhiteSur intactos. Mudanca puramente
  estatica/declarativa (dados em kdeglobals), sem mutar o plasmashell em runtime.
  Reversivel num unico ponto -- ver docs/REVERT-CORES-VERDE.md.
- Rotulo do preview alpha22 -> alpha23 (ISO/os-release).

* Thu Sep 03 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.22.alpha22
- Reverte o wallpaper dinamico por hora (era o alpha21, NAO lancado). Em teste de
  VM ele quebrava o 1o boot da sessao live: fundo preto e dock ausente. Causa: o
  timer de usuario (Persistent=true) disparava o servico de wallpaper JA no login,
  concorrendo com o script de layout/dock -- duas mutacoes simultaneas no
  plasmashell (plasma-apply-wallpaperimage + evaluateScript) corrompiam a
  containment do desktop. O capivaraos-set-wallpaper volta ao comportamento
  estavel: aplica o wallpaper padrao (Luar) uma vez no 1o login, sem timer nem
  servico de usuario. FEAT-132 parada; identidade dinamica fica p/ outra abordagem
  que nao mexa no plasmashell durante a montagem do 1o boot.
- Bateria visivel por padrao na bandeja (FEAT-128) mantida.
- Rotulo do preview alpha20 -> alpha22 (ISO/os-release); alpha21 pulado.

* Wed Sep 02 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.20.alpha20
- Medidor de bateria visivel por padrao na bandeja do painel superior (FEAT-128):
  movido de hiddenItems para shownItems no layout macos-layout.js, aparecendo no
  canto direito sem o usuario precisar adiciona-lo a mao.
- Rotulo do preview alpha19 -> alpha20 (ISO/os-release).

* Thu Aug 27 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.19.alpha19
- Rótulo do preview alpha18 -> alpha19 (ISO/os-release). Rebuild p/ empacotar o
  COS Dev Center 0.1.8: faixa "Instalados" (mini-lancador) + estado de instalado
  nos cards de Trilhas e Ferramentas de dev. FEAT-90.

* Thu Aug 27 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.18.alpha18
- Rótulo do preview alpha17 -> alpha18 (ISO/os-release). Rebuild p/ empacotar o
  COS Dev Center 0.1.7: Open WebUI vira best-effort no card "Ferramentas de dev"
  (falha de download nao derruba mais o card). FEAT-90 (FEAT-120).

* Thu Aug 27 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.17.alpha17
- Rótulo do preview alpha16 -> alpha17 (ISO/os-release). Sem mudanca de branding;
  rebuild p/ empacotar o COS Dev Center 0.1.6, que fecha o catalogo do Dev Center:
  cards "Ligar GPU" (FEAT-119), "Ferramentas de dev" (FEAT-120) e "GitHub CLI +
  pre-commit" (FEAT-121). FEAT-90.

* Wed Aug 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.16.alpha16
- Rótulo do preview alpha15 -> alpha16 (ISO/os-release). Sem mudanca de branding;
  rebuild p/ empacotar o COS Dev Center 0.1.5 (correcao critica: launcher usa
  /usr/bin/python3, senao a trilha de Python via mise fazia o app fechar no
  import do PySide6). FEAT-90 (FEAT-118).

* Wed Aug 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.15.alpha15
- Rótulo do preview alpha14 -> alpha15 (ISO/os-release). Sem mudanca de branding;
  rebuild p/ empacotar o COS Dev Center 0.1.4: botao "Abrir o Alpaca" + deteccao
  de instalado exigindo Ollama E Alpaca; card "Trilhas de linguagem" (mise).
  FEAT-90 (FEAT-117/FEAT-118).

* Wed Aug 26 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.14.alpha14
- Login PRETO (2a rodada): o drop-in em /etc/plasmalogin.conf.d/ do alpha13 NAO
  surtiu efeito -- o greeter do plasma-login-manager le o wallpaper SO do
  defaults.conf do vendor, nao da cascata do /etc. Fix definitivo (o que
  funcionou ao vivo na VM): reescrever Image/PreviewImage no proprio
  /usr/lib/plasmalogin/defaults.conf p/ o pacote KDE do luar, no %posttrans, e
  reaplicar via %transfiletriggerin quando o plasma-login-manager atualizar.
  Removido o drop-in inutil. BUG-43.

* Tue Aug 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.13.alpha13
- CAUSA RAIZ do login preto (finalmente): o gerenciador de login da ISO e o
  plasma-login-manager (plasmalogin.service), NAO o SDDM. O fundo do greeter dele
  vem de /usr/lib/plasmalogin/defaults.conf, que aponta para
  Image=file:///usr/share/wallpapers/Fedora/ -- pacote de wallpaper que REMOVEMOS
  do seletor no alpha10 (FEAT-105). Sem o pacote, o login ficava PRETO. NAO era
  GPU/GL nem SDDM (por isso as tentativas de FHD e software-render no SDDM nao
  surtiram efeito -- eram no programa errado). Fix: drop-in em
  /etc/plasmalogin.conf.d/10-capivaraos-wallpaper.conf apontando o
  [Greeter][Wallpaper][org.kde.image] para o pacote KDE do luar (mantido). Removida
  a config inutil /etc/sddm.conf.d/10-capivaraos-greeter.conf. FEAT-108.

* Tue Aug 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.12.alpha12
- Login SDDM ainda preto em VM mesmo com o fundo 1080p: o GL do greeter esta
  quebrado demais (ZINK sem Vulkan). Forca o greeter a renderizar por software
  via /etc/sddm.conf.d/10-capivaraos-greeter.conf (GreeterEnvironment=
  QT_QUICK_BACKEND=software,LIBGL_ALWAYS_SOFTWARE=1). So afeta o greeter, nao a
  sessao do usuario; o fundo do login passa a renderizar em qualquer VM/hardware.
  Mantido o fundo 1920x1080. FEAT-108.
- Anaconda dizia "Reinstalar Fedora"/"Instalado atualmente: Fedora Linux 44" ao
  reinstalar sobre um CapivaraOS ja instalado. Causa: o titulo GRUB/BLS e gravado
  pelo kernel-install DURANTE a transacao (os-release ainda do Fedora); o
  %posttrans branda o os-release mas nao regenerava o BLS, e o trigger de
  /usr/lib sai pela guarda. Fix: regenera as entradas BLS no %posttrans, depois
  do os-release branded -> titulo vira "CapivaraOS Marsh ...".

* Tue Aug 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.11.alpha11
- Login SDDM preto em VM: o plasma-login-greeter roda antes do login e
  inicializa o proprio GL; em VM/GL degradado (ZINK sem Vulkan) a textura 4K do
  fundo (a arte do luar e 3840x2160) estoura o GL_MAX_TEXTURE_SIZE e o fundo sai
  preto -- so a UI (texturas pequenas) aparece. A tela de bloqueio funciona por
  rodar DENTRO da sessao. Fix: gera um fundo 1920x1080 dedicado
  (%{_datadir}/capivaraos/sddm-background.png) e aponta o background do
  theme.conf do SDDM para ele (%posttrans + %transfiletriggerin). Lock screen
  segue no luar do pacote. FEAT-108.

* Tue Aug 25 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.10.alpha10
- Seletor de wallpaper: elimina as copias duplicadas do luar. (1) O script
  capivaraos-set-wallpaper passa a aplicar o DIRETORIO do pacote (nao o arquivo)
  -> some o tile de imagem avulsa "1920x1080" separado do "CapivaraOS Luar".
  (2) O default.jxl e symlink para o f44 do Fedora: troca cp -f por
  cp --remove-destination (%posttrans e %transfiletriggerin) para nao escrever
  ATRAVES do link e sobrescrever a arte do Fedora com o luar.
- Remove os wallpapers de marca Fedora do seletor (F44="Fedora Forty-Four",
  Fedora, Default): apaga so os diretorios em %posttrans + %transfiletriggerin
  (nao da para excluir os pacotes: kde-settings-plasma e essencial e
  desktop-backgrounds-kde exige f44-backgrounds-kde). Fica so os 8 do CapivaraOS
  + os neutros do plasma-workspace-wallpapers, com o luar como padrao.

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.9.alpha9
- Rotulo do disco: no alpha8 o relabel JA FUNCIONAVA (o journal mostrava
  "btrfs -> capivaraos" e o findmnt confirmava capivaraos), mas o Dolphin seguia
  mostrando "fedora" cacheado do momento da montagem, porque o udevadm trigger
  recebia "/dev/sda3[/root]" (com o sufixo de subvolume btrfs) -> comando
  invalido, sem refresh. Fix: extrai o device real (sem [subvol]) e emite um
  evento "change" nele para o udev/udisks relerem o rotulo ja no 1o boot.

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.8.alpha8
- Leva de correcoes a partir do 6o feedback do live (alpha7).
- Tela de setup #26 identificada: e o plasma-setup.service (OOBE de 1o boot do
  Plasma: idioma/teclado/usuario), REDUNDANTE com o Anaconda WebUI. Criamos o
  flag /etc/plasma-setup-done no %post (a unit tem
  ConditionPathExists=!/etc/plasma-setup-done) -> nao roda no sistema instalado.
- Tela de BLOQUEIO com o mapa 3D: era o /usr/share/backgrounds/default.jxl
  (desktop-backgrounds-compat). Trocado pelo luar (JXL) no %posttrans + filetrigger
  em /usr/share/backgrounds para reaplicar apos updates. Vira tambem o wallpaper
  padrao da marca. + kscreenlockerrc do skel passa a usar o CAMINHO DE ARQUIVO do
  luar (nao o diretorio do pacote, que a tela de bloqueio nao renderiza sem script).

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.7.alpha7
- Leva de correcoes a partir do 5o feedback do live (alpha6).
- FEAT-108 (CAUSA RAIZ do login): descoberto inspecionando a squashfs da ISO que
  o /usr/share/sddm/themes estava VAZIO -- sddm-breeze (temas breeze/01-breeze-
  fedora) e kde-settings-sddm (Current=) sao deps FRACAS que vinham via
  fedora-release-kde-desktop, que EXCLUIMOS (-fedora-release-kde-desktop). Sem o
  tema, o greeter Plasma caia no fundo padrao do Fedora e QUALQUER edicao de
  theme.conf era inutil (por isso nunca funcionou). Fix: instala sddm-breeze +
  kde-settings-sddm explicitos no %packages -> o tema existe, e o sed do
  %posttrans troca o background para o wallpaper luar. (Ver kickstart.)
- Rotulo do disco: o servico capivaraos-relabel-root estava habilitado mas tinha
  DefaultDependencies=no, rodando cedo demais (antes da raiz regravavel) -> o
  relabel falhava calado. Removido DefaultDependencies=no + log no journal +
  udevadm trigger. Deve reetiquetar a raiz para "capivaraos" no 1o boot.
- Menu de boot da midia: build-all.sh troca "CapivaraOS Marsh 44" pela versao
  real via xorriso + implantisomd5 (so-cosmetico, na midia live).

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.6.alpha6
- Leva de correcoes a partir do 4o feedback do live (alpha5).
- FEAT-104 (fix da logo): o instalador ficou verde no alpha5 mas SEM a logo. O
  index.css do Anaconda WebUI aplica na .logo um filter:invert(1) grayscale(1)
  brightness(2.5) + mix-blend-mode:screen (para a logo SVG do Fedora): isso
  invertia nossa capivara branca para preta e o screen a sumia. Agora o branding
  do Cockpit anula filter/mix-blend-mode na .anaconda .logo e entrega a logo ja
  em branco -> aparece no header verde.
- FEAT-102 (avatar): o avatar do usuario/live passa a ser a capivara BRANCA sobre
  fundo VERDE da marca (#15B22C), no lugar da capivara marrom sobre branco.
- FEAT-108 (fix DEFINITIVO): o login SDDM nunca mudou em NENHUMA versao porque
  todas escreviam theme.conf.user -- e o binario do SDDM (sddm-greeter-qt6) le SO
  o ConfigFile do metadata (theme.conf), nunca um ".user" (confirmado: a string
  ".user" nao existe no binario). Agora editamos in-place o background/logo do
  theme.conf do tema ATIVO (01-breeze-fedora) no %posttrans (depois do sddm-breeze
  instalar) + %transfiletriggerin no diretorio dos temas para reaplicar apos
  updates do sddm-breeze (que revertem o theme.conf). So aparece num sistema
  RECEM-INSTALADO com alpha6+.

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.5.alpha5
- Leva de correcoes a partir do 3o feedback do live (alpha4).
- FEAT-108 (fix REAL): login SDDM continuava com o fundo padrao do Fedora
  (mapa-mundi) porque o tema ATIVO no Fedora 44 KDE e "01-breeze-fedora" (Current=
  no kde-settings-sddm), nao "breeze" -- escreviamos o theme.conf.user no tema
  errado. Agora escreve no tema ativo (01-breeze-fedora) + breeze como fallback,
  com background=luar e logo=capivaraos-white (troca a fedora_whitelogo).
- FEAT-105 (wallpaper): a logo carimbada nas 3 cenas (luar/por-do-sol/dev) subiu
  de 6,5% para 13% da margem inferior, para a dock (que expande lateralmente) nao
  passar por cima dela.
- Rotulo do disco: o Anaconda rotulava a raiz como "fedora". Novo servico de 1o
  boot capivaraos-relabel-root reetiqueta a raiz instalada para "capivaraos"
  (btrfs/ext4 online; nao roda na live; so troca rotulo generico).

* Fri Aug 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.4.alpha4
- Leva de correcoes a partir do feedback do live boot do alpha3.
- FEAT-105 (wallpaper): troca "CapivaraOS Cartoon" por "CapivaraOS Comics" (a
  logo central nao e cortada pelo recorte 16:9). Pacote KDE capivaraos-cartoon ->
  capivaraos-comics.
- FEAT-103 (dock): fixa KeePassXC, Konsole, KAddressBook e KCalc alem dos atuais.
  Alpaca fora (Ollama virou opcional) e Spotify fora (descartado).
- FEAT-102 (avatar): novo capivaraos-set-avatar (autostart de 1o login) registra
  a face da marca no AccountsService via D-Bus, para o SDDM/greeter mostrar a
  capivara no lugar do boneco generico (o ~/.face sozinho nao basta: home 0700
  nao e legivel pelo processo do SDDM).
- FEAT-104 (fix): instalador continuava AZUL porque o CSS anterior era de
  Anaconda GTK, mas a ISO live do Fedora 44 usa o Anaconda WebUI (Cockpit), que
  ignora CSS GTK. Portado o mecanismo do Pup/Snout: branding do Cockpit em
  /usr/share/cockpit/branding/capivaraos (branding.css sobrescreve as variaveis
  PatternFly da cor de marca para o verde #15B22C + logo da capivara). O CSS GTK
  foi mantido apenas como fallback.
- FEAT-105 (fix): elimina a duplicata do seletor do Plasma. Cada wallpaper
  aparecia 2x -- como pacote KDE ("CapivaraOS Luar") E como arquivo solto em
  backgrounds/capivaraos/ (listado pelo nome do arquivo, "capivaraos-wp-*"), que
  ainda era copia identica da imagem ja contida no pacote. Os 8 passam a existir
  SO como pacote KDE; login/bloqueio/desktop apontam para o diretorio do pacote
  luar e SDDM/script para a imagem interna. Cada wallpaper 1x + os padrao do KDE
  (nenhum removido). Bonus: some a copia duplicada de ~69 MB.
- FEAT-89/90: ollama passa de PADRAO para OPCIONAL (instalado no onboarding /
  Central do Desenvolvedor no 1o boot). O ollama + suas deps obrigatorias de GPU
  (rocblas ~974 MB + rocm-hip) somam ~1,9 GB e eram o unico motivo de a raiz do
  live ter subido de 16->24 GiB. Removido do %packages; o cliente Alpaca saiu do
  %post junto (segue o ollama). Raiz baixada para 18 GiB -> requisito de disco do
  instalador cai de ~27 para ~21 GB. Decisao do usuario (reverte a de 19/08).

* Thu Aug 20 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.3.alpha3
- FEAT-105: conjunto de wallpapers refeito. Removidas as 6 fotos CC BY-SA do
  Wikimedia (assinaturas de terceiros) E as 7 de cor solida; o Marsh 2.x passa a
  ter 8 wallpapers EXCLUSIVOS da marca (luar[default]/por-do-sol/dev + 4 abstratos
  + cartoon), 3840x2160. As 3 cenas levam a logo branca padronizada no canto
  (largura 9,5%, margem 5,3%/6,5%). License dos pacotes KDE agora e
  LicenseRef-CapivaraOS-Trademark (marca propria), nao CC. Removidos CREDITOS.txt,
  as tags CC-BY-SA da License do spec e os scripts regen-photo/regen-solid.
- FEAT-108: tela de login (SDDM) e de bloqueio passam a usar o novo wallpaper
  padrao (luar). Mecanismo (theme.conf.user do breeze + kscreenlockerrc no skel)
  ja existia do 1.x; so foi repontado para capivaraos-wp-moonlight.png.
- FEAT-104: branding visual do instalador Anaconda. Barra superior e sidebar
  passam de azul Fedora (#51a2da) para o verde da marca (#15B22C) e a sidebar
  ganha o logo (nome+capivara) branco. Via custom_stylesheet no profile.d
  (sobrescreve o fedora.css herdado) + capivaraos.css + sidebar-logo.png.
- FEAT-103 (fix flatpak): Alpaca separado num comando proprio (instala no
  compose). Spotify DESCARTADO (decisao do usuario): flatpak de extra-data nao
  instala no compose (apply_extra falhava) e nao vale o oneshot de 1o boot.

* Thu Aug 20 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.2.alpha2
- 2a leva de testes, a partir do feedback do live boot do alpha1.
- FEAT-109: corrige a instalacao de VSCodium/mise/starship/lazygit no %post. O
  copr enable montava o chroot como "capivaraos-44" (por ID=capivaraos) e falhava
  calado; agora passa "fedora-NN" explicito e separa o dnf install em dois.
- FEAT-107: remove Dragon Player e K3b (-dragon -k3b).
- FEAT-103 (apps): pre-instala Alpaca (cliente grafico do Ollama) e Spotify via
  Flatpak/Flathub. Cliente Ollama e Spotify escolhidos pelo usuario.
- Identidade visual (avatar liveuser, layout da dock, instalador, SDDM) e os 10
  wallpapers exclusivos ficam para a proxima leva (alpha3).

* Wed Aug 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 2.0.0-0.1.alpha1
- Inicio da linha 2.x ("estacao de dev da era da IA"), construida no repo
  ISOLADO capivaraos-marsh-next. Build de teste/PREVIEW no Fedora 44 -- NAO e
  a linha estavel 1.x (capivaraos-marsh-fedora), que segue recebendo correcoes.
- Versionamento: 2.0.0 fica RESERVADO para o lancamento publico (no rebase p/
  Fedora 45); os previews usam Release 0.N.<estagio> (0.1.alpha1 -> ... -> rc),
  que ordena abaixo do 2.0.0-1 final. VERSION/VARIANT/PRETTY_NAME/issue
  rotulados "(alpha1, preview)" para nunca confundir com release estavel.
- (Codecs RPM Fusion entraram no kickstart via FEAT-88.)

* Tue Aug 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.4-1
- Instala em UEFI real: adiciona /etc/anaconda/profile.d/capivaraos.conf com
  base_profile=fedora. Sem ele o Anaconda nao casava perfil (ID=capivaraos),
  caia em efi_dir=default e o gen_grub_cfgstub falhava no fim da instalacao em
  UEFI ("gen_grub_cfgstub script failed") -- BUG-38. So aparecia em UEFI real;
  VM em modo BIOS/legacy nao pegava. Herdar fedora reusa efi_dir=fedora.
- (kickstart) initramfs de build agora --no-hostonly --no-hostonly-cmdline: o
  sistema instalado passa a achar o disco raiz em hardware com storage diferente
  do build (BUG-40), em vez de cair em emergency mode ("Not all disks have been
  found").

* Fri Aug 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.3-2
- Reconciliacao de licenca/marca (LEG-4): corrige o metadado License: do RPM.
  Antes "CC-BY-SA-4.0 AND MIT" -- (a) marcava MIT sem nada MIT no pacote (codigo
  e config do projeto sao GPLv3, como o LICENSE de topo), (b) varria a identidade
  visual sob CC-BY-SA (contradiz a marca) e (c) omitia CC-BY-SA-3.0 de uma das
  fotos embarcadas. Agora: GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
  AND CC-BY-SA-3.0 AND CC-BY-SA-4.0. Correcao de metadado apenas; a atribuicao
  exigida (CREDITOS.txt + creditos gravados nas imagens) ja estava correta (LEG-3).
- Adiciona TRADEMARK.md: nome/logo CapivaraOS sao marca do projeto (direitos
  reservados); codigo GPLv3; wallpapers fotograficos de terceiros CC BY-SA
  creditados em backgrounds/CREDITOS.txt.

* Wed Aug 12 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.3-1
- Corrige a atribuicao das fotos de Giles Laurent nos wallpapers: a
  licenca CC BY-SA 4.0 do autor exige o texto verbatim "(c) Giles
  Laurent, gileslaurent.com, License CC BY-SA 4.0"; o credito gravado
  antes ("Foto: Giles Laurent - CC BY-SA 4.0") omitia o dominio
  gileslaurent.com exigido. Ajustadas as 3 fotos (ipe, natacao, salto)
  e o CREDITOS.txt. Ver LEG-3.

* Tue Jul 21 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.2-1
- Zona segura nos wallpapers de foto: a logo e o credito de autoria sairam de
  40px/24px das laterais para 250px. Numa tela 4:3 exibindo um wallpaper 16:9
  com preenchimento por zoom ("Escalado e Cortado", padrao do Plasma), o corte
  e de 240px de CADA lado -- logo e credito caiam inteiros na faixa cortada.
  Diagnosticado na spin Pup em VM 4:3, onde o credito aparecia truncado como
  "...ann - CC BY-SA 4.0"; a Marsh tinha exatamente a mesma geometria, entao a
  1.2.1 publicada perde a atribuicao nesses monitores. As fotos sao CC BY-SA e
  a licenca EXIGE atribuicao -- e um problema de licenciamento, nao de layout.
  O deslocamento vertical (+120/+130) nao mudou: existe para manter logo e
  credito acima do dock.
- A arte-mestre backgrounds/CapivaraOS_Logo.png deixa de ser instalada como
  papel de parede: o %install usava glob "*.png" e a levava junto, entao ela
  aparecia no seletor de fundo do Plasma como opcao escolhivel. Diagnosticado
  na spin Pup; as tres tinham o mesmo defeito.
- Sufixo ".marsh" no Release, pelo mesmo motivo do build-rpm.sh (BUG-30):
  torna impossivel uma spin consumir o RPM de outra.

* Sun Jul 19 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.2.1-1
- Nova identidade visual: logo do CapivaraOS trocada (capivara "andando" no
  lugar da sentada) em todos os wallpapers (cor solida + foto), icones,
  logo do "Sobre o Sistema", splash do Plymouth e tela de login SDDM.
- Motivo: a logo anterior tinha semelhanca com um desenho de banco de
  imagens (Vecteezy); a nova e original.
- Wallpapers de cor solida agora sao reproduziveis via
  branding/regen-solid-wallpapers.sh (novo); os de foto continuam via
  branding/regen-photo-wallpapers.sh.
- icons/capivaraos-logo.png passa a ser apenas a capivara (sem o texto
  "CapivaraOS"), como o build sempre pressupos: evita o nome duplicado/
  sobreposto no lancador "Instalar CapivaraOS".
- Wallpapers de foto: marca d'agua e credito subiram (45->120 e 104->130 px
  a partir da base) para nao ficarem atras do dock inferior.
- LOGO= do /etc/os-release passa a apontar para "capivaraos-logo" (sem
  texto). O plasma-welcome desenha esse logo em marca d'agua atras do botao
  "Instalar CapivaraOS" (Live.qml, opacity 0.1), e com o logo completo o
  nome aparecia duplicado por tras do botao. O KCM "Sobre este Sistema"
  nao muda: ele usa LogoPath= do kcm-about-distrorc (capivaraos-full-logo).
- Novo conjunto de icones "capivaraos-head" (so a cabeca da capivara, em
  silhueta branca) e o lancador de aplicativos do dock passa a usa-lo no
  lugar do logo do KDE.

* Fri Jul 17 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.3-1
- Corrige titulo "Fedora Linux" no GRUB apos o primeiro update: o file
  trigger de 1.1.2 vigiava so /etc/os-release (symlink, do
  fedora-release-common) e nunca disparava quando o
  fedora-release-identity-basic -- dono do /usr/lib/os-release, que guarda o
  conteudo real -- era atualizado sozinho. Agora vigia os dois caminhos.
- Corrige ISO saindo com o Fedora 44 GA (~1068 pacotes / 7,4 GiB de update no
  primeiro boot): o anaconda nao expande $releasever nas linhas "repo" do
  kickstart, e o mirrorlist responde 200 + "invalid repo or arch" sem nenhum
  mirror, deixando o repo "updates" vazio silenciosamente. Ver
  kickstart/upstream/fedora-repo.ks.

* Thu Jun 18 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.2-1
- Corrige plasma-welcome aparecendo no primeiro login (chave LastSeenVersion)
- Corrige tema Plymouth sem logo/animacao (plymouth-plugin-script ausente)
- Corrige dock inferior duplicado por alguns segundos apos login
- Adiciona tela do Plymouth para atualizacoes offline com percentual
- Corrige titulo GRUB/BLS revertendo para "Fedora Linux" apos updates do
  sistema (file trigger em /etc/os-release)

* Sun Jun 14 2026 CapivaraOS Project <capivaraos-bot@users.noreply.github.com> - 1.1.0-1
- Versao inicial para Fedora 44 (portado do CapivaraOS Marsh / Debian trixie)
