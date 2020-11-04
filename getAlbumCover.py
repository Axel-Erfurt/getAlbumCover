#!/usr/bin/python3
# -*- coding: utf-8 -*-
#####################################################################
import os
from PyQt5.QtCore import (QDir, QSize, Qt)
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox)
                            
import musicbrainzngs
import requests
from shutil import copy

myApp = "Cover Finder"
#####################################################################

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowIcon(QIcon.fromTheme("applications-multimedia"))
        self.setStyleSheet("QMainWindow {padding: 10px; margin: 10px}")
        self.setContentsMargins(10, 10, 10, 10)
        self.artist = ""
        self.album = ""
        self.tempdirname = "/tmp/covers"
        self.img = ""
        
        self.releasesList = []
        self.releasesListID = []
        self.releasesTitle = ""
        self.releasesID = 0
        
        self.artistEntry = QLineEdit("", placeholderText = "Artist")
        self.artistEntry.setFixedWidth(250)

        self.albumEntry = QLineEdit("", placeholderText = "Album Name")
        self.albumEntry.setFixedWidth(250)
        
        self.findButton = QPushButton("get Cover")
        self.findButton.clicked.connect(self.getCover)
        
        self.tracklistButton = QPushButton("get Tracklist")
        self.tracklistButton.clicked.connect(self.getTracks)
        
        self.releasesButton = QPushButton("get all Artist releases")
        self.releasesButton.clicked.connect(self.getReleases)
        self.releasesButton.setFixedWidth(150)
        
        self.releasesCombo = QComboBox()
        self.releasesCombo.setFixedWidth(250)
        self.releasesCombo.currentIndexChanged.connect(self.setReleaseIndex)
        
        self.imageLabel = QLabel()
        self.imageLabel.setScaledContents(False)
        self.imageLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        self.setCentralWidget(self.imageLabel)

        self.createActions()
        self.createToolBars()
        self.createStatusBar()

        self.setGeometry(50, 50, 800, 700)

        self.setWindowTitle(myApp + '[*]')
        
        musicbrainzngs.set_useragent(
            "python-musicbrainzngs-example",
            "0.1",
            "https://github.com/alastair/python-musicbrainzngs/",)
            
    def setReleaseIndex(self):
        self.releasesTitle = self.releasesCombo.currentText()
        self.releasesID = self.releasesListID[self.releasesCombo.currentIndex()]
        self.albumEntry.setText(self.releasesCombo.currentText())
        print(self.releasesTitle, self.releasesID)
            
    def getReleases(self):
        self.artist = self.artistEntry.text()
        print(f"getting releases of artist '{self.artist}'")
        self.statusBar().showMessage(f"getting releases of artist '{self.artist}'", 4000)
        if not self.artist == "":
            self.getArtistReleases(self.artist)
        else:
            print("Artist missing")
            self.msgbox("Artist missing")
            
    def getArtistReleases(self, artist):
        self.releasesCombo.clear()
        self.releasesList = []
        self.releasesListID = []
        try:
            result = musicbrainzngs.search_releases(artist=artist, limit=99, primarytype = 'Album', strict=True)
            for releases in result["release-list"]:
                self.releasesList.append(releases["title"])
                self.releasesListID.append(releases["id"])
        except Exception as e:
            print(e)
        self.releasesCombo.addItems(self.releasesList)
        
    def getTracklist(self, artist, album):
        tracklist = []
        try:
            result = musicbrainzngs.search_releases(artist=artist, release=album, limit=1, primarytype = 'Album', strict=True)
            id = result["release-list"][0]["id"]
            print(f'{artist.title()} - {album.title()}\nTracks:')
            tracklist.append(f'{artist.title()} - {album.title()}\nTracks:')
            #### get tracklist
            new_result = musicbrainzngs.get_release_by_id(id, includes=["recordings"])
            t = (new_result["release"]["medium-list"][0]["track-list"])
            for x in range(len(t)):
                line = (t[x])
                tracknumber = line["number"]
                title = line["recording"]["title"]
                tracklist.append(f'{tracknumber}. {title}')
            tracks = ('\n'.join(tracklist))
            print(tracks)
            self.imageLabel.setText(tracks)
        except Exception as e:
            print(e)
            self.statusBar().showMessage("nothing found", 4000)

    def get_albumCover(self, artist, album):
        idList = []
        try:
            os.mkdir(self.tempdirname)
        except Exception as e:
            print(f"folder '{self.tempdirname}' already exists")
        result = musicbrainzngs.search_releases(artist=artist, release=album, limit=10, primarytype = 'Album', strict=True)
        ### get all album ID
        for a in result["release-list"]:
            idList.append(a["id"])
        data = []
        
        coverList = []
        for x in range(len(idList)):        
            try:    
                id = idList[x]
                data = musicbrainzngs.get_image_list(id)
                url = data["images"][0]["image"]
                coverList.append(url)
                break
            except Exception as e:
                print(e)
        print(f"Cover URLs: {coverList}")
        if len(coverList) > 0:
            ### download cover
            url = coverList[0]
            print(f'downloading Cover from URL: {url}')

            r = requests.get(url, allow_redirects=True)
            if r:
                self.img = f"{self.tempdirname}/{album}.jpg"
                with open(self.img, 'wb') as f:
                    print("saving image")
                    f.write(r.content)
                    f.close()
                    print("loading image into QLabel")
                    self.statusBar().showMessage("loading image", 4000)
                    h = self.imageLabel.height()
                    pixmap = QPixmap(self.img)          
                    self.imageLabel.setPixmap(pixmap.scaledToHeight(h, 0))
                    f.close()
        
    def getCover(self):
        self.artist = self.artistEntry.text()
        self.album = self.albumEntry.text()
        print(f"getting cover of album '{self.album}' from '{self.artist}'")
        self.statusBar().showMessage(f"getting cover of album '{self.album}' from '{self.artist}'", 4000)
        if not self.artist == "" and not self.album == "":
            self.get_albumCover(self.artist, self.album)
        else:
            print("Artist or Album missing")
            self.msgbox("Artist or Album missing")
            
    def getTracks(self):
        self.artist = self.artistEntry.text()
        self.album = self.albumEntry.text()
        print(f"getting tracklist of album '{self.album}' from '{self.artist}'")
        self.statusBar().showMessage(f"getting tracklist of album '{self.album}' from '{self.artist}'", 4000)
        if not self.artist == "" and not self.album == "":
            self.getTracklist(self.artist, self.album)
        else:
            print("Artist or Album missing")
            self.msgbox("Artist or Album missing")
        
    def closeEvent(self, event):
        event.accept()


    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", f"front.jpg", "Images (*.jpg)")
        if fileName:
            if os.path.isfile(self.img):
                print(f"saving {fileName}")
                copy(self.img, fileName)
                self.statusBar().showMessage("File saved", 0)
            else:
                print(f"{self.img} does not exist")          

    def createActions(self):

        self.saveAsAct = QAction(QIcon.fromTheme('document-save-as'),"Save &As...", self,
                shortcut=QKeySequence.SaveAs,
                statusTip="Save Cover",
                triggered=self.saveAs)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.setStyleSheet("QToolBar {border: 0px;}")
        self.fileToolBar.setIconSize(QSize(16, 16))
        self.fileToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.fileToolBar.setMovable(False)
        self.fileToolBar.addWidget(self.artistEntry)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.albumEntry)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.findButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addWidget(self.tracklistButton)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.saveAsAct)
        self.addToolBarBreak()
        self.releasesToolBar = self.addToolBar("Releases")
        self.releasesToolBar.setStyleSheet("QToolBar {border: 0px;}")
        self.releasesToolBar.setIconSize(QSize(16, 16))
        self.releasesToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.releasesToolBar.setMovable(False)
        self.releasesToolBar.addWidget(self.releasesCombo)
        self.releasesToolBar.addSeparator()
        self.releasesToolBar.addWidget(self.releasesButton)

    def createStatusBar(self):
        self.statusBar().setStyleSheet("font-size: 8pt; color: #888a85;")
        self.statusBar().showMessage("Ready")
        
    def msgbox(self, message):
        msg = QMessageBox(2, "Information", message, QMessageBox.Ok)
        msg.exec()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
