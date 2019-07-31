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
import time
from libAppRun import appRun
QString=type("")


class th_runApp(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app,parent=None):
		QThread.__init__(self,parent)
		self.app=app

	def __del__(self):
		self.wait()
		pass

	def run(self):
		retval=False
		print("Launching thread...")
		try:
			os.environ['DISPLAY']=":13"
#			subprocess.Popen(["ratposion"],stdin=None,stdout=None,stderr=None,shell=False)
			subprocess.Popen([self.app],stdin=None,stdout=None,stderr=None,shell=False)
			retval=True
		except Exception as e:
			print("Error running: %s"%e)
		self.signal.emit(retval)


class testKid(QWidget):
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.pid=0
		self.app_icons={}
		self.categories={"lliurex-infantil":"applications-games","network":"applications-internet","education":"applications-education"}
#		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.showFullScreen()
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self._render_gui()
		self.runner=appRun()
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)

	def _render_gui(self):
		self.show()
		self.box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.box.addWidget(self.statusBar,0,0,1,1)
		self.tabBar=self._tabBar()
		self.box.addWidget(self.tabBar,0,0,1,1)
		self.setLayout(self.box)
	#def _render_gui

	def _tabBar(self):
		tabBar=QTabWidget()
		tabScroll=QWidget()
		scrollArea=QScrollArea(tabScroll)
		tabContent=QWidget()
#		icn=QtGui.QIcon.fromTheme("go-previous")
		icn=QtGui.QIcon.fromTheme("go-home")
		vbox=QGridLayout()
		row=0
		col=0
		scr=app.primaryScreen()
		w=scr.size().width()-128
		h=scr.size().height()-256
		maxCol=int(w/128)-3
		self._debug("Size: %s\nCols: %s"%(self.width(),maxCol))
		for category,icon in self.categories.items():
			apps=self._get_category_apps(category)
			sigmap_run=QSignalMapper(self)
			sigmap_run.mapped[QString].connect(self._launch)
			for appName,appIcon in apps.items():
				if QtGui.QIcon.hasThemeIcon(appIcon):
					icnApp=QtGui.QIcon.fromTheme(appIcon)
				else:
					continue
				self.app_icons[appName]=appIcon
				self._debug("Adding %s"%appName)
				btnApp=QPushButton()
				btnApp.setIcon(icnApp)
				btnApp.setIconSize(QSize(128,128))
				btnApp.setToolTip(appName)
				sigmap_run.setMapping(btnApp,appName)
				btnApp.clicked.connect(sigmap_run.map)
				vbox.addWidget(btnApp,row,col,Qt.Alignment(-1))
				col+=1
				if col==maxCol:
					col=0
					row+=1

		tabContent.setLayout(vbox)
		scrollArea.setWidget(tabContent)
		scrollArea.alignment()
		tabBar.addTab(tabScroll,icn,(""))
		scrollArea.setGeometry(QRect(0,0,w,h))
		tabBar.setIconSize(QSize(96,96))
		return (tabBar)
	#def _tabBar

	def _get_category_apps(self,category):
		apps={}
		applist=App2Menu.app2menu().get_apps_from_category(category)
		for key,app in applist.items():
			apps[app['exe']]=app['icon']
		return (apps)
	#def _get_category_apps

	def _launchZone(self,app):
		tabContent=QWidget()
		box=QVBoxLayout()
		wid=self.runner.get_wid(self.display)
		self._debug("W: %s"%wid)
		subZone=QtGui.QWindow.fromWinId(int(wid))
		zone=QWidget.createWindowContainer(subZone)
		zone.setParent(self)
		box.addWidget(zone)
		tabContent.setLayout(box)
		icn=QtGui.QIcon.fromTheme(self.app_icons[app])
		self.tabBar.addTab(tabContent,icn,"")
	#def _launchZone

	def _launch(self,app):
		self.tabBar.setCurrentIndex(3)
		os.environ["HOME"]="/home/lliurex"
		os.environ["XAUTHORITY"]="/home/lliurex/.Xauthority"
#		if self.pid==0:
		self.display,self.pid=self.runner.new_Xephyr(self.tabBar)
		self._launchZone(app)
		self.runner.launch(app,self.display)
	#def _launch


#_debug("Init %s"%sys.argv)
app=QApplication(["Test Kid Launcher"])
testKidLauncher=testKid()
app.exec_()
