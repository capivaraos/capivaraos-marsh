// SPDX-License-Identifier: GPL-3.0-or-later
// Card de uma ação opcional do catálogo (título, descrição, ícone e botão).
import QtQuick
import QtQuick.Controls as Controls
import QtQuick.Layouts
import org.kde.kirigami as Kirigami

Kirigami.AbstractCard {
    id: card

    property string heading: ""
    property string description: ""
    property string iconName: "applications-other"
    property string actionText: qsTr("Instalar")
    property bool installed: false
    // Quando instalado, oferece um botão "Abrir" (ex.: abrir o Alpaca).
    property bool openable: false
    property string openText: qsTr("Abrir")
    // Desabilita o botão quando outra tarefa está rodando.
    property bool globalBusy: false

    signal activated()
    signal openRequested()

    contentItem: RowLayout {
        spacing: Kirigami.Units.largeSpacing

        Kirigami.Icon {
            source: card.iconName
            Layout.alignment: Qt.AlignTop
            implicitWidth: Kirigami.Units.iconSizes.large
            implicitHeight: Kirigami.Units.iconSizes.large
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Kirigami.Units.smallSpacing

            Kirigami.Heading {
                Layout.fillWidth: true
                level: 3
                text: card.heading
            }
            Controls.Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                opacity: 0.8
                text: card.description
            }
        }

        // Estado "já instalado" x botão de ação.
        RowLayout {
            Layout.alignment: Qt.AlignVCenter
            spacing: Kirigami.Units.smallSpacing
            visible: card.installed
            Kirigami.Icon {
                source: "emblem-success"
                implicitWidth: Kirigami.Units.iconSizes.small
                implicitHeight: Kirigami.Units.iconSizes.small
            }
            Controls.Label {
                text: qsTr("Instalado")
                opacity: 0.8
            }
        }
        // Abrir o app instalado (só quando instalado e o card suporta abrir).
        Controls.Button {
            Layout.alignment: Qt.AlignVCenter
            visible: card.installed && card.openable
            enabled: !card.globalBusy
            text: card.openText
            icon.name: "media-playback-start"
            onClicked: card.openRequested()
        }
        Controls.Button {
            Layout.alignment: Qt.AlignVCenter
            visible: !card.installed
            enabled: !card.globalBusy
            text: card.actionText
            icon.name: "install"
            highlighted: true
            onClicked: card.activated()
        }
    }
}
