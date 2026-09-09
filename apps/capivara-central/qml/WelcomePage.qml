// SPDX-License-Identifier: GPL-3.0-or-later
// Tela de boas-vindas: a primeira coisa que o dev vê no 1º boot.
import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.Page {
    id: page

    signal start()

    title: qsTr("Bem-vindo ao CapivaraOS Marsh")
    padding: Kirigami.Units.largeSpacing * 2

    ColumnLayout {
        anchors.centerIn: parent
        width: Math.min(parent.width - Kirigami.Units.largeSpacing * 4,
                        Kirigami.Units.gridUnit * 30)
        spacing: Kirigami.Units.largeSpacing * 2

        Kirigami.Icon {
            Layout.alignment: Qt.AlignHCenter
            source: "org.capivaraos.Central"
            fallback: "applications-development"
            implicitWidth: Kirigami.Units.iconSizes.enormous
            implicitHeight: Kirigami.Units.iconSizes.enormous
        }

        Kirigami.Heading {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            level: 1
            text: qsTr("Sua estação de dev pronta em minutos")
        }

        Controls.Label {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            opacity: 0.85
            text: qsTr("O básico já vem instalado. A Central liga os extras opcionais — "
                     + "IA local, trilhas de linguagem e mais — em um clique, sem terminal.")
        }

        Controls.Button {
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: Kirigami.Units.largeSpacing
            text: qsTr("Começar")
            icon.name: "go-next"
            highlighted: true
            onClicked: page.start()
        }
    }
}
