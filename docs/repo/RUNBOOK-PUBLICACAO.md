# Roteiro da sessão de publicação — update in-place (FEAT-111)

Passo a passo para **ligar** a atualização in-place do CapivaraOS Marsh no
lançamento do 2.0/F45. Tudo já está construído e mesclado; falta só esta sessão
(que exige a **chave privada** do cofre) + o teste real em VM.

> **Guardrail central:** o modelo de confiança é a **assinatura** (GPG), não o
> host. A chave privada só entra na máquina **temporariamente**; remover ao fim.
> Fingerprint da chave pública (já commitada em `keys/RPM-GPG-KEY-capivaraos`):
> `75FA334040FD01504AAD9337E07F78EA407011BD`.

## Pré-requisitos
- Chave **privada** de assinatura no cofre de senhas (tem passphrase).
- `capivaraos-bot` é colaborador (write) do repo `capivaraos/repo` (Pages) — ok.
- `repo.capivaraos.org` no ar (GitHub Pages, HTTPS). Confirmar:
  `curl -sI https://repo.capivaraos.org/RPM-GPG-KEY-capivaraos` → **200**.
- ISO 2.0/F45 já **validada em VM** (instalador, snapper 1º boot, tema, login).
- Ferramentas: `rpmsign`, `createrepo_c`, `gnupg2`, `git`, `rsync`.

## Ordem crítica (não inverter)
1. Repo assinado **no ar** → 2. QA no **testing** → 3. promover **stable** →
4. **só então** embarcar `capivaraos-repos` no `%packages` e rebuildar a ISO.
Embarcar o pacote antes do repo existir faz o `dnf` reclamar de repo inacessível
no sistema instalado/live.

## Passos

### 0. Confirmar o host
```
curl -sI https://repo.capivaraos.org/RPM-GPG-KEY-capivaraos   # espera 200
```

### 1. Reimportar a chave privada (temporária)
Do cofre de senhas (nota segura, texto armored) → importar no gpg:
```
gpg --import /caminho/para/CHAVE-PRIVADA.asc     # pede a passphrase
gpg --list-secret-keys 75FA334040FD01504AAD9337E07F78EA407011BD
```
Garantir `%_gpg_name` em `~/.rpmmacros` = a uid da chave (ver `keys/README.md`).

### 2. Build + assinar + stage no TESTING (rel 45)
```
./build-updates.sh --rel 45 --stage
```
Reconstrói os 4 pacotes próprios (branding, capivara-central, capivaraos-repos,
capivaraos-upgrade) com EVR correto, **assina** e adiciona ao canal **testing**
(via `publish-repo.sh add`). Fica em `out/repo/marsh/f45/x86_64/testing/`.

### 3. Publicar (testing) no Pages e testar integridade NO AR
```
./publish-repo.sh pages --rel 45 --arch x86_64
curl -sI https://repo.capivaraos.org/marsh/f45/x86_64/testing/repodata/repomd.xml       # 200
curl -s  https://repo.capivaraos.org/marsh/f45/x86_64/testing/repodata/repomd.xml.asc   # existe
```
Prova de confiança em contêiner/VM limpo (o mesmo do `tests/test-repo-signing.sh`,
agora contra o host real): apontar o `.repo` p/ testing → instalar um pacote (OK,
`gpgcheck`) → adulterar repomd/pacote → **recusa** (`repo_gpgcheck`).

### 4. QA em VM do fluxo do usuário
Instalar a ISO, `capivaraos-upgrade check` deve ver o repo; o card "Atualizar o
CapivaraOS" (COS Dev Center) aparece quando há versão nova. Rodar um update de
pacote próprio (dentro da versão) ponta a ponta.

### 5. Promover TESTING → STABLE e republicar
```
./publish-repo.sh promote --rel 45 --arch x86_64
./publish-repo.sh pages   --rel 45 --arch x86_64
curl -sI https://repo.capivaraos.org/marsh/f45/x86_64/stable/repodata/repomd.xml        # 200
```

### 6. Embarcar `capivaraos-repos` na ISO (remover o guardrail)
Agora que o repo está no ar: adicionar `capivaraos-repos` ao `%packages` do
kickstart (`kickstart/capivaraos-marsh.ks`) e **rebuildar a ISO**
(`./build-all.sh`). O sistema instalado nasce com o repo de updates configurado.

### 7. Teste REAL de upgrade entre versões em VM (FEAT-115)
Com `marsh/f45/.../stable` publicado: numa VM da linha anterior (F44) OU na 2.0,
rodar `capivaraos-upgrade check` → `download` → `reboot`. Confirmar:
- **snapshot snapper `root` criado ANTES** (depende da config de 1º boot — PROD-118, já feito);
- transação **offline** no reboot; boot na versão nova; branding/login/apps ok;
- rollback pelo snapshot se necessário (`docs/upgrade/README.md`).

### 8. Publicar o fingerprint
Colocar `75FA…11BD` na página de **Segurança** do site/docs (cliente confere),
junto do fpr do Herd (`C852…85C0`).

### 9. Encerrar a chave e os tickets
```
shred -u /caminho/para/CHAVE-PRIVADA.asc
gpg --delete-secret-keys 75FA334040FD01504AAD9337E07F78EA407011BD
```
Mover FEAT-112/113/114/115/116 → **Done** e atualizar a memória.

## Alternativa futura de host
`publish-repo.sh upload` (object storage + CDN) substitui o passo `pages`
repointando o CNAME — **sem tocar nos pacotes** (a assinatura é a mesma). Só
quando os limites do Pages apertarem.
