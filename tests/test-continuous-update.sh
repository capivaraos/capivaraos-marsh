#!/bin/bash
# =============================================================================
# Teste do UPDATE CONTÍNUO dentro da versão (FEAT-111 / FEAT-114).
# =============================================================================
# Prova, ISOLADO num contêiner Fedora 44 e com CHAVE DESCARTÁVEL (nunca a de
# produção), o caminho do dia a dia do update in-place:
#   1. instala um pacote assinado (v1) a partir do nosso repo assinado;
#   2. publicamos a v2 (EVR maior, assinada) e o `dnf update` PEGA a v2;
#   3. um repomd ADULTERADO faz a transação de update ABORTAR (repo_gpgcheck).
#
# Não toca o host. Roda AGORA, sem depender da chave do cofre nem de host. No
# lançamento, o MESMO fluxo é revalidado contra o `testing` publicado de verdade
# (passo 4 do docs/repo/RUNBOOK-PUBLICACAO.md). Ver docs/upgrade/ESTRATEGIA-TESTE.md.
#
# Uso (a partir da raiz do repo):  ./tests/test-continuous-update.sh
# Requer: podman. Baixa a imagem fedora:44 e ferramentas de build no contêiner.
#
# NOTA (dnf5 5.x, F44): `makecache` só AVISA sobre repomd ruim (exit 0); é a
# TRANSAÇÃO (install/update) que aplica o repo_gpgcheck e aborta. O gate é a
# operação de update — é isso que o passo 3 valida.
# =============================================================================
set -euo pipefail
command -v podman >/dev/null || { echo "ERRO: podman necessário" >&2; exit 1; }

podman run -i --rm fedora:44 bash -s <<'CONTAINER'
set -euo pipefail
ok()   { echo "  [OK] $*"; }
fail() { echo "  [FALHA] $*"; exit 1; }
say()  { echo; echo "=== $* ==="; }

say "0. Ferramentas"
dnf install -y --setopt=install_weak_deps=False \
    rpm-build rpm-sign createrepo_c gnupg2 >/dev/null 2>&1 \
    || dnf install -y rpm-build rpm-sign createrepo_c gnupg2 >/dev/null
echo "  dnf5 $(rpm -q --qf '%{version}' dnf5) | $(createrepo_c --version | head -1)"

say "1. Chave DESCARTÁVEL (nunca a de produção)"
cat > /root/kp <<'KP'
%no-protection
Key-Type: RSA
Key-Length: 3072
Name-Real: CapivaraOS TEST throwaway
Name-Email: test@example.invalid
Expire-Date: 0
%commit
KP
gpg --batch --gen-key /root/kp 2>/dev/null
KID=$(gpg --list-keys --with-colons test@example.invalid | awk -F: '/^pub:/{print $5;exit}')
gpg --armor --export "$KID" > /root/pub.asc
printf '%s\n' '%_gpg_name CapivaraOS TEST throwaway' '%_gpg_digest_algo sha512' >> ~/.rpmmacros
ok "chave gerada ($KID)"

# Spec mínimo de um pacote sintético; grava a EVR num arquivo p/ conferência.
mkdir -p ~/rpmbuild/SPECS
cat > ~/rpmbuild/SPECS/capivaraos-testpkg.spec <<'SPEC'
Name:           capivaraos-testpkg
Version:        1.0.0
Release:        %{brel}%{?dist}
Summary:        Pacote sintético de teste do update contínuo (descartável)
License:        MIT
BuildArch:      noarch
%description
Pacote de teste — prova o caminho de update assinado. Não vai para produção.
%install
mkdir -p %{buildroot}/usr/share/capivaraos-testpkg
echo "%{version}-%{release}" > %{buildroot}/usr/share/capivaraos-testpkg/VERSION
%files
/usr/share/capivaraos-testpkg/VERSION
%changelog
* Thu Jan 01 2026 CapivaraOS TEST <test@example.invalid> - 1.0.0
- teste
SPEC

REPO=/root/repo/stable
mkdir -p "$REPO"

# Função: builda a Release N, assina e (re)gera o repo assinado.
publish() {
    local BREL="$1"
    rpmbuild -bb --define "brel ${BREL}" --define "dist %{nil}" \
        ~/rpmbuild/SPECS/capivaraos-testpkg.spec >/dev/null 2>&1
    local RPM
    RPM=$(ls ~/rpmbuild/RPMS/noarch/capivaraos-testpkg-1.0.0-"${BREL}".noarch.rpm)
    rpmsign --addsign "$RPM" >/dev/null 2>&1
    cp -f "$RPM" "$REPO/"
    createrepo_c --quiet "$REPO"
    rm -f "$REPO/repodata/repomd.xml.asc"
    gpg --detach-sign --armor -u "$KID" "$REPO/repodata/repomd.xml"
}

say "2. Publica a v1 (1.0.0-1) e instala a partir do repo assinado"
publish 1
cat > /etc/yum.repos.d/capivaraos-test.repo <<EOF
[capivaraos-test]
name=capivaraos-test
baseurl=file://$REPO
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=file:///root/pub.asc
EOF
dnf -y --disablerepo='*' --enablerepo=capivaraos-test install capivaraos-testpkg >/dev/null 2>&1 \
    || fail "install da v1 falhou"
V1=$(rpm -q --qf '%{version}-%{release}' capivaraos-testpkg)
[ "$V1" = "1.0.0-1" ] && ok "v1 instalada: $V1" || fail "esperava 1.0.0-1, veio $V1"

say "3. Publica a v2 (1.0.0-2) e o \`dnf update\` PEGA a v2"
publish 2
dnf -y --refresh --disablerepo='*' --enablerepo=capivaraos-test upgrade capivaraos-testpkg >/dev/null 2>&1 \
    || fail "dnf update para a v2 falhou"
V2=$(rpm -q --qf '%{version}-%{release}' capivaraos-testpkg)
[ "$V2" = "1.0.0-2" ] && ok "update aplicado: $V1 -> $V2" || fail "esperava 1.0.0-2, veio $V2"
grep -q '1.0.0-2' /usr/share/capivaraos-testpkg/VERSION && ok "conteúdo do arquivo atualizado" || fail "arquivo não atualizou"

say "4. Publica a v3 com repomd ADULTERADO -> update deve ABORTAR (repo_gpgcheck)"
publish 3
# adultera o repomd APÓS assinar: a .asc não bate mais -> transação recusa
printf '<!-- adulterado -->' >> "$REPO/repodata/repomd.xml"
OUT=$(dnf -y --refresh --disablerepo='*' --enablerepo=capivaraos-test upgrade capivaraos-testpkg 2>&1 || true)
V3=$(rpm -q --qf '%{version}-%{release}' capivaraos-testpkg)
if [ "$V3" = "1.0.0-2" ]; then
    ok "update ABORTADO — segue na v2 ($V3); metadado adulterado recusado"
    echo "$OUT" | grep -iq 'signature\|repomd\|GPG\|bad' && ok "dnf sinalizou assinatura/repomd inválido"
else
    fail "update NÃO foi barrado — subiu para $V3 com repomd adulterado!"
fi

say "RESULTADO: TODOS OS TESTES PASSARAM"
CONTAINER
echo
echo "==> test-continuous-update: OK"
