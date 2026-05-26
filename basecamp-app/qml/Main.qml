import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    visible: true
    width: 960
    height: 640
    title: "LP-0003 Private Airdrop"

    Rectangle {
        anchors.fill: parent
        color: "#0b1020"

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 18

            Label {
                text: "LP-0003 Private Airdrop"
                color: "#dbeafe"
                font.pixelSize: 32
                font.bold: true
            }

            Label {
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                color: "#a7f3d0"
                text: "Create a hidden eligibility-set commitment, prove private membership, and claim with a distribution-bound nullifier."
            }

            GroupBox {
                Layout.fillWidth: true
                title: "Privacy boundary"
                label: Label { text: parent.title; color: "#fef3c7" }
                background: Rectangle { color: "#111827"; border.color: "#374151"; radius: 8 }

                ColumnLayout {
                    anchors.fill: parent
                    Label { color: "#e5e7eb"; text: "Public: distribution id, Merkle root, nullifier, recipient commitment, fixed allocation, proof context." }
                    Label { color: "#e5e7eb"; text: "Private: eligible address/control secret, leaf salt, Merkle path, membership witness." }
                    Label { color: "#fca5a5"; text: "Status: source package only. Final Basecamp load evidence is a separate publication gate." }
                }
            }

            Button {
                text: "Run local safe-lane demo from terminal: bash demo.sh"
                enabled: false
            }
        }
    }
}
