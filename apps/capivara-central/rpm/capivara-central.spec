Name:           capivara-central
Version:        0.1.1
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
install -Dm0755 libexec/setup-ai           %{buildroot}%{_libexecdir}/%{name}/setup-ai
install -Dm0755 libexec/install-ai-system  %{buildroot}%{_libexecdir}/%{name}/install-ai-system

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
* Tue Aug 25 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.1-1.marsh
- Renomeia o app para "COS Dev Center" (nome exibido; id tecnico segue
  org.capivaraos.Central / capivara-central).
- Novo icone "COS Dev" (tile arredondado com fundo transparente), instalado em
  varios tamanhos nativos (48/64/128/256/512) no hicolor.

* Mon Aug 24 2026 CapivaraOS Bot <capivaraos-bot@users.noreply.github.com> - 0.1.0-1.marsh
- MVP: casca do onboarding (Kirigami) + card "IA local" (Ollama + Alpaca +
  extensao Continue), com etapa privilegiada via polkit. FEAT-90.
