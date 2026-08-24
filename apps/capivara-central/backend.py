# SPDX-License-Identifier: GPL-3.0-or-later
# Backend da Central do Desenvolvedor (CapivaraOS Marsh).
#
# Expõe ações de instalação ao QML e transmite o progresso linha a linha.
# Cada ação roda um script orquestrador (em /usr/libexec/capivara-central)
# via QProcess; a parte que precisa de root é elevada por pkexec DENTRO do
# script (polkit action org.capivaraos.central.setup-ai), então o app em si
# nunca roda como root.

import os
import shutil

from PySide6.QtCore import QObject, Signal, Slot, Property, QProcess

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self._busy = False
        self._proc: QProcess | None = None

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

    # ---- Execução com streaming ------------------------------------------
    def _run(self, program: str, step: str = ""):
        if self._busy:
            self.logLine.emit("Já há uma tarefa em andamento; aguarde terminar.")
            return
        if step:
            self.stepChanged.emit(step)
        self._set_busy(True)

        proc = QProcess(self)
        proc.setProcessChannelMode(QProcess.MergedChannels)  # junta stdout+stderr
        proc.readyReadStandardOutput.connect(lambda: self._drain(proc))
        proc.finished.connect(lambda code, _st: self._on_finished(code))
        proc.errorOccurred.connect(self._on_error)
        self._proc = proc
        self.logLine.emit(f"$ {os.path.basename(program)}")
        proc.start("/bin/bash", [program])

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
        if code == 0:
            self.stepChanged.emit("Concluído!")
            self.finished.emit(True, "Instalação concluída com sucesso.")
        else:
            self.stepChanged.emit("Falhou")
            self.finished.emit(False, f"A instalação terminou com erro (código {code}).")

    # ---- Consultas simples de estado (para os cards) ---------------------
    @Slot(result=bool)
    def isAiLocalInstalled(self) -> bool:
        """True se o Ollama já está presente (pré-marca o card como pronto)."""
        return shutil.which("ollama") is not None
