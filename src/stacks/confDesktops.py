#!/usr/bin/python3

import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QGridLayout,QComboBox,QFileDialog
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,pyqtSignal,QSignalMapper,QProcess,QEvent,QSize
from app2menu import App2Menu
from appconfig.appConfigStack import appConfigStack as confStack
from urllib.request import Request,urlopen,urlretrieve
from bs4 import BeautifulSoup
import re
import gettext
_ = gettext.gettext

class confDesktops(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("confDesktops Load")
		self.menu=App2Menu.app2menu()
		home=os.environ['HOME']
#		self.menu.desktoppath="%s/.local/share/applications/"%home
		self.menu.desktoppath="/usr/share/runomatic/applications"
		self.default_icon='shell'
		self.app_icon='shell'
		self.menu_description=(_("Add new launchers"))
		self.description=(_("Add custom launcher"))
		self.icon=('org.kde.plasma.quicklaunch')
		self.tooltip=(_("From here you can add a custom launcher"))
		self.defaultName=""
		self.defaultExec=""
		self.defaultDesc=""
		self.index=3
		self.enabled=True
		self.level='user'
	#def __init__
		
	def _debug(self,msg):
		if self.dbg:
			print("ConfDesktops: %s"%msg)
	#def _debug

	def initScreen(self):
		self.default_icon='shell'
		self.defaultName=""
		self.defaultExec=""
		self.defaultDesc=""
		self.filename=""
	#def initScreen


	def _load_screen(self):
		box=QGridLayout()
		lbl_txt=QLabel(_("From here you can add Launchers"))
		box.addWidget(lbl_txt)
		lbl_icon=QLabel(_("Icon: "))
		box.addWidget(lbl_icon,1,2,1,1)
		self.btn_icon=QPushButton()
		self.btn_icon.setObjectName("btnIcon")
		icn_desktop=QtGui.QIcon.fromTheme("shell")
		self.btn_icon.setIcon(icn_desktop)
		self.btn_icon.setIconSize(QSize(64,64))
		self.btn_icon.setToolTip(_("Push to change icon"))
		self.btn_icon.clicked.connect(lambda:self._file_chooser(widget=self.btn_icon,path="/usr/share/icons",imgDialog=True))
		box.addWidget(self.btn_icon,2,2,3,1,Qt.AlignTop)
		lbl_name=QLabel(_("Name: "))
		box.addWidget(lbl_name,1,0,1,2)
		self.inp_name=QLineEdit()
		self.inp_name.setPlaceholderText(_("Desktop name"))
		self.inp_name.setToolTip(_("Insert desktop name"))
		box.addWidget(self.inp_name,2,0,1,2)
		lbl_exec=QLabel(_("Executable: "))
		box.addWidget(lbl_exec,3,0,1,2)
		self.inp_exec=QLineEdit()
		self.inp_exec.editingFinished.connect(self._get_icon)
		self.inp_exec.setPlaceholderText(_("Executable path"))
		self.inp_exec.setToolTip(_("Insert path to the executable"))
		box.addWidget(self.inp_exec,4,0,1,1,Qt.Alignment(0))
		btn_exec=QPushButton("...")
		btn_exec.setObjectName("btnFile")
		btn_exec.setToolTip(_("Press button to select an executable"))
		btn_exec.clicked.connect(lambda:self._file_chooser(widget=self.inp_exec,path="/usr/bin"))
		box.addWidget(btn_exec,4,1,1,1,Qt.Alignment(1))
		lbl_desc=QLabel(_("Description: "))
		box.addWidget(lbl_desc,5,0,1,2)
		self.inp_desc=QLineEdit()
		self.inp_desc.setPlaceholderText(_("Description"))
		self.inp_desc.setToolTip(_("Insert a description for the app"))
		box.addWidget(self.inp_desc,6,0,1,3)
		self.setLayout(box)
	
	def _file_chooser(self,widget=None,path=None,imgDialog=None):
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if imgDialog:
			fdia.setNameFilter(_("images(*.png *.xpm *jpg)"))
		else:
			fdia.setNameFilter(_("All files(*.*)"))
		if path:
			self._debug("Set path to %s"%path)
			fdia.setDirectory(path)
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			if widget:
				if imgDialog:
					self.app_icon=fdia.selectedFiles()[0]
					icn=QtGui.QIcon(self.app_icon)
					widget.setIcon(icn)
				else:
					widget.setText(fchoosed)
			self.btn_ok.setEnabled(True)
			self.btn_cancel.setEnabled(True)
			return(fchoosed)
	#def _file_chooser

	def _get_icon(self):
		exeLine=self.inp_exec.text().split(' ')
		if 'firefox' not in exeLine and 'chromium' not in exeLine and 'chrome' not in exeLine:
			return
		path=exeLine[-1]
		path=path.split(" ")[0]
		splitPath=path.split("/")
		if "://" in path:
			path=("%s//%s"%(splitPath[0],splitPath[1]))
		else:
			path=("http://%s"%(splitPath[0]))
		try:
			req=Request(path)
		except:
			return
		ico=""
		try:
			content=urlopen(req).read()
			soup=BeautifulSoup(content,'html.parser')
			favicon=soup.head
			for link in favicon.find_all(href=re.compile("favicon")):
				fname=link
				if "favicon" in str(fname):
					splitName=str(fname).split(" ")
					for splitWord in splitName:
						if splitWord.startswith("href="):
							ico=splitWord.split("\"")[1].split("?")[0]
							outputIco="/tmp/%s.ico"%splitPath[0]
							try:
								urlretrieve(ico,outputIco)
							except:
								return
							self.app_icon=ico
							icn=QtGui.QIcon(outputIco)
							self.btn_icon.setIcon(icn)
							break
		except:
			self._debug("Couldn't open %s"%url)
	#def _get_icon


	def updateScreen(self):
		self.inp_name.setText(self.defaultName)
		self.inp_exec.setText(self.defaultExec)
		self.inp_desc.setText(self.defaultDesc)
		self.app_icon=self.default_icon
		icn=QtGui.QIcon.fromTheme(self.app_icon)
		self.btn_icon.setIcon(icn)
	#def updateScreen

	def writeConfig(self):
		categories=[]
		desktop={}
		desktop['Categories']='run-o-matic;'
		desktop['NoDisplay']='True'
		desktop['Name']=self.inp_name.text()
		desktop['Exec']=self.inp_exec.text()
		desktop['Icon']=self.app_icon
		desktop['Comment']=self.inp_desc.text()
		if self.filename:
			filename=os.path.join(self.menu.desktoppath,"%s"%self.filename)
		else:
			filename=os.path.join(self.menu.desktoppath,"%s.desktop"%self.inp_name.text().lower().replace(" ","_"))
		self._debug("File %s"%filename)
		self._debug("Saving %s"%desktop)
		self.changes=False
		try:
			subprocess.check_call(["pkexec","/usr/share/app2menu/app2menu-helper.py",desktop['Name'],desktop['Icon'],desktop['Comment'],desktop['Categories'],desktop['Exec'],filename])
			self.btn_ok.setEnabled(False)
			self.btn_cancel.setEnabled(False)
			self.refresh=True
			retval=True
			if self.editBtn:
				self.editBtn=False
				self.default_icon='shell'
				self.defaultName=""
				self.defaultExec=""
				self.defaultDesc=""
				self.stack.gotoStack(idx=2,parms=self.editBtn)
		except Exception as e:
			self._debug(e)

	#def writeChanges

	def setParms(self,parms):
		self._debug("Loading %s"%parms)
		desktop=self.menu.get_desktop_info(parms)
		self.filename=os.path.basename(parms)
		self.defaultName=desktop['Name']
		self.defaultExec=desktop['Exec']
		self.defaultDesc=desktop['Comment']
		self.default_icon=desktop['Icon']

		self.inp_name.setText(desktop['Name'])
		self.inp_exec.setText(desktop['Exec'])
		self.inp_desc.setText(desktop['Comment'])
		self.app_icon=desktop['Icon']
		if os.path.isfile(desktop['Icon']):
			icn=QtGui.QIcon(desktop['Icon'])
			pass
		else:
			icn=QtGui.QIcon.fromTheme(desktop['Icon'])
		self.btn_icon.setIcon(icn)
		self.btn_ok.setEnabled(False)
		self.btn_cancel.setEnabled(False)
		self.editBtn=parms
