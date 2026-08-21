# capivaraos-branding — identidade visual do CapivaraOS Marsh (Fedora)
#
# Reimplementa em formato RPM o que os hooks do live-build faziam no
# CapivaraOS Marsh (Debian):
#   - 0010-wallpaper.hook.chroot  -> wallpapers, pacotes de wallpaper KDE,
#                                     script de aplicação no primeiro login
#   - 0020-desktop.hook.chroot    -> os-release, issue, plymouth, ícones
#                                     "Sobre o sistema", avatar, layout macOS
#
# O tema WhiteSur (GTK/KDE) e o ajuste fino do layout estilo macOS que
# dependem dele continuam em kickstart/capivaraos-post-theme.ks, pois
# exigem git clone de repositórios externos durante o build da imagem.

Name:           capivaraos-branding
Version:        2.0.0
# Sufixo ".marsh": as tres spins constroem um pacote com este MESMO Name e
# compartilham ~/rpmbuild, entao sem ele duas spins na mesma Version-Release
# geram nomes de arquivo identicos -- ja causou dois incidentes (ver BUG-30).
# Com o sufixo a colisao e impossivel por construcao.
Release:        0.7.alpha7%{?dist}.marsh
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

# ── 2b. Ícones hicolor "capivaraos-head" (só a cabeça da capivara) ──────────
# Usado como ícone do lançador de aplicativos (kickoff) no dock, no lugar do
# logo do KDE. Fonte: icons/capivaraos-head.png (215x215, canvas quadrado) —
# silhueta BRANCA, para combinar com o painel/dock escuro do Breeze Dark.
for SIZE in 16 22 24 32 48 64 96 128 256 512; do
    mkdir -p "build/icons/hicolor/${SIZE}x${SIZE}/apps"
    convert icons/capivaraos-head.png -resize "${SIZE}x${SIZE}" \
        "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-head.png"
done

# ── 3. Ícone branco para a área de trabalho ("Instalar CapivaraOS" etc) ─────
mkdir -p build/pixmaps
convert icons/capivaraos-logo.png -fill white -colorize 100% \
    -resize 256x256 build/pixmaps/capivaraos-white.png

# ── 4. Avatar padrão (.face): capivara BRANCA sobre fundo VERDE da marca ─────
# (pedido do usuario: avatar do live user / SDDM = fundo verde + logo branca,
# no lugar da capivara marrom sobre branco). Recorta so a capivara da arte-
# mestre, pinta de branco (colorize preservando o alfa) e poe sobre quadrado
# verde #15B22C. Exibido em circulo pelo greeter -> o quadrado verde preenche.
convert backgrounds/CapivaraOS_Logo.png -crop 1536x600+0+0 +repage -trim +repage \
    -colorspace sRGB -fill white -colorize 100% \
    -gravity center -background '#15B22C' -extent 1700x1700 \
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

# Spinner branco (arco girando) exibido logo abaixo da logo no splash.
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
# o conjunto do Marsh 2.x passa a ser exatamente estes 8. As 3 cenas (luar/por-do-
# sol/dev) levam a logo branca padronizada no canto; as abstratas ja trazem a
# marca no proprio desenho.
create_kde_wallpaper_pkg "capivaraos-luar"       "CapivaraOS Luar"       backgrounds/capivaraos-wp-moonlight.png
create_kde_wallpaper_pkg "capivaraos-por-do-sol" "CapivaraOS Pôr do Sol" backgrounds/capivaraos-wp-sunset.png
create_kde_wallpaper_pkg "capivaraos-dev"        "CapivaraOS Dev"        backgrounds/capivaraos-wp-dev.png
create_kde_wallpaper_pkg "capivaraos-abstrato-1" "CapivaraOS Abstrato 1" backgrounds/capivaraos-wp-abstract-1.png
create_kde_wallpaper_pkg "capivaraos-abstrato-2" "CapivaraOS Abstrato 2" backgrounds/capivaraos-wp-abstract-2.png
create_kde_wallpaper_pkg "capivaraos-abstrato-3" "CapivaraOS Abstrato 3" backgrounds/capivaraos-wp-abstract-3.png
create_kde_wallpaper_pkg "capivaraos-abstrato-4" "CapivaraOS Abstrato 4" backgrounds/capivaraos-wp-abstract-4.png
create_kde_wallpaper_pkg "capivaraos-comics"     "CapivaraOS Comics"     backgrounds/capivaraos-wp-comics.png

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
# Os 8 wallpapers da marca sao instalados APENAS como pacotes KDE (bloco
# "Pacotes de wallpaper KDE" abaixo), em %{_datadir}/wallpapers/capivaraos-*/.
# NAO instalamos mais os arquivos soltos em %{_datadir}/backgrounds/capivaraos/:
# (1) o seletor do Plasma lista TANTO os pacotes KDE (com nome bonito, ex.
#     "CapivaraOS Luar") QUANTO os arquivos soltos (pelo nome do arquivo, ex.
#     "capivaraos-wp-moonlight") -> cada wallpaper aparecia DUPLICADO no seletor.
# (2) o arquivo solto era uma copia identica da imagem que ja vai dentro do
#     pacote (contents/images/1920x1080.png) -> ~69 MB duplicados no sistema.
# Eliminando os soltos, cada wallpaper aparece 1x (o pacote) e some a duplicata,
# mantendo os 8 do CapivaraOS + os wallpapers padrao do KDE. Login/bloqueio/
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
    install -m 0644 "build/icons/hicolor/${SIZE}x${SIZE}/apps/capivaraos-head.png" \
        %{buildroot}%{_datadir}/icons/hicolor/${SIZE}x${SIZE}/apps/
