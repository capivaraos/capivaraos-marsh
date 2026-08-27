Name:           capivara-central
Version:        0.1.8
Release:        1%{?dist}.marsh
Summary:        COS Dev Center — onboarding do CapivaraOS Marsh

# App próprio (GPLv3); o ícone "COS Dev" (tile CapivaraOS) é marca reservada.
License:        GPL-3.0-or-later AND LicenseRef-CapivaraOS-Trademark
URL:            https://capivaraos.org
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

# UI em QML/Kirigami com backend PySide6; instalações privilegiadas via polkit.
Requires:       python3-pyside6
Requires:       kf6-kirigami
Requires:       kf6-qqc2-desktop-style
Requires:       polkit
Requires:       flatpak
# curl: usado pelo instalador do mise (card "Trilhas de linguagem").
Requires:       curl
# git: template global de hooks do card "GitHub CLI + pre-commit".
Requires:       git
# podman: Open WebUI roda em container rootless (card "Ferramentas de dev").
Requires:       podman
# konsole: terminal para o login interativo do gh (gh auth login).
Requires:       konsole

%description
COS Dev Center é o app de onboarding em português do CapivaraOS
Marsh. No primeiro boot, oferece instalar em um clique os extras opcionais da
estação de desenvolvimento — a começar pelo pacote de IA local (Ollama +
Alpaca + extensão Continue no VSCodium). Interface nativa do KDE Plasma
(Kirigami); as etapas que exigem administrador são autenticadas por polkit.

%prep
%autosetup -n %{name}-%{version}

%build
# Nada a compilar: aplicação Python/QML.

%install
# --- Código da aplicação (Python + QML) ---
install -d %{buildroot}%{_datadir}/%{name}
install -m0644 capivara-central.py %{buildroot}%{_datadir}/%{name}/capivara-central.py
install -m0644 backend.py          %{buildroot}%{_datadir}/%{name}/backend.py
cp -a qml %{buildroot}%{_datadir}/%{name}/qml

# --- Launcher em /usr/bin ---
install -Dm0755 capivara-central %{buildroot}%{_bindir}/capivara-central

# --- Helpers privilegiados/orquestrador em /usr/libexec ---
install -Dm0755 libexec/setup-ai                %{buildroot}%{_libexecdir}/%{name}/setup-ai
install -Dm0755 libexec/install-ai-system       %{buildroot}%{_libexecdir}/%{name}/install-ai-system
install -Dm0755 libexec/setup-langs             %{buildroot}%{_libexecdir}/%{name}/setup-langs
install -Dm0755 libexec/setup-gpu               %{buildroot}%{_libexecdir}/%{name}/setup-gpu
install -Dm0755 libexec/install-gpu-system      %{buildroot}%{_libexecdir}/%{name}/install-gpu-system
install -Dm0755 libexec/setup-devtools          %{buildroot}%{_libexecdir}/%{name}/setup-devtools
install -Dm0755 libexec/install-devtools-system %{buildroot}%{_libexecdir}/%{name}/install-devtools-system
install -Dm0755 libexec/setup-gh                %{buildroot}%{_libexecdir}/%{name}/setup-gh
install -Dm0755 libexec/install-gh-system       %{buildroot}%{_libexecdir}/%{name}/install-gh-system

# --- polkit action ---
install -Dm0644 data/org.capivaraos.central.policy \
    %{buildroot}%{_datadir}/polkit-1/actions/org.capivaraos.central.policy

# --- .desktop + ícone ---
install -Dm0644 data/org.capivaraos.Central.desktop \
    %{buildroot}%{_datadir}/applications/org.capivaraos.Central.desktop
# Icone "COS Dev" (tile arredondado com fundo transparente), varios tamanhos
# nativos para nitidez no menu/dock/barra de titulo.
for S in 48 64 128 256 512; do
    install -Dm0644 data/org.capivaraos.Central-${S}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${S}x${S}/apps/org.capivaraos.Central.png
done

# --- Autostart de 1º boot (via /etc/skel; a Central abre uma vez no 1º login) ---
install -Dm0644 data/org.capivaraos.Central-autostart.desktop \
    %{buildroot}%{_sysconfdir}/skel/.config/autostart/org.capivaraos.Central.desktop

