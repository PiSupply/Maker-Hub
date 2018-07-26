#!/usr/bin/python3
import sys
import logging
import os
import subprocess
import requests
from makerhub import installer
from PyQt5.QtCore import QUrl, pyqtSlot, QObject, pyqtProperty, QAbstractListModel, Qt
from PyQt5.QtQuick import QQuickView, QQuickItem
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType
from PyQt5.QtQml import QQmlApplicationEngine,QQmlEngine, QQmlComponent
from PyQt5.QtWidgets import QErrorMessage, QApplication, QMessageBox
from os import system



logging.basicConfig(level=logging.DEBUG)


class ProjectsModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    WebsiteLinkRole = Qt.UserRole + 4
    GithubLinkRole = Qt.UserRole + 5
    PostInstallRole = Qt.UserRole + 6
    PostUninstallRole = Qt.UserRole + 7
    CheckLinkRole = Qt.UserRole + 8

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dict = installer.get_software_objects()
        self._roles = {self.NameRole: "name".encode("utf-8"),
                       self.DescriptionRole: "description_full".encode("utf-8"),
                       self.IconRole: "icon_16x16".encode("utf-8"),
                       self.PostInstallRole: "post_install".encode("utf-8"),
                       self.WebsiteLinkRole: "website_link".encode("utf-8"),
                       self.GithubLinkRole: "github_link".encode("utf-8"),
                       self.PostUninstallRole: "post_uninstall".encode("utf-8"),
                       self.CheckLinkRole: "check_link".encode("utf-8")
                       }


    def rowCount(self, parent=None):
        return len(self.dict)

    def data(self, index, role):
        return self.dict[index.row()][self._roles[role].decode("utf-8")]

    def roleNames(self):
        return self._roles


class Api(QObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    @pyqtSlot(str)
    def installing(self, inst_prop):
        r = requests.get(inst_prop)
        with open('/tmp/install.sh','wb') as f:
            f.write(r.content)


        system("x-terminal-emulator -e sudo bash /tmp/install.sh")

        #checkInstall = 0
        #command = "lxterminal -e "
        #checkInstall = system(command + inst_prop)
        #err_dialog = QErrorMessage()
       # print(checkInstall)
        #if checkInstall == 0:
           # err_dialog.showMessage("Installation successful")
            #err_dialog.exec()
       # else:
           # err_dialog.showMessage("Installation failed")
            #err_dialog.exec()

    @pyqtSlot(str,str)
    def uninstalling(self,uninstall_script_link,check_link):
        check_install = system("test -f " + check_link)
        inform_dialog = QErrorMessage()
        if(check_install == 0):
            r = requests.get(uninstall_script_link)
            with open('/tmp/uninstall.sh', 'wb') as f:
                f.write(r.content)

            system("x-terminal-emulator -e sudo bash /tmp/uninstall.sh")
            inform_dialog.showMessage("Uninstalling project")
            inform_dialog.exec()
        else:
            inform_dialog.showMessage("This project in not installed")
            inform_dialog.exec()


#        print(check_link)




def createapi(engine, script_engine):
    return Api()


def run():
    app = QApplication(sys.argv) #app = QGuiApplication(sys.argv)

    qmlRegisterSingletonType(Api, 'Makerhub', 1, 0, 'Api', createapi)
    qmlRegisterType(ProjectsModel, "Makerhub", 1, 0, "ProjectsModel")

    path = "data/main.qml"

    if not os.path.exists(path):
        path = "/usr/share/makerhub/data/main.qml"

    engine = QQmlApplicationEngine()
    engine.load(path)
    app.exec_()


if __name__ == '__main__':
    run()
