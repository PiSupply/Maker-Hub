#!/usr/bin/python3
import sys
import threading
import queue
import logging
import os
from makerhub.installer import (install_package, check_system, get_software_objects, IMAGES_FOLDER,
                                DESTINATION_FOLDER, DEFAULT_ICON_32_PATH, DEFAULT_ICON_16_PATH, LOG_FILE)
from PyQt5.QtWidgets import (QWidget, QApplication, QHBoxLayout, QTextEdit, QListWidgetItem,
                             QVBoxLayout, QLabel, QPushButton, QListWidget, QMainWindow,
                             QErrorMessage, QMessageBox)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize

logging.basicConfig(level=logging.DEBUG)


class UICommunication(QObject):
    installBeginSignal = pyqtSignal()
    installEndSignal = pyqtSignal()
    checksFailedSignal = pyqtSignal()


class MainWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pi-Supply Maker Hub")
        self.setGeometry(300, 300, 500, 500)
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        self.statusBar()

        self.UISignals = UICommunication()
        self.queue = queue.Queue()

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

        linksBox = self._setupLinksBox()

        titleBox.addWidget(self.itemIconLabel)
        titleBox.addWidget(self.itemLabel)
        titleBox.addLayout(linksBox)
        rightVBox.addLayout(titleBox)

        self.descriptionText = QTextEdit()
        self.descriptionText.setReadOnly(True)
        rightVBox.addWidget(self.descriptionText)

        btnBox = self._setupBtnBox()
        rightVBox.addLayout(btnBox)

        hbox.addLayout(rightVBox)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(hbox)
        self.setCentralWidget(self.mainWidget)

        self.UISignals.checksFailedSignal.connect(sys.exit)  # TODO: Proper way to quit

        self.show()
        self.preLaunchCheck()

    def preLaunchCheck(self):
        success, errorMessage = check_system()
        # Exit and show message if found problems
        if not success:
            err_dialog = QErrorMessage()
            err_dialog.showMessage(errorMessage)
            err_dialog.exec()
            self.UISignals.checksFailedSignal.emit()

    def onItemChanged(self, curr, prev):
        self.currentProduct = self.softwareObjects[curr.text()]
        self.descriptionText.setText(self.currentProduct['description_full'])
        self.itemLabel.setText(self.currentProduct['title'])
        self.itemIconLabel.setPixmap(QPixmap(
            os.path.join(IMAGES_FOLDER, self.currentProduct.get('icon_32x32', DEFAULT_ICON_32_PATH))
        ))
        self.githubLinkLabel.setText("<a href='{}'>Github</a>".format(self.currentProduct['github_link']))
        self.storeLinkLabel.setText("<a href='{}'>PiSupply</a>".format(self.currentProduct['website_link']))

    def install(self, event):
        self.UISignals.installBeginSignal.emit()
        install_thread = threading.Thread(target=install_package, args=[
            self.currentProduct, self.queue, DESTINATION_FOLDER, self._installEndCallback])
        install_thread.start()
        # QTimer.singleShot(1000, lambda: self.UISignals.installEndSignal.emit())
        # self.UISignals.installEndSignal.emit()

    def _installEndCallback(self, success):
        self.UISignals.installEndSignal.emit()
        if success:
            QMessageBox.question(self, "Installation success", "Successfully installed {}".format(self.currentProduct['name']),
                                 QMessageBox.Ok)
        else:
            err_dialog = QErrorMessage()
            err_dialog.showMessage('Installation failed. Please, check logs at {}'.format(LOG_FILE))
            err_dialog.exec()

    def _populateSoftwareList(self, listWidget):
        listWidget.setIconSize(QSize(16, 16))
        for name, softDict in self.softwareObjects.items():
            item = QListWidgetItem(listWidget)
            item.setText(softDict['title'])
            item.setIcon(QIcon(os.path.join(IMAGES_FOLDER, softDict.get('icon_16x16', DEFAULT_ICON_16_PATH))))

    def _setupLinksBox(self):
        linksBox = QVBoxLayout()
        linksBox.setAlignment(Qt.AlignRight)
        self.githubLinkLabel = QLabel(self)
        self.githubLinkLabel.setAlignment(Qt.AlignRight)
        self.storeLinkLabel = QLabel(self)
        self.githubLinkLabel.setOpenExternalLinks(True)
        self.storeLinkLabel.setOpenExternalLinks(True)
        linksBox.addWidget(self.githubLinkLabel)
        linksBox.addWidget(self.storeLinkLabel)
        return linksBox

    def _setupBtnBox(self):
        self.installBtn = QPushButton("Install", self)
        self.installBtn.clicked.connect(self.install)
        self.UISignals.installBeginSignal.connect(self.disableUI)
        self.UISignals.installEndSignal.connect(self.enableUI)

        self.moreInfoBtn = QPushButton("More Info", self)
        btnBox = QHBoxLayout()
        btnBox.addWidget(self.moreInfoBtn)
        btnBox.addWidget(self.installBtn)
        return btnBox

    def enableUI(self):
        for _ in range(self.queue.qsize()):
            stdout, stderr = self.queue.get()
            logging.debug("STDOUT: {}\nSTDERR: {}\n".format(stdout, stderr))

        self.installBtn.setText("Install")
        self.installBtn.setDisabled(False)
        self.statusBar().showMessage("Installation finished")

    def disableUI(self):
        self.installBtn.setText("Installing...")
        self.installBtn.setDisabled(True)
        self.statusBar().showMessage("Installing " + self.currentProduct['title'])


def start_app():
    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start_app()
