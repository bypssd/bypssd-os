// SPDX-License-Identifier: GPL-2.0-or-later
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: "#000000"
    property bool authenticating: false
    function login() {
        if (username.text.length && !authenticating) {
            authenticating = true;
            status.text = "Iniciando sesión…";
            sddm.login(username.text, password.text, session.currentIndex);
        }
    }
    Image { anchors.fill: parent; source: config.background; fillMode: Image.PreserveAspectCrop; opacity: 0.35 }
    Rectangle {
        anchors.centerIn: parent
        width: Math.min(440, parent.width - 40)
        height: form.implicitHeight + 64
        color: "#191919"; radius: 20; border.color: "#FFB800"
        ColumnLayout {
            id: form
            anchors.centerIn: parent
            width: parent.width - 64
            spacing: 16
            Image { source: "/usr/share/bypssd/logo-256.png"; Layout.preferredWidth: 96; Layout.preferredHeight: 96; Layout.alignment: Qt.AlignHCenter }
            Label { text: "BYPSSD OS"; color: "white"; font.pixelSize: 30; Layout.alignment: Qt.AlignHCenter }
            Label { text: "Renacer"; color: "#FFB800"; font.pixelSize: 18; Layout.alignment: Qt.AlignHCenter }
            TextField { palette.highlight: "#FFB800"; palette.base: "#24262B"; palette.text: "#FFFFFF"; palette.placeholderText: "#A2A5AF"; id: username; placeholderText: "Usuario"; text: userModel.lastUser; Layout.fillWidth: true; Accessible.name: "Usuario"; onAccepted: password.forceActiveFocus() }
            TextField { palette.highlight: "#FFB800"; palette.base: "#24262B"; palette.text: "#FFFFFF"; palette.placeholderText: "#A2A5AF"; id: password; placeholderText: "Contraseña"; echoMode: TextInput.Password; Layout.fillWidth: true; Accessible.name: "Contraseña"; onAccepted: root.login() }
            ComboBox { id: session; model: sessionModel; textRole: "name"; currentIndex: sessionModel.lastIndex; Layout.fillWidth: true; Accessible.name: "Sesión" }
            Button { palette.button: "#FFB800"; palette.buttonText: "#111111"; text: "Entrar"; enabled: !root.authenticating; Layout.fillWidth: true; onClicked: root.login() }
            Label { id: status; text: ""; color: "#FFB800"; wrapMode: Text.WordWrap; Layout.fillWidth: true; Accessible.role: Accessible.AlertMessage }
            RowLayout {
                Button { text: "Reiniciar"; visible: sddm.canReboot; onClicked: sddm.reboot() }
                Item { Layout.fillWidth: true }
                Button { text: "Apagar"; visible: sddm.canPowerOff; onClicked: sddm.powerOff() }
            }
        }
    }
    Connections {
        target: sddm
        function onLoginFailed() { root.authenticating = false; status.text = "No se ha podido iniciar sesión. Comprueba tus credenciales."; password.clear(); password.forceActiveFocus(); }
    }
    Component.onCompleted: { if (username.text.length) password.forceActiveFocus(); else username.forceActiveFocus(); }
}
