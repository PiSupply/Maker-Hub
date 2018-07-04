#!/usr/bin/python3
import sys
import logging
import os
from makerhub import installer
from PyQt5.QtCore import QUrl, pyqtSlot, QObject, pyqtProperty, QAbstractListModel, Qt
from PyQt5.QtQuick import QQuickView, QQuickItem
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import qmlRegisterType, qmlRegisterSingletonType
from os import system


logging.basicConfig(level=logging.DEBUG)


class ProjectsModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    DescriptionRole = Qt.UserRole + 2
    IconRole = Qt.UserRole + 3
    WebsiteLinkRole = Qt.UserRole + 4
    GithubLinkRole = Qt.UserRole + 5
    PostInstallRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.dict = installer.get_software_objects()
        self._roles = {self.NameRole: "name".encode("utf-8"),
                       self.DescriptionRole: "description_full".encode("utf-8"),
                       self.IconRole: "icon_16x16".encode("utf-8"),
                       self.PostInstallRole: "post_install".encode("utf-8"),
                       self.WebsiteLinkRole: "website_link".encode("utf-8"),
                       self.GithubLinkRole: "github_link".encode("utf-8")}

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
    def fun(self, inst_prop):
        checkInstall = 0
        checkInstall=system(inst_prop)
        print(checkInstall)


def createapi(engine, script_engine):
    return Api()


def run():
    app = QGuiApplication(sys.argv)

    qmlRegisterSingletonType(Api, 'Makerhub', 1, 0, 'Api', createapi)
    qmlRegisterType(ProjectsModel, "Makerhub", 1, 0, "ProjectsModel")

    v = QQuickView()
    if os.path.exists("data/main.qml"):
        v.setSource(QUrl("data/main.qml"))
    else:
        v.setSource(QUrl("/usr/share/makerhub/data/main.qml"))
    #v.show()

    app.exec_()


if __name__ == '__main__':
    run()