done

# ── Pacotes de wallpaper KDE ─────────────────────────────────────────────────
install -d %{buildroot}%{_datadir}/wallpapers
cp -r build/wallpapers/* %{buildroot}%{_datadir}/wallpapers/
find %{buildroot}%{_datadir}/wallpapers -type f -exec chmod 0644 {} \;
find %{buildroot}%{_datadir}/wallpapers -type d -exec chmod 0755 {} \;

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

cat > %{buildroot}%{_sysconfdir}/skel/.config/kscreenlockerrc << EOF
[Greeter][Wallpaper][org.kde.image][General]
Image=${DEFAULT_WP_PKG}
FillMode=2
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/kdeglobals << 'EOF'
[General]
ColorScheme=BreezeDark

[KDE]
LookAndFeelPackage=org.kde.breezedark.desktop
SingleClick=false

[KSplash]
Theme=None
EOF

cat > %{buildroot}%{_sysconfdir}/skel/.config/plasmarc << 'EOF'
[Theme]
name=breeze-dark
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

// Bandeja do sistema: mostra apenas volume, redes, layout de teclado e
// notificacoes; os demais itens ficam recolhidos (showAllItems=false) e os
// mais comuns sao explicitamente ocultados.
var systray = topPanel.addWidget("org.kde.plasma.systemtray");
systray.currentConfigGroup = ["General"];
systray.writeConfig("showAllItems", false);
// shownItems / hiddenItems sao StringList -> precisam ser ARRAYS JS (idem
// launchers do dock; string com virgulas nao funciona).
systray.writeConfig("shownItems", [
    "org.kde.plasma.volume",
    "org.kde.plasma.networkmanagement",
    "org.kde.plasma.keyboardlayout",
    "org.kde.plasma.notifications"
]);
systray.writeConfig("hiddenItems", [
    "org.kde.plasma.battery",
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

if command -v plasma-apply-wallpaperimage >/dev/null 2>&1; then
    plasma-apply-wallpaperimage "${DEFAULT_WP_IMG}" >/dev/null 2>&1
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
echo "relabel: raiz SRC=$SRC FST=$FST LABEL_ATUAL='$CUR'"

case "$CUR" in
    capivaraos) echo "relabel: ja e capivaraos"; touch "$MARK"; exit 0 ;;
    fedora|anaconda|localhost-live|"" ) ;;           # generico -> reetiquetar
    *) echo "relabel: rotulo proprio '$CUR', respeitando"; touch "$MARK"; exit 0 ;;
esac

case "$FST" in
    btrfs)          btrfs filesystem label / capivaraos && echo "relabel: btrfs -> capivaraos" ;;
    ext2|ext3|ext4) e2label "$SRC" capivaraos && echo "relabel: $FST -> capivaraos" ;;
    *)              echo "relabel: FST '$FST' nao suportado online, pulando" ;;
esac
# udev reprobe para o rotulo novo aparecer sem reboot
udevadm trigger --settle "$SRC" 2>/dev/null || true
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
        -e "s|^background=.*|background=%{_datadir}/wallpapers/capivaraos-luar/contents/images/1920x1080.png|" \
        -e "s|^logo=.*|logo=%{_datadir}/pixmaps/capivaraos-white.png|" \
        "$TC"
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
VERSION="Marsh 2.0.0 (alpha7, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS Marsh 2.0.0 (alpha7, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Marsh 2.0.0 (alpha7, preview)"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha7, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha7, preview)
EOF

install -d %{_sysconfdir}/xdg
cat > %{_sysconfdir}/xdg/kcm-about-distrorc << 'EOF'
[General]
LogoPath=capivaraos-full-logo
Variant=Marsh 2.0.0 (alpha7, preview)
Website=https://capivaraos.org
UseOSReleaseVersion=true
EOF

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
VERSION="Marsh 2.0.0 (alpha7, preview)"
RELEASE_TYPE=stable
ID=capivaraos
ID_LIKE=fedora
VERSION_ID=44
VERSION_CODENAME=marsh
PLATFORM_ID="platform:f44"
PRETTY_NAME="CapivaraOS Marsh 2.0.0 (alpha7, preview)"
ANSI_COLOR="0;32"
LOGO=capivaraos-logo
CPE_NAME="cpe:/o:capivaraos:capivaraos:44"
DEFAULT_HOSTNAME=capivaraos
HOME_URL="https://capivaraos.org"
DOCUMENTATION_URL="https://capivaraos.org"
SUPPORT_URL="https://capivaraos.org"
BUG_REPORT_URL="https://capivaraos.org"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=44
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=44
VARIANT="Marsh 2.0.0 (alpha7, preview)"
VARIANT_ID=marsh
EOF

cat > %{_sysconfdir}/issue << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha7, preview) \n \l

EOF

cat > %{_sysconfdir}/issue.net << 'EOF'
CapivaraOS Marsh 2.0.0 (alpha7, preview)
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
    grep -q '^background=%{_datadir}/wallpapers/capivaraos-luar' "$TC" && continue
    sed -i \
        -e "s|^background=.*|background=%{_datadir}/wallpapers/capivaraos-luar/contents/images/1920x1080.png|" \
        -e "s|^logo=.*|logo=%{_datadir}/pixmaps/capivaraos-white.png|" \
        "$TC"
done

%files
%license fonts/LICENSE-FiraCode-OFL.txt
%{_datadir}/pixmaps/capivaraos.png
%{_datadir}/pixmaps/capivaraos-logo.png
%{_datadir}/pixmaps/capivaraos-white.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-full-logo.png
%{_datadir}/icons/hicolor/*/apps/capivaraos-head.png
%{_datadir}/wallpapers/capivaraos-*/
%{_datadir}/plymouth/themes/capivaraos/
%{_datadir}/capivaraos/
%{_datadir}/fonts/capivaraos-firacode-nerd/
%{_bindir}/capivaraos-set-layout
%{_bindir}/capivaraos-set-wallpaper
%{_bindir}/capivaraos-set-avatar
%{_bindir}/capivaraos-relabel-root
%{_unitdir}/capivaraos-relabel-root.service
%{_sysconfdir}/xdg/autostart/capivaraos-wallpaper.desktop
%{_sysconfdir}/xdg/autostart/capivaraos-layout.desktop
%{_sysconfdir}/xdg/autostart/capivaraos-avatar.desktop
%{_sysconfdir}/skel/.config/plasma-org.kde.plasma.desktop-appletsrc
%{_sysconfdir}/skel/.config/kscreenlockerrc
%{_sysconfdir}/skel/.config/kdeglobals
%{_sysconfdir}/skel/.config/plasmarc
%{_sysconfdir}/skel/.config/plasma-welcomerc
%{_sysconfdir}/skel/.face
%{_sysconfdir}/skel/.face.icon
%{_sysconfdir}/anaconda/profile.d/capivaraos.conf
%{_datadir}/anaconda/pixmaps/capivaraos.css
%{_datadir}/anaconda/pixmaps/capivaraos/
%{_datadir}/cockpit/branding/capivaraos/

%changelog
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
