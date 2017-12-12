import sys
import json
from PyQt5.QtWidgets import (QWidget, QApplication, QHBoxLayout, QTextEdit, QListWidgetItem,
                             QVBoxLayout, QLabel, QPushButton, QListView, QListView, QListWidget)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap

PACKAGES_FILE = 'resources/packages.json'


def get_software_objects():
    with open(PACKAGES_FILE, 'r') as f:
        content = json.load(f)
    packages = {item['name']: item for item in content['packages']}
    return packages


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Supply Maker Hub")
        self.setGeometry(300, 300, 500, 500)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        hbox = QHBoxLayout()

        self.softwareObjects = get_software_objects()
        self.currentProduct = self.softwareObjects[list(self.softwareObjects.keys())[0]]

        softwareListWidget = QListWidget(self)
        self._populateSoftwareList(softwareListWidget)
        softwareListWidget.setMaximumWidth(200)
        softwareListWidget.currentItemChanged.connect(self.onItemChanged)

        hbox.addWidget(softwareListWidget)

        vbox = QVBoxLayout()
        titleBox = QHBoxLayout()
        self.itemLabel = QLabel(self)
        self.itemIconLabel = QLabel(self)

        linksBox = QVBoxLayout()
        self.githubLinkLabel = QLabel(self)
        self.storeLinkLabel = QLabel(self)
        self.githubLinkLabel.setOpenExternalLinks(True)
        self.storeLinkLabel.setOpenExternalLinks(True)
        linksBox.addWidget(self.githubLinkLabel)
        linksBox.addWidget(self.storeLinkLabel)

        titleBox.addWidget(self.itemIconLabel)
        titleBox.addWidget(self.itemLabel)
        titleBox.addLayout(linksBox)
        vbox.addLayout(titleBox)

        self.descriptionText = QTextEdit()
        self.descriptionText.setReadOnly(True)
        vbox.addWidget(self.descriptionText)

        self.installBtn = QPushButton("Install", self)
        self.pinoutBtn = QPushButton("Pinout", self)
        btnBox = QHBoxLayout()
        btnBox.addWidget(self.pinoutBtn)
        btnBox.addWidget(self.installBtn)
        # btnBox.addStretch(1)
        vbox.addLayout(btnBox)

        hbox.addLayout(vbox)
        self.setLayout(hbox)

        self.show()

    def onItemChanged(self, curr, prev):
        self.currentProduct = self.softwareObjects[curr.text()]
        self.descriptionText.setText(self.currentProduct['description_full'])
        self.itemLabel.setText(self.currentProduct['name'])
        self.itemIconLabel.setPixmap(QPixmap(self.currentProduct['icon_32x32']))
        self.githubLinkLabel.setText(f"<a href='{self.currentProduct['github_link']}'>Github</a>")
        self.storeLinkLabel.setText(f"<a href='{self.currentProduct['website_link']}'>PiSupply</a>")

    def _populateSoftwareList(self, listWidget):
        for name, softDict in self.softwareObjects.items():
            item = QListWidgetItem(listWidget)
            item.setText(name)
            item.setIcon(QIcon(softDict['icon_16x16']))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    sys.exit(app.exec_())
