# =============================================================================
# CapivaraOS Marsh — pós-instalação: ajustes finos de branding
# =============================================================================
#
# A maior parte do branding (wallpapers, ícones "Sobre o Sistema", tema
# Plymouth, tela de login SDDM, /etc/os-release, /etc/issue, avatar padrão,
# configuração padrão do Plasma) já é instalada pelo pacote
# `capivaraos-branding` (ver ../rpm/capivaraos-branding.spec), análogo ao que
# os hooks 0010-wallpaper e 0020-desktop faziam no live-build Debian.
#
# Este post-script cobre apenas o que não cabe num pacote RPM: idioma de
# fallback e o atalho "Instalar CapivaraOS" na área de trabalho da sessão
# live.

%post
# ── DM correto: forçar o plasma-login-manager (plasmalogin.service) ──────────
# REGRESSÃO F45 (PROD-113): no F44 o DM ativo era o plasma-login-manager e toda a
# nossa branding do greeter (defaults.conf do plasmalogin) + o autologin do live
# (livesys escreve em /etc/plasmalogin.conf) assumem isso. No F45, os pacotes
# SDDM que instalamos p/ o tema do greeter (sddm-breeze/kde-settings-sddm) fazem
# o SDDM "ganhar" a eleição do display-manager → o SDDM lê /etc/sddm.conf (SEM
# autologin) e a sessão LIVE cai na tela de senha, além de ignorar a branding do
# greeter do plasmalogin. Este %post roda DEPOIS de todos os presets de pacote,
# então é a palavra final: fixamos o display-manager no plasmalogin. (No F44 é
# no-op — já era o DM.) Ver reference_plasmalogin_wallpaper / reference_sddm_theme.
if [ -f /usr/lib/systemd/system/plasmalogin.service ]; then
    systemctl disable sddm.service >/dev/null 2>&1 || true
    systemctl enable plasmalogin.service >/dev/null 2>&1 || true
    # Belt + suspenders: fixa o alias display-manager direto (o enable em chroot
    # nem sempre grava o Alias=display-manager.service).
    ln -sf /usr/lib/systemd/system/plasmalogin.service \
        /etc/systemd/system/display-manager.service
fi

# ── Regera a initramfs com o tema Plymouth do CapivaraOS ────────────────────
# O kernel-core gera /boot/initramfs-*.img durante a transacao de pacotes do
# dnf (no %posttrans/scriptlet do proprio kernel), que roda ANTES do
# %posttrans do pacote capivaraos-branding (que escreve
# /etc/plymouth/plymouthd.conf com Theme=capivaraos). Sem regenerar aqui, a
# initramfs da ISO live continua com o tema padrao do Plymouth (spinner
# generico em fundo preto). Este %post roda depois de toda a transacao de
# pacotes, garantindo que o dracut leia o plymouthd.conf ja atualizado.
#
# --no-hostonly (e --no-hostonly-cmdline) e OBRIGATORIO (BUG-40, comprovado
# 2026-08-17 no Pup). O padrao do dracut no Fedora e hostonly="yes"; como este
# %post roda no BUILD (o dracut enxerga o hardware da MAQUINA DE BUILD), sem
# estes flags o initramfs sai so com os drivers do build. Isso NAO afeta o live
# boot (roda do USB, drivers genericos), mas o SISTEMA INSTALADO herda esse
# mesmo initramfs e, num hardware com storage diferente do build, NAO acha o
# disco raiz -> dracut-initqueue timeout -> "Not all disks have been found" ->
# emergency mode. Caso real: Positivo NTB Q232A (eMMC/Bay Trail): o initramfs
# hostonly tinha nvme (do build) mas NAO tinha sdhci-acpi/sdhci-pci/mmc_block
# (do eMMC do alvo). Generico (--no-hostonly) inclui todos -> boota em qualquer
# hardware. Depois de instalado, updates de kernel regeneram hostonly no
# proprio alvo (correto). NAO reverter para hostonly.
for kver in $(ls /lib/modules); do
    dracut -f --no-hostonly --no-hostonly-cmdline "/boot/initramfs-${kver}.img" "${kver}"
