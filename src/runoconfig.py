#!/usr/bin/python3
import sys
import os,shutil
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig

oldUser="{}/.config/runomatic.conf".format(os.environ.get('HOME'))
if os.path.isfile(oldUser):
	newUser="{}/.config/runomatic/runomatic.conf".format(os.environ.get('HOME'))
	if os.path.isdir(os.path.dirname(newUser))==False:
		os.makedirs(os.path.dirname(newUser))
	if os.path.isfile(newUser)==False:
		shutil.move(oldUser,newUser)

app=QApplication(["Run-O-Matic"])
config=appConfig("Runoconfig",{'app':app})
config.setRsrcPath("/usr/share/runomatic/rsrc")
config.setIcon('runomatic.svg')
config.setBanner('banner.png')
config.setBackgroundImage('background.png')
config.setConfig(confDirs={'system':'/usr/share/runomatic','user':'%s/.config/runomatic'%os.environ['HOME']},confFile="runomatic.conf")
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
if len(sys.argv)>1:
	if os.path.isfile("/usr/bin/runomatic"):
		os.execv("/usr/bin/runomatic",["1"])

