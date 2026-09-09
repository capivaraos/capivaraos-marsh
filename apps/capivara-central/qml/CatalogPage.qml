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

    // Estado dos cards — reavaliado ao terminar cada instalação (onFinished).
    property bool aiInstalled: backend.isAiLocalInstalled()
    property bool gpuEnabled: backend.isGpuEnabled()
    property bool ghReady: backend.isGhReady()
    // Faixa "Instalados" + resumos dos cards de seleção múltipla.
    property var installedApps: backend.installedApps()
    property string langsInstalled: backend.installedLangs()
    property string toolsInstalled: backend.installedDevTools()

    // Reavalia tudo (chamado após cada instalação).
    function refreshState() {
        aiInstalled = backend.isAiLocalInstalled()
        gpuEnabled = backend.isGpuEnabled()
        ghReady = backend.isGhReady()
        installedApps = backend.installedApps()
        langsInstalled = backend.installedLangs()
        toolsInstalled = backend.installedDevTools()
    }

    ColumnLayout {
        spacing: Kirigami.Units.largeSpacing

        // ---- Faixa "Instalados": mini-lançador do que já foi instalado -----
        Kirigami.AbstractCard {
            Layout.fillWidth: true
            visible: page.installedApps.length > 0
            contentItem: ColumnLayout {
                spacing: Kirigami.Units.smallSpacing

                Kirigami.Heading {
                    Layout.fillWidth: true
                    level: 3
                    text: qsTr("Instalados")
                }
                Controls.Label {
                    Layout.fillWidth: true
                    wrapMode: Text.WordWrap
                    opacity: 0.8
                    text: qsTr("Abra aqui o que você já instalou pelo Dev Center.")
                }
                Flow {
                    Layout.fillWidth: true
                    spacing: Kirigami.Units.smallSpacing
                    Repeater {
                        model: page.installedApps
                        delegate: Controls.Button {
                            text: modelData.name
                            icon.name: modelData.icon
                            // Itens não-abríveis (Docker, trilhas) viram chip.
                            flat: !modelData.launch
                            enabled: modelData.launch && !backend.busy
                            onClicked: if (modelData.launch) backend.openApp(modelData.kind)
                        }
                    }
                }
            }
        }

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
            statusText: page.langsInstalled
            globalBusy: backend.busy
            onActivated: langSheet.open()
        }

        Components.ActionCard {
            Layout.fillWidth: true
            heading: qsTr("Ligar GPU")
            description: qsTr("Acelere a IA local com sua placa de vídeo: ROCm (AMD) ou "
                            + "CUDA (NVIDIA). Sem GPU dedicada, a IA continua rodando na CPU.")
            iconName: "preferences-desktop-display"
            actionText: qsTr("Ativar GPU")
            installed: page.gpuEnabled
            globalBusy: backend.busy
            onActivated: {
                logView.clear()
                progressSheet.title = qsTr("Ativando a GPU")
                progressSheet.open()
                backend.enableGpu()
            }
        }

        Components.ActionCard {
            Layout.fillWidth: true
            heading: qsTr("Ferramentas de dev")
            description: qsTr("Complete seu arsenal: VS Code, extensão Cline (IA agentic no "
                            + "editor), Open WebUI (chat web do Ollama) e Docker CE.")
            iconName: "applications-development"
            actionText: qsTr("Escolher ferramentas")
            installed: false
            statusText: page.toolsInstalled
            globalBusy: backend.busy
            onActivated: toolsSheet.open()
        }

        Components.ActionCard {
            Layout.fillWidth: true
            heading: qsTr("GitHub CLI + pre-commit")
            description: qsTr("Configure o gh (GitHub pelo terminal) e um template de "
                            + "pre-commit com verificações de segurança (gitleaks, chaves, ShellCheck).")
            iconName: "git"
            actionText: qsTr("Configurar")
            installed: page.ghReady
            openable: true
            openText: qsTr("Entrar no GitHub")
            globalBusy: backend.busy
            onActivated: {
                logView.clear()
                progressSheet.title = qsTr("Configurando gh + pre-commit")
                progressSheet.open()
                backend.setupGh()
            }
            onOpenRequested: backend.openGhLogin()
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

    // ---- Seleção das ferramentas de dev ----------------------------------
    Kirigami.OverlaySheet {
        id: toolsSheet
        title: qsTr("Ferramentas de dev")

        ColumnLayout {
            implicitWidth: Kirigami.Units.gridUnit * 28
            spacing: Kirigami.Units.smallSpacing

            Controls.Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: qsTr("Escolha o que instalar. VS Code e Docker CE são de sistema "
                         + "(pedem senha); Cline e Open WebUI ficam no seu usuário.")
            }

            Controls.CheckBox { id: cbVscode;    text: qsTr("VS Code (editor da Microsoft)") }
            Controls.CheckBox { id: cbCline;     text: qsTr("Cline — IA agentic no editor (code/codium)") }
            Controls.CheckBox { id: cbOpenwebui; text: qsTr("Open WebUI — chat web do Ollama (podman)") }
            Controls.CheckBox { id: cbDocker;    text: qsTr("Docker CE — containers") }

            Controls.Button {
                Layout.alignment: Qt.AlignRight
                text: qsTr("Instalar selecionadas")
                icon.name: "install"
                highlighted: true
                enabled: !backend.busy && (cbVscode.checked || cbCline.checked
                         || cbOpenwebui.checked || cbDocker.checked)
                onClicked: {
                    var tools = []
                    if (cbVscode.checked)    tools.push("vscode")
                    if (cbCline.checked)     tools.push("cline")
                    if (cbOpenwebui.checked) tools.push("openwebui")
                    if (cbDocker.checked)    tools.push("docker")
                    toolsSheet.close()
                    logView.clear()
                    progressSheet.title = qsTr("Instalando ferramentas de dev")
                    progressSheet.open()
                    backend.installDevTools(tools)
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
            // Reavalia o estado mesmo em falha parcial (ex.: alguns itens do card
            // de ferramentas instalaram e só o Open WebUI não).
            page.refreshState()
        }
    }
}
