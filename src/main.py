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
import signal
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
		self.categories={}
		self.desktops={}
		self.pid=0
		self.app_icons={}
		self.tab_icons={}
		self.tab_id={}
		self.focusWidgets=[]
		self.id=0
		self.firstLaunch=True
		self.currentTab=0
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
		self.tab_id[0]={'index':self.id,'thread':0,'xephyr':None,'show':btnHome,'close':btnPrevious}
		self.closeIcon=QtGui.QIcon.fromTheme("window-close")
#		self.setWindowIcon(QtGui.QIcon("/usr/share/icons/hicolor/48x48/apps/x-appimage.png"))
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setWindowState(Qt.WindowFullScreen)
		self.display=os.environ['DISPLAY']
		self.runner=appRun()
		self._read_config()
		self._render_gui()
	#def init
	
	def _debug(self,msg):
		if self.dbg:
			print("%s"%msg)
	#def _debug

	def _read_config(self):
		data=self.runner.get_apps()
		self.categories=data['categories']
		self.desktops=data['desktops']

	def _render_gui(self):
		self.show()
		self.box=QGridLayout()
		self.tabBar=self._tabBar()
		self.tabBar.currentChanged.connect(lambda:self._on_tabChanged(False))
		self.box.addWidget(self.tabBar,0,0,1,1)
		self.setLayout(self.box)
		self.tabBar.setFocusPolicy(Qt.NoFocus)
		self._debug("Focus to %s"%self.focusWidgets[0])
		self.focusWidgets[0].setFocus()
	#def _render_gui

	def _tabBar(self):
		row=0
		col=0
		def _add_widgets():
			nonlocal row
			nonlocal col
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
				self.focusWidgets.append(btnApp)
				sigmap_run.setMapping(btnApp,appName)
				btnApp.clicked.connect(sigmap_run.map)
				vbox.addWidget(btnApp,row,col,Qt.Alignment(-1))
				col+=1
				if col==maxCol:
					col=0
					row+=1
		tabBar=QTabWidget()
		tabScroll=QWidget()
		tabScroll.setFocusPolicy(Qt.NoFocus)
		scrollArea=QScrollArea(tabScroll)
		scrollArea.setFocusPolicy(Qt.NoFocus)
		tabContent=QWidget()
		vbox=QGridLayout()
		scr=app.primaryScreen()
		w=scr.size().width()-BTN_SIZE
		h=scr.size().height()-(2*BTN_SIZE)
		maxCol=int(w/BTN_SIZE)-3
		self._debug("Size: %s\nCols: %s"%(self.width(),maxCol))
		for category in self.categories:
			apps=self._get_category_apps(category)
			_add_widgets()
		for desktop in self.desktops:
			apps=self._get_desktop_apps(desktop)
			_add_widgets()

		tabContent.setLayout(vbox)
		scrollArea.setWidget(tabContent)
		scrollArea.alignment()
		tabBar.addTab(tabScroll,"")
		tabBar.tabBar().setTabButton(0,QTabBar.LeftSide,self.tab_id[0]['show'])
		tabBar.tabBar().tabButton(0,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		scrollArea.setGeometry(QRect(0,0,w,h))
		return (tabBar)
	#def _tabBar

	def _on_tabChanged(self,remove=True):
		self._debug("From Tab: %s"%self.currentTab)
		index=self._get_tabId_from_index(self.currentTab)
		self._debug("Tab Index: %s"%index)
		key='show'
		if self.currentTab==0:
			index=0
			key='close'
		self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
		self.tabBar.tabBar().tabButton(self.currentTab,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		self.runner.send_signal_to_thread("stop",self.tab_id[index]['thread'])
		index=self._get_tabId_from_index(self.tabBar.currentIndex())
		self.currentTab=self.tabBar.currentIndex()
		key='close'
		if self.currentTab==0:
			index=0
			key='show'
		self._debug("New Tab Index: %s"%self.tab_id[index])
		self._debug("New index: %s"%index)
		self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
		self.tabBar.tabBar().tabButton(self.currentTab,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		self.runner.send_signal_to_thread("cont",self.tab_id[index]['thread'])
		self._debug("New Current Tab: %s Icon:%s"%(self.currentTab,key))
	#def _on_tabChanged

	def _on_tabSelect(self,index):
		self._debug("Select tab: %s"%index)
		self.tabBar.setCurrentIndex(self.tab_id[index]['index'])
	#def _on_tabSelect

	def _on_tabRemove(self,index):
		self._debug("Remove tab: %s"%index)
		self.tabBar.blockSignals(True)
		self.tabBar.removeTab(self.tab_id[index]['index'])
		self.runner.send_signal_to_thread("kill",self.tab_id[index]['thread'])
		self.runner.send_signal_to_thread("term",self.tab_id[index]['xephyr'])
		for idx in range(index+1,len(self.tab_id)):
			if idx in self.tab_id.keys():
				self._debug("%s"%self.tab_id)
				if 'index' in self.tab_id[idx].keys():
					self._debug("Reasign %s"%(self.tab_id[idx]['index']))
					self.tab_id[idx]['index']=self.tab_id[idx]['index']-1
					self._debug("Reasigned %s -> %s"%(idx,self.tab_id[idx]['index']))
		self.tab_id[index]={}
		self.tabBar.blockSignals(False)
		self.currentTab=self._get_tabId_from_index(self.tabBar.currentIndex())
		self._on_tabChanged()
		self._debug("Removed tab: %s"%index)
	#def _on_tabRemove

	def _get_category_apps(self,category):
		apps=self.runner.get_category_apps(category.lower())
		return (apps)
	#def _get_category_apps
	
	def _get_desktop_apps(self,desktop):
		apps=self.runner.get_desktop_app(desktop)
		return (apps)
	#def _get_category_apps

	def _launchZone(self,app):
		tabContent=QWidget()
		box=QVBoxLayout()
		wid=self.runner.get_wid("Xephyr on",self.display)
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
		self._debug("New Tab id %s"%self.id)
		self.sigmap_tabSelect.setMapping(btn,self.id)
		btn.clicked.connect(self.sigmap_tabSelect.map)
		btn_close=QPushButton()
		btn_close.setIcon(self.closeIcon)
		btn_close.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		self.sigmap_tabRemove.setMapping(btn_close,self.id)
		btn_close.clicked.connect(self.sigmap_tabRemove.map)
		self.tab_id[self.id]={'index':self.tabBar.count(),'thread':None,'show':btn,'close':btn_close}
		self.tabBar.addTab(tabContent,"")
		return(tabContent)
	#def _launchZone

	def _launch(self,app):
		self.tabBar.setTabIcon(0,self.previousIcon)
		self._debug("Tabs: %s"%self.tabBar.count())
		#Tabs BEFORE new tab is added
		tabCount=self.tabBar.count()
		os.environ["HOME"]="/home/lliurex"
		os.environ["XAUTHORITY"]="/home/lliurex/.Xauthority"
		self.display,self.pid,x_pid=self.runner.new_Xephyr(self.tabBar)
		tabRun=self._launchZone(app)
		self.tab_id[self.id]['thread']=self.runner.launch(app,self.display)
		self.tab_id[self.id]['xephyr']=x_pid
		#For some reason on first launch the tab doesn't loads the content until there's a tab switch
		#This is a quick and dirty fix...
		if self.firstLaunch:
			self.firstLaunch=False
			self.tabBar.tabBar().setTabButton(self.id,QTabBar.LeftSide,self.tab_id[self.id]['close'])
			self.tabBar.tabBar().setTabButton(0,QTabBar.LeftSide,self.tab_id[0]['close'])
			self.currentTab=tabCount
			self.tabBar.blockSignals(True)
			self.tabBar.setCurrentIndex(1)
			self.tabBar.blockSignals(False)
		else:
			self.tabBar.setCurrentIndex(tabCount)
	#def _launch

	def _get_tabId_from_index(self,index):
		idx=index
		self._debug("Search id for display: %s"%(index))
		self._debug("%s"%(self.tab_id))
		for key,data in self.tab_id.items():
			if 'index' in data.keys():
				if index==data['index']:
					idx=key
					break
		self._debug("Find idx: %s For index: %s"%(idx,index))
		return idx
	#def _get_tabId_from_index
#class testKid

def _define_css():
	css="""
	QPushButton{
		padding:10px;
		margin:0px;
		border:0px;
	}
	QPushButton:active{
		font: 14px Roboto;
		color:black;
		background:none;
	}
	QPushButton:focus{
		border:2px solid grey;
		border-radius:25px;
	}
	"""
	return(css)
	#def _define_css


#_debug("Init %s"%sys.argv)
app=QApplication(["Test Kid Launcher"])
signal.signal(signal.SIGINT, lambda *a: app.quit())
testKidLauncher=testKid()
app.instance().setStyleSheet(_define_css())
app.exec_()
