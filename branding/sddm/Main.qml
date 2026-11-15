// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#101217"
    property bool authenticating: false
    property bool wide: width >= 980
    property bool compact: height < 740
    property date now: new Date()
    function login() {
        var chosen = String(users.currentValue || "");
        if (chosen.length && !authenticating) {
            authenticating = true;
            status.text = "";
            sddm.login(chosen, password.text, session.currentIndex);
        }
    }
    Image { anchors.fill: parent; source: config.background; fillMode: Image.PreserveAspectCrop; opacity: 0.32 }
    Rectangle { anchors.fill: parent; color: "#101217"; opacity: 0.36 }
    Timer { interval: 30000; running: true; repeat: true; onTriggered: root.now = new Date() }
    Text {
        anchors.top: parent.top; anchors.right: parent.right; anchors.margins: 32
        text: Qt.formatTime(root.now, "HH:mm"); color: "#C3C7D1"; font.pixelSize: 18
    }
    RowLayout {
        anchors.centerIn: parent
        width: Math.min(root.wide ? 1060 : 440, root.width - 48)
        spacing: root.wide ? 100 : 0
        ColumnLayout {
            visible: root.wide; Layout.fillWidth: true; spacing: 22
            Image { source: "/usr/share/bypssd/logo-256.png"; Layout.preferredWidth: 82; Layout.preferredHeight: 82; fillMode: Image.PreserveAspectFit }
            Text { text: "BYPSSD OS  /  RENACER"; color: "#FFB800"; font.pixelSize: 13; font.bold: true; font.letterSpacing: 2 }
            Text { text: "Tu espacio.\nTu próxima idea."; color: "#FFFFFF"; font.pixelSize: 50; font.weight: Font.DemiBold; lineHeight: 1.12 }
            Rectangle { width: 52; height: 3; radius: 1; color: "#FFB800" }
            Text { text: "Todo empieza con una nueva sesión."; color: "#A4AAB7"; font.pixelSize: 15 }
        }
        Rectangle {
            Layout.preferredWidth: root.wide ? 418 : Math.min(440, root.width - 48)
            implicitHeight: form.implicitHeight + (root.compact ? 48 : 64)
            radius: 24; color: "#191D25"; border.color: "#353B47"; border.width: 1
            ColumnLayout {
                id: form
                anchors.centerIn: parent; width: parent.width - 64; spacing: root.compact ? 10 : 14
                Text { text: "BIENVENIDO A CASA"; color: "#FFB800"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 2; Layout.topMargin: 2 }
                Text { text: "Inicia tu sesión"; color: "#F8F9FC"; font.pixelSize: 30; font.weight: Font.DemiBold }
                Text { text: "BYPSSD OS Renacer"; color: "#9EA6B5"; font.pixelSize: 13; Layout.bottomMargin: 12 }
                Text { text: "USUARIO"; color: "#AEB5C2"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1 }
                ComboBox {
                    id: users
                    Layout.fillWidth: true; Layout.preferredHeight: root.compact ? 44 : 50
                    model: userModel; textRole: "realName"; valueRole: "name"
                    currentIndex: userModel.count > 0 ? Math.max(0, userModel.lastIndex) : -1
                    displayText: currentIndex >= 0 ? (textAt(currentIndex) || String(currentValue)) : "Elige una cuenta"
                    enabled: !root.authenticating
                    palette.text: "#FFFFFF"; palette.buttonText: "#FFFFFF"; palette.base: "#1B222D"; palette.window: "#1B222D"; palette.highlight: "#FFB800"; palette.highlightedText: "#11151C"
                    contentItem: Text { text: users.displayText; color: "#FFFFFF"; font.pixelSize: 14; leftPadding: 15; rightPadding: 28; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
                    background: Rectangle { radius: 11; color: "#11151C"; border.color: users.activeFocus ? "#FFB800" : "#343C49"; border.width: users.activeFocus ? 2 : 1 }
                    Accessible.name: "Selecciona tu cuenta"
                    onActivated: { password.clear(); reveal.checked = false; status.text = ""; password.forceActiveFocus(); }
                }
                Text { text: "CONTRASEÑA"; color: "#AEB5C2"; font.pixelSize: 10; font.bold: true; font.letterSpacing: 1; Layout.topMargin: 5 }
                TextField {
                    id: password
                    Layout.fillWidth: true; Layout.preferredHeight: root.compact ? 44 : 50
                    enabled: !root.authenticating; placeholderText: "Introduce tu contraseña"
                    echoMode: reveal.checked ? TextInput.Normal : TextInput.Password
                    color: "#FFFFFF"; placeholderTextColor: "#747E90"; leftPadding: 15; rightPadding: 75; font.pixelSize: 14
                    selectionColor: "#FFB800"; selectedTextColor: "#101217"
                    background: Rectangle { radius: 11; color: "#11151C"; border.color: password.activeFocus ? "#FFB800" : "#343C49"; border.width: password.activeFocus ? 2 : 1 }
                    ToolButton {
                        id: reveal; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; anchors.rightMargin: 5
                        checkable: true; text: checked ? "Ocultar" : "Mostrar"; enabled: !root.authenticating
                        contentItem: Text { text: reveal.text; color: "#B1BACB"; font.pixelSize: 10; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 7; color: reveal.hovered ? "#29313F" : "transparent" }
                        Accessible.name: checked ? "Ocultar contraseña" : "Mostrar contraseña"
                    }
                    Accessible.name: "Contraseña"; onAccepted: root.login()
                }
                ComboBox {
                    id: session; Layout.fillWidth: true; Layout.preferredHeight: root.compact ? 34 : 38; Layout.topMargin: 3
                    model: sessionModel; textRole: "name"; currentIndex: Math.max(0, sessionModel.lastIndex)
                    enabled: !root.authenticating
                    palette.text: "#C2CAD8"; palette.buttonText: "#C2CAD8"; palette.base: "#1B222D"; palette.window: "#1B222D"; palette.highlight: "#FFB800"; palette.highlightedText: "#11151C"
                    background: Rectangle { radius: 9; color: "#1B222D"; border.color: "#343C49" }
                    Accessible.name: "Tipo de sesión"
                }
                Button {
                    id: enter; Layout.fillWidth: true; Layout.preferredHeight: root.compact ? 44 : 50; Layout.topMargin: 7
                    enabled: !root.authenticating; text: root.authenticating ? "Entrando…" : "Entrar"
                    contentItem: Text { text: enter.text; color: "#16130B"; font.pixelSize: 14; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                    background: Rectangle { radius: 11; color: enter.down ? "#D99D00" : enter.hovered ? "#FFD166" : "#FFB800"; opacity: enter.enabled ? 1 : 0.65 }
                    onClicked: root.login()
                }
                Text {
                    id: status; text: ""; visible: text.length > 0
                    color: "#FFB4AB"; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true
                    Accessible.role: Accessible.AlertMessage
                }
                Rectangle { Layout.fillWidth: true; height: 1; color: "#303744"; Layout.topMargin: 8; Layout.bottomMargin: 1 }
                RowLayout {
                    Layout.fillWidth: true
                    Button {
                        id: reboot; text: "Reiniciar"; visible: sddm.canReboot; flat: true
                        contentItem: Text { text: reboot.text; color: reboot.hovered ? "#FFFFFF" : "#A6AFBF"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 8; color: reboot.hovered ? "#2B3340" : "transparent" }
                        onClicked: sddm.reboot()
                    }
                    Item { Layout.fillWidth: true }
                    Button {
                        id: shutdown; text: "Apagar"; visible: sddm.canPowerOff; flat: true
                        contentItem: Text { text: shutdown.text; color: shutdown.hovered ? "#FFFFFF" : "#A6AFBF"; font.pixelSize: 11; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
                        background: Rectangle { radius: 8; color: shutdown.hovered ? "#2B3340" : "transparent" }
                        onClicked: sddm.powerOff()
                    }
                }
            }
        }
    }
    Text { anchors.bottom: parent.bottom; anchors.left: parent.left; anchors.margins: 28; text: "BYPSSD INFORMÁTICA RETRO  ·  VALENCIA"; color: "#9098A8"; font.pixelSize: 10; font.letterSpacing: 1; visible: root.height > 680 }
    Connections {
        target: sddm
        function onLoginFailed() { root.authenticating = false; status.text = "No se ha podido entrar. Comprueba el usuario y la contraseña."; password.clear(); password.forceActiveFocus(); }
    }
    Component.onCompleted: { if (users.currentIndex >= 0) password.forceActiveFocus(); else users.forceActiveFocus(); }
}
