// SPDX-License-Identifier: GPL-3.0-or-later
// Janela principal da COS Dev Center.
import QtQuick
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.ApplicationWindow {
    id: root

    title: qsTr("COS Dev Center")
    width: Kirigami.Units.gridUnit * 44
    height: Kirigami.Units.gridUnit * 32
    minimumWidth: Kirigami.Units.gridUnit * 30
    minimumHeight: Kirigami.Units.gridUnit * 24

    // Sem sidebar global: é um fluxo de onboarding, então usamos o pageStack.
    // Coluna ÚNICA: numa janela larga o pageStack mostraria a boas-vindas e o
    // catálogo lado a lado (2 colunas), fazendo o "Começar" parecer que não
    // navega. Em coluna única ele desliza a tela cheia p/ o catálogo, com botão
    // de voltar no cabeçalho.
    pageStack.globalToolBar.style: Kirigami.ApplicationHeaderStyle.ToolBar
    pageStack.columnView.columnResizeMode: Kirigami.ColumnView.SingleColumn
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
