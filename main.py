import os
import sys
import json

from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QStackedLayout, QLineEdit, QFrame, QTabBar)
from PyQt5.QtGui import QWindow, QIcon
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, i):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web-Browser")
        self.CreateApp()
        # self.resize(1366, 768)

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Tabbar(tabs)
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.closeTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)

        self.tabbar.setCurrentIndex(0)

        # keep tracks of tabs
        self.tabCount = 0
        self.tabs = []

        # toolbar items

        # back,forward,reload button (item 1)
        self.BackButton = QPushButton("<")
        self.ForwardButton = QPushButton(">")
        self.ReloadButton = QPushButton("R")

        self.BackButton.clicked.connect(self.GoBack)
        self.ForwardButton.clicked.connect(self.GoForward)
        self.ReloadButton.clicked.connect(self.ReloadPage)

        # Address (item 2)
        self.addressbar = AddressBar()
        self.addressbar.returnPressed.connect(self.BrowseTo)

        # new tab button (item 3)
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.AddTab)

        # Toolbar
        self.Toolbar = QWidget()
        self.ToolbarLayout = QHBoxLayout()
        self.Toolbar.setLayout(self.ToolbarLayout)

        # adding buttons and addressbar in toolbar
        self.ToolbarLayout.addWidget(self.BackButton)
        self.ToolbarLayout.addWidget(self.ForwardButton)
        self.ToolbarLayout.addWidget(self.ReloadButton)
        self.ToolbarLayout.addWidget(self.addressbar)
        self.ToolbarLayout.addWidget(self.AddTabButton)

        # main view (container)
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        # adding widget to main layout: tabbar,toolbar,container
        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)
        self.AddTab()
        self.show()

    def closeTab(self, i):
        self.tabbar.removeTab(i)

    def AddTab(self):
        i = self.tabCount

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].setObjectName("tab" + str(i))

        # Open webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("https://google.com"))
        self.tabs[i].content.titleChanged.connect(lambda: self.SetTabTitle(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.SetTabTitle(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.SetTabTitle(i, "url"))

        # Add webview to tabs layout
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        # set top level tab from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # Add tab to top level stackedWidget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # set tab at top of screen
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab" + str(i), "initial": i})
        self.tabbar.setCurrentIndex(i)

        self.tabCount += 1

    def SwitchTab(self, i):
        tab_data = self.tabbar.tabData(i)["object"]
        tab_content = self.findChild(QWidget, tab_data)
        self.container.layout.setCurrentWidget(tab_content)
        new_url = tab_content.content.url().toString()
        self.addressbar.setText(new_url)

    def BrowseTo(self):
        text = self.addressbar.text()
        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        web_view = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/search?q=" + text
            else:
                url = "https://" + text
        else:
            url = text

        web_view.load(QUrl.fromUserInput(url))

    def SetTabTitle(self, i, type):
        tab_name = self.tabs[i].objectName()
        count = 0
        running = True

        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]
        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressbar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count > 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    newTitle = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, newTitle)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)
                running = False

            else:
                count += 1

    def GoBack(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoForward(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec())