done

# ── Remove o /etc/kernel/cmdline "fantasma" da imagem live (PROD-133) ───────
# BLOCKER do 2.0. Este %post roda no BUILD; o instalador live do Fedora (liveimg)
# COPIA o rootfs da live para o alvo, arrastando junto o /etc/kernel/cmdline que
# nasce aqui no build — com o UUID de raiz do AMBIENTE DE BUILD (inexistente no
# disco do usuario) e SEM rootflags=subvol=root (a raiz e btrfs num subvolume).
# O Anaconda reescreve as entradas BLS do install corretamente (por isso o kernel
# do install boota), mas NAO corrige esse arquivo. Resultado: o kernel-install usa
# esse /etc/kernel/cmdline como molde da linha `options` de TODO kernel novo -> o
# 1o update de kernel gera uma entrada BLS com root inexistente e sem subvol ->
# nao acha /sbin/init -> dracut emergency mode (root vem locked, sem shell de
# resgate). Caso real: VM (Boxes) da comunidade, update 7.2.7 -> 7.2.8, 2026-09-28.
#
# Fix: eliminamos o arquivo (e a variante /usr/lib/kernel/cmdline, por seguranca).
# Sem ele, na proxima atualizacao de kernel o kernel-install deriva a cmdline do
# /proc/cmdline REAL do sistema JA INSTALADO -- que traz root=UUID=<real> ro
# rootflags=subvol=root rhgb quiet corretos, para qualquer layout (btrfs/LUKS/...).
# Ordem de precedencia do kernel-install (man kernel-install): /etc/kernel/cmdline,
# senao /usr/lib/kernel/cmdline, senao /proc/cmdline (sem BOOT_IMAGE=/initrd=).
# E o comportamento do Fedora live padrao, que nao embarca esse arquivo.
# VALIDAR sempre num install limpo: instalar em VM -> rodar 1 update de kernel ->
# conferir a entrada nova (root+rootflags) e o boot.
rm -f /etc/kernel/cmdline /usr/lib/kernel/cmdline

# ── Idioma: pt_BR com fallback para en_US (equivalente ao
# "update-locale LANGUAGE=pt_BR:en_US" do hook 0015-locales) ────────────────
# A diretiva "lang pt_BR.UTF-8" do kickstart já grava LANG=pt_BR.UTF-8 em
# /etc/locale.conf; adicionamos LANGUAGE para que traduções ausentes em
# pt_BR caiam para en_US em vez de en_US "puro" sem fallback.
if [ -f /etc/locale.conf ]; then
    sed -i '/^LANGUAGE=/d' /etc/locale.conf
fi
echo 'LANGUAGE=pt_BR:en_US' >> /etc/locale.conf

# ── Desativa o assistente de primeiro boot do Plasma (plasma-welcome) ───────
# A tela "Iniciar configuração" do plasma-welcome usa um fundo de imagem
# COMPILADO no binário (não personalizável para a identidade do CapivaraOS) e
# exibe branding genérico do KDE (Konqi, cidade isométrica). Removemos seu
# autostart para que o usuário caia direto na área de trabalho já com a
# identidade do CapivaraOS. Feito aqui (e não no RPM) porque roda depois de
# toda a transação de pacotes — garante que o arquivo já exista. O livesys-kde
# já remove esse mesmo autostart na sessão live; aqui cobrimos o sistema
# instalado. (O pacote plasma-welcome continua instalado e pode ser aberto
# manualmente pelo menu, se o usuário quiser.)
rm -f /etc/xdg/autostart/org.kde.plasma-welcome.desktop

