# SPDX-License-Identifier: GPL-3.0-or-later
# Backend da COS Dev Center (CapivaraOS Marsh).
#
# Expõe ações de instalação ao QML e transmite o progresso linha a linha.
# Cada ação roda um script orquestrador (em /usr/libexec/capivara-central)
# via QProcess; a parte que precisa de root é elevada por pkexec DENTRO do
# script (polkit action org.capivaraos.central.setup-ai), então o app em si
# nunca roda como root.

import os
import re
import shutil
import subprocess

from PySide6.QtCore import QObject, Signal, Slot, Property, QProcess

# App-id do Alpaca no Flathub (interface gráfica da IA local).
ALPACA_APP_ID = "com.jeffser.Alpaca"

# Trilhas de linguagem suportadas (ids de ferramenta do mise).
LANG_TRACKS = ("node", "python", "go", "rust", "java")

# Itens do card "Ferramentas de dev".
DEV_TOOLS = ("vscode", "cline", "openwebui", "docker")

# Ferramenta de upgrade de versão in-place (FEAT-115). O card "Atualizar o
# CapivaraOS" (FEAT-116) só aparece quando ela está instalada — sem dependência
# RPM rígida, para não puxar o repo de updates para a ISO antes de o repo existir.
UPGRADE_TOOL = "capivaraos-upgrade"

# Diretório dos helpers. Em produção é /usr/libexec/capivara-central (instalado
# pelo RPM); em desenvolvimento cai para a pasta libexec/ ao lado deste arquivo.
_HERE = os.path.dirname(os.path.abspath(__file__))
LIBEXEC_DIRS = [
    "/usr/libexec/capivara-central",
    os.path.join(_HERE, "libexec"),
]


def _helper(name: str) -> str:
    for d in LIBEXEC_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    # Último recurso: nome cru (deixa o QProcess falhar com erro claro).
    return name


