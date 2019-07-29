#!/usr/bin/env python3
import getpass
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess
import gettext
import subprocess
from edupals.ui import QAnimatedStatusBar
from app2menu import App2Menu


class th_runApp(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,parent=None):
		QThread.__init__(self,parent)

	def __del__(self):
		self.wait()
		pass

	def run(self):
		pass


class testKid(QWidget):
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.categories={"lliurex infantil":"applications-games","internet":"applications-internet","education":"applications-education"}
#		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.showFullScreen()
		self._render_gui()
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)

	def _render_gui(self):
		box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		box.addWidget(self.statusBar,0,0,1,1)
		tabBar=self._tabBar()
		box.addWidget(tabBar,0,0,1,1)
		self.zone=self._launchZone()
		box.addWidget(self.zone,1,0,1,1)
		self.setLayout(box)
		self.show()

	def _tabBar(self):
		tabBar=QTabWidget()
		for category,icon in self.categories.items():
			tabContent=QWidget()
			icn=QtGui.QIcon.fromTheme(icon)
			vbox=QGridLayout()
			apps=self._get_category_apps(category)
			for appName,appIcon in apps.items():
				btnApp=QPushButton()
				icnApp=QtGui.QIcon.fromTheme(appIcon)
				btnApp.setIcon(icnApp)
				btnApp.setIconSize(QSize(48,48))
				btnApp.setToolTip(appName)
				btnApp.clicked.connect(lambda: self._launch(appName))
				vbox.addWidget(btnApp,0,Qt.Alignment(0))
			tabContent.setLayout(vbox)
			tabBar.addTab(tabContent,icn,(""))
		return (tabBar)

	def _get_category_apps(self,category):
		apps={}
		#Fake for test
		apps={"xterm":"firefox"}
		return (apps)

	def _launchZone(self):
		Qzone=QWidget()
		self.winID=int(Qzone.winId())
		subZone=QtGui.QWindow.fromWinId(self.winID)
		zone=QWidget.createWindowContainer(subZone)
		return(zone)

	def _launch(self,app):
		proc=QProcess(self.zone)
#		args=["-parent %s"%self.winID]
		args=[]
		app="Xephyr"
		port=13001
		xpra_cmd="xpra start :"+str(port)
		xpra_cmd=xpra_cmd+" --systemd-run=no --exit-with-children --start-via-proxy=no  --start-child='xterm'"
#		proc.setProgram(app)
		proc.start(xpra_cmd,args)



#_debug("Init %s"%sys.argv)
app=QApplication(["Test Kid Launcher"])
testKidLauncher=testKid()
app.exec_()
