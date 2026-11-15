// SPDX-License-Identifier: GPL-3.0-or-later
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
    property int page: 0
    readonly property var pages: [
        { tag: "BIENVENIDO A RENACER", title: "Tu equipo.\nUna nueva etapa.", body: "Un escritorio KDE Plasma cómodo, personalizable y preparado para acompañarte cada día.", detail: "BYPSSD OS · Hecho con ilusión en Valencia", icon: "desktop" },
        { tag: "OFICINA Y EDUCACIÓN", title: "Tus ideas,\nbien presentadas.", body: "Escribe documentos, organiza hojas de cálculo y prepara presentaciones con LibreOffice. Lee tus PDF con Okular.", detail: "Documentos · Cálculo · Presentaciones · PDF", icon: "office" },
        { tag: "CONECTA Y EXPLORA", title: "Abre una ventana\nal mundo.", body: "Navega con Chromium o Firefox. Consulta tus recursos educativos y utiliza tus herramientas web habituales.", detail: "Navegación · Aprendizaje · Herramientas web", icon: "web" },
        { tag: "APLICACIONES CON DISCOVER", title: "Encuentra tu\npróxima herramienta.", body: "Busca e instala aplicaciones desde Discover. La base recibe paquetes de openSUSE y dispone de un canal propio BYPSSD Updates.", detail: "BYPSSD Updates empieza vacío y listo para crecer", icon: "store" },
        { tag: "UN ESCRITORIO A TU MEDIDA", title: "Haz espacio\na tu estilo.", body: "Organiza tus archivos con Dolphin y ajusta el escritorio desde Preferencias del sistema. El amarillo BYPSSD pone el toque final.", detail: "Cuando termine, retira el medio de instalación y reinicia", icon: "style" }
    ]
    function onActivate() { page = 0; }
    function onLeave() { advance.stop(); }
    Timer { id: advance; interval: 10000; repeat: true; running: presentation.activatedInCalamares; onTriggered: presentation.page = (presentation.page + 1) % presentation.pages.length }
    mouseNavigation: false
    arrowNavigation: false
    keyShortcutsEnabled: false
    Slide {
        x: 0; y: 0; width: presentation.width; height: presentation.height
        Rectangle {
            anchors.fill: parent
            color: "#101114"
            Rectangle { width: parent.width * 0.30; height: parent.height; anchors.right: parent.right; color: "#181A1E" }
            Rectangle { width: 5; height: parent.height * 0.56; y: parent.height * 0.18; color: "#FFB800" }
            Item {
                id: content
                anchors.fill: parent
                anchors.margins: Math.max(24, parent.width * 0.055)
                Image { id: logo; source: "logo.png"; width: 44; height: 44; fillMode: Image.PreserveAspectFit }
                Text { anchors.left: logo.right; anchors.leftMargin: 12; anchors.verticalCenter: logo.verticalCenter; text: "BYPSSD OS  /  RENACER"; color: "#FFFFFF"; font.pixelSize: 14; font.bold: true; font.letterSpacing: 1.3 }
                Item {
                    id: story
                    anchors.left: parent.left; anchors.top: logo.bottom; anchors.topMargin: Math.max(20, content.height * 0.08)
                    width: parent.width * 0.66; height: parent.height * 0.66
                    opacity: 1
                    SequentialAnimation { id: reveal; NumberAnimation { target: story; property: "opacity"; to: 0; duration: 120 } NumberAnimation { target: story; property: "opacity"; to: 1; duration: 380 } }
                    Connections { target: presentation; function onPageChanged() { reveal.restart(); } }
                    Text { id: tag; text: presentation.pages[presentation.page].tag; color: "#FFB800"; font.pixelSize: 12; font.bold: true; font.letterSpacing: 1.7 }
                    Text { id: title; anchors.top: tag.bottom; anchors.topMargin: 12; width: parent.width; text: presentation.pages[presentation.page].title; color: "#FFFFFF"; font.pixelSize: Math.min(40, content.width * 0.052); font.bold: true; lineHeight: 1.08 }
                    Text { id: body; anchors.top: title.bottom; anchors.topMargin: 18; width: parent.width; text: presentation.pages[presentation.page].body; color: "#D6D9DF"; font.pixelSize: 16; wrapMode: Text.WordWrap; lineHeight: 1.25 }
                    Text { anchors.top: body.bottom; anchors.topMargin: 20; width: parent.width; text: presentation.pages[presentation.page].detail; color: "#A1A6AF"; font.pixelSize: 12; wrapMode: Text.WordWrap }
                }
                Image { anchors.right: parent.right; anchors.verticalCenter: story.verticalCenter; width: parent.width * 0.25; height: width; source: "icons/" + presentation.pages[presentation.page].icon + ".svg"; fillMode: Image.PreserveAspectFit }
                Row {
                    anchors.left: parent.left; anchors.bottom: parent.bottom; spacing: 7
                    Repeater { model: 5; Rectangle { width: index === presentation.page ? 28 : 8; height: 4; radius: 2; color: index === presentation.page ? "#FFB800" : "#494D55"; Behavior on width { NumberAnimation { duration: 250 } } } }
                }
                Text { anchors.right: parent.right; anchors.bottom: parent.bottom; text: "0" + (presentation.page + 1) + " / 05"; color: "#A1A6AF"; font.pixelSize: 12 }
            }
        }
    }
}
