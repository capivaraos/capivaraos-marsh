# =============================================================================
# capivaraos-post-devstation.ks — %post da "estacao de dev" (linha 2.x, FEAT-89)
# =============================================================================
# Instala as ferramentas de dev que NAO estao nos repos do Fedora, a partir de
# repos externos com CHAVE GPG explicita. Os .repo ficam habilitados no sistema
# instalado (updates), o que casa com a pegada de compliance (fonte de cada
# pacote e rastreavel). Ver o mapa de empacotamento na FEAT-89.
#
# >>> PONTOS A VALIDAR NO 1o BUILD (nao da para testar sem compor a ISO) <<<
#  (0) PRE-REQUISITO: este %post usa REDE. Se a composicao rodar o %post sem
#      rede, TODAS as etapas abaixo falham -> nesse caso migrar os 4 pacotes
#      externos para linhas `repo`/`%packages` (instalacao em tempo de build).
#  (1) resolucao + GPG dos repos VSCodium, mise e COPR atim/* ;
#  (2) semgrep via pipx com binario em /usr/local/bin (PATH global) ;
#  (3) extensao Continue no VSCodium headless PODE falhar -> o onboarding
#      (FEAT-90) cobre esse caso, por isso e best-effort/tolerante ;
#  (4) flatpak remote-add do Flathub.
# Etapas criticas (dnf install dos 4 pacotes) FALHAM alto de proposito, para a
# gente descobrir problema de repo/GPG ja no build. As nao-criticas sao
# tolerantes (|| ...) para nao quebrar a ISO por um solucos de rede.
# =============================================================================
%post --log=/var/log/capivaraos-post-devstation.log

# ---------------------------------------------------------------------------
# CODECS (RPM Fusion) — movido do %packages para ca (FEAT-88). Habilitar RPM
# Fusion no BUILD (payload) forcava a troca ffmpeg-free -> ffmpeg, que a
# transacao do compose nao faz sozinha (sem --allowerasing) e QUEBRAVA o build
# (PayloadInstallationError). Aqui o swap e explicito. Tolerante: se faltar
# rede, a ISO ainda sai (so sem os codecs extras). VALIDAR no build.
# ---------------------------------------------------------------------------
echo "== [codecs] habilita RPM Fusion free+nonfree =="
dnf install -y \
    "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm" \
    "https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm" \
    || echo "AVISO: rpmfusion-release falhou (sem rede no %post?)"

echo "== [codecs] troca ffmpeg-free -> ffmpeg (full) =="
dnf swap -y ffmpeg-free ffmpeg --allowerasing || echo "AVISO: swap ffmpeg falhou"

echo "== [codecs] gstreamer freeworld + libav =="
dnf install -y gstreamer1-plugins-bad-freeworld gstreamer1-plugins-ugly \
    gstreamer1-libav || echo "AVISO: gstreamer freeworld falhou"

echo "== [devstation] pre-reqs: dnf-plugins-core + pipx =="
dnf install -y dnf-plugins-core pipx

echo "== [devstation] repo VSCodium (paulcarroty) =="
cat > /etc/yum.repos.d/vscodium.repo << 'EOF'
[vscodium]
name=VSCodium
baseurl=https://download.vscodium.com/rpms/
enabled=1
gpgcheck=1
gpgkey=https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/-/raw/master/pub.gpg
metadata_expire=1h
EOF

echo "== [devstation] repo mise (jdx) =="
cat > /etc/yum.repos.d/mise.repo << 'EOF'
[mise]
name=mise
baseurl=https://mise.jdx.dev/rpm
enabled=1
gpgcheck=1
gpgkey=https://mise.jdx.dev/gpg-key.pub
EOF

echo "== [devstation] COPR atim/starship + atim/lazygit =="
# GOTCHA (alpha1): com ID=capivaraos no os-release, o plugin copr do dnf monta o
# nome do chroot a partir de ID+VERSION_ID -> pediu "capivaraos-44-x86_64", que
# NAO existe no COPR (so "fedora-44-x86_64"). Os `copr enable` falhavam em
# silencio e starship/lazygit saiam sem repo ("No match" no install). Fix:
# passar o chroot fedora explicito. Mesma familia do ID=capivaraos do EFI.
COPR_CHROOT="fedora-$(rpm -E %fedora)-$(uname -m)"
dnf -y copr enable atim/starship "$COPR_CHROOT"
dnf -y copr enable atim/lazygit "$COPR_CHROOT"

# Instala em DOIS comandos de proposito: no alpha1 um unico `dnf install codium
# mise starship lazygit` abortava a transacao INTEIRA por causa do "No match" de
# starship/lazygit, levando junto codium e mise (que estavam OK). Separado, um
# tropeco do COPR nao derruba o editor.
echo "== [devstation] instala VSCodium + mise (repos proprios, critico) =="
dnf install -y codium mise

echo "== [devstation] instala starship + lazygit (COPR atim, critico) =="
dnf install -y starship lazygit

echo "== [devstation] Semgrep via pipx (binario global em /usr/local/bin) =="
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install semgrep \
    || echo "AVISO: semgrep via pipx falhou (validar no build)"

echo "== [devstation] Continue: adiado para o onboarding (FEAT-90) =="
# NAO rodar o codium (Electron) aqui: rodar o VSCodium como root no %post cria
# /run/user/0 e deixa processo pendurado, o que QUEBRA o unmount do
# livemedia-creator no cleanup (novirt) -> "Image creation failed". A extensao
# Continue e instalada no 1o login do usuario pelo onboarding (FEAT-90), que e
# o lugar certo.

echo "== [devstation] habilita Flathub =="
flatpak remote-add --if-not-exists flathub \
    https://flathub.org/repo/flathub.flatpakrepo \
    || echo "AVISO: flathub remote-add falhou"

# ---------------------------------------------------------------------------
# Alpaca (FEAT-103): cliente grafico do Ollama. MOVIDO para o onboarding
# (FEAT-90) junto com o ollama (2026-08-21): como o ollama saiu do base para
# enxugar a ISO, seu cliente grafico nao faz sentido pre-instalado (ficaria sem
# backend) e o flatpak dele ainda puxa runtime pesado. O bundle de IA local
# (ollama + Alpaca + Continue) e instalado no 1o login pela Central do
# Desenvolvedor. Flathub segue habilitado acima para o onboarding usar.
# (Spotify ja havia sido DESCARTADO em 2026-08-20.)

# NOTA: NAO usar 'loginctl terminate-user root' aqui. Em --no-virt o %post
# compartilha o systemd/logind do HOST, entao terminate-user root MATA o
# proprio processo do build (visto como "Terminated" no 4o build). A causa do
# /run/user/0 pendurado era o codium (Electron), ja removido acima -- nao ha
# necessidade de limpeza defensiva.

echo "== [devstation] concluido =="

%end
