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
dnf -y copr enable atim/starship
dnf -y copr enable atim/lazygit

echo "== [devstation] instala VSCodium, mise, starship, lazygit (critico) =="
dnf install -y codium mise starship lazygit

echo "== [devstation] Semgrep via pipx (binario global em /usr/local/bin) =="
PIPX_HOME=/opt/pipx PIPX_BIN_DIR=/usr/local/bin pipx install semgrep \
    || echo "AVISO: semgrep via pipx falhou (validar no build)"

echo "== [devstation] extensao Continue no VSCodium (best-effort, headless) =="
export HOME=/root
if codium --install-extension Continue.continue --force 2>/dev/null; then
    # replica no /etc/skel para o usuario criado ja receber a extensao
    mkdir -p /etc/skel/.vscode-oss
    cp -a /root/.vscode-oss/. /etc/skel/.vscode-oss/ 2>/dev/null || true
else
    echo "AVISO: pre-instalacao do Continue falhou (onboarding FEAT-90 cobre)"
fi

echo "== [devstation] habilita Flathub =="
flatpak remote-add --if-not-exists flathub \
    https://flathub.org/repo/flathub.flatpakrepo \
    || echo "AVISO: flathub remote-add falhou"

echo "== [devstation] concluido =="

%end
