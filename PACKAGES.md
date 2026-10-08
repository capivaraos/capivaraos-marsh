# Mapeamento de pacotes: CapivaraOS Marsh (Debian 13/trixie) -> CapivaraOS Marsh (Fedora 44)

Base original: `config/package-lists/capivaraos.list.chroot` e `live.list.chroot`
do CapivaraOS Marsh (Debian, live-build).

Convenções do kickstart Fedora:
- `@nome` = grupo comps
- `@^nome` = grupo "environment" (define o ambiente todo)
- `-pacote` = remove um pacote que viria por dependência/grupo

## ===== SISTEMA BASE =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| task-portuguese | `langpacks-pt_BR`, `glibc-langpack-pt` | Pacotes de idioma pt-BR |
| locales | `glibc-all-langpacks` | Já incluso na base live (fedora-live-base) |
| keyboard-configuration | — | `keyboard br-abnt2` no próprio kickstart |
| console-setup | — | Tratado automaticamente pelo systemd/kbd |
| firmware-linux, firmware-linux-nonfree, firmware-misc-nonfree | `linux-firmware` | Já vem por padrão com o kernel no Fedora |

## ===== BOOTLOADER =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| grub-efi-amd64 | `grub2-efi-x64` | |
| grub-efi-amd64-signed | (incluso em grub2-efi-x64) | Fedora já distribui assinado |
| shim-signed | `shim-x64` | |
| efibootmgr | `efibootmgr` | |
| mokutil | `mokutil` | |
| os-prober | `os-prober` | |

## ===== DESKTOP KDE PLASMA =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| task-kde-desktop | `@^kde-desktop-environment` | Environment group oficial do Spin KDE |
| kde-standard | `@kde-apps`, `@kde-media`, `@kde-pim` | Conjunto equivalente de apps padrão |
| plasma-desktop | (incluso no environment group) | |
| plasma-workspace | (incluso no environment group) | |
| sddm | `sddm` | (incluso no environment group, listado por clareza) |

## ===== AUDIO =====

| Debian (Marsh) | Fedora 44 |
|---|---|
| pipewire | `pipewire` |
| pipewire-pulse | `pipewire-pulseaudio` |
| wireplumber | `wireplumber` |

## ===== INTERNET =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| firefox-esr | `firefox` | Fedora não distribui canal ESR separado |
| thunderbird | `thunderbird` | |
| network-manager | `NetworkManager` | Já vem na imagem live base |
| plasma-nm | `plasma-nm` | |

## ===== OFFICE =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| libreoffice | `@libreoffice` (grupo) | |
| libreoffice-l10n-pt-br | `libreoffice-langpack-pt-BR` | |
| libreoffice-help-pt-br | `libreoffice-help-pt-BR` | |
| libreoffice-kf6 | `libreoffice-kf6` | Integração com KDE Frameworks 6 |

## ===== MIDIA =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| vlc | `vlc` | Disponível nos repos oficiais do Fedora 44. **Sem RPM Fusion, alguns codecs proprietários (ex.: H.264/AAC via patentes) ficam limitados.** Ver nota abaixo. |
| gwenview | `gwenview` | Já incluso via `@kde-media`/`@kde-apps`, listado por clareza |
| gimp | `gimp` | |

## ===== INSTALADOR =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| calamares | **(não usado)** | Decisão: usar Anaconda nativo (`anaconda-live`, `@anaconda-tools`, `@kde-spin-initial-setup`), já integrado à imagem live do Fedora. |
| calamares-settings-debian | **(não usado)** | Limpeza pós-instalação (remoção do usuário live etc.) é feita pelo `livesys-scripts` + Anaconda/Initial Setup, não precisa de scripts Calamares. |

## ===== UTILITARIOS =====

| Debian (Marsh) | Fedora 44 |
|---|---|
| gparted | `gparted` |
| htop | `htop` |
| fastfetch | `fastfetch` |
| curl | `curl` |
| wget | `wget` |
| zip | `zip` |
| unzip | `unzip` |
| rsync | `rsync` |
| ark | `ark` (incluso via kde-apps, listado por clareza) |
| kate | `kate` (incluso via kde-apps, listado por clareza) |
| okular | `okular` (incluso via kde-apps, listado por clareza) |

## ===== DESENVOLVIMENTO =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| git | `git` | |
| nano | `nano` | |
| vim | `vim-enhanced` | |
| build-essential | `@development-tools` | Grupo com gcc, make, etc. |

## ===== FONTES =====

