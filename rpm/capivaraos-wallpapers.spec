# capivaraos-wallpapers (Marsh) — wallpapers da marca, empacotados à parte.
#
# POR QUE ESTE PACOTE EXISTE (ver PROD-187 / PROD-188 no Jira)
# ============================================================
# Ate a 2.0.0 os wallpapers moravam dentro do capivaraos-branding e respondiam
# pela maior parte do peso dele. Como o RPM e republicado inteiro a cada
# mudanca, qualquer correcao de tema obrigava o usuario a rebaixar tudo de novo.
#
# Separando, o branding fica pequeno e os wallpapers sao publicados uma vez so.
# Para isso funcionar, a Version deste pacote e INDEPENDENTE da do branding:
#
#   /!\  NAO acompanhe a Version do capivaraos-branding aqui.
#        Se as duas subirem juntas, o usuario rebaixa as imagens de novo e todo
#        o ganho evapora. So suba a Version DESTE pacote quando uma imagem mudar
#        de verdade. Um subpacote (%%package) do branding NAO serviria: subpacote
#        herda Version-Release do principal, que e justamente o que evitamos.
#
# O capivaraos-branding declara "Requires: capivaraos-wallpapers >= 2.0.0" e
# aponta o wallpaper padrao (DEFAULT_WP_PKG/DEFAULT_WP_IMG) para caminhos
# servidos por aqui. Os dois caminham juntos na mesma transacao do dnf.

Name:           capivaraos-wallpapers
Version:        2.0.0
# Release independente do branding. Ver o aviso acima antes de mexer.
Release:        1%{?dist}.marsh
Summary:        Wallpapers da marca CapivaraOS Marsh

# Arte própria da marca (não é CC do Wikimedia — essas saíram na linha 2.x).
License:        LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
BuildArch:      noarch

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  ImageMagick

%description
Wallpapers exclusivos da marca CapivaraOS, no formato de pacote do KDE Plasma
(aparecem no seletor de papel de parede). Vive separado do capivaraos-branding
para que correções de tema não obriguem cada usuário a rebaixar dezenas de
megabytes de imagem que não mudaram.

%prep
%setup -q

%build
set -e
# ── Pacotes de wallpaper no formato KDE (aparecem no seletor do Plasma) ──
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
install -d %{buildroot}%{_datadir}/wallpapers
cp -r build/wallpapers/* %{buildroot}%{_datadir}/wallpapers/
find %{buildroot}%{_datadir}/wallpapers -type f -exec chmod 0644 {} \;
find %{buildroot}%{_datadir}/wallpapers -type d -exec chmod 0755 {} \;

%files
%{_datadir}/wallpapers/capivaraos-*/

%changelog
* Mon Nov 09 2026 CapivaraOS <contato@capivaraos.org> - 2.0.0-1.marsh
- Pacote novo: wallpapers da marca, antes entregues pelo capivaraos-branding
  (PROD-187). Mesmos wallpapers, mesmos caminhos, imagens inalteradas.
