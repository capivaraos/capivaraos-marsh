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
            globalBusy: backend.busy
            onActivated: {
                logView.clear()
                progressSheet.title = qsTr("Instalando IA local")
                progressSheet.open()
                backend.installAiLocal()
            }
        }

        // Espaço reservado para as próximas levas (desabilitado no MVP).
        Kirigami.AbstractCard {
            Layout.fillWidth: true
            opacity: 0.6
            contentItem: RowLayout {
                spacing: Kirigami.Units.largeSpacing
                Kirigami.Icon {
                    source: "media-playlist-shuffle"
                    implicitWidth: Kirigami.Units.iconSizes.large
                    implicitHeight: Kirigami.Units.iconSizes.large
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Kirigami.Heading { level: 3; text: qsTr("Trilhas de linguagem") }
                    Controls.Label {
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                        opacity: 0.8
                        text: qsTr("Web/JS, Python, Go, Rust, Java… via mise. Em breve.")
                    }
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