| Debian (Marsh) | Fedora 44 |
|---|---|
| fonts-liberation | `liberation-fonts` |
| fonts-dejavu | `dejavu-fonts-all` |
| fonts-noto | `google-noto-sans-fonts`, `google-noto-serif-fonts`, `google-noto-emoji-fonts` |

## ===== IMPRESSAO =====

| Debian (Marsh) | Fedora 44 |
|---|---|
| cups | `cups` |
| system-config-printer | `system-config-printer` |

## ===== APLICATIVOS PRÓPRIOS DO CAPIVARAOS =====

Pacotes feitos pelo projeto — não têm equivalente Debian (são próprios do CapivaraOS).

| Pacote | Versão | O que é / como entra na ISO |
|---|---|---|
| `capivaraos-branding` | 2.0.0 (série alpha) | Identidade visual: wallpapers, ícones (inclui o ícone do lançador adaptável), tema Plasma/Aurorae, Plymouth, greeter, os-release. Buildado localmente no `build-all.sh`. |
| `capivara-central` | 0.2.x | **COS Dev Center** — onboarding de 1º boot da estação de dev (cards: IA local, trilhas de linguagem, ferramentas de dev, Ligar GPU). QML/Kirigami + PySide6. Buildado localmente. |
| `cos-config` | **0.11.1** | **COS Config Center** — central de configuração do sistema. 9 módulos: codecs/RPM Fusion/Flathub, limpeza de disco, discos ao ligar, tamanho dos logs, diagnóstico, teclado, idioma, firewall, acesso remoto e rede. GTK4. **NÃO é buildado aqui:** vem JÁ ASSINADO do repositório (`repo.capivaraos.org/marsh/f45/x86_64/${COS_CONFIG_CHANNEL}`, padrão `testing`), baixado e verificado (assinatura) no `build-all.sh` passo 3. Épico PROD-5; inclusão na ISO em PROD-141. |
| `capivaraos-repos` | 1.0.0 | Configura o repo de updates assinado (.repo + chave pública em /etc/pki/rpm-gpg). Update in-place (FEAT-111). |
| `capivaraos-upgrade` | 1.0.0 | Motor de upgrade de versão (invólucro auditável do `dnf5 system-upgrade`, com snapshot snapper antes). FEAT-111. |

> O `cos-config` é o único que entra **assinado do repositório** (o mesmo pacote que o usuário recebe por update), em vez de buildado na ISO — a confiança vem da **assinatura verificada** no build. Para promover à produção, trocar `COS_CONFIG_CHANNEL=stable` (gated no PROD-165).

## ===== TEMA MACOS (WHITESUR) =====

| Debian (Marsh) | Fedora 44 | Observações |
|---|---|---|
| sassc | `sassc` | |
| optipng | `optipng` | |
| gtk2-engines-murrine | `gtk-murrine-engine` | |
| gtk2-engines-pixbuf | `gtk2-engines` | Inclui o engine pixbuf |
| appmenu-gtk3-module | **(sem equivalente direto)** | Fedora não empacota `appmenu-gtk-module` para GTK3/4 nos repos oficiais. `appmenu-qt5` existe para apps Qt5. **Efeito**: o menu global no painel superior (estilo macOS) funciona para apps Qt/KDE, mas apps GTK (Firefox, GIMP) não exportam menu para a barra superior — ficam com o menu interno normal. Documentado como limitação conhecida. |

## ===== NOTA SOBRE CODECS / RPM FUSION =====

A lista original do Debian já trazia `firmware-*-nonfree` e dependia dos repos
`contrib`/`non-free`/`non-free-firmware` do Debian para codecs completos no
VLC. No Fedora, o equivalente é o repositório **RPM Fusion** (free + nonfree),
não habilitado por padrão. Optamos por **não habilitar RPM Fusion neste
kickstart** (mesma postura "conservadora" adotada no hook `0030-macos-theme`
do CapivaraOS original, que evita dependências jurídicas extras). O VLC dos
repositórios oficiais do Fedora funciona, mas com suporte a codecs reduzido.

Se decidirmos habilitar RPM Fusion depois, basta adicionar ao kickstart:

```
repo --name=rpmfusion-free --baseurl=https://download1.rpmfusion.org/free/fedora/releases/$releasever/Everything/$basearch/os/
repo --name=rpmfusion-nonfree --baseurl=https://download1.rpmfusion.org/nonfree/fedora/releases/$releasever/Everything/$basearch/os/
```

## ===== live.list.chroot =====

| Debian (Marsh) | Fedora 44 |
|---|---|
| live-boot, live-config, live-config-systemd, systemd-sysv | `livesys-scripts`, `anaconda-live`, `@anaconda-tools`, `dracut-live` (parte do `fedora-live-base`) |
