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
		self.categories={"lliurex-infantil":"applications-games","network":"applications-internet","education":"applications-education"}
#		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.showFullScreen()
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self._render_gui()
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)

	def _render_gui(self):
		self.box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("success","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(0,0,255,1), stop:1 rgba(0,0,255,0.6));color:white;")
		self.box.addWidget(self.statusBar,0,0,1,1)
		self.tabBar=self._tabBar()
		self.box.addWidget(self.tabBar,0,0,1,1)
		self.setLayout(self.box)
		self.show()

	def _tabBar(self):
		tabBar=QTabWidget()
		for category,icon in self.categories.items():
			tabContent=QWidget()
			icn=QtGui.QIcon.fromTheme(icon)
			vbox=QGridLayout()
			apps=self._get_category_apps(category)
			row=0
			col=0
			maxCol=int(self.width()/128)
			self._debug("Size: %s\nCols: %s"%(self.width(),maxCol))
			sigmap_run=QSignalMapper(self)
			sigmap_run.mapped[QString].connect(self._launch)
			for appName,appIcon in apps.items():
				if QtGui.QIcon.hasThemeIcon(appIcon):
					icnApp=QtGui.QIcon.fromTheme(appIcon)
				else:
					continue
				self._debug("Adding %s"%appName)
				btnApp=QPushButton()
				btnApp.setIcon(icnApp)
				btnApp.setIconSize(QSize(128,128))
				btnApp.setToolTip(appName)
#				btnApp.clicked.connect(lambda: self._launch(appName))
				sigmap_run.setMapping(btnApp,appName)
				btnApp.clicked.connect(sigmap_run.map)
				vbox.addWidget(btnApp,row,col,Qt.Alignment(-1))
				col+=1
				if col==maxCol:
					col=0
					row+=1

			tabContent.setLayout(vbox)
			tabBar.addTab(tabContent,icn,(""))
		return (tabBar)

	def _get_category_apps(self,category):
		apps={}
		applist=App2Menu.app2menu().get_apps_from_category(category)
		for key,app in applist.items():
			apps[app['exe']]=app['icon']
		return (apps)

	def _launchZone(self):
#		self.winID=int(Qzone.winId())
#		subZone=QtGui.QWindow.fromWinId(self.winID)
		tabContent=QWidget()
		box=QVBoxLayout()
		wid=0
		count=0
		while not wid and count<=50:
			p_wid=subprocess.run(["xdotool","search","--any","--pid","%s"%self.pid],stdout=subprocess.PIPE)
			wid=p_wid.stdout.decode()
			time.sleep(0.1)
			count+=1
		if not wid:
			p_wid=subprocess.run(["xdotool","getactivewindow"],stdout=subprocess.PIPE)
			wid=p_wid.stdout.decode()
		self._debug("W: %s"%wid)
		subZone=QtGui.QWindow.fromWinId(int(wid))
		zone=QWidget.createWindowContainer(subZone)
		zone.setParent(self)
		box.addWidget(zone)
		tabContent.setLayout(box)
		self.tabBar.addTab(tabContent,"R")
		os.environ['DISPLAY']=":13"
		subprocess.Popen(["ratpoison"],stdin=None,stdout=None,stderr=None,shell=False)
#		self.box.show()

	def _launch2(self,app):
		th_run=th_runApp(app)
		th_run.start()


	def _launch(self,app):
		self.tabBar.setCurrentIndex(3)
		os.environ["HOME"]="/home/lliurex"
		os.environ["XAUTHORITY"]="/home/lliurex/.Xauthority"
		if self.pid==0:
			args=[]
			self._debug("Width: %s Height: %s"%(self.tabBar.width(),self.tabBar.height()))
			xephyr_cmd=["Xephyr",
			"-br",
			"-ac",
			"-screen",
			"%sx%s"%(self.tabBar.width(),self.tabBar.height()),
			":13"]

			p_pid=subprocess.Popen(xephyr_cmd)
			self.pid=p_pid.pid
			self._launchZone()
		self._launch2(app)



#_debug("Init %s"%sys.argv)
app=QApplication(["Test Kid Launcher"])
testKidLauncher=testKid()
app.exec_()
