// SPDX-License-Identifier: GPL-3.0-or-later
// Janela principal da Central do Desenvolvedor.
import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.ApplicationWindow {
    id: root

    title: qsTr("Central do Desenvolvedor")
    width: Kirigami.Units.gridUnit * 44
    height: Kirigami.Units.gridUnit * 32
    minimumWidth: Kirigami.Units.gridUnit * 30
    minimumHeight: Kirigami.Units.gridUnit * 24

    // Sem sidebar global: é um fluxo de onboarding, então usamos o pageStack.
    pageStack.globalToolBar.style: Kirigami.ApplicationHeaderStyle.ToolBar
    pageStack.initialPage: welcomePage

    WelcomePage {
        id: welcomePage
        onStart: root.pageStack.push(catalogComponent)
    }

    Component {
        id: catalogComponent
        CatalogPage {}
    }
}