%files
%license LICENSE
%doc README.md
%{_datadir}/%{name}/
%{_bindir}/capivara-central
%{_libexecdir}/%{name}/
%{_datadir}/polkit-1/actions/org.capivaraos.central.policy
%{_datadir}/applications/org.capivaraos.Central.desktop
%{_datadir}/icons/hicolor/*/apps/org.capivaraos.Central.png
%{_sysconfdir}/skel/.config/autostart/org.capivaraos.Central.desktop

%changelog
* Thu Aug 27 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.8-1.marsh
- Faixa "Instalados" no topo do catalogo: mini-lancador com o que ja foi
  instalado pelo Dev Center — botao Abrir p/ Alpaca, VS Code, Open WebUI
  (navegador em :3000) e gh; Docker e as trilhas aparecem como chip.
  backend.installedApps()/openApp().
- Cards de selecao multipla agora mostram o que ja esta instalado: Trilhas
  ("Instalado: Python, Go" via mise) e Ferramentas de dev (VS Code/Cline/
  Open WebUI/Docker). Novo ActionCard.statusText; refreshState() reavalia tudo
  ao fim de cada instalacao (inclusive em falha parcial).

* Thu Aug 27 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.7-1.marsh
- Ferramentas de dev (FEAT-120): o Open WebUI agora e best-effort — se o
  download da imagem (varios GB) falhar por rede ou falta de espaco, vira AVISO
  e NAO derruba mais o card inteiro (VS Code/Docker/Cline seguem valendo).
  Separa 'podman pull' do 'run' e da uma dica clara (rede/espaco em disco).

* Thu Aug 27 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.6-1.marsh
- Fecha os cards restantes do catalogo (FEAT-90):
  * "Ligar GPU" (FEAT-119): detecta AMD/NVIDIA e instala ROCm ou driver+CUDA
    (RPM Fusion) via polkit; reinicia o ollama p/ usar a GPU. Sem GPU: usa CPU.
  * "Ferramentas de dev" (FEAT-120): folha de selecao — VS Code (repo MS) e
    Docker CE (repo Docker) via polkit; Cline (extensao code/codium) e
    Open WebUI (container rootless podman) por usuario.
  * "GitHub CLI + pre-commit" (FEAT-121): instala gh + pre-commit (Fedora),
    configura template global de hooks + config de exemplo (gitleaks/ShellCheck/
    chaves); botao "Entrar no GitHub" abre gh auth login num terminal.
- Novas polkit actions: enable-gpu, install-devtools, install-gh.
- Requires: git, podman, konsole.

* Wed Aug 26 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.5-1.marsh
- Correcao critica: o launcher passa a usar /usr/bin/python3 (interpretador do
  SISTEMA), nao o "python3" do PATH. Depois de instalar a trilha de Python (mise),
  o "python3" do usuario apontava para um Python SEM PySide6 e o app fechava no
  import (ModuleNotFoundError: No module named 'PySide6'). Afeta qualquer toolchain
  de Python do usuario (mise/pyenv/venv/conda). BUG do COS Dev Center.

* Wed Aug 26 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.4-1.marsh
- Card "Trilhas de linguagem" (FEAT-118): substitui o stub "Em breve". Folha de
  selecao (Node/Python/Go/Rust/Java) que instala via mise por USUARIO (sem root):
  helper setup-langs instala o mise em ~/.local, ativa no bash e roda
  "mise use --global <lang>@latest". Requires: curl (instalador do mise).

* Wed Aug 26 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.3-1.marsh
- Card "IA local": botao "Abrir o Alpaca" quando instalado (abre direto, sem
  cacar no menu). openAiLocal() no backend (flatpak run com.jeffser.Alpaca).
- Deteccao de instalado agora exige Ollama E Alpaca (antes marcava "Instalado"
  so pelo Ollama, mesmo se o Alpaca falhasse) -- se faltar Alpaca, o card volta
  a oferecer instalar.
- Helper: garante o remote Flathub (--if-not-exists) antes de instalar o Alpaca.

* Tue Aug 25 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.2-1.marsh
- Icone "COS Dev": recorte por mascara de retangulo arredondado -> os 4 cantos
  ficam limpos por igual (a sombra deixava resto cinza nos cantos de baixo).

* Tue Aug 25 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.1-1.marsh
- Renomeia o app para "COS Dev Center" (nome exibido; id tecnico segue
  org.capivaraos.Central / capivara-central).
- Novo icone "COS Dev" (tile arredondado com fundo transparente), instalado em
  varios tamanhos nativos (48/64/128/256/512) no hicolor.

* Mon Aug 24 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.0-1.marsh
- MVP: casca do onboarding (Kirigami) + card "IA local" (Ollama + Alpaca +
  extensao Continue), com etapa privilegiada via polkit. FEAT-90.
