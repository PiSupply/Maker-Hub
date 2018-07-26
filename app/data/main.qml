import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.1

import Makerhub 1.0

ApplicationWindow
{
    visible: true
    //visibility: "Maximized"
    minimumHeight:480
    minimumWidth:600
    title: qsTr("MakerHub")

    RowLayout
    {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: 5
        spacing: 10

        Component
        {
            id: list_row
            Item
            {
                property string name: model.name
                property string description: model.description_full
                property string icon: model.icon_16x16
                property string post_install: model.post_install
                property string website_link: model.website_link
                property string github_link: model.github_link
                property string post_uninstall: model.post_uninstall
                property string check_link: model.check_link


                width: parent.width
                height: childrenRect.height
                Text
                {
                    text: model.name
                    color: list.currentIndex == model.index ? "white" : "black"
                }
                MouseArea
                {
                    anchors.fill: parent
                    onClicked:
                    {
                        list.currentIndex = model.index
                    }
                }
            }
        }
        Item
        {
            Layout.preferredWidth: 300
            Layout.fillHeight: true
            GroupBox
            {
                title: "Projects:"
                anchors.fill: parent
                ListView
                {
                    id: list
                    anchors.fill: parent
                    model: ProjectsModel {}
                    delegate: list_row
                    focus: true
                    highlight: Rectangle { color: "blue"; radius: 2 }

                    onCurrentIndexChanged:
                    {
                        text_area.text = currentItem.description
                        img.source = "media/" + currentItem.icon
                        website_link_text.text = "<a href=\"%1\">Website</a>".arg(currentItem.website_link)
                        github_link_text.text = "<a href=\"%1\">Github</a>".arg(currentItem.github_link)
                    }
                }
            }
        }


        ColumnLayout
        {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 2

            Item
            {
                Layout.preferredHeight: 100
                Layout.fillWidth: true
                Image
                {
                    id: img
                    anchors.left: parent.left
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.right: website_link_text.left
                    width: height
                    fillMode: Image.PreserveAspectFit
                }

                Text
                {
                    id: website_link_text
                    anchors.right: parent.right
                    textFormat: Text.RichText
                    text: "Website"
                    onLinkActivated: Qt.openUrlExternally(link)
                }

                Text
                {
                    id:  github_link_text
                    anchors.right: parent.right
                    anchors.top: website_link_text.bottom
                    textFormat: Text.RichText
                    text: "Github"
                    onLinkActivated: Qt.openUrlExternally(link)
                }
            }
            TextArea
            {
                id: text_area
                Layout.fillHeight: true
                Layout.fillWidth: true
                readOnly: true
                text: ""
            }

            Row
            {
                spacing: 2
                //layoutDirection: Qt.RightToLeft
                Button
                {
                    id: firstbutton
                    text: "Uninstall"
                    onClicked:
                    {
                    Api.uninstalling(list.currentItem.post_uninstall,list.currentItem.check_link)
                    }
                }
                Button
                {   id: track
                    text: "Install"
                    onClicked:
                        {
                        Api.installing(list.currentItem.post_install)
                        }
                }
            }
        }
    }
}
