// SPDX-License-Identifier: GPL-3.0-or-later
// Catálogo de extras opcionais. No MVP há um card funcional (IA local);
// os demais entram nas próximas levas (trilhas mise, GPU, VS Code, etc.).
import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import "components" as Components

Kirigami.ScrollablePage {
    id: page

    title: qsTr("Extras para sua estação")

    // Card de IA local — referenciado para atualizar o estado ao terminar.
    property bool aiInstalled: backend.isAiLocalInstalled()

    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing

        Kirigami.InlineMessage {
            Layout.fillWidth: true
            visible: true
            position: Kirigami.InlineMessage.Header
            text: qsTr("Escolha o que instalar. Pediremos sua senha de administrador "
                     + "quando for necessário.")
        }

        Components.ActionCard {
            Layout.fillWidth: true
            heading: qsTr("IA local")
            description: qsTr("Rode modelos de IA na sua máquina, sem nuvem: Ollama (motor), "
                            + "Alpaca (interface) e a extensão Continue no VSCodium.")
            iconName: "system-run"
            actionText: qsTr("Instalar IA local")
            installed: page.aiInstalled
            openable: true
            openText: qsTr("Abrir o Alpaca")
            globalBusy: backend.busy
            onActivated: {
                logView.clear()
                progressSheet.title = qsTr("Instalando IA local")
                progressSheet.open()
                backend.installAiLocal()
            }
            onOpenRequested: backend.openAiLocal()
        }

        Components.ActionCard {
            Layout.fillWidth: true
            heading: qsTr("Trilhas de linguagem")
            description: qsTr("Instale linguagens sob demanda com o mise (por usuário, "
                            + "sem afetar o sistema): Web/JS (Node.js), Python, Go, Rust, Java.")
            iconName: "media-playlist-shuffle"
            actionText: qsTr("Escolher linguagens")
            installed: false
            globalBusy: backend.busy
            onActivated: langSheet.open()
        }
    }

    // ---- Seleção de trilhas de linguagem ---------------------------------
    Kirigami.OverlaySheet {
        id: langSheet
        title: qsTr("Trilhas de linguagem")

        ColumnLayout {
            implicitWidth: Kirigami.Units.gridUnit * 26
            spacing: Kirigami.Units.smallSpacing

            Controls.Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: qsTr("Escolha as linguagens para instalar via mise. Elas ficam "
                         + "no seu usuário; abra um novo terminal depois de instalar.")
            }

            Controls.CheckBox { id: cbNode;   text: qsTr("Web / JavaScript (Node.js)") }
            Controls.CheckBox { id: cbPython; text: qsTr("Python") }
            Controls.CheckBox { id: cbGo;     text: qsTr("Go") }
            Controls.CheckBox { id: cbRust;   text: qsTr("Rust") }
            Controls.CheckBox { id: cbJava;   text: qsTr("Java") }

            Controls.Button {
                Layout.alignment: Qt.AlignRight
                text: qsTr("Instalar selecionadas")
                icon.name: "install"
                highlighted: true
                enabled: !backend.busy && (cbNode.checked || cbPython.checked
                         || cbGo.checked || cbRust.checked || cbJava.checked)
                onClicked: {
                    var langs = []
                    if (cbNode.checked)   langs.push("node")
                    if (cbPython.checked) langs.push("python")
                    if (cbGo.checked)     langs.push("go")
                    if (cbRust.checked)   langs.push("rust")
                    if (cbJava.checked)   langs.push("java")
                    langSheet.close()
                    logView.clear()
                    progressSheet.title = qsTr("Instalando trilhas de linguagem")
                    progressSheet.open()
                    backend.installLangTracks(langs)
                }
            }
        }
    }

    // ---- Folha de progresso com o log da instalação ----------------------
    Kirigami.OverlaySheet {
        id: progressSheet

        ColumnLayout {
            implicitWidth: Kirigami.Units.gridUnit * 34
            spacing: Kirigami.Units.largeSpacing

            RowLayout {
                Layout.fillWidth: true
                spacing: Kirigami.Units.largeSpacing
                Controls.BusyIndicator {
                    running: backend.busy
                    visible: backend.busy
                }
                Kirigami.Heading {
                    Layout.fillWidth: true
                    level: 3
                    text: stepLabel.text
                }
            }

            Controls.Label {
                id: stepLabel
                visible: false
                text: qsTr("Preparando…")
            }

            Controls.ScrollView {
                Layout.fillWidth: true
                implicitHeight: Kirigami.Units.gridUnit * 14
                Controls.TextArea {
                    id: logView
                    readOnly: true
                    wrapMode: TextEdit.NoWrap
                    font.family: "monospace"
                    text: ""
                }
            }

            Controls.Button {
                Layout.alignment: Qt.AlignRight
                text: backend.busy ? qsTr("Instalando…") : qsTr("Fechar")
                enabled: !backend.busy
                onClicked: progressSheet.close()
            }
        }
    }

    Connections {
        target: backend
        function onLogLine(line) {
            logView.text += line + "\n"
            logView.cursorPosition = logView.length
        }
        function onStepChanged(step) {
            stepLabel.text = step
        }
        function onFinished(ok, message) {
            logView.text += "\n" + message + "\n"
            if (ok)
                page.aiInstalled = backend.isAiLocalInstalled()
        }
    }
}
