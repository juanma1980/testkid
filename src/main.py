#!/usr/bin/env python3
import getpass
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QStackedWidget,QGridLayout,QTabBar,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
import gettext
import subprocess
from edupals.ui import QAnimatedStatusBar
from app2menu import App2Menu
import time
from libAppRun import appRun
QString=type("")
QInt=type(0)
TAB_BTN_SIZE=96
BTN_SIZE=128

class testKid(QWidget):
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self.dbg=True
		self.pid=0
		self.app_icons={}
		self.tab_icons={}
		self.tab_id={0:{'index':0}}
		self.id=0
		self.currentTab=0
		self.categories={"lliurex-infantil":"applications-games","network":"applications-internet","education":"applications-education"}
		self.sigmap_tabSelect=QSignalMapper(self)
		self.sigmap_tabSelect.mapped[QInt].connect(self._on_tabSelect)
		self.sigmap_tabRemove=QSignalMapper(self)
		self.sigmap_tabRemove.mapped[QInt].connect(self._on_tabRemove)
		self.previousIcon=QtGui.QIcon.fromTheme("go-previous")
		btnPrevious=QPushButton()
		btnPrevious.setIcon(self.previousIcon)
		btnPrevious.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		self.sigmap_tabSelect.setMapping(btnPrevious,0)
		btnPrevious.clicked.connect(self.sigmap_tabSelect.map)
		self.homeIcon=QtGui.QIcon.fromTheme("go-home")
		btnHome=QPushButton()
		btnHome.setIcon(self.homeIcon)
		btnHome.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
#		self.tab_icons['home']={"show":btnHome,"close":btnPrevious}
		self.tab_id['home']={'index':0,'pid':0,'show':btnHome,'close':btnPrevious}
		self.closeIcon=QtGui.QIcon.fromTheme("window-close")
#		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.showFullScreen()
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.display=os.environ['DISPLAY']
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
		self.tabBar.currentChanged.connect(lambda:self._on_tabChanged(False))
		self.box.addWidget(self.tabBar,0,0,1,1)
		self.setLayout(self.box)
	#def _render_gui

	def _tabBar(self):
		tabBar=QTabWidget()
		tabScroll=QWidget()
		scrollArea=QScrollArea(tabScroll)
		tabContent=QWidget()
		vbox=QGridLayout()
		row=0
		col=0
		scr=app.primaryScreen()
		w=scr.size().width()-BTN_SIZE
		h=scr.size().height()-(2*BTN_SIZE)
		maxCol=int(w/BTN_SIZE)-3
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
				btnApp.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
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
		tabBar.addTab(tabScroll,"")
		tabBar.tabBar().setTabButton(0,QTabBar.LeftSide,self.tab_id['home']['show'])
		scrollArea.setGeometry(QRect(0,0,w,h))
		return (tabBar)
	#def _tabBar

	def _on_tabChanged(self,remove=True):
		if remove==False:
			self._debug("Current: %s"%self.currentTab)
			index=self._get_tabId_from_index(self.currentTab)
			index=self.currentTab
			key='show'
			if self.currentTab==0:
				index='home'
				key='close'
			self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
			index=self._get_tabId_from_index(self.tabBar.currentIndex())
			self.currentTab=self.tabBar.currentIndex()
#			index=self.currentTab
			key='close'
			if self.currentTab==0:
				index='home'
				key='show'
			self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
			self._debug("New: %s key:%s"%(self.currentTab,key))

	def _on_tabSelect(self,index):
		self._debug("Select tab: %s"%index)
		self.tabBar.setCurrentIndex(self.tab_id[index]['index'])

	def _on_tabRemove(self,index):
		self._debug("Remove tab: %s"%index)
		self.tabBar.blockSignals(True)
		self.tabBar.removeTab(self.tab_id[index]['index'])
		for idx in range(index+1,len(self.tab_id)):
			if idx in self.tab_id.keys():
				self._debug("Reasign %s"%(self.tab_id[idx]['index']))
				self.tab_id[idx]['index']=self.tab_id[idx]['index']-1
				self._debug("Reasigned %s -> %s"%(idx,self.tab_id[idx]['index']))
		self.tab_id[index]={}
		self.currentTab=self._get_tabId_from_index(self.tabBar.currentIndex())
		self.tabBar.blockSignals(False)
		self._debug("Removed tab: %s"%index)

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
		btn=QPushButton()
		btn.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		btn.setIcon(icn)
		self.id+=1
		self.tab_id[self.id]={'index':self.tabBar.count(),'pid':0}
		self.sigmap_tabSelect.setMapping(btn,self.tabBar.count())
		btn.clicked.connect(self.sigmap_tabSelect.map)
		btn_close=QPushButton()
		btn_close.setIcon(self.closeIcon)
		btn_close.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		self.sigmap_tabRemove.setMapping(btn_close,self.id)
		btn_close.clicked.connect(self.sigmap_tabRemove.map)
		self.tab_id[self.id]={'index':self.tabBar.count(),'pid':0,'show':btn,'close':btn_close}
#		self.tab_icons[self.tabBar.count()]={"show":btn,"close":btn_close}
		self.tabBar.addTab(tabContent,"")
		return(tabContent)
	#def _launchZone

	def _launch(self,app):
		self.tabBar.setTabIcon(0,self.previousIcon)
		self._debug("Tabs: %s"%self.tabBar.count())
		tabCount=self.tabBar.count()
		os.environ["HOME"]="/home/lliurex"
		os.environ["XAUTHORITY"]="/home/lliurex/.Xauthority"
		self.display,self.pid=self.runner.new_Xephyr(self.tabBar)
		tabRun=self._launchZone(app)
		self.tabBar.setCurrentIndex(tabCount)
		self.runner.launch(app,self.display)
	#def _launch

	def _get_tabId_from_index(self,index):
		idx=0
		self._debug("Search id for display: %s"%(index))
		for key,data in self.tab_id.items():
			if 'index' in data.keys():
				if index==data['index']:
					print(key)
					idx=key
					break
		if index==0:
			idx=0
		self._debug("Find idx: %s For index: %s"%(idx,index))
		return idx

def _define_css():
	css="""
	QPushButton{
		padding: 0px;
		margin:0px;
		border:0px;
	}
	QPushButton:active{
		padding: 6px;
		margin:6px;
		font: 14px Roboto;
		color:black;
		background:none;
	}
	QStatusBar{
		background:red;
		color:white;
		font: 14px Roboto bold;
	}
	QLabel{
		padding:6px;
		margin:6px;
	}

	#dlgLabel{
		font:12px Roboto;
		margin:0px;
		border:0px;
		padding:3px;
	}
	
	QLineEdit{
		border:0px;
		border-bottom:1px solid grey;
		padding:1px;
		font:14px Roboto;
		margin-right:6px;
	}
	"""
	return(css)
	#def _define_css


#_debug("Init %s"%sys.argv)
app=QApplication(["Test Kid Launcher"])
testKidLauncher=testKid()
app.instance().setStyleSheet(_define_css())
app.exec_()