class Backend(QObject):
    """Ponte QML <-> sistema. Uma ação de cada vez (busy)."""

    logLine = Signal(str)        # uma linha de saída do processo
    stepChanged = Signal(str)    # rótulo do passo atual (pt-BR)
    busyChanged = Signal()
    finished = Signal(bool, str)  # (sucesso, mensagem)
    # (upgrade disponível?, versão de destino, pronto para reiniciar/aplicar?)
    upgradeStatus = Signal(bool, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self._proc: QProcess | None = None
        self._action = ""                 # rótulo da tarefa atual (p/ _on_finished)
        self._probe: QProcess | None = None  # sonda de upgrade (não-bloqueante)
        self._upgrade_target = ""         # versão Fedora de destino detectada
        self._upgrade_ready = False       # download já concluído nesta sessão

    # ---- Property busy (para desabilitar botões no QML) -------------------
    def _is_busy(self) -> bool:
        return self._busy

    busy = Property(bool, _is_busy, notify=busyChanged)

    def _set_busy(self, value: bool):
        if self._busy != value:
            self._busy = value
            self.busyChanged.emit()

    # ---- Ações expostas ao QML -------------------------------------------
    @Slot()
    def installAiLocal(self):
        """Instala o pacote de IA local: Ollama + Alpaca + extensão Continue."""
        self._run(_helper("setup-ai"), step="Preparando instalação da IA local…")

    @Slot()
    def openAiLocal(self):
        """Abre o Alpaca (interface gráfica da IA local), sem caçar no menu."""
        if not QProcess.startDetached("flatpak", ["run", ALPACA_APP_ID]):
            # Fallback: launcher .desktop do Flatpak (system).
            QProcess.startDetached("gtk-launch", [ALPACA_APP_ID])

    @Slot("QVariantList")
    def installLangTracks(self, langs):
        """Instala trilhas de linguagem via mise (por usuário, sem root)."""
        picks = [str(x) for x in langs if str(x) in LANG_TRACKS]
        if not picks:
            self.logLine.emit("Nenhuma linguagem selecionada.")
            self.finished.emit(False, "Nenhuma linguagem selecionada.")
            return
        self._run(_helper("setup-langs"),
                  step="Preparando trilhas de linguagem…", args=picks)

    @Slot()
    def enableGpu(self):
        """Liga a aceleração por GPU (ROCm/AMD ou CUDA/NVIDIA) para o Ollama."""
        self._run(_helper("setup-gpu"), step="Preparando a ativação da GPU…")

    @Slot("QVariantList")
    def installDevTools(self, tools):
        """Instala ferramentas de dev (VS Code/Cline/Open WebUI/Docker CE)."""
        picks = [str(x) for x in tools if str(x) in DEV_TOOLS]
        if not picks:
            self.logLine.emit("Nenhuma ferramenta selecionada.")
            self.finished.emit(False, "Nenhuma ferramenta selecionada.")
            return
        self._run(_helper("setup-devtools"),
                  step="Preparando ferramentas de dev…", args=picks)

    @Slot()
    def setupGh(self):
        """Instala/configura gh + pre-commit (template global de hooks)."""
        self._run(_helper("setup-gh"), step="Configurando gh + pre-commit…")

    @Slot()
    def openGhLogin(self):
        """Abre um terminal para o login interativo no GitHub (gh auth login)."""
        # gh auth login é interativo (device flow); precisa de um terminal.
        for term, args in (
            ("konsole", ["-e", "gh", "auth", "login"]),
            ("x-terminal-emulator", ["-e", "gh", "auth", "login"]),
        ):
            if shutil.which(term) and QProcess.startDetached(term, args):
                return
        # Último recurso: tenta o gh direto (pode não achar um TTY).
        QProcess.startDetached("gh", ["auth", "login"])

    @Slot(str)
    def openApp(self, kind: str):
        """Abre um app instalado a partir da seção 'Instalados' do catálogo."""
        if kind == "alpaca":
            self.openAiLocal()
        elif kind == "vscode":
            QProcess.startDetached("code", [])
        elif kind == "openwebui":
            # Garante o container de pé antes de abrir o navegador.
            try:
                subprocess.run(["podman", "start", "open-webui"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               timeout=15)
            except (OSError, subprocess.SubprocessError):
                pass
            QProcess.startDetached("xdg-open", ["http://localhost:3000"])
        elif kind == "gh":
            self.openGhLogin()
        # docker e lang:* não são "abríveis" (daemon / runtimes).

    # ---- Atualização de versão do CapivaraOS (FEAT-116) ------------------
    @Slot()
    def checkUpgrade(self):
        """Sonda, sem bloquear a UI, se há uma nova versão do CapivaraOS. Só faz
        sentido se a ferramenta capivaraos-upgrade (FEAT-115) estiver instalada;
        senão o card fica escondido. `capivaraos-upgrade check` é read-only
        (não baixa nem reinicia)."""
        if shutil.which(UPGRADE_TOOL) is None:
            self.upgradeStatus.emit(False, "", False)
            return
        probe = QProcess(self)
        probe.setProcessChannelMode(QProcess.MergedChannels)
        buf = {"out": ""}

        def drain():
            buf["out"] += bytes(probe.readAllStandardOutput()).decode("utf-8", "replace")

        def done(code, _st):
            target = ""
            for line in buf["out"].splitlines():
                if "destino" in line:
                    m = re.search(r"(\d+)", line)
                    if m:
                        target = m.group(1)
            self._upgrade_target = target
            # Disponível quando o pré-voo aprova (exit 0: repo assinado do destino
            # existe). readyToReboot só vira True após um download nesta sessão.
            self.upgradeStatus.emit(code == 0, target, self._upgrade_ready)
            self._probe = None

        probe.readyReadStandardOutput.connect(drain)
        probe.finished.connect(done)
        self._probe = probe
        probe.start(UPGRADE_TOOL, ["check"])

    @Slot()
    def downloadUpgrade(self):
        """Baixa a transação de upgrade (privilegiado; snapshot + dnf5
        system-upgrade download). Não reinicia."""
        self._run(_helper("setup-upgrade"),
                  step="Baixando a atualização do CapivaraOS…",
                  args=["download"], kind="upgrade-download")

    @Slot()
    def rebootUpgrade(self):
        """Aplica: reinicia no modo offline. Passo terminal — a máquina reinicia
        (o processo pode não retornar)."""
        self._run(_helper("setup-upgrade"),
                  step="Reiniciando para aplicar a atualização…",
                  args=["reboot"], kind="upgrade-reboot")

    # ---- Execução com streaming ------------------------------------------
    def _run(self, program: str, step: str = "", args=None, kind: str = ""):
        if self._busy:
            self.logLine.emit("Já há uma tarefa em andamento; aguarde terminar.")
            return
        self._action = kind
        if step:
            self.stepChanged.emit(step)
        self._set_busy(True)

        args = list(args or [])
        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)  # junta stdout+stderr
        proc.readyReadStandardOutput.connect(lambda: self._drain(proc))
        proc.finished.connect(lambda code, _st: self._on_finished(code))
        proc.errorOccurred.connect(self._on_error)
        self._proc = proc
        self.logLine.emit(f"$ {os.path.basename(program)} {' '.join(args)}".rstrip())
        proc.start("/bin/bash", [program] + args)

    def _drain(self, proc: QProcess):
        data = bytes(proc.readAllStandardOutput()).decode("utf-8", "replace")
        for line in data.splitlines():
            # Passos marcados com o prefixo >>> viram rótulo grande no QML.
            if line.startswith(">>> "):
                self.stepChanged.emit(line[4:].strip())
            self.logLine.emit(line)

    def _on_error(self, err):
        self.logLine.emit(f"Erro ao iniciar o processo ({err}).")

    def _on_finished(self, code: int):
        self._set_busy(False)
        self._proc = None
        action = self._action
        self._action = ""
        if code == 0:
            self.stepChanged.emit("Concluído!")
            if action == "upgrade-download":
                self._upgrade_ready = True
                self.finished.emit(
                    True, "Download da atualização concluído. Reinicie para aplicar.")
                self.upgradeStatus.emit(True, self._upgrade_target, True)
            else:
                self.finished.emit(True, "Instalação concluída com sucesso.")
        else:
            self.stepChanged.emit("Falhou")
            self.finished.emit(False, f"A operação terminou com erro (código {code}).")

    # ---- Consultas simples de estado (para os cards) ---------------------
    @Slot(result=bool)
    def isAiLocalInstalled(self) -> bool:
        """True só quando o pacote está completo: Ollama (motor) E Alpaca
        (interface). Se o Alpaca falhou, o card volta a oferecer instalar."""
        return shutil.which("ollama") is not None and self._alpaca_installed()

    @staticmethod
    def _alpaca_installed() -> bool:
        """True se o Alpaca (Flatpak) está instalado no sistema."""
        try:
            r = subprocess.run(
                ["flatpak", "info", "--system", ALPACA_APP_ID],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=10,
            )
            return r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    @Slot(result=bool)
    def isGpuEnabled(self) -> bool:
        """Aproximação: há suporte de GPU se existir o utilitário da NVIDIA
        (nvidia-smi) ou do ROCm (rocminfo)."""
        return (shutil.which("nvidia-smi") is not None
                or shutil.which("rocminfo") is not None)

    @Slot(result=bool)
    def isGhReady(self) -> bool:
        """True quando o GitHub CLI (gh) já está instalado."""
        return shutil.which("gh") is not None

    # ---- Deteção de instalados (seção "Instalados" + resumos por card) ----
    @staticmethod
    def _lang_installed(lang: str) -> bool:
        """True se a trilha do mise para `lang` tem alguma versão instalada."""
        base = os.path.expanduser(f"~/.local/share/mise/installs/{lang}")
        try:
            return os.path.isdir(base) and bool(os.listdir(base))
        except OSError:
            return False

    @staticmethod
    def _openwebui_present() -> bool:
        """True se existe o container 'open-webui' (rodando ou parado)."""
        try:
            r = subprocess.run(
                ["podman", "ps", "-a", "--format", "{{.Names}}",
                 "--filter", "name=^open-webui$"],
                capture_output=True, text=True, timeout=10,
            )
            return "open-webui" in r.stdout
        except (OSError, subprocess.SubprocessError):
            return False

    @staticmethod
    def _cline_installed() -> bool:
        """True se a extensão Cline (saoudrizwan.claude-dev) está no code/codium."""
        for d in ("~/.vscode-oss/extensions", "~/.vscode/extensions"):
            p = os.path.expanduser(d)
            try:
                if os.path.isdir(p):
                    for name in os.listdir(p):
                        if name.startswith("saoudrizwan.claude-dev"):
                            return True
            except OSError:
                pass
        return False

    @Slot(result="QVariantList")
    def installedApps(self):
        """Apps/itens instalados pelo Dev Center, para a faixa 'Instalados'.
        Cada item: {kind, name, icon, launch}. launch=True vira botão 'Abrir';
        launch=False vira um chip (indicador) — ex.: Docker e as trilhas."""
        apps = []
        if self._alpaca_installed():
            apps.append({"kind": "alpaca", "name": "Alpaca",
                         "icon": "com.jeffser.Alpaca", "launch": True})
        if shutil.which("code"):
            apps.append({"kind": "vscode", "name": "VS Code",
                         "icon": "vscode", "launch": True})
        if self._openwebui_present():
            apps.append({"kind": "openwebui", "name": "Open WebUI",
                         "icon": "internet-web-browser", "launch": True})
        if shutil.which("gh"):
            apps.append({"kind": "gh", "name": "GitHub CLI",
                         "icon": "git", "launch": True})
        if shutil.which("docker"):
            apps.append({"kind": "docker", "name": "Docker",
                         "icon": "application-x-executable", "launch": False})
        for lang in LANG_TRACKS:
            if self._lang_installed(lang):
                apps.append({"kind": "lang:" + lang, "name": lang.capitalize(),
                             "icon": "media-playlist-shuffle", "launch": False})
        return apps

    @Slot(result=str)
    def installedLangs(self) -> str:
        """Resumo (card Trilhas): trilhas de linguagem já instaladas."""
        got = [l.capitalize() for l in LANG_TRACKS if self._lang_installed(l)]
        return ", ".join(got)

    @Slot(result=str)
    def installedDevTools(self) -> str:
        """Resumo (card Ferramentas de dev): ferramentas já presentes."""
        got = []
        if shutil.which("code"):
            got.append("VS Code")
        if self._cline_installed():
            got.append("Cline")
        if self._openwebui_present():
            got.append("Open WebUI")
        if shutil.which("docker"):
            got.append("Docker")
        return ", ".join(got)
