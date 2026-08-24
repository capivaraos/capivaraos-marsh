#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Central do Desenvolvedor — app de onboarding pt-BR do CapivaraOS Marsh.
#
# UI em QML/Kirigami (nativa do KDE Plasma); a lógica de instalação fica no
# backend.py (PySide6). Ponto de entrada: carrega qml/main.qml e injeta o
# Backend como contexto "backend".

import os
import sys
import signal

from PySide6.QtCore import QUrl
from PySide6.QtGui import QIcon
from PySide6.QtQml import QQmlApplicationEngine

# Kirigami precisa do estilo QtQuick Controls "org.kde.desktop" no desktop.
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "org.kde.desktop")

# PySide6.QtWidgets fornece o QApplication que o estilo desktop do Kirigami usa
# (ícones nativos, diálogos). Importado depois de setar o estilo.
from PySide6.QtWidgets import QApplication  # noqa: E402

from backend import Backend  # noqa: E402

APP_ID = "org.capivaraos.Central"
_HERE = os.path.dirname(os.path.abspath(__file__))
# QML: instalado em /usr/share/capivara-central/qml (RPM) ou ao lado (dev).
QML_DIRS = [
    "/usr/share/capivara-central/qml",
    os.path.join(_HERE, "qml"),
]


def _qml_main() -> str:
    for d in QML_DIRS:
        p = os.path.join(d, "main.qml")
        if os.path.exists(p):
            return p
    sys.exit("main.qml não encontrado")


def main() -> int:
    # Ctrl+C encerra o app quando rodado no terminal (dev).
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("Central do Desenvolvedor")
    app.setOrganizationName("CapivaraOS")
    app.setDesktopFileName(APP_ID)
    QIcon.setThemeName(QIcon.themeName() or "breeze")
    app.setWindowIcon(QIcon.fromTheme(APP_ID, QIcon.fromTheme("applications-development")))

    engine = QQmlApplicationEngine()
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)
    engine.load(QUrl.fromLocalFile(_qml_main()))
    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
