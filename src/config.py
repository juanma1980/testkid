#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig

app=QApplication(["Run-O-Matic"])
config=appConfig("Run-O-Matic",{'app':app})
config.setRsrcPath="/home/lliurex/git/testkid/rsrc"
config.setIcon('runomatic.svg')
config.setBanner('banner.png')
config.setBackgroundImage('background.png')
config.load_stacks()

app.exec_()