# ── Welcome Center do live: forca o estilo QQC2 do Breeze ──────────────────
# Na sessao LIVE o plasma-welcome continua aparecendo (o modulo kded
# kded_plasma_welcome o lanca sempre que detecta ambiente live). Nessa tela o
# botao "Instalar CapivaraOS" vinha com o nome escrito DUAS vezes: uma pelo
# contentItem customizado do ApplicationIcon.qml (o rotulo branco, correto) e
# outra pelo proprio QStyle, que o ToolButton do qqc2-desktop-style pinta no
# background — essa segunda caia bem atras da logo da capivara.
#
#   qqc2-desktop-style/org.kde.desktop/ToolButton.qml:
#       background: StylePrivate.StyleItem {
#           text: controlRoot.Kirigami.MnemonicData.mnemonicLabel
#           properties: { "toolButtonStyle": Qt.ToolButtonTextBesideIcon, ... }
#       }
#
# O ToolButton do estilo org.kde.breeze (qqc2-breeze-style) e 100% QML e nao
# pinta rotulo no background, entao o fantasma some. Como o kded lanca o
# binario direto — KIO::CommandLauncherJob("plasma-welcome") — e nao a linha
# Exec= do .desktop, nao adianta editar o .desktop: trocamos o binario por um
# wrapper que injeta a variavel de ambiente. Afeta SOMENTE o plasma-welcome.
if [ -x /usr/bin/plasma-welcome ] && [ ! -e /usr/bin/plasma-welcome-real ]; then
    mv /usr/bin/plasma-welcome /usr/bin/plasma-welcome-real
    cat > /usr/bin/plasma-welcome << 'WRAPEOF'
#!/bin/sh
# Wrapper do CapivaraOS — ver capivaraos-post-branding.ks.
exec env QT_QUICK_CONTROLS_STYLE=org.kde.breeze /usr/bin/plasma-welcome-real "$@"
WRAPEOF
    chmod 0755 /usr/bin/plasma-welcome
fi

# ── Ícone "Instalar CapivaraOS" — APENAS na sessão live ─────────────────────
# O instalador é fornecido pelo Anaconda live via
# /usr/share/applications/liveinst.desktop (NoDisplay=true). Em sessões live, o
# script livesys-kde (pacote livesys-scripts) copia esse liveinst.desktop para
# a área de trabalho do usuário "liveuser" (e só lá — ele NÃO roda no sistema
# já instalado). Por isso NÃO criamos mais um atalho em /etc/skel/Desktop: isso
# fazia o ícone vazar para os usuários criados na instalação (queremos o ícone
# só no live) e, somado ao liveinst.desktop do livesys, gerava DOIS ícones de
# "Instalar" na área de trabalho live.
#
# Em vez disso, renomeamos/reidentificamos o próprio liveinst.desktop com o
# nome e o ícone do CapivaraOS. Assim o livesys-kde copia um único ícone, já
# com a identidade do CapivaraOS, e somente na sessão live. Mantemos
# NoDisplay=true: o livesys-kde faz o sed para NoDisplay=false ao copiá-lo para
# a área de trabalho live.
if [ -f /usr/share/applications/liveinst.desktop ]; then
    sed -i \
        -e '/^Name\[/d' \
        -e '/^GenericName\[/d' \
        -e '/^Comment\[/d' \
        -e 's/^Name=.*/Name=Instalar CapivaraOS/' \
        -e 's/^GenericName=.*/GenericName=Instalar CapivaraOS/' \
        -e 's/^Comment=.*/Comment=Instala o CapivaraOS permanentemente no computador/' \
        -e 's#^Icon=.*#Icon=/usr/share/pixmaps/capivaraos-white.png#' \
        /usr/share/applications/liveinst.desktop
    # Garante que Name/Icon existam mesmo que as linhas originais tivessem
    # outro formato (algumas versões usam Name[C]= etc.)
    grep -q '^Name=Instalar CapivaraOS' /usr/share/applications/liveinst.desktop || \
        echo 'Name=Instalar CapivaraOS' >> /usr/share/applications/liveinst.desktop
    grep -q '^Icon=/usr/share/pixmaps/capivaraos-white.png' /usr/share/applications/liveinst.desktop || \
        echo 'Icon=/usr/share/pixmaps/capivaraos-white.png' >> /usr/share/applications/liveinst.desktop
fi

%end
