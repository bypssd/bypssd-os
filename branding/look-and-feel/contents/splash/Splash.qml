// SPDX-License-Identifier: MIT
import QtQuick
Rectangle {
    id: root
    color: "#090A0C"
    property int stage: 0
    property real progress: Math.min(1, stage / 6)
    property real angle: 0
    onStageChanged: { if (stage >= 5) content.opacity = 0; }
    NumberAnimation on angle { from: 0; to: 360; duration: 1800; loops: Animation.Infinite; running: root.visible }
    Item {
        id: content
        anchors.centerIn: parent
        width: 460; height: 310
        opacity: 0
        Behavior on opacity { NumberAnimation { duration: 650; easing.type: Easing.InOutCubic } }
        Canvas {
            id: ring
            anchors.horizontalCenter: parent.horizontalCenter
            width: 160; height: 160
            Connections { target: root; function onAngleChanged() { ring.requestPaint(); } }
            onPaint: {
                var c = getContext("2d"); c.reset();
                c.lineWidth = 2; c.strokeStyle = "#282319";
                c.beginPath(); c.arc(80,80,74,0,Math.PI*2); c.stroke();
                c.strokeStyle = "#FFB800"; c.lineCap = "round";
                c.beginPath(); c.arc(80,80,74,root.angle*Math.PI/180,(root.angle+85)*Math.PI/180); c.stroke();
            }
            Image { anchors.centerIn: parent; width: 108; height: 108; source: "/usr/share/bypssd/logo-256.png"; smooth: true }
        }
        Text { anchors.horizontalCenter: parent.horizontalCenter; y: 186; text: "BYPSSD OS"; color: "#FFFFFF"; font.pixelSize: 30; font.weight: Font.DemiBold; font.letterSpacing: 2 }
        Text { anchors.horizontalCenter: parent.horizontalCenter; y: 230; text: "R E N A C E R"; color: "#FFB800"; font.pixelSize: 13 }
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter; y: 286; width: 180; height: 2; radius: 1; color: "#292929"
            Rectangle { width: parent.width * root.progress; height: 2; radius: 1; color: "#FFB800"; Behavior on width { NumberAnimation { duration: 600; easing.type: Easing.OutCubic } } }
        }
        Component.onCompleted: opacity = 1
    }
}
