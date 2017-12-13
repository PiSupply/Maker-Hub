import sys
import json
from multiprocessing import Process, Queue
from installer import install_package
from PyQt5.QtWidgets import (QWidget, QApplication, QHBoxLayout, QTextEdit, QListWidgetItem,
                             QVBoxLayout, QLabel, QPushButton, QListView, QListView, QListWidget)
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer

PACKAGES_FILE = 'resources/packages.json'
DESTINATION_FOLDER = '/opt'


def get_software_objects():
    with open(PACKAGES_FILE, 'r') as f:
        content = json.load(f)
    packages = {item['name']: item for item in content['packages']}
    return packages


class UICommunication(QObject):
    installBeginSignal = pyqtSignal()
    installEndSignal = pyqtSignal()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pi-Supply Maker Hub")
        self.setGeometry(300, 300, 500, 500)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        self.UISignals = UICommunication()

        hbox = QHBoxLayout()

        self.softwareObjects = get_software_objects()
        self.currentProduct = self.softwareObjects[list(self.softwareObjects.keys())[0]]

        softwareListWidget = QListWidget(self)
        self._populateSoftwareList(softwareListWidget)
        softwareListWidget.setMaximumWidth(200)
        softwareListWidget.currentItemChanged.connect(self.onItemChanged)

        hbox.addWidget(softwareListWidget)

        rightVBox = QVBoxLayout()
        titleBox = QHBoxLayout()
        self.itemLabel = QLabel(self)
        self.itemIconLabel = QLabel(self)

        linksBox = QVBoxLayout()
        linksBox.setAlignment(Qt.AlignRight)
        self.githubLinkLabel = QLabel(self)
        self.githubLinkLabel.setAlignment(Qt.AlignRight)
        self.storeLinkLabel = QLabel(self)
        self.githubLinkLabel.setOpenExternalLinks(True)
        self.storeLinkLabel.setOpenExternalLinks(True)
        linksBox.addWidget(self.githubLinkLabel)
        linksBox.addWidget(self.storeLinkLabel)

        titleBox.addWidget(self.itemIconLabel)
        titleBox.addWidget(self.itemLabel)
        titleBox.addLayout(linksBox)
        rightVBox.addLayout(titleBox)

        self.descriptionText = QTextEdit()
        self.descriptionText.setReadOnly(True)
        rightVBox.addWidget(self.descriptionText)

        self.installBtn = QPushButton("Install", self)
        self.installBtn.clicked.connect(self.install)
        self.UISignals.installBeginSignal.connect(self.disableUI)
        self.UISignals.installEndSignal.connect(self.enableUI)

        self.pinoutBtn = QPushButton("Pinout", self)
        btnBox = QHBoxLayout()
        btnBox.addWidget(self.pinoutBtn)
        btnBox.addWidget(self.installBtn)
        # btnBox.addStretch(1)
        rightVBox.addLayout(btnBox)

        hbox.addLayout(rightVBox)
        self.setLayout(hbox)

        self.show()

    def onItemChanged(self, curr, prev):
        self.currentProduct = self.softwareObjects[curr.text()]
        self.descriptionText.setText(self.currentProduct['description_full'])
        self.itemLabel.setText(self.currentProduct['title'])
        self.itemIconLabel.setPixmap(QPixmap(self.currentProduct['icon_32x32']))
        self.githubLinkLabel.setText(f"<a href='{self.currentProduct['github_link']}'>Github</a>")
        self.storeLinkLabel.setText(f"<a href='{self.currentProduct['website_link']}'>PiSupply</a>")

    def install(self, event):
        self.UISignals.installBeginSignal.emit()
        queue = Queue()
        install_process = Process(target=install_package, args=[self.currentProduct, queue, DESTINATION_FOLDER])
        install_process.start()
        install_process.join()
        for _ in range(queue.qsize()):
            print(queue.get())
        QTimer.singleShot(1000, lambda: self.UISignals.installEndSignal.emit())
        # self.UISignals.installEndSignal.emit()

    def _populateSoftwareList(self, listWidget):
        for name, softDict in self.softwareObjects.items():
            item = QListWidgetItem(listWidget)
            item.setText(softDict['title'])
            item.setIcon(QIcon(softDict['icon_16x16']))

    def enableUI(self):
        self.installBtn.setText("Install")
        self.installBtn.setDisabled(False)
        print("Enable UI")

    def disableUI(self):
        self.installBtn.setText("Installing...")
        self.installBtn.setDisabled(True)
        print("Disable UI")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    sys.exit(app.exec_())
